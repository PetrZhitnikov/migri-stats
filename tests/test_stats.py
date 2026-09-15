from typing import Any

import pytest

from migri_stats import add_metrics, monthly_stats

AUGUST_2026_DATA: dict[str, Any] = {
    "applications": {
        "678": {
            "group": "MONTH",
            "count": 100,
            "children": {
                "23331": {
                    "group": "ASIARYHMA_ID",
                    "count": 100,
                    "children": {"42": {"group": "ASIA_TYYPPI_ID", "count": 100}},
                }
            },
        },
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
        },
    },
    "decisions": {
        "678": {
            "group": "MONTH",
            "count": 150,
            "children": {
                "23331": {
                    "group": "ASIARYHMA_ID",
                    "count": 150,
                    "children": {"42": {"group": "ASIA_TYYPPI_ID", "count": 150}},
                }
            },
        },
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
        },
    },
}


def test_august_2026_stats_and_accumulation_match_expected_values() -> None:
    stats = add_metrics(monthly_stats(AUGUST_2026_DATA, start="2026-07"))
    august = stats.iloc[1]

    assert august["month"].strftime("%Y-%m") == "2026-08"
    assert august["applications"] == 522
    assert august["decisions"] == 1179
    assert august["speed_ratio"] == pytest.approx(1179 / 522)
    assert august["queue_reduction"] == 657
    assert august["cumulative_queue_reduction"] == 707
