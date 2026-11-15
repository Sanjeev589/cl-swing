# cl-swing

A testable rule set for price-action swing trading of stocks, distilled from 20
books, with a backtester that scores every rule on real daily data.

- `docs/BOOKS.md` - the 20 books, what each contributes, where they agree and disagree
- `docs/RULES.md` - the 39 rules in exact, codable form (9 context filters, 22 entry setups, 8 risk/exit rules)
- `swing/rules.py` - the same rules as code
- `swing/engine.py` - data loading, trade simulation, event study
- `results/` - reports from two real-data runs

## Run it

```bash
pip install -r requirements.txt
```

```bash
python scripts/fetch_sample_data.py
```

```bash
python -m swing.run --data data/sp500_2013_2018.csv --out results/sp500_2013_2018
```

```bash
python -m pytest -q
```

To test your own market, pass any CSV with columns
`date, open, high, low, close, volume, name` (one row per ticker per day,
split-adjusted). Thresholds such as minimum price and dollar volume are in the
`P` dict at the top of `swing/rules.py`.

## What the first two runs show

Samples: S&P 500 constituents 2013-2018 (500 tickers) and Dow 30 2006-2017
(31 tickers, includes 2008). Full tables are in `results/*/report.md`.

Average R per trade with the baseline exit (structure stop, 20-bar time exit),
after costs. A random-entry benchmark earned +0.14R (Dow) and +0.12R (S&P),
so that is the bar to clear, not zero.

| Outcome | Setups (Dow R / S&P R) |
|---------|------------------------|
| Beat random in both samples | E22 anchored-VWAP support (0.19 / 0.21) |
| Beat random in one sample only | E02 SMA50 pullback (0.02 / 0.27), E07 spring (0.10 / 0.17), E09 52-week-high breakout (0.22 / 0.04), E05 bull flag (0.20 / 0.02), E16 gap up (0.11 / 0.18), E19 key reversal (-0.12 / 0.15), E20 stopping volume (-0.28 / 0.34) |
| About equal to random | E06 RSI(2) (0.16 / 0.09, but the highest win rate at 50%), E15 thrust bar (0.08 / 0.14), E04 High 2 (0.15 / 0.00) |
| Worse than random in both | E01 Holy Grail, E03 Landry pullback, E08 breakout retest, E10 tight base, E11 VCP, E13 NR7, E14 inside day, E17 engulfing, E18 hammer, E21 no-supply pullback |

Other findings that held in both samples:

- **No setup showed a statistically significant edge over the same-day universe
  average.** Every 20-day excess return had |t| below 1. On large caps the
  entry pattern explains very little; most of the profit is market drift.
- **Relative strength (C05) and market trend (C01) improved trade results.**
  Trades taken with C05 true averaged 0.16R vs 0.03R (Dow) and 0.07R vs -0.03R (S&P).
- **The other filters did not help.** C02, C07 and C08 were neutral or negative.
- **Wider stops and letting trades run beat taking quick profits.** The 2 ATR
  stop and the chandelier trail were the best exits; the 2R target, half-off at
  1R, the stale-trade exit and the EMA10 trail all lowered expectancy.

## Limits of these results

- Both samples are large caps and survivorship-biased (only stocks that were in
  the index at the end). Breakout methods from O'Neil, Minervini and Darvas were
  designed for small and mid-cap growth leaders, which these samples do not contain.
- The S&P sample is a single five-year bull market.
- The market filter uses an equal-weight proxy built from the universe, not a real index.
- Trades are scored per signal. There is no portfolio-level capital limit, so
  results are per-trade expectancy, not an equity curve.
- Thresholds were set from the books and not optimised. Tuning them on these
  samples would overfit.
- A handful of unadjusted spin-off gaps remain in the S&P file.

Nothing here is investment advice.
