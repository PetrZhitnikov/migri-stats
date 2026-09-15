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
import plotly.graph_objects as go
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots

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
    application_months = {int(index) for index in data.get("applications", {})}
    decision_months = {int(index) for index in data.get("decisions", {})}
    available = application_months & decision_months
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
    """Build the three-section interactive report chart."""
    required = {"speed_ratio", "queue_reduction", "cumulative_queue_reduction"}
    prepared = stats if required <= set(stats.columns) else add_metrics(stats)

    figure = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.09,
        row_heights=[0.45, 0.25, 0.30],
        subplot_titles=(
            "Applications and decisions",
            "Decision speed",
            "Cumulative estimated queue reduction",
        ),
    )
    figure.add_trace(
        go.Scatter(
            x=prepared["month"],
            y=prepared["applications"],
            name="Applications",
            mode="lines",
            line={"color": "#25836f", "width": 2.4},
            hovertemplate="%{y:,.0f} applications<extra></extra>",
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=prepared["month"],
            y=prepared["decisions"],
            name="Decisions",
            mode="lines",
            line={"color": "#d65a4a", "width": 2.4},
            hovertemplate="%{y:,.0f} decisions<extra></extra>",
        ),
        row=1,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=prepared["month"],
            y=prepared["speed_ratio"],
            name="Speed ratio",
            mode="lines",
            line={"color": "#d49422", "width": 2.2},
            fill="tozeroy",
            fillcolor="rgba(212, 148, 34, 0.12)",
            hovertemplate="%{y:.2f}×<extra></extra>",
        ),
        row=2,
        col=1,
    )
    figure.add_trace(
        go.Scatter(
            x=prepared["month"],
            y=prepared["cumulative_queue_reduction"],
            name="Cumulative queue reduction",
            mode="lines",
            line={"color": "#6655a5", "width": 2.5},
            fill="tozeroy",
            fillcolor="rgba(102, 85, 165, 0.12)",
            hovertemplate="%{y:+,.0f}<extra></extra>",
        ),
        row=3,
        col=1,
    )
    figure.add_hline(y=1, line_dash="dot", line_color="#8a8f98", row=2, col=1)
    figure.add_hline(y=0, line_dash="dot", line_color="#8a8f98", row=3, col=1)
    figure.update_yaxes(title_text="Cases", rangemode="tozero", row=1, col=1)
    figure.update_yaxes(title_text="Decisions / applications", rangemode="tozero", row=2, col=1)
    figure.update_yaxes(title_text="Cases", zeroline=False, row=3, col=1)
    figure.update_xaxes(title_text="Month", row=3, col=1)
    figure.update_layout(
        height=900,
        template="plotly_white",
        hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.04, "x": 0},
        margin={"l": 72, "r": 32, "t": 86, "b": 64},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#fbfaf7",
        font={"family": "Inter, system-ui, sans-serif", "color": "#28302d"},
    )
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
