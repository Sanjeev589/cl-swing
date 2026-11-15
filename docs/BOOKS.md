# The 20 books and what each contributes

Scope: price-action swing trading of stocks (holding days to weeks, daily bars).
This is a synthesis from knowledge of the books, not a page-by-page re-read, and
none of it is quoted. The rule IDs point to `docs/RULES.md`.

## Selection

Books were chosen for (a) price/volume-based method rather than indicators or
fundamentals, (b) applicability to stocks on a daily chart, and (c) rules concrete
enough to code. Books that are mainly psychology, options, or intraday futures
scalping were left out.

| # | Book | Author | Core contribution to swing trading | Rules derived |
|---|------|--------|-------------------------------------|---------------|
| 1 | Trading Price Action: Trends / Trading Ranges / Reversals | Al Brooks | Bar-by-bar reading; with-trend pullback entries (High 1/High 2), two-legged corrections, strong breakout bars with follow-through, most breakouts from ranges fail | C07, E04, E08, E15 |
| 2 | The Art and Science of Technical Analysis | Adam Grimes | Statistical testing of patterns; pullbacks in trends are the one robust pattern family, most candlestick and MA folklore has no edge on its own | E01, E05, the test design |
| 3 | YTC Price Action Trader | Lance Beggs | Market structure (swing highs/lows), trade toward trapped traders, retests of broken levels | C07, E07, E08 |
| 4 | Trade Like a Stock Market Wizard | Mark Minervini | Trend template, volatility contraction pattern (VCP), volume dry-up before the pivot, tight stops, sell stale trades | C04, E11, X01, X06 |
| 5 | How to Make Money in Stocks | William O'Neil | Bases (cup with handle), pivot breakouts on 40-50%+ volume, relative strength rank, market direction via distribution days, cut losses at 7-8% | C02, C05, E09, E12, E16, X01 |
| 6 | Secrets for Profiting in Bull and Bear Markets | Stan Weinstein | Four-stage model; only buy stage 2 (above a rising 30-week MA), market filter first | C01, C03, C08 |
| 7 | How I Made $2,000,000 in the Stock Market | Nicolas Darvas | Box theory: buy new-high breakouts out of tight boxes on volume, stop just under the box, trail by rising boxes | C06, E10, X05 |
| 8 | How to Trade in Stocks | Jesse Livermore | Pivotal points, trade the line of least resistance, add only to winners, wait for the market to confirm | C01, C06, E09 |
| 9 | The Master Swing Trader | Alan Farley | Pattern cycles (contraction to expansion), flags, reversal bars at support, execution zone, exits into strength | E05, E19, X07 |
| 10 | Street Smarts | Linda Raschke & Larry Connors | Holy Grail (ADX + 20 EMA pullback), Turtle Soup (failed 20-day breakout), 80-20s, ID/NR4 | E01, E07, E14, X04 |
| 11 | Short Term Trading Strategies That Work | Larry Connors & Cesar Alvarez | Quantified mean reversion: buy pullbacks above the 200-day MA (RSI-2), exit on strength, tight stops hurt | E06, X08 |
| 12 | Dave Landry on Swing Trading | Dave Landry | Trend qualifiers, 3-7 bar pullbacks entered above the prior high, take half at 1R and trail | E03, X04, X06 |
| 13 | Day Trading with Short Term Price Patterns and Opening Range Breakout | Toby Crabel | Volatility contraction precedes expansion: NR4/NR7, inside days; measured with statistics | E13, E14 |
| 14 | Encyclopedia of Chart Patterns | Thomas Bulkowski | Measured failure rates and average moves for every classic pattern; throwbacks, flags, gaps, breakouts near the yearly high do best | E05, E08, E10, E16 |
| 15 | Technical Analysis of Stock Trends | Edwards & Magee | Classic continuation/reversal formations, support-resistance role reversal, measured moves, volume confirmation | E08, E10, X03 |
| 16 | Technical Analysis of the Financial Markets | John Murphy | Dow theory trend definition, moving-average trend filters, key reversal days, multiple-timeframe confirmation | C01, C07, C08, E19 |
| 17 | Japanese Candlestick Charting Techniques | Steve Nison | Engulfing, hammer, windows (gaps); candles are triggers that need location and trend context | E16, E17, E18 |
| 18 | Trades About to Happen (Wyckoff method) | David Weis | Springs and upthrusts, effort versus result, climactic volume, tests on low volume | E07, E20, E21 |
| 19 | A Complete Guide to Volume Price Analysis | Anna Coulling | Volume validates or contradicts the bar: stopping volume, no-supply tests, anomalies | E20, E21 |
| 20 | Technical Analysis Using Multiple Timeframes | Brian Shannon | Trade in the direction of the higher timeframe, anchored VWAP as the average holder's cost | C08, E22 |

## Where the books agree

Reading across all 20, the same handful of ideas recur. These agreements shaped
the rule set more than any single book did.

1. **Trade with the larger trend.** Weinstein, O'Neil, Minervini, Murphy, Brooks,
   Landry and Shannon all filter by a long moving average or a higher timeframe
   before looking for an entry. (C01, C03, C04, C08)
2. **Market first, stock second.** Most stocks follow the index; O'Neil, Weinstein
   and Livermore stop buying when the market trend breaks. (C01, C02)
3. **Buy leaders near highs, not laggards near lows.** O'Neil, Darvas, Minervini,
   Livermore. (C05, C06)
4. **Enter on a pullback or on a breakout from contraction.** Two families:
   pullback entries (Brooks, Grimes, Raschke, Landry, Connors) and
   contraction-then-expansion breakouts (Crabel, Darvas, Minervini, O'Neil).
5. **Volume confirms.** Expansion on breakouts, dry-up on pullbacks, climax at
   turning points (O'Neil, Wyckoff/Weis, Coulling, Minervini).
6. **Failed moves are signals.** Springs, Turtle Soup, failed breakouts (Wyckoff,
   Raschke, Brooks, Beggs).
7. **Define risk before entry and keep losses small.** Every author; the specifics
   (7-8% max, structure stop, 1-2% of equity) vary.

## Where they disagree

These are real conflicts, and they are exactly what testing has to settle:

- **Stops:** Minervini/O'Neil want tight stops; Connors and Alvarez show tight
  stops reduce returns on short-term setups.
- **Exits:** Raschke, Landry and Farley take quick partial profits; Darvas,
  Weinstein and Livermore let winners run with a trailing stop.
- **Buy strength or weakness:** O'Neil/Darvas buy new highs; Connors buys
  short-term oversold. Both can be right on different horizons.
- **Candlesticks:** Nison treats them as signals; Grimes and Bulkowski find most
  have little edge without context.

## How "proven" each idea is

"Proven" needs care. Three levels of evidence exist for these techniques:

| Evidence | Techniques |
|----------|-----------|
| Independent academic support | Trend/time-series momentum (C01, C03), cross-sectional momentum (C05), 52-week-high effect (C06), short-term reversal (E06) |
| Statistics published in the book itself | Bulkowski's pattern studies (E05, E08, E10, E16), Connors/Alvarez (E06, X08), Crabel (E13, E14), Grimes (pullbacks) |
| Author track record and case studies only | Minervini VCP, O'Neil cup with handle, Darvas box, Wyckoff/VPA volume reading, Brooks bar counting, Raschke setups, anchored VWAP |

The third group is the largest. That is why the rule set is written to be
falsified on data rather than taken on authority.
