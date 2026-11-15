# Backtest report: Dow 30, 2006-2017

31 tickers, 2006-01-03 to 2017-12-29, 93,587 ticker-days. Long only, 5 bps cost per side, one open trade per rule per ticker.

## 1. Entry setups

`excessN%` = mean N-day return after the signal (bought at next open) minus the same-day universe average; `t20` is date-clustered and overlap-adjusted (|t| > 2 is meaningful). Trade columns use the baseline exit (X00 baseline: setup stop + 20-bar time exit). `stack` = only signals where C01 + C04 + C05 are all true.

|                                       |   signals |   excess5% |   excess10% |   excess20% |   t20 |   trades |   win% |   avgR |   PF |     t |   stack trades |   stack avgR |
|:--------------------------------------|----------:|-----------:|------------:|------------:|------:|---------:|-------:|-------:|-----:|------:|---------------:|-------------:|
| E00 random entry (benchmark)          |      2699 |      -0.07 |       -0.07 |        0.05 |  0.09 |     2099 |  26.3  |   0.14 | 1.17 |  2.5  |            279 |         0.36 |
| E01 Holy Grail (ADX + EMA20 pullback) |       535 |       0.15 |        0.07 |        0.22 |  0.22 |      273 |  29.3  |  -0.09 | 0.88 | -0.8  |             92 |         0.1  |
| E02 first pullback to SMA50           |       199 |       0.04 |       -0.09 |       -0.27 | -0.17 |      194 |  27.84 |   0.02 | 1.02 |  0.09 |             67 |         0.21 |
| E03 Landry 3-7 bar pullback           |      2184 |       0.02 |       -0.09 |       -0.41 | -0.74 |      947 |  28.83 |   0.03 | 1.04 |  0.48 |            259 |         0.08 |
| E04 High 2 (two-legged pullback)      |      1943 |       0.08 |        0.08 |        0.27 |  0.45 |     1534 |  34.55 |   0.15 | 1.21 |  2.76 |            371 |         0.39 |
| E05 bull flag breakout                |       843 |      -0.03 |        0.11 |       -0.01 | -0.01 |      607 |  43.66 |   0.2  | 1.34 |  2.64 |            183 |         0.36 |
| E06 RSI(2) < 10 above SMA200          |      4987 |       0.12 |        0.13 |        0.1  |  0.24 |     1631 |  51.44 |   0.16 | 1.36 |  5.09 |            261 |         0.1  |
| E07 spring / Turtle Soup              |      1273 |      -0.12 |       -0.18 |       -0.16 | -0.2  |     1122 |  26.92 |   0.1  | 1.13 |  1.4  |             51 |         0.05 |
| E08 breakout retest (throwback)       |      1769 |      -0.05 |       -0.04 |       -0.16 | -0.3  |     1191 |  26.36 |   0.07 | 1.08 |  0.96 |            359 |         0.15 |
| E09 52-week-high breakout on volume   |       375 |      -0.03 |       -0.12 |        0.13 |  0.1  |      313 |  41.85 |   0.22 | 1.36 |  1.99 |            155 |         0.24 |
| E10 tight base (Darvas box) breakout  |       326 |       0.09 |        0.04 |        0.31 |  0.25 |      247 |  52.23 |   0.08 | 1.24 |  1.27 |             54 |         0.14 |
| E11 volatility contraction (VCP)      |        65 |       0.16 |        0.41 |        0.83 |  0.37 |       59 |  50.85 |   0.04 | 1.11 |  0.34 |             35 |         0.05 |
| E12 cup with handle                   |        47 |       0.36 |        0.08 |        0.99 |  0.23 |       34 |  50    |   0.16 | 1.39 |  0.73 |             12 |         0.17 |
| E13 NR7 breakout                      |      6893 |       0.04 |       -0.01 |        0.03 |  0.09 |     2407 |  25.09 |   0.07 | 1.08 |  1.29 |            596 |         0.42 |
| E14 inside day + NR4                  |      3230 |       0.02 |       -0    |        0.02 |  0.05 |     1479 |  24.68 |   0.03 | 1.04 |  0.53 |            404 |         0.16 |
| E15 thrust bar breakout               |       370 |      -0.02 |       -0.13 |       -0.02 | -0.01 |      345 |  29.86 |   0.08 | 1.1  |  0.64 |            106 |         0.17 |
| E16 gap up on volume                  |        87 |      -0.22 |       -0.3  |        0.21 |  0.08 |       54 |  53.7  |   0.11 | 1.32 |  0.82 |             17 |         0.25 |
| E17 bullish engulfing in pullback     |       522 |      -0.39 |       -0.31 |       -0.41 | -0.43 |      475 |  29.05 |  -0.07 | 0.9  | -0.85 |            141 |        -0.06 |
| E18 hammer at 10-day low              |       641 |       0.12 |       -0.05 |       -0.44 | -0.42 |      423 |  30.26 |  -0.03 | 0.96 | -0.33 |             66 |        -0.35 |
| E19 outside-day key reversal          |       206 |      -0.16 |       -0.26 |       -0.59 | -0.4  |      199 |  33.17 |  -0.12 | 0.83 | -0.98 |             33 |        -0.16 |
| E20 stopping volume (climax low)      |       133 |       0.35 |        0.87 |        0.46 |  0.13 |       92 |  25    |  -0.28 | 0.63 | -1.74 |              4 |        -0.51 |
| E21 no-supply pullback                |      1434 |       0.02 |       -0.05 |        0.16 |  0.22 |      800 |  29.25 |   0.12 | 1.15 |  1.43 |            173 |         0.57 |
| E22 anchored-VWAP support             |      2580 |       0.04 |        0.09 |        0.28 |  0.54 |     1123 |  27.25 |   0.19 | 1.23 |  2.42 |              9 |         0.37 |

