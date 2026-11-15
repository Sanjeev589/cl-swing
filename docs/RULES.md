# Swing trading rule set (39 rules)

Stocks only, long only, daily bars. Every rule is decided at the **close of bar t**
using data up to and including t. The code in `swing/rules.py` is the authoritative
definition; this file describes the same rules in words.

Notation: `O H L C V` = today's bar; `X[n]` = value n bars ago; `SMAn`, `EMAn` =
moving averages of the close; `ATR` = 14-bar Wilder ATR; `V50` = 50-bar average
volume excluding today; `CLV` = (C - L) / (H - L), where the close sits in the bar;
`HHn` / `LLn` = highest high / lowest low of the **previous** n bars.

Sources refer to the numbered books in `docs/BOOKS.md`.

## A. Context filters (C) - is this a stock and a market worth trading?

A filter is a true/false state per day. It never triggers a trade by itself.

| ID | Rule | Exact condition | Sources |
|----|------|-----------------|---------|
| C01 | Market trend | Index C > SMA200 and SMA50 > SMA200 | 6, 5, 8, 16 |
| C02 | Market not under distribution | Fewer than 5 distribution days in the last 25 (index down 0.2% or more on higher volume than the day before) | 5 |
| C03 | Stage 2 uptrend | C > SMA150 > SMA200 and SMA200 higher than 20 bars ago | 6, 4 |
| C04 | Trend template | C03, plus SMA50 > SMA150, C > SMA50, C at least 30% above the 52-week low and no more than 25% below the 52-week high | 4 |
| C05 | Relative strength | 126-bar return ranks in the top 30% of the universe (percentile >= 70) | 5, 4 |
| C06 | Near the 52-week high | C >= 85% of the 252-bar high | 7, 5, 8 |
| C07 | Swing structure | Last two confirmed swing highs are rising and last two confirmed swing lows are rising (a swing point is the extreme of 3 bars either side, known 3 bars later) | 16, 1, 3 |
| C08 | Weekly trend | In the last completed week: weekly close > 13-week EMA and the EMA is rising | 20, 6, 16 |
| C09 | Liquidity | C >= 5 and 20-bar average dollar volume >= 5 million. Applied to every signal as a precondition | 5, 4 |

## B. Entry setups (E)

"Next open" = buy at the open of bar t+1. "Buy stop" = buy only if price trades
0.01 above the setup bar's high within the stated number of bars, otherwise the
setup is cancelled. "Stop ref" is the structural level used by rule X01.

### Pullbacks in a trend

| ID | Setup | Exact condition | Entry | Stop ref | Sources |
|----|-------|-----------------|-------|----------|---------|
| E01 | Holy Grail | ADX(14) > 30 and +DI > -DI; L <= EMA20 today after 5 straight bars with L > EMA20 | Buy stop, 3 bars | L | 10, 2 |
| E02 | First pullback to SMA50 | C > SMA200; SMA50 higher than 10 bars ago; L <= 1.01 x SMA50; C > SMA50; CLV >= 0.5; no bar within 1% of SMA50 in the prior 20 | Next open | L | 5 |
| E03 | Landry pullback | A 20-bar high, followed immediately by 3 to 7 consecutive lower highs; C > SMA50 and SMA50 rising | Buy stop, 1 bar | 3-bar low | 12 |
| E04 | High 2 | After a 20-bar high: a run of lower highs, a bar that takes out the prior high (High 1), more lower highs, then a second bar that takes out the prior high. Within 20 bars of the high; EMA20 > SMA50 and C > SMA50 | Next open | Low since the high | 1 |
| E05 | Bull flag | Pole: highest high of the last 12 bars, 3-12 bars ago, at least 4 ATR above the low of the 10 bars before it. Flag gives back no more than 50% of the pole on lower average volume than the pole's last 5 bars. Today C > highest high of the flag; C > SMA50 | Next open | Flag low | 9, 14, 2 |
| E06 | RSI(2) oversold | C > SMA200 and RSI(2) < 10 | Next open | C - 2.5 ATR | 11 |
| E21 | No-supply pullback | EMA20 > SMA50, C > SMA50; at least 2 of the last 3 closes down; V is the lowest of 10 bars; range <= 0.7 ATR | Buy stop, 2 bars | 3-bar low | 18, 19, 4 |
| E22 | Anchored-VWAP support | VWAP anchored at the lowest low of the last 126 bars (anchor at least 20 bars old); L <= 1.005 x AVWAP, C > AVWAP, prior 5 closes all above AVWAP | Next open | L | 20 |

### Failed moves and reversals at lows

