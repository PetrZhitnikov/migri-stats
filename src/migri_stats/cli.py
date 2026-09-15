from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from migri_stats.core import DEFAULT_START, refresh


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download and visualize Migri citizenship application statistics."
    )
    parser.add_argument("--start", default=DEFAULT_START, help="first month (YYYY-MM)")
    parser.add_argument("--end", help="last month (YYYY-MM); defaults to latest")
    parser.add_argument("--csv", type=Path, default=Path("data/migri_stats.csv"))
    parser.add_argument("--html", type=Path, default=Path("migri_stats.html"))
    parser.add_argument("--dataset-url", help="override automatic dataset discovery")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    stats, figure = refresh(start=args.start, end=args.end, dataset_url=args.dataset_url)

    args.csv.parent.mkdir(parents=True, exist_ok=True)
    args.html.parent.mkdir(parents=True, exist_ok=True)
    stats.to_csv(args.csv, index=False)
    figure.write_html(args.html, include_plotlyjs="cdn")

    latest = stats.iloc[-1]
    print(f"Wrote {len(stats)} months to {args.csv} and {args.html}")
    print(
        f"Latest ({latest['month']:%Y-%m}): "
        f"{latest['applications']:,} applications, "
        f"{latest['decisions']:,} decisions, "
        f"ratio {latest['speed_ratio']:.2f}, "
        f"queue reduction {latest['queue_reduction']:,}"
    )
    return 0