## 2. Context filters

`fwd20% on/off` = raw 20-day forward return of all liquid ticker-days with the filter true/false. `avgR on/off` = baseline-exit result of all entry-setup trades split by the filter at signal time.

|                                  |   % days on |   fwd20% on |   fwd20% off |   excess20% |    t20 |   trades on |   avgR on |   avgR off |
|:---------------------------------|------------:|------------:|-------------:|------------:|-------:|------------:|----------:|-----------:|
| C01 market trend                 |       70.93 |        0.95 |         0.82 |      nan    | nan    |       12609 |      0.11 |      -0.03 |
| C02 market distribution days < 5 |       49.2  |        0.72 |         1.1  |      nan    | nan    |        9043 |      0.05 |       0.14 |
| C03 stage 2 uptrend              |       44.78 |        0.8  |         1    |       -0.03 |  -0.2  |        9618 |      0.07 |       0.12 |
| C04 trend template               |       22.36 |        0.85 |         0.93 |        0.29 |   1.27 |        5393 |      0.1  |       0.08 |
| C05 relative strength >= 70      |       31.11 |        0.83 |         0.95 |       -0.13 |  -0.79 |        6317 |      0.16 |       0.03 |
| C06 within 15% of 52w high       |       68.08 |        0.8  |         1.15 |       -0.18 |  -1.26 |       12701 |      0.07 |       0.18 |
| C07 HH+HL swing structure        |       34.64 |        0.8  |         0.98 |       -0.16 |  -1    |        7450 |      0.02 |       0.15 |
| C08 weekly trend up              |       60.05 |        0.85 |         1.01 |       -0.05 |  -0.42 |       13512 |      0.08 |       0.14 |

## 3. Exit rules (all entry setups pooled)

| exit_rule                                   |   trades |   win% |   avgR |   PF |      t |   avg bars |
|:--------------------------------------------|---------:|-------:|-------:|-----:|-------:|-----------:|
| X00 baseline: setup stop + 20-bar time exit |    15549 |  31.9  |   0.09 | 1.12 |   4.92 |      11.06 |
| X01b ATR stop (2 ATR) instead of setup stop |    14180 |  45.61 |   0.11 | 1.2  |   9.07 |      15.15 |
| X03 fixed 2R target                         |    17283 |  38.84 |   0    | 1    |   0.24 |       7.35 |
| X04 half off at 1R, stop to breakeven       |    16450 |  50.67 |   0.01 | 1.01 |   0.61 |       9.21 |
| X05a trail: close below EMA10               |    16916 |  36.7  |   0.05 | 1.08 |   3.06 |       7.86 |
| X05b trail: chandelier 3 ATR                |    14711 |  29.37 |   0.16 | 1.23 |   7.41 |      14.1  |
| X06 stale exit: <0.5R after 5 bars          |    17103 |  37.33 |   0.04 | 1.07 |   2.73 |       7.31 |
| X07 climax exit: close > EMA20 + 3 ATR      |    16207 |  34.08 |   0.06 | 1.08 |   3.67 |       9.5  |
| X08 exit on strength: close > SMA5          |    19792 |  50.35 |  -0.06 | 0.82 | -10.64 |       2.45 |