| ID | Setup | Exact condition | Entry | Stop ref | Sources |
|----|-------|-----------------|-------|----------|---------|
| E07 | Spring / Turtle Soup | L < LL20 where that 20-bar low was set at least 4 bars ago, and C closes back above it | Next open | L | 10, 18, 3 |
| E08 | Breakout retest | C closed above HH50 2-10 bars ago; no close since below 97% of that level; today L <= 1.01 x level, C > level, C > O. First retest only | Next open | L | 14, 1, 15 |
| E17 | Bullish engulfing | Prior bar down, today up, today's body engulfs the prior body; the two bars hold the 5-bar low; C > SMA50 > SMA200 | Next open | 2-bar low | 17 |
| E18 | Hammer | Lower shadow >= 2 x body, upper shadow <= 25% of range, range >= 0.8 ATR, L is the 10-bar low, C > SMA200 | Buy stop, 2 bars | L | 17 |
| E19 | Outside-day key reversal | L < L[1] and C > H[1]; L is the 10-bar low; C > SMA200 | Next open | L | 16, 9 |
| E20 | Stopping volume | L is the 20-bar low; V >= 2.5 x V50; range >= 1.5 ATR; CLV >= 0.5 | Next open | L | 18, 19 |

### Breakouts from contraction

| ID | Setup | Exact condition | Entry | Stop ref | Sources |
|----|-------|-----------------|-------|----------|---------|
| E09 | 52-week-high breakout | First close above HH252; V >= 1.5 x V50; CLV >= 0.5 | Next open | L | 5, 7, 8 |
| E10 | Tight base (Darvas box) | Prior 15 bars span no more than 3.5 x ATR50; box top within 15% of the 52-week high; first close above the box top; V >= 1.5 x V50; C > SMA50 | Next open | Box low | 7, 15, 14 |
| E11 | Volatility contraction (VCP) | C04 true; three successively tighter ranges (bars 40-21 ago > 20-11 ago > last 10) with the last <= 10%; 10-bar average volume < 85% of V50; C > HH10 on V >= 1.3 x V50 | Next open | 10-bar low | 4 |
| E12 | Cup with handle | Left rim 25-120 bars before the right rim, rims within 5% of each other, cup depth 12-35%, 25%+ advance before the left rim; handle 5-20 bars, no deeper than 12%, in the upper half of the cup; C > right rim on V >= 1.4 x V50 | Next open | Handle low | 5 |
| E13 | NR7 | Narrowest range of the last 7 bars; C > SMA50 and SMA50 rising | Buy stop, 1 bar | L | 13 |
| E14 | Inside day + NR4 | Inside bar that is also the narrowest of 4; C > SMA50 and SMA50 rising | Buy stop, 1 bar | L | 13, 10 |
| E15 | Thrust bar | True range >= 2 x yesterday's ATR; CLV >= 0.75; C > HH20; V >= 1.5 x V50 | Next open | Bar midpoint | 1, 13 |
| E16 | Gap up on volume | O >= 3% above H[1]; L > H[1] (gap unfilled); C >= O; V >= 2 x V50 | Next open | H[1] | 14, 5, 17 |

## C. Risk and exit rules (X)

| ID | Rule | Definition | Sources |
|----|------|------------|---------|
| X01 | Initial stop | Stop = stop ref - 0.1 ATR, never closer than 0.75 ATR to entry. If the stop is more than 8% from entry, skip the trade. Variant X01b: stop = entry - 2 ATR | 5, 4, 1 |
| X02 | Position size | Risk 1% of equity per trade: shares = 0.01 x equity / (entry - stop). All results are therefore reported in R (multiples of initial risk) | all |
| X03 | Reward target | Sell all at +2R | 15, 14 |
| X04 | Partial profit | Sell half at +1R and move the stop to breakeven | 10, 12 |
| X05 | Trailing stop | (a) exit on the first close below EMA10 once price has closed above it, or (b) chandelier: highest high since entry - 3 ATR. Maximum hold 60 bars | 7, 6, 12 |
| X06 | Time stop | Hard exit after 20 bars. Variant: exit after 5 bars if the trade is below +0.5R | 4, 12, 11 |
| X07 | Sell into a climax | Exit when C > EMA20 + 3 ATR | 9, 5 |
| X08 | Exit on strength | Exit when C > SMA5; maximum hold 10 bars | 11 |

All end-of-bar exits are executed at the next open. If a bar opens below the stop,
the fill is that open (gap risk is included). If a stop and a target fall inside
the same bar, the stop is assumed to have been hit first.

## Not in the tested set

These recur in the books but cannot be tested from daily OHLCV alone, so they are
left as discretionary guidance:

- Do not hold a new position through an earnings report (needs an earnings calendar).
- Sector and industry-group leadership (needs sector membership).
- Measured-move targets for flags and boxes (pole height or box height projected
  from the breakout). The fixed 2R target in X03 stands in for these.
- Portfolio heat limits, such as Elder's cap on total open risk.
- Short selling. Every rule has a mirror image, but shorts are not coded.

## How each rule is tested

1. **Event study.** For every ticker-day where a rule is true, the 5/10/20-bar
   return from the next open is compared with the average of all liquid stocks on
   the same day. This removes the market's drift and does not depend on any exit.
2. **Trade simulation.** Each entry setup is traded with every exit rule, one open
   position per setup per ticker, 5 bps cost per side, results in R.
3. **Random benchmark.** A random 3% of days is traded with the same stop and exit
   logic. A setup has to beat this, not zero, because a rising market makes random
   long entries profitable.
4. **Filter split.** All trades are split by each context filter at signal time.

A rule earns a place in a live system only if it beats the random benchmark, has
a t-statistic above 2, and does so in more than one sample.
