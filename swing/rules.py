"""The rule set: 9 context filters (C), 22 entry setups (E), 8 exit/risk rules (X).

Long-only, daily bars. Every rule is evaluated at the close of bar t and may use
bars <= t only (tests/test_rules.py verifies this). Full prose spec: docs/RULES.md.

Input frame: indicators.enrich() output, plus the cross-sectional/market columns
added by engine.prepare_universe(): rs_pct, mkt_trend, mkt_dist_ok.
"""
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from .indicators import bars_since, ema, streak

# Parameters live here so a test run can override them in one place.
P = dict(
    min_price=5.0, min_dollar_vol=5e6,       # C09
    rs_min_pct=70,                           # C05
    near_high=0.85,                          # C06
    pivot_k=3,                               # C07
    vol_breakout=1.5,                        # E09/E10/E15 volume multiple
)


# --------------------------------------------------------------------------- #
# Context filters: boolean state per bar
# --------------------------------------------------------------------------- #
def c01_market_trend(d):
    return d["mkt_trend"].fillna(False).astype(bool)


def c02_market_distribution(d):
    return d["mkt_dist_ok"].fillna(False).astype(bool)


def c03_stage2(d):
    return (d.close > d.s150) & (d.s150 > d.s200) & (d.s200 > d.s200.shift(20))


def c04_trend_template(d):
    return (
        c03_stage2(d) & (d.s50 > d.s150) & (d.close > d.s50)
        & (d.close >= 1.30 * d.lo252) & (d.close >= 0.75 * d.hi252)
    )


def c05_relative_strength(d):
    return d["rs_pct"] >= P["rs_min_pct"]


def c06_near_52w_high(d):
    return d.close >= P["near_high"] * d.hi252


def c07_swing_structure(d):
    """Last two confirmed swing highs AND swing lows are both rising (HH + HL)."""
    k = P["pivot_k"]
    w = 2 * k + 1
    # a pivot at bar i is only known k bars later -> shift by k
    ph = d.high.shift(k).where((d.high == d.high.rolling(w, center=True).max()).shift(k, fill_value=False))
    pl = d.low.shift(k).where((d.low == d.low.rolling(w, center=True).min()).shift(k, fill_value=False))

    def rising(p):
        v = p.dropna()
        return (v > v.shift(1)).reindex(p.index).ffill().fillna(False).astype(bool)

    return rising(ph) & rising(pl)


def c08_weekly_trend(d):
    """Last COMPLETED week: close > 13-week EMA and the EMA is rising."""
    wk = d.index.to_period("W-FRI")
    wc = d.close.groupby(wk).last()
    e = ema(wc, 13)
    ok = ((wc > e) & (e > e.shift(1))).shift(1, fill_value=False)
    return pd.Series(ok.reindex(wk).to_numpy(), index=d.index).astype(bool)


def c09_liquidity(d):
    dv = (d.close * d.volume).rolling(20).mean()
    return (d.close >= P["min_price"]) & (dv >= P["min_dollar_vol"])


# --------------------------------------------------------------------------- #
# Entry setups
# --------------------------------------------------------------------------- #
@dataclass
class Signal:
    sig: pd.Series                 # bool, True on the setup bar
    stop_ref: pd.Series            # structural stop reference (setup low)
    entry: str = "next_open"       # or "stop_high": buy stop 1 tick above setup-bar high
    valid: int = 1                 # bars a buy stop stays live


def _uptrend(d):
    return (d.close > d.s50) & (d.s50 > d.s50.shift(10))


def e01_holy_grail(d):
    touch = d.low <= d.e20
    above5 = (d.low > d.e20).astype(float).shift(1).rolling(5).min() == 1
    s = (d.adx > 30) & (d.pdi > d.mdi) & touch & above5
    return Signal(s, d.low, "stop_high", 3)


def e02_sma50_pullback(d):
    near = d.low <= 1.01 * d.s50
    first = (~near).astype(float).shift(1).rolling(20).min() == 1
    s = (d.close > d.s200) & (d.s50 > d.s50.shift(10)) & near & (d.close > d.s50) & (d.clv >= 0.5) & first
    return Signal(s, d.low)


def e03_landry_pullback(d):
    made_high = d.high >= d.high.rolling(20).max()
    lh = streak(d.high < d.high.shift(1))
    s = (lh >= 3) & (lh <= 7) & (bars_since(made_high) == lh) & _uptrend(d)
    return Signal(s, d.low.rolling(3).min(), "stop_high", 1)


