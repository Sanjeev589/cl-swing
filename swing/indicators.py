"""Indicators. Every function is causal: the value at bar t uses bars <= t only."""
import numpy as np
import pandas as pd


def sma(s, n):
    return s.rolling(n).mean()


def ema(s, n):
    return s.ewm(span=n, adjust=False, min_periods=n).mean()


def wilder(s, n):
    return s.ewm(alpha=1.0 / n, adjust=False, min_periods=n).mean()


def true_range(df):
    pc = df["close"].shift(1)
    return pd.concat(
        [df["high"] - df["low"], (df["high"] - pc).abs(), (df["low"] - pc).abs()], axis=1
    ).max(axis=1)


def atr(df, n=14):
    return wilder(true_range(df), n)


def rsi(s, n):
    d = s.diff()
    up = wilder(d.clip(lower=0), n)
    dn = wilder((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn.replace(0, np.nan))


def adx(df, n=14):
    up = df["high"].diff()
    dn = -df["low"].diff()
    pdm = up.where((up > dn) & (up > 0), 0.0)
    mdm = dn.where((dn > up) & (dn > 0), 0.0)
    a = atr(df, n)
    pdi = 100 * wilder(pdm, n) / a
    mdi = 100 * wilder(mdm, n) / a
    dx = 100 * (pdi - mdi).abs() / (pdi + mdi).replace(0, np.nan)
    return wilder(dx, n), pdi, mdi


def bars_since(cond):
    """Bars elapsed since cond was last True (0 on the bar itself, NaN before first)."""
    idx = pd.Series(np.arange(len(cond), dtype=float), index=cond.index)
    return idx - idx.where(cond).ffill()


def streak(cond):
    """Length of the current run of consecutive True values."""
    c = cond.astype(int)
    return c.groupby((c == 0).cumsum()).cumsum()


def enrich(df):
    """Add the shared indicator columns the rules read."""
    d = df.copy()
    c, h, l, o, v = d["close"], d["high"], d["low"], d["open"], d["volume"]
    d["atr"] = atr(d, 14)
    d["atr50"] = atr(d, 50)
    d["tr"] = true_range(d)
    d["e10"], d["e20"] = ema(c, 10), ema(c, 20)
    d["s5"], d["s50"], d["s150"], d["s200"] = sma(c, 5), sma(c, 50), sma(c, 150), sma(c, 200)
    d["v50p"] = sma(v, 50).shift(1)          # average volume, excluding today
    d["adx"], d["pdi"], d["mdi"] = adx(d, 14)
    d["rsi2"] = rsi(c, 2)
    d["rng"] = h - l
    d["clv"] = ((c - l) / d["rng"].replace(0, np.nan)).fillna(0.5)  # close location 0..1
    d["hi252"] = h.rolling(252).max()
    d["lo252"] = l.rolling(252).min()
    d["ret126"] = c / c.shift(126) - 1
    return d
