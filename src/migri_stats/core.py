from __future__ import annotations

import gzip
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import Any, cast
from urllib.parse import urljoin
from urllib.request import Request, urlopen

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

DEFAULT_BASE_URL = "https://tilastot.migri.fi/"
DEFAULT_HIERARCHY = ("23331", "42")
DEFAULT_START = "2015-01"

RawData = dict[str, Any]


class MigriStatsError(RuntimeError):
    """Raised when the Migri data source cannot be discovered or parsed."""


def _read_bytes(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "Accept-Encoding": "gzip",
            "User-Agent": "migri-stats/0.1 (+https://github.com/PetrZhitnikov/migri-stats)",
        },
    )
    with urlopen(request, timeout=30) as response:  # noqa: S310 - trusted Migri URL
        body = cast(bytes, response.read())
        if response.headers.get("Content-Encoding") == "gzip":
            return gzip.decompress(body)
        return body


def discover_dataset_url(base_url: str = DEFAULT_BASE_URL) -> str:
    """Find the current versioned JSON dataset used by Migri's statistics site."""
    index_html = _read_bytes(base_url).decode("utf-8")
    script_match = re.search(r'<script[^>]+src=["\']([^"\']*index-[^"\']+\.js)["\']', index_html)
    if script_match is None:
        raise MigriStatsError("Could not find Migri's application bundle")

    script_url = urljoin(base_url, script_match.group(1))
    bundle = _read_bytes(script_url).decode("utf-8")
    assets = sorted(set(re.findall(r'["\']([0-9a-f]{32}\.json)["\']', bundle)))
    if len(assets) != 1:
        raise MigriStatsError(f"Expected one Migri JSON dataset, found {len(assets)}")
    return cast(str, urljoin(script_url, assets[0]))


def download_data(dataset_url: str | None = None) -> RawData:
    """Download Migri's raw statistics dataset."""
    url = dataset_url or discover_dataset_url()
    data = json.loads(_read_bytes(url))
    if not isinstance(data, dict) or not {"applications", "decisions"} <= data.keys():
        raise MigriStatsError("Migri dataset has an unexpected structure")
    return data


def _month_index(period: str) -> int:
    try:
        parsed = datetime.strptime(period, "%Y-%m")
    except ValueError as error:
        raise ValueError(f"Expected a month in YYYY-MM format, got {period!r}") from error
    return (parsed.year - 1970) * 12 + parsed.month - 1


def _month_timestamp(index: int) -> pd.Timestamp:
    year_offset, month_offset = divmod(index, 12)
    return pd.Timestamp(year=1970 + year_offset, month=month_offset + 1, day=1)


def _count_for(
    data: Mapping[str, Any], case_type: str, month_index: int, hierarchy: Sequence[str]
) -> int:
    node = data.get(case_type, {}).get(str(month_index))
    for item_id in hierarchy:
        if not isinstance(node, Mapping):
            return 0
        node = node.get("children", {}).get(item_id)
    if not isinstance(node, Mapping):
        return 0
    return int(node.get("count", 0))


def monthly_stats(
    data: Mapping[str, Any],
    hierarchy: Sequence[str] = DEFAULT_HIERARCHY,
    *,
    start: str = DEFAULT_START,
    end: str | None = None,
) -> pd.DataFrame:
    """Extract monthly application and decision counts for a Migri hierarchy."""
    available = {
        int(index)
        for case_type in ("applications", "decisions")
        for index in data.get(case_type, {})
    }
    columns = ["month", "applications", "decisions"]
    if not available:
        return pd.DataFrame(columns=columns)

    first = _month_index(start)
    last = _month_index(end) if end is not None else max(available)
    if first > last:
        raise ValueError("start must not be after end")

    rows = [
        {
            "month": _month_timestamp(index),
            "applications": _count_for(data, "applications", index, hierarchy),
            "decisions": _count_for(data, "decisions", index, hierarchy),
        }
        for index in range(first, last + 1)
    ]
    return pd.DataFrame(rows, columns=columns)


def add_metrics(stats: pd.DataFrame) -> pd.DataFrame:
    """Add throughput ratio and monthly/cumulative queue-reduction estimates."""
    result = stats.copy()
    applications = result["applications"].astype("float64")
    result["speed_ratio"] = result["decisions"].div(applications.where(applications.ne(0)))
    result["queue_reduction"] = result["decisions"] - result["applications"]
    result["cumulative_queue_reduction"] = result["queue_reduction"].cumsum()
    return result


def build_figure(stats: pd.DataFrame) -> Figure:
    """Build an interactive, faceted Plotly Express chart."""
    required = {"speed_ratio", "queue_reduction", "cumulative_queue_reduction"}
    prepared = stats if required <= set(stats.columns) else add_metrics(stats)

    volumes = prepared.melt(
        id_vars="month",
        value_vars=["applications", "decisions"],
        var_name="metric",
        value_name="value",
    )
    volumes["panel"] = "Applications and decisions"
    reduction = prepared[["month", "queue_reduction"]].rename(columns={"queue_reduction": "value"})
    reduction["metric"] = "queue reduction"
    reduction["panel"] = "Queue reduction"
    ratio = prepared[["month", "speed_ratio"]].rename(columns={"speed_ratio": "value"})
    ratio["metric"] = "speed ratio"
    ratio["panel"] = "Speed ratio"
    accumulation = prepared[["month", "cumulative_queue_reduction"]].rename(
        columns={"cumulative_queue_reduction": "value"}
    )
    accumulation["metric"] = "cumulative queue reduction"
    accumulation["panel"] = "Cumulative queue reduction"
    chart_data = pd.concat([volumes, reduction, ratio, accumulation], ignore_index=True)

    figure = px.bar(
        chart_data,
        x="month",
        y="value",
        color="metric",
        facet_row="panel",
        barmode="group",
        category_orders={
            "panel": [
                "Cumulative queue reduction",
                "Speed ratio",
                "Queue reduction",
                "Applications and decisions",
            ]
        },
        color_discrete_map={
            "applications": "#3b9880",
            "decisions": "#b63847",
            "queue reduction": "#4589bc",
            "speed ratio": "#f99b1f",
            "cumulative queue reduction": "#540f5f",
        },
        labels={"month": "Month", "value": "Value", "metric": "Metric"},
        title="Migri applications and decision throughput",
    )
    figure.update_yaxes(matches=None)
    figure.for_each_annotation(
        lambda annotation: annotation.update(text=annotation.text.split("=")[-1])
    )
    figure.update_layout(height=1050, hovermode="x unified", legend_title_text="")
    return figure


def refresh(
    *,
    hierarchy: Sequence[str] = DEFAULT_HIERARCHY,
    start: str = DEFAULT_START,
    end: str | None = None,
    dataset_url: str | None = None,
) -> tuple[pd.DataFrame, Figure]:
    """Download, transform, and plot the latest data in one notebook-friendly call."""
    stats = add_metrics(
        monthly_stats(download_data(dataset_url), hierarchy=hierarchy, start=start, end=end)
    )
    return stats, build_figure(stats)