def e04_high2(d):
    """Second attempt to resume the trend after a two-legged pullback."""
    h, l = d.high.to_numpy(), d.low.to_numpy()
    made_high = (d.high >= d.high.rolling(20).max()).to_numpy()
    ok = ((d.e20 > d.s50) & (d.close > d.s50)).to_numpy()
    n = len(d)
    sig = np.zeros(n, bool)
    stop = np.full(n, np.nan)
    anchor, count, in_pull, low_since = -1, 0, False, np.inf
    for i in range(1, n):
        if made_high[i]:
            anchor, count, in_pull, low_since = i, 0, False, np.inf
            continue
        if anchor < 0:
            continue
        low_since = min(low_since, l[i])
        if h[i] < h[i - 1]:
            in_pull = True
        elif h[i] > h[i - 1] and in_pull:
            count += 1
            in_pull = False
            if count == 2 and i - anchor <= 20 and ok[i]:
                sig[i], stop[i] = True, low_since
    return Signal(pd.Series(sig, d.index), pd.Series(stop, d.index))


def e05_bull_flag(d):
    h, l, c, v = (d[x].to_numpy() for x in ("high", "low", "close", "volume"))
    a = d.atr.to_numpy()
    cand = ((d.close > d.high.shift(1)) & (d.close > d.s50)).to_numpy()
    n = len(d)
    sig = np.zeros(n, bool)
    stop = np.full(n, np.nan)
    for t in np.flatnonzero(cand):
        if t < 25:
            continue
        j = t - 12 + int(np.argmax(h[t - 12:t]))       # pole top = highest high of last 12 bars
        if t - j < 3 or np.isnan(a[j]):                # flag must last 3..12 bars
            continue
        pole = h[j] - l[j - 10:j + 1].min()
        flag_low = l[j + 1:t].min()
        if (pole >= 4 * a[j] and h[j] - flag_low <= 0.5 * pole
                and v[j + 1:t].mean() < v[j - 4:j + 1].mean()
                and c[t] > h[j + 1:t].max()):
            sig[t], stop[t] = True, flag_low
    return Signal(pd.Series(sig, d.index), pd.Series(stop, d.index))


def e06_rsi2_oversold(d):
    s = (d.close > d.s200) & (d.rsi2 < 10)
    return Signal(s, d.close - 2.5 * d.atr)


def e07_spring(d):
    """Turtle Soup / Wyckoff spring: undercut of an older 20-day low that closes back above it."""
    prior = d.low.shift(1)
    pl20 = prior.rolling(20).min()
    age = prior.rolling(20).apply(lambda x: len(x) - np.argmin(x), raw=True)  # bars back from t
    s = (d.low < pl20) & (d.close > pl20) & (age >= 4)
    return Signal(s, d.low)


def e08_breakout_retest(d):
    p = d.high.shift(1).rolling(50).max()
    bo = (d.close > p) & (d.close.shift(1) <= p.shift(1))
    gid = bo.cumsum()
    lvl = p.where(bo).groupby(gid).ffill()
    since = bars_since(bo)
    held = d.close.groupby(gid).cummin() >= 0.97 * lvl
    raw = (since >= 2) & (since <= 10) & (d.low <= 1.01 * lvl) & (d.close > lvl) & (d.close > d.open) & held
    s = raw & (raw.astype(int).groupby(gid).cumsum() == 1)       # first retest only
    return Signal(s, d.low)


def e09_52w_high_breakout(d):
    p = d.high.shift(1).rolling(252).max()
    s = ((d.close > p) & (d.close.shift(1) <= p.shift(1))
         & (d.volume >= P["vol_breakout"] * d.v50p) & (d.clv >= 0.5))
    return Signal(s, d.low)


def e10_tight_base_breakout(d):
    """Darvas box / rectangle: 15-bar range no wider than 3.5 ATR, near highs, broken on volume."""
    bh = d.high.shift(1).rolling(15).max()
    bl = d.low.shift(1).rolling(15).min()
    s = ((bh - bl <= 3.5 * d.atr50.shift(15)) & (d.close > bh) & (d.close.shift(1) <= bh.shift(1))
         & (d.volume >= P["vol_breakout"] * d.v50p) & (bh >= 0.85 * d.hi252.shift(1)) & (d.close > d.s50))
    return Signal(s, bl)


def e11_vcp(d):
    def width(shift, n):
        hi = d.high.shift(shift).rolling(n).max()
        return (hi - d.low.shift(shift).rolling(n).min()) / hi

    r1, r2, r3 = width(21, 20), width(11, 10), width(1, 10)
    dry = d.volume.rolling(10).mean().shift(1) < 0.85 * d.v50p
    s = ((r1 > r2) & (r2 > r3) & (r3 <= 0.10) & dry & c04_trend_template(d)
         & (d.close > d.high.shift(1).rolling(10).max()) & (d.volume >= 1.3 * d.v50p))
    return Signal(s, d.low.shift(1).rolling(10).min())