### Average R by entry setup and exit rule

| rule                                  |   X00 |   X01b |   X03 |   X04 |   X05a |   X05b |   X06 |   X07 |   X08 |
|:--------------------------------------|------:|-------:|------:|------:|-------:|-------:|------:|------:|------:|
| E01 Holy Grail (ADX + EMA20 pullback) | -0.09 |   0.02 | -0.09 | -0.07 |  -0.1  |  -0.07 | -0.15 | -0.06 | -0.06 |
| E02 first pullback to SMA50           |  0.02 |   0.06 | -0.09 |  0.02 |   0.08 |   0.09 | -0.07 |  0    | -0.05 |
| E03 Landry 3-7 bar pullback           |  0.03 |   0.03 | -0.06 | -0.03 |  -0.04 |   0.13 | -0    |  0.01 | -0.12 |
| E04 High 2 (two-legged pullback)      |  0.15 |   0.11 |  0.05 |  0.06 |   0.06 |   0.19 |  0.1  |  0.12 | -0.03 |
| E05 bull flag breakout                |  0.2  |   0.21 |  0.13 |  0.09 |   0.1  |   0.23 |  0.11 |  0.11 | -0.04 |
| E06 RSI(2) < 10 above SMA200          |  0.16 |   0.14 |  0.14 |  0.13 |   0.09 |   0.23 |  0.09 |  0.15 |  0.06 |
| E07 spring / Turtle Soup              |  0.1  |   0.1  | -0.05 | -0.02 |  -0.02 |   0.15 |  0.05 |  0.11 | -0.1  |
| E08 breakout retest (throwback)       |  0.07 |   0.09 | -0.01 | -0.05 |   0.06 |   0.2  |  0    |  0.04 | -0.04 |
| E09 52-week-high breakout on volume   |  0.22 |   0.15 |  0.18 |  0.12 |   0.18 |   0.27 |  0.05 |  0.07 | -0.06 |
| E10 tight base (Darvas box) breakout  |  0.08 |   0.11 |  0.07 |  0.08 |   0.01 |   0.06 | -0.01 |  0.07 | -0.03 |
| E11 volatility contraction (VCP)      |  0.04 |   0.03 |  0.07 |  0.12 |   0    |   0    |  0.02 |  0.07 | -0.04 |
| E12 cup with handle                   |  0.16 |   0.36 |  0.1  |  0.03 |  -0.02 |  -0.02 | -0.12 | -0.08 |  0.02 |
| E13 NR7 breakout                      |  0.07 |   0.13 | -0.03 | -0.04 |   0.05 |   0.15 |  0.04 |  0.03 | -0.13 |
| E14 inside day + NR4                  |  0.03 |   0.14 | -0.1  | -0.09 |  -0.04 |   0.07 | -0.02 | -0.01 | -0.13 |
| E15 thrust bar breakout               |  0.08 |   0.13 |  0.07 |  0.01 |  -0    |   0.08 |  0.07 | -0.04 | -0.02 |
| E16 gap up on volume                  |  0.11 |   0.2  |  0.09 |  0.06 |   0.15 |   0.16 |  0.06 | -0.06 | -0.03 |
| E17 bullish engulfing in pullback     | -0.07 |  -0.02 | -0.1  | -0.12 |  -0.03 |  -0.03 | -0.12 | -0.1  | -0.15 |
| E18 hammer at 10-day low              | -0.03 |  -0.1  | -0.05 |  0.01 |   0.09 |   0.11 |  0.04 | -0.04 |  0.02 |
| E19 outside-day key reversal          | -0.12 |   0.01 | -0.08 | -0.1  |  -0.03 |  -0.09 | -0.16 | -0.14 | -0.13 |
| E20 stopping volume (climax low)      | -0.28 |  -0.12 | -0.28 | -0.24 |  -0.19 |  -0.16 | -0.07 | -0.25 | -0.07 |
| E21 no-supply pullback                |  0.12 |   0.16 |  0.03 |  0.04 |   0.08 |   0.16 |  0    |  0.09 | -0.06 |
| E22 anchored-VWAP support             |  0.19 |   0.16 |  0.05 |  0.09 |   0.15 |   0.4  |  0.14 |  0.16 | -0.02 |
