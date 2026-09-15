import json
from pathlib import Path

from migri_stats.cli import main


def test_cli_writes_the_site_page_and_csv(tmp_path: Path) -> None:
    month = {
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
    decision_month = {
        **month,
        "count": 1179,
        "children": {
            "23331": {
                "group": "ASIARYHMA_ID",
                "count": 1179,
                "children": {"42": {"group": "ASIA_TYYPPI_ID", "count": 1179}},
            }
        },
    }
    dataset = tmp_path / "dataset.json"
    dataset.write_text(
        json.dumps({"applications": {"679": month}, "decisions": {"679": decision_month}}),
        encoding="utf-8",
    )
    csv_path = tmp_path / "site" / "migri-stats.csv"
    html_path = tmp_path / "site" / "index.html"

    result = main(
        [
            "--start",
            "2026-08",
            "--dataset-url",
            dataset.as_uri(),
            "--csv",
            str(csv_path),
            "--html",
            str(html_path),
        ]
    )

    assert result == 0
    assert csv_path.read_text(encoding="utf-8").startswith("month,applications,decisions")
    page = html_path.read_text(encoding="utf-8")
    assert page.startswith("<!doctype html>")
    assert "Updated through August 2026" in page
