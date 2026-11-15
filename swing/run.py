"""CLI: python -m swing.run --data data/sp500_2013_2018.csv --out results/sp500"""
import argparse
import os
import zlib

import numpy as np
import pandas as pd

from .engine import event_study, load_long_csv, run, trade_stats
from .rules import CONTEXT, ENTRIES, EXITS, Signal

BASE_EXIT = next(iter(EXITS))
STACK = ["C01 market trend", "C04 trend template", "C05 relative strength >= 70"]
RANDOM = "E00 random entry (benchmark)"


def random_entry(d, p=0.03):
    """Benchmark: buy a random 3% of days with the same stop logic as a one-bar setup."""
    rng = np.random.default_rng(zlib.crc32(str(d.close.iloc[0]).encode()))
    return Signal(pd.Series(rng.random(len(d)) < p, d.index), d.low)


def md(df, digits=2):
    return df.round(digits).to_markdown()


def build_report(panel, trades, title):
    rules = [RANDOM] + list(ENTRIES)
    base = trades[trades.exit_rule == BASE_EXIT]
    stack = base[base[STACK].all(axis=1)]

    ev = pd.DataFrame({r: event_study(panel, r) for r in rules}).T
    ts = base.groupby("rule").apply(trade_stats, include_groups=False).reindex(rules)
    st = stack.groupby("rule").apply(trade_stats, include_groups=False).reindex(rules)
    entry_tbl = pd.concat([
        ev[["signals", "excess5%", "excess10%", "excess20%", "t20"]],
        ts[["trades", "win%", "avgR", "PF", "t"]],
        st[["trades", "avgR"]].add_prefix("stack "),
    ], axis=1)

    real = base[base.rule != RANDOM]
    ctx_rows = {}
    for c in CONTEXT:
        if c == "C09 liquidity":
            continue
        e = event_study(panel, c)
        on, off = real[real[c]], real[~real[c]]
        uni = panel[panel["C09 liquidity"]]
        ctx_rows[c] = {
            "% days on": 100 * uni[c].mean(),
            "fwd20% on": 100 * uni.loc[uni[c], "fwd20"].mean(),
            "fwd20% off": 100 * uni.loc[~uni[c], "fwd20"].mean(),
            # market-wide filters are identical for every ticker, so no cross-sectional excess
            "excess20%": np.nan if c[:3] in ("C01", "C02") else e["excess20%"],
            "t20": np.nan if c[:3] in ("C01", "C02") else e["t20"],
            "trades on": len(on), "avgR on": on.R.mean(), "avgR off": off.R.mean(),
        }
    ctx_tbl = pd.DataFrame(ctx_rows).T

    realx = trades[trades.rule != RANDOM]
    exit_tbl = realx.groupby("exit_rule").apply(trade_stats, include_groups=False).reindex(list(EXITS))
    matrix = realx.pivot_table(index="rule", columns="exit_rule", values="R", aggfunc="mean").reindex(
        index=list(ENTRIES), columns=list(EXITS))
    matrix.columns = [c.split(" ")[0] for c in matrix.columns]

    dates = panel.date
    return "\n".join([
        f"# Backtest report: {title}", "",
        f"{panel.ticker.nunique()} tickers, {dates.min().date()} to {dates.max().date()}, "
        f"{len(panel):,} ticker-days. Long only, 5 bps cost per side, one open trade per rule per ticker.", "",
        "## 1. Entry setups", "",
        "`excessN%` = mean N-day return after the signal (bought at next open) minus the same-day universe "
        "average; `t20` is date-clustered and overlap-adjusted (|t| > 2 is meaningful). "
        f"Trade columns use the baseline exit ({BASE_EXIT}). `stack` = only signals where "
        f"{' + '.join(s.split(' ')[0] for s in STACK)} are all true.", "",
        md(entry_tbl), "",
        "## 2. Context filters", "",
        "`fwd20% on/off` = raw 20-day forward return of all liquid ticker-days with the filter true/false. "
        "`avgR on/off` = baseline-exit result of all entry-setup trades split by the filter at signal time.", "",
        md(ctx_tbl), "",
        "## 3. Exit rules (all entry setups pooled)", "",
        md(exit_tbl), "",
        "### Average R by entry setup and exit rule", "",
        md(matrix), "",
    ]), entry_tbl, ctx_tbl, exit_tbl, matrix


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="long CSV: date,open,high,low,close,volume,name")
    ap.add_argument("--out", required=True)
    ap.add_argument("--title", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    frames = load_long_csv(a.data)
    panel, trades = run(frames, entries={RANDOM: random_entry, **ENTRIES})
    report, entry_tbl, ctx_tbl, exit_tbl, matrix = build_report(panel, trades, a.title or a.data)
    with open(os.path.join(a.out, "report.md"), "w") as f:
        f.write(report)
    for name, t in [("entries", entry_tbl), ("context", ctx_tbl), ("exits", exit_tbl), ("entry_x_exit", matrix)]:
        t.to_csv(os.path.join(a.out, f"{name}.csv"))
    trades.to_csv(os.path.join(a.out, "trades.csv.gz"), index=False)
    print(report)


if __name__ == "__main__":
    main()