def e12_cup_with_handle(d):
    h, l, c = (d[x].to_numpy() for x in ("high", "low", "close"))
    cand = ((d.close > d.high.shift(1).rolling(5).max()) & (d.volume >= 1.4 * d.v50p)).to_numpy()
    n = len(d)
    sig = np.zeros(n, bool)
    stop = np.full(n, np.nan)
    for t in np.flatnonzero(cand):
        if t < 270:
            continue
        j = t - 20 + int(np.argmax(h[t - 20:t - 4]))    # right rim, 5..20 bars back
        pr = h[j]
        if c[t] <= pr or c[j + 1:t].max() > pr:
            continue
        handle_low = l[j + 1:t].min()
        a = j - 120 + int(np.argmax(h[j - 120:j - 24]))  # left rim, 25..120 bars before right rim
        pleft = h[a]
        cup_low = l[a:j + 1].min()
        depth = 1 - cup_low / pleft
        if (0.95 <= pr / pleft <= 1.05 and 0.12 <= depth <= 0.35
                and handle_low >= 0.88 * pr
                and handle_low >= cup_low + 0.5 * (pleft - cup_low)
                and pleft >= 1.25 * l[a - 120:a].min()):
            sig[t], stop[t] = True, handle_low
    return Signal(pd.Series(sig, d.index), pd.Series(stop, d.index))


def e13_nr7(d):
    s = (d.rng > 0) & (d.rng <= d.rng.rolling(7).min()) & _uptrend(d)
    return Signal(s, d.low, "stop_high", 1)


def e14_inside_day_nr4(d):
    s = ((d.high < d.high.shift(1)) & (d.low > d.low.shift(1))
         & (d.rng <= d.rng.rolling(4).min()) & _uptrend(d))
    return Signal(s, d.low, "stop_high", 1)


def e15_thrust_bar(d):
    s = ((d.tr >= 2 * d.atr.shift(1)) & (d.clv >= 0.75)
         & (d.close > d.high.shift(1).rolling(20).max()) & (d.volume >= P["vol_breakout"] * d.v50p))
    return Signal(s, (d.high + d.low) / 2)


def e16_gap_up(d):
    ph = d.high.shift(1)
    s = (d.open >= 1.03 * ph) & (d.low > ph) & (d.close >= d.open) & (d.volume >= 2 * d.v50p)
    return Signal(s, ph)


def e17_bullish_engulfing(d):
    po, pc = d.open.shift(1), d.close.shift(1)
    s = ((pc < po) & (d.close > d.open) & (d.open <= pc) & (d.close >= po)
         & (d.low.rolling(2).min() <= d.low.rolling(5).min())
         & (d.close > d.s50) & (d.s50 > d.s200))
    return Signal(s, d.low.rolling(2).min())


def e18_hammer(d):
    body = (d.close - d.open).abs()
    lower = d[["open", "close"]].min(axis=1) - d.low
    upper = d.high - d[["open", "close"]].max(axis=1)
    s = ((lower >= 2 * body) & (upper <= 0.25 * d.rng) & (d.rng >= 0.8 * d.atr)
         & (d.low <= d.low.rolling(10).min()) & (d.close > d.s200))
    return Signal(s, d.low, "stop_high", 2)


def e19_key_reversal(d):
    s = ((d.low < d.low.shift(1)) & (d.close > d.high.shift(1))
         & (d.low <= d.low.rolling(10).min()) & (d.close > d.s200))
    return Signal(s, d.low)


def e20_stopping_volume(d):
    s = ((d.low <= d.low.rolling(20).min()) & (d.volume >= 2.5 * d.v50p)
         & (d.rng >= 1.5 * d.atr.shift(1)) & (d.clv >= 0.5))
    return Signal(s, d.low)


def e21_no_supply_pullback(d):
    down = (d.close < d.close.shift(1)).astype(int).rolling(3).sum() >= 2
    s = ((d.e20 > d.s50) & (d.close > d.s50) & down
         & (d.volume <= d.volume.rolling(10).min()) & (d.rng <= 0.7 * d.atr))
    return Signal(s, d.low.rolling(3).min(), "stop_high", 2)


