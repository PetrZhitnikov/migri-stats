from __future__ import annotations

import pandas as pd
from plotly.graph_objects import Figure


def build_page(stats: pd.DataFrame, figure: Figure) -> str:
    """Render the interactive report as a standalone web page."""
    latest = stats.iloc[-1]
    period = latest["month"].strftime("%B %Y")
    applications = int(latest["applications"])
    decisions = int(latest["decisions"])
    speed_ratio = float(latest["speed_ratio"])
    monthly_reduction = int(latest["queue_reduction"])
    cumulative_reduction = int(latest["cumulative_queue_reduction"])
    chart = figure.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={"displaylogo": False, "responsive": True},
        div_id="migri-chart",
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description"
        content="Monthly Finnish citizenship application and decision throughput statistics.">
  <title>Migri citizenship statistics</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1f2925;
      --muted: #65706b;
      --paper: #fbfaf7;
      --card: #ffffff;
      --line: #e5e3dc;
      --green: #25836f;
      --coral: #d65a4a;
      --gold: #d49422;
      --purple: #6655a5;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system,
        BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; padding: 64px 0 48px; }}
    header {{ max-width: 780px; margin-bottom: 34px; }}
    .eyebrow {{
      margin: 0 0 12px;
      color: var(--green);
      font-size: .78rem;
      font-weight: 750;
      letter-spacing: .11em;
      text-transform: uppercase;
    }}
    h1 {{
      margin: 0;
      font-size: clamp(2.2rem, 6vw, 4.6rem);
      letter-spacing: -.055em;
      line-height: .98;
    }}
    .intro {{
      max-width: 680px;
      margin: 22px 0 18px;
      color: var(--muted);
      font-size: 1.08rem;
    }}
    .updated {{
      display: inline-flex;
      padding: 7px 11px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: var(--card);
      font-size: .88rem;
    }}
    .summary {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
      margin: 0 0 24px;
    }}
    .metric {{
      min-width: 0;
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 16px;
      background: var(--card);
      box-shadow: 0 8px 30px rgba(38, 45, 42, .04);
    }}
    .metric dt {{
      color: var(--muted);
      font-size: .78rem;
      font-weight: 700;
      letter-spacing: .04em;
      text-transform: uppercase;
    }}
    .metric dd {{
      margin: 8px 0 0;
      font-size: clamp(1.55rem, 4vw, 2.35rem);
      font-weight: 760;
      letter-spacing: -.04em;
    }}
    .applications dd {{ color: var(--green); }}
    .decisions dd {{ color: var(--coral); }}
    .speed dd {{ color: var(--gold); }}
    .reduction dd {{ color: var(--purple); }}
    .chart-card {{
      overflow: hidden;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 18px;
      background: var(--card);
      box-shadow: 0 12px 40px rgba(38, 45, 42, .05);
    }}
    #migri-chart {{ width: 100%; }}
    .notes {{
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 32px;
      margin-top: 28px;
      color: var(--muted);
      font-size: .94rem;
    }}
    .notes h2 {{ margin: 0 0 8px; color: var(--ink); font-size: 1rem; }}
    .notes p {{ margin: 0 0 10px; }}
    a {{ color: var(--green); text-underline-offset: 3px; }}
    footer {{
      margin-top: 42px;
      padding-top: 18px;
      border-top: 1px solid var(--line);
      color: var(--muted);
      font-size: .84rem;
    }}
    @media (max-width: 760px) {{
      main {{ width: min(100% - 20px, 1120px); padding-top: 36px; }}
      .summary {{ grid-template-columns: repeat(2, 1fr); }}
      .metric {{ padding: 16px; }}
      .chart-card {{ padding: 2px; }}
      .notes {{ grid-template-columns: 1fr; gap: 10px; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <p class="eyebrow">Finnish Immigration Service data</p>
      <h1>Citizenship applications and decisions</h1>
      <p class="intro">
        Monthly volumes and a simple view of whether decisions are keeping pace with new
        applications.
      </p>
      <span class="updated">Updated through {period}</span>
    </header>

    <dl class="summary" aria-label="Latest month summary">
      <div class="metric applications"><dt>Applications</dt><dd>{applications:,}</dd></div>
      <div class="metric decisions"><dt>Decisions</dt><dd>{decisions:,}</dd></div>
      <div class="metric speed"><dt>Decision speed</dt><dd>{speed_ratio:.2f}×</dd></div>
      <div class="metric reduction">
        <dt>Estimated monthly reduction</dt><dd>{monthly_reduction:+,}</dd>
      </div>
    </dl>

    <section class="chart-card" aria-label="Historical statistics">
      {chart}
    </section>

    <section class="notes">
      <div>
        <h2>How to read this</h2>
        <p>
          Decision speed is decisions divided by applications. Above 1× means decisions outpaced
          new applications that month.
        </p>
        <p>
          The cumulative estimate is decisions minus applications since January 2015. Its latest
          value is {cumulative_reduction:+,}. It is a throughput indicator, not a measured
          application backlog.
        </p>
      </div>
      <div>
        <h2>Data and methodology</h2>
        <p><a href="migri-stats.csv">Download the normalized data</a></p>
        <p>
          Source:
          <a href="https://tilastot.migri.fi/#applications/23331/42?l=en&amp;start=540">
            Migri statistical service
          </a>.
        </p>
      </div>
    </section>

    <footer>
      Applications and decisions from different months do not represent matched cases.
    </footer>
  </main>
</body>
</html>
"""
