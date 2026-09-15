import re

import pandas as pd

from migri_stats import add_metrics, build_figure
from migri_stats.report import build_page


def _stats() -> pd.DataFrame:
    return add_metrics(
        pd.DataFrame(
            [
                {"month": pd.Timestamp("2026-01-01"), "applications": 100, "decisions": 80},
                {"month": pd.Timestamp("2026-02-01"), "applications": 120, "decisions": 180},
            ]
        )
    )


def test_figure_contains_the_three_report_sections() -> None:
    figure = build_figure(_stats())

    assert [trace.name for trace in figure.data] == [
        "Applications",
        "Decisions",
        "Speed ratio",
        "Cumulative queue reduction",
    ]
    assert len(figure.layout.annotations) == 3


def test_page_presents_latest_figures_and_download() -> None:
    stats = _stats()

    page = build_page(stats, build_figure(stats))

    assert page.startswith("<!doctype html>")
    assert '<meta name="viewport" content="width=device-width, initial-scale=1">' in page
    assert "<title>Migri citizenship statistics</title>" in page
    assert "Updated through February 2026" in page
    assert ">120<" in page
    assert ">180<" in page
    assert ">1.50×<" in page
    assert ">+60<" in page
    assert 'href="migri-stats.csv"' in page
    assert "not a measured application backlog" in re.sub(r"\s+", " ", page)