def e22_avwap_support(d, lookback=126):
    """Pullback to the VWAP anchored at the lowest low of the last 126 bars."""
    tp = (d.high + d.low + d.close) / 3
    cpv = (tp * d.volume).cumsum().to_numpy()
    cv = d.volume.cumsum().to_numpy()
    back = d.low.rolling(lookback).apply(lambda x: len(x) - 1 - np.argmin(x), raw=True).to_numpy()
    n = len(d)
    av = np.full(n, np.nan)
    for t in np.flatnonzero(~np.isnan(back)):
        a = t - int(back[t])
        pv0, v0 = (cpv[a - 1], cv[a - 1]) if a > 0 else (0.0, 0.0)
        if cv[t] > v0:
            av[t] = (cpv[t] - pv0) / (cv[t] - v0)
    av = pd.Series(av, d.index)
    above5 = (d.close > av).astype(float).shift(1).rolling(5).min() == 1
    s = (pd.Series(back, d.index) >= 20) & (d.low <= 1.005 * av) & (d.close > av) & above5
    return Signal(s, d.low)


# --------------------------------------------------------------------------- #
# Exit / risk rules (X) -- parameters consumed by engine.simulate()
# --------------------------------------------------------------------------- #
@dataclass
class ExitCfg:
    stop: str = "setup"            # X01: "setup" (structure low - 0.1 ATR) or "atr"
    atr_mult: float = 2.0
    max_risk_pct: float = 0.08     # X01: skip trade if stop is further than 8% away
    min_risk_atr: float = 0.75     # widen absurdly tight stops to 0.75 ATR
    target_r: float | None = None  # X03: fixed reward:risk target
    partial_r: float | None = None # X04: sell half at this R, stop to breakeven
    trail: str | None = None       # X05: "ema10" or "chandelier" (3 ATR from highest high)
    stale: tuple | None = None     # X06: (bars, min R) -> exit if not working
    max_hold: int = 20             # X06: hard time stop
    climax: bool = False           # X07: exit when close > EMA20 + 3 ATR
    sma5_exit: bool = False        # X08: exit when close > SMA5
    cost_bps: float = 5.0          # per side
    # X02 (risk a fixed 1% of equity per trade) is implicit: results are in R multiples.


EXITS = {
    "X00 baseline: setup stop + 20-bar time exit": ExitCfg(),
    "X01b ATR stop (2 ATR) instead of setup stop": ExitCfg(stop="atr"),
    "X03 fixed 2R target": ExitCfg(target_r=2.0),
    "X04 half off at 1R, stop to breakeven": ExitCfg(partial_r=1.0),
    "X05a trail: close below EMA10": ExitCfg(trail="ema10", max_hold=60),
    "X05b trail: chandelier 3 ATR": ExitCfg(trail="chandelier", max_hold=60),
    "X06 stale exit: <0.5R after 5 bars": ExitCfg(stale=(5, 0.5)),
    "X07 climax exit: close > EMA20 + 3 ATR": ExitCfg(climax=True),
    "X08 exit on strength: close > SMA5": ExitCfg(sma5_exit=True, max_hold=10),
}

CONTEXT = {
    "C01 market trend": c01_market_trend,
    "C02 market distribution days < 5": c02_market_distribution,
    "C03 stage 2 uptrend": c03_stage2,
    "C04 trend template": c04_trend_template,
    "C05 relative strength >= 70": c05_relative_strength,
    "C06 within 15% of 52w high": c06_near_52w_high,
    "C07 HH+HL swing structure": c07_swing_structure,
    "C08 weekly trend up": c08_weekly_trend,
    "C09 liquidity": c09_liquidity,
}

ENTRIES = {
    "E01 Holy Grail (ADX + EMA20 pullback)": e01_holy_grail,
    "E02 first pullback to SMA50": e02_sma50_pullback,
    "E03 Landry 3-7 bar pullback": e03_landry_pullback,
    "E04 High 2 (two-legged pullback)": e04_high2,
    "E05 bull flag breakout": e05_bull_flag,
    "E06 RSI(2) < 10 above SMA200": e06_rsi2_oversold,
    "E07 spring / Turtle Soup": e07_spring,
    "E08 breakout retest (throwback)": e08_breakout_retest,
    "E09 52-week-high breakout on volume": e09_52w_high_breakout,
    "E10 tight base (Darvas box) breakout": e10_tight_base_breakout,
    "E11 volatility contraction (VCP)": e11_vcp,
    "E12 cup with handle": e12_cup_with_handle,
    "E13 NR7 breakout": e13_nr7,
    "E14 inside day + NR4": e14_inside_day_nr4,
    "E15 thrust bar breakout": e15_thrust_bar,
    "E16 gap up on volume": e16_gap_up,
    "E17 bullish engulfing in pullback": e17_bullish_engulfing,
    "E18 hammer at 10-day low": e18_hammer,
    "E19 outside-day key reversal": e19_key_reversal,
    "E20 stopping volume (climax low)": e20_stopping_volume,
    "E21 no-supply pullback": e21_no_supply_pullback,
    "E22 anchored-VWAP support": e22_avwap_support,
}
