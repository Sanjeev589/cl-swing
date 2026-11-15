"""Data loading, universe preparation, trade simulation and the event study."""
import numpy as np
import pandas as pd

from .indicators import enrich, sma
from .rules import CONTEXT, ENTRIES, ExitCfg

HORIZONS = (5, 10, 20)


# --------------------------------------------------------------------------- #
# Data
# --------------------------------------------------------------------------- #
def load_long_csv(path):
    """Read a long-format CSV: date, open, high, low, close, volume, name (any case)."""
    raw = pd.read_csv(path)
    raw.columns = [c.lower() for c in raw.columns]
    raw = raw.rename(columns={"ticker": "name", "symbol": "name"}).dropna()
    raw["date"] = pd.to_datetime(raw["date"])
    raw["open"] = raw["open"].clip(raw["low"], raw["high"])   # repair bad opening ticks
    out = {}
    for name, g in raw.groupby("name"):
        g = g.drop_duplicates("date").set_index("date").sort_index()
        out[name] = g[["open", "high", "low", "close", "volume"]].astype(float)
    return out


def market_proxy(frames):
    """Equal-weight index of the universe (use a real index instead if you have one)."""
    rets = pd.DataFrame({k: f.close.pct_change() for k, f in frames.items()})
    vol = pd.DataFrame({k: f.volume for k, f in frames.items()}).sum(axis=1)
    close = (1 + rets.mean(axis=1).fillna(0)).cumprod()
    return pd.DataFrame({"close": close, "volume": vol})


def prepare_universe(frames, market=None):
    """Enrich every ticker and attach market + cross-sectional columns."""
    m = market if market is not None else market_proxy(frames)
    s50, s200 = sma(m.close, 50), sma(m.close, 200)
    mkt_trend = (m.close > s200) & (s50 > s200)
    dist = (m.close.pct_change() <= -0.002) & (m.volume > m.volume.shift(1))
    mkt_dist_ok = dist.astype(int).rolling(25).sum() <= 4

    out = {k: enrich(f) for k, f in frames.items()}
    rs = pd.DataFrame({k: d.ret126 for k, d in out.items()}).rank(axis=1, pct=True) * 100
    for k, d in out.items():
        d["rs_pct"] = rs[k].reindex(d.index)
        d["mkt_trend"] = mkt_trend.reindex(d.index)
        d["mkt_dist_ok"] = mkt_dist_ok.reindex(d.index)
    return out


# --------------------------------------------------------------------------- #
# Trade simulation (one position per rule per ticker; results in R multiples)
# --------------------------------------------------------------------------- #
def simulate(d, signal, cfg: ExitCfg):
    o, h, l, c = (d[x].to_numpy() for x in ("open", "high", "low", "close"))
    atr, e10, e20, s5 = (d[x].to_numpy() for x in ("atr", "e10", "e20", "s5"))
    stop_ref = signal.stop_ref.to_numpy()
    n = len(d)
    cost = cfg.cost_bps / 1e4
    trades, last_exit = [], -1

    for t in np.flatnonzero(signal.sig.to_numpy()):
        if t <= last_exit or t + 1 >= n or np.isnan(atr[t]):
            continue
        # ---- entry
        if signal.entry == "next_open":
            e, entry = t + 1, o[t + 1]
        else:
            trig, e = h[t] + 0.01, -1
            for k in range(t + 1, min(t + 1 + signal.valid, n)):
                if h[k] >= trig:
                    e, entry = k, max(o[k], trig)
                    break
            if e < 0:
                continue
        # ---- X01 initial stop
        stop = stop_ref[t] - 0.1 * atr[t] if cfg.stop == "setup" else entry - cfg.atr_mult * atr[t]
        if np.isnan(stop):
            continue
        stop = min(stop, entry - cfg.min_risk_atr * atr[t])
        risk = entry - stop
        if risk / entry > cfg.max_risk_pct:
            continue
        target = entry + cfg.target_r * risk if cfg.target_r else None
        pos, realized, partial_done, armed, hh = 1.0, 0.0, False, False, h[e]
        i = e
        while True:
            first = i == e
            # stop first (conservative when stop and target fall in the same bar)
            if not first and o[i] <= stop:
                px = o[i]; break
            if l[i] <= stop:
                px = stop; break
            if cfg.partial_r and not partial_done and h[i] >= entry + cfg.partial_r * risk:
                lvl = entry + cfg.partial_r * risk
                realized += 0.5 * ((lvl if first else max(o[i], lvl)) - entry) / risk
                pos, partial_done, stop = 0.5, True, max(stop, entry)
            if target is not None and h[i] >= target:
                px = target if first else max(o[i], target); break
            # end-of-bar decisions -> act at next open
            held = i - e + 1
            out = held >= cfg.max_hold
            if cfg.trail == "ema10":
                armed = armed or c[i] > e10[i]
                out |= armed and c[i] < e10[i]
            elif cfg.trail == "chandelier":
                hh = max(hh, h[i])
                stop = max(stop, hh - 3 * atr[i])
            if cfg.climax:
                out |= c[i] > e20[i] + 3 * atr[i]
            if cfg.sma5_exit:
                out |= c[i] > s5[i]
            if cfg.stale and held >= cfg.stale[0]:
                out |= (c[i] - entry) / risk < cfg.stale[1]
            if i + 1 >= n:
                px = c[i]; break
            i += 1
            if out:
                px = o[i]; break
        last_exit = i
        r = realized + pos * (px - entry) / risk - cost * (entry + px) / risk
        trades.append((d.index[t], d.index[e], d.index[i], entry, stop, px, r, i - e + 1))
    return pd.DataFrame(trades, columns=["sig_date", "entry_date", "exit_date", "entry", "stop", "exit", "R", "bars"])


