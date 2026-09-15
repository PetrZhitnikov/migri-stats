from typing import Any

import pytest

from migri_stats import add_metrics, monthly_stats

AUGUST_2026_DATA: dict[str, Any] = {
    "applications": {
        "679": {
            "group": "MONTH",
            "count": 522,
            "children": {
                "23331": {
                    "group": "ASIARYHMA_ID",
                    "count": 522,
                    "children": {"42": {"group": "ASIA_TYYPPI_ID", "count": 522}},
                }
            },
        }
    },
    "decisions": {
        "679": {
            "group": "MONTH",
            "count": 1179,
            "children": {
                "23331": {
                    "group": "ASIARYHMA_ID",
                    "count": 1179,
                    "children": {"42": {"group": "ASIA_TYYPPI_ID", "count": 1179}},
                }
            },
        }
    },
}


def test_august_2026_stats_match_migri_values() -> None:
    stats = add_metrics(monthly_stats(AUGUST_2026_DATA, start="2026-08"))

    assert stats.loc[0, "month"].strftime("%Y-%m") == "2026-08"
    assert stats.loc[0, "applications"] == 522
    assert stats.loc[0, "decisions"] == 1179
    assert stats.loc[0, "speed_ratio"] == pytest.approx(1179 / 522)
    assert stats.loc[0, "queue_reduction"] == 657
