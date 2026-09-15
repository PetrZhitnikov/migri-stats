# Migri throughput report

Downloaded from the [Migri statistics service](https://tilastot.migri.fi/#applications/23331/42?l=en&start=540).
The dataset covers citizenship hierarchy `23331/42` from January 2015 through August 2026.

- [Open the interactive Plotly report](migri-stats.html)
- [Download the normalized data](migri-stats.csv)

## Summary

| Period | Applications | Decisions | Throughput ratio | Net queue reduction |
|---|---:|---:|---:|---:|
| Full period | 148,088 | 134,230 | 0.91 | -13,858 |
| Latest 12 months | 11,557 | 14,982 | 1.30 | 3,425 |
| August 2026 | 522 | 1,179 | 2.26 | 657 |

Since January 2015, applications exceeded decisions by 13,858, so the cumulative queue-reduction
estimate ends at **-13,858**. Over the latest 12 months, decisions exceeded applications by 3,425,
indicating that this estimated queue has been shrinking recently.

## Latest 12 months

| Month | Applications | Decisions | Speed ratio | Monthly reduction | Cumulative reduction |
|---|---:|---:|---:|---:|---:|
| 2025-09 | 961 | 1,606 | 1.67 | 645 | -16,638 |
| 2025-10 | 1,213 | 1,415 | 1.17 | 202 | -16,436 |
| 2025-11 | 1,473 | 1,358 | 0.92 | -115 | -16,551 |
| 2025-12 | 1,774 | 1,083 | 0.61 | -691 | -17,242 |
| 2026-01 | 1,291 | 1,064 | 0.82 | -227 | -17,469 |
| 2026-02 | 957 | 1,152 | 1.20 | 195 | -17,274 |
| 2026-03 | 976 | 1,380 | 1.41 | 404 | -16,870 |
| 2026-04 | 611 | 1,292 | 2.11 | 681 | -16,189 |
| 2026-05 | 498 | 1,331 | 2.67 | 833 | -15,356 |
| 2026-06 | 649 | 1,369 | 2.11 | 720 | -14,636 |
| 2026-07 | 632 | 753 | 1.19 | 121 | -14,515 |
| 2026-08 | 522 | 1,179 | 2.26 | 657 | -13,858 |

## Interpretation

- **Speed ratio** is decisions divided by applications. Values above 1 mean decisions outpaced
  new applications during that month.
- **Monthly reduction** is decisions minus applications. Positive values are an estimated queue
  reduction; negative values are estimated queue growth.
- **Cumulative reduction** is the running sum of monthly reduction from January 2015. It is not an
  actual backlog count because the starting backlog is unknown.

Migri cautions that monthly applications and decisions do not represent matched cases: an
application recorded in one month may be decided later. These figures are therefore throughput
indicators, not application processing-time measurements.