# --------------------------------------------------------------------------- #
# Full run
# --------------------------------------------------------------------------- #
def run(frames, market=None, exits=None, entries=None):
    """Returns (panel, trades).

    panel : one row per ticker-day with forward returns, context flags, entry flags
    trades: one row per simulated trade for every entry rule x exit variant
    """
    from .rules import EXITS
    exits = exits or EXITS
    entries = entries or ENTRIES
    uni = prepare_universe(frames, market)
    panels, trades = [], []
    for name, d in uni.items():
        if len(d) < 260:
            continue
        p = pd.DataFrame(index=d.index)
        for hz in HORIZONS:     # buy next open, hold hz bars
            p[f"fwd{hz}"] = d.close.shift(-hz) / d.open.shift(-1) - 1
        ctx = pd.DataFrame({k: f(d).fillna(False).astype(bool) for k, f in CONTEXT.items()})
        liquid = ctx["C09 liquidity"]
        p = p.join(ctx)
        for rule, fn in entries.items():
            sg = fn(d)
            sg.sig = sg.sig.fillna(False).astype(bool) & liquid
            p[rule] = sg.sig
            for xname, cfg in exits.items():
                tr = simulate(d, sg, cfg)
                if len(tr):
                    tr.insert(0, "exit_rule", xname)
                    tr.insert(0, "rule", rule)
                    tr.insert(0, "ticker", name)
                    trades.append(tr.join(ctx, on="sig_date"))
        p.insert(0, "ticker", name)
        panels.append(p)
    panel = pd.concat(panels).rename_axis("date").reset_index()
    return panel, (pd.concat(trades, ignore_index=True) if trades else pd.DataFrame())


# --------------------------------------------------------------------------- #
# Statistics
# --------------------------------------------------------------------------- #
def trade_stats(tr):
    if not len(tr):
        return pd.Series(dtype=float)
    r = tr.R
    wins, losses = r[r > 0].sum(), -r[r <= 0].sum()
    return pd.Series({
        "trades": len(r),
        "win%": 100 * (r > 0).mean(),
        "avgR": r.mean(),
        "PF": wins / losses if losses > 0 else np.nan,
        "t": r.mean() / (r.std(ddof=1) / np.sqrt(len(r))) if len(r) > 2 else np.nan,
        "avg bars": tr.bars.mean(),
    })


def event_study(panel, flag, base="C09 liquidity"):
    """Forward return of flagged ticker-days minus the same-day universe average.

    The t-stat clusters by date and is divided by sqrt(horizon) to allow for
    overlapping holding periods, so it is deliberately conservative.
    """
    uni = panel[panel[base]]
    sel = uni[uni[flag]]
    out = {"signals": len(sel)}
    for hz in HORIZONS:
        col = f"fwd{hz}"
        ex = (sel.groupby("date")[col].mean() - uni.groupby("date")[col].mean()).dropna()
        out[f"raw{hz}%"] = 100 * sel[col].mean()
        out[f"excess{hz}%"] = 100 * ex.mean()
        sd = ex.std(ddof=1) if len(ex) > 2 else 0
        out[f"t{hz}"] = ex.mean() / (sd / np.sqrt(len(ex))) / np.sqrt(hz) if sd > 0 else np.nan
    return pd.Series(out)
