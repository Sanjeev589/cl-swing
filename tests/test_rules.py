import numpy as np
import pandas as pd
import pytest

from swing.engine import prepare_universe, simulate
from swing.rules import CONTEXT, ENTRIES, ExitCfg, Signal


def synth(seed, n=700):
    rng = np.random.default_rng(seed)
    close = 50 * np.exp(np.cumsum(rng.normal(0.0006, 0.018, n)))
    open_ = np.r_[close[0], close[:-1]] * np.exp(rng.normal(0, 0.006, n))
    high = np.maximum(open_, close) * (1 + rng.uniform(0, 0.015, n))
    low = np.minimum(open_, close) * (1 - rng.uniform(0, 0.015, n))
    vol = rng.lognormal(14, 0.5, n)
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.DataFrame({"open": open_, "high": high, "low": low, "close": close, "volume": vol}, idx)


@pytest.fixture(scope="module")
def frames():
    return {f"S{i}": synth(i) for i in range(8)}


def test_no_lookahead(frames):
    """A rule's output on bar t must not change when later bars are removed."""
    cut = 600
    full = prepare_universe(frames)
    part = prepare_universe({k: f.iloc[:cut] for k, f in frames.items()})
    fired = 0
    for k in frames:
        for name, fn in {**CONTEXT, **ENTRIES}.items():
            a, b = fn(full[k]), fn(part[k])
            if isinstance(a, Signal):
                sa, sb = a.sig.fillna(False), b.sig.fillna(False)
                pd.testing.assert_series_equal(sa.iloc[:cut], sb, check_names=False, obj=name)
                m = sb.to_numpy(bool)
                np.testing.assert_allclose(a.stop_ref.iloc[:cut][m], b.stop_ref[m], err_msg=name)
                fired += m.sum()
            else:
                pd.testing.assert_series_equal(a.fillna(False).iloc[:cut], b.fillna(False), check_names=False, obj=name)
    assert fired > 100


def _frame(rows):
    d = pd.DataFrame(rows, columns=["open", "high", "low", "close"], index=pd.bdate_range("2020-01-01", periods=len(rows)))
    for c in ("atr", "e10", "e20", "s5"):
        d[c] = 1.0
    return d


def _sig(d, entry="next_open", stop=9.1):
    s = pd.Series(False, d.index)
    s.iloc[0] = True
    return Signal(s, pd.Series(stop, d.index), entry, 1)


def test_stop_and_gap_through_stop():
    cfg = ExitCfg(cost_bps=0, max_risk_pct=1)
    d = _frame([(10, 10, 10, 10), (10, 10.5, 9.8, 10.2), (10.2, 10.3, 8.5, 8.6)])
    t = simulate(d, _sig(d), cfg).iloc[0]           # stop = 9.1 - 0.1 = 9.0, risk 1.0
    assert t.exit == 9.0 and t.R == pytest.approx(-1.0)
    d = _frame([(10, 10, 10, 10), (10, 10.5, 9.8, 10.2), (8.0, 8.2, 7.9, 8.0)])
    t = simulate(d, _sig(d), cfg).iloc[0]           # gaps below the stop -> filled at the open
    assert t.exit == 8.0 and t.R == pytest.approx(-2.0)


def test_target_partial_and_buy_stop():
    d = _frame([(10, 10, 10, 10), (10, 10.5, 9.8, 10.2), (10.4, 12.5, 10.3, 12.4), (12.4, 12.6, 12.0, 12.5)])
    assert simulate(d, _sig(d), ExitCfg(cost_bps=0, max_risk_pct=1, target_r=2)).iloc[0].R == pytest.approx(2.0)
    t = simulate(d, _sig(d), ExitCfg(cost_bps=0, max_risk_pct=1, partial_r=1, max_hold=2)).iloc[0]
    assert t.R == pytest.approx(0.5 * 1.0 + 0.5 * 2.4)   # half at 11, rest at 12.4 open after time stop
    # buy stop above the setup high (10.01) is not touched on the next bar -> no trade
    d = _frame([(10, 10, 10, 10), (9.9, 10.0, 9.5, 9.6), (9.6, 11, 9.5, 11)])
    assert simulate(d, _sig(d, "stop_high"), ExitCfg(max_risk_pct=1)).empty
