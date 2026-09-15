# migri-stats

Download monthly Finnish Immigration Service (Migri) citizenship application and decision
statistics, calculate simple throughput metrics, and generate an interactive Plotly chart.

By default, the project uses Migri hierarchy `23331/42` from January 2015 through the latest
available month.

## Setup and run

```bash
uv sync --group dev --group notebook
uv run migri-stats
```

The command creates:

- `data/migri_stats.csv` with normalized monthly data and calculated metrics
- `migri_stats.html` with a responsive report and interactive Plotly visualization

A checked-in snapshot is available in [`reports/`](reports/README.md).

Select a date range or custom output locations when needed:

```bash
uv run migri-stats --start 2024-01 --end 2026-08 \
  --csv data/throughput.csv --html throughput.html
```

## Notebook helpers

Start JupyterLab with `uv run --group notebook jupyter lab`, then:

```python
from migri_stats import add_metrics, build_figure, download_data, monthly_stats, refresh

# Convenient all-in-one path
stats, figure = refresh(start="2024-01", end="2026-08")
stats.tail()
figure.show()

# Or inspect each step
raw = download_data()
monthly = monthly_stats(raw, start="2024-01")
stats = add_metrics(monthly)
figure = build_figure(stats)
```

The returned pandas DataFrame has these columns:

- `month`
- `applications`
- `decisions`
- `speed_ratio`: decisions divided by applications
- `queue_reduction`: decisions minus applications; positive values indicate a smaller estimated
  queue for that month
- `cumulative_queue_reduction`: running sum of `queue_reduction` from the selected start month

For August 2026 the source data contains 522 applications and 1,179 decisions. This produces a
speed ratio of about 2.26 and an estimated queue reduction of 657.

## Important interpretation note

Migri states that application and decision statistics cannot be compared as if they represented
the same cases: an application recorded in one month may be decided in a later month. Therefore,
`speed_ratio` is a monthly throughput indicator, and `queue_reduction` is an estimate rather than
a measured application backlog.

Sources:

- [Migri statistics](https://tilastot.migri.fi/#applications/23331/42?l=en&start=540)
- [Migri guidance for the statistical service](https://migri.fi/en/using-the-statistical-service)

## GitHub Pages

The Pages workflow builds the report with fresh Migri data, runs the development checks, commits
changed snapshots in `reports/` back to `main`, and deploys the same generated files. It runs on
every push to `main`, can be started manually, and checks for newly published statistics every day
at 06:17 Europe/Helsinki time. Commits made by the workflow use GitHub's built-in token, so they do
not trigger another workflow run.

To enable the first deployment, open **Settings → Pages** in the GitHub repository and select
**GitHub Actions** as the source. The project site will be available at
<https://petrzhitnikov.github.io/migri-stats/>.

Build the exact Pages artifact locally with:

```bash
uv run --frozen migri-stats \
  --csv reports/migri-stats.csv \
  --html reports/migri-stats.html
mkdir -p _site
cp reports/migri-stats.csv _site/migri-stats.csv
cp reports/migri-stats.html _site/index.html
```

## Development checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy src
```
