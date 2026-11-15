# Backtest report: S&P 500 constituents, 2013-2018

500 tickers, 2013-02-08 to 2018-02-07, 618,367 ticker-days. Long only, 5 bps cost per side, one open trade per rule per ticker.

## 1. Entry setups

`excessN%` = mean N-day return after the signal (bought at next open) minus the same-day universe average; `t20` is date-clustered and overlap-adjusted (|t| > 2 is meaningful). Trade columns use the baseline exit (X00 baseline: setup stop + 20-bar time exit). `stack` = only signals where C01 + C04 + C05 are all true.

|                                       |   signals |   excess5% |   excess10% |   excess20% |   t20 |   trades |   win% |   avgR |   PF |     t |   stack trades |   stack avgR |
|:--------------------------------------|----------:|-----------:|------------:|------------:|------:|---------:|-------:|-------:|-----:|------:|---------------:|-------------:|
| E00 random entry (benchmark)          |     18133 |       0.05 |        0.06 |        0.05 |  0.23 |    14212 |  25.89 |   0.12 | 1.15 |  5.65 |           1717 |         0.16 |
| E01 Holy Grail (ADX + EMA20 pullback) |      3917 |      -0.04 |       -0.12 |       -0.1  | -0.17 |     1904 |  28.68 |  -0.09 | 0.88 | -2.12 |            549 |        -0.08 |
| E02 first pullback to SMA50           |      1203 |       0.16 |        0.14 |        0.43 |  0.43 |     1185 |  33.84 |   0.27 | 1.38 |  3.75 |            401 |         0.34 |
| E03 Landry 3-7 bar pullback           |     14327 |       0.02 |       -0.03 |       -0.16 | -0.39 |     6121 |  27.71 |  -0.03 | 0.96 | -1.09 |           1457 |         0.04 |
| E04 High 2 (two-legged pullback)      |     13056 |      -0.09 |       -0.13 |       -0.05 | -0.1  |    10456 |  31.78 |  -0    | 1    | -0.09 |           2241 |         0.08 |
| E05 bull flag breakout                |      5390 |       0.01 |       -0.02 |       -0.08 | -0.13 |     3793 |  40.81 |   0.02 | 1.03 |  0.79 |            936 |         0.13 |
| E06 RSI(2) < 10 above SMA200          |     28601 |       0.04 |       -0.04 |        0.04 |  0.11 |     9662 |  50.26 |   0.09 | 1.21 |  7.71 |           1546 |         0.1  |
| E07 spring / Turtle Soup              |      8477 |       0.07 |        0.11 |        0.07 |  0.13 |     7420 |  28.54 |   0.17 | 1.21 |  5.72 |            390 |         0.11 |
| E08 breakout retest (throwback)       |     11135 |      -0.1  |       -0.13 |       -0.32 | -0.77 |     7796 |  24.67 |  -0.07 | 0.92 | -2.58 |           2085 |         0.06 |
| E09 52-week-high breakout on volume   |      2135 |      -0.07 |       -0.08 |       -0.08 | -0.11 |     1784 |  37.33 |   0.04 | 1.06 |  0.78 |            944 |         0.1  |
| E10 tight base (Darvas box) breakout  |      1927 |      -0.11 |       -0.21 |       -0.19 | -0.23 |     1348 |  51.34 |   0.03 | 1.07 |  0.89 |            373 |         0.06 |
| E11 volatility contraction (VCP)      |       476 |      -0.03 |       -0.11 |       -0.11 | -0.07 |      371 |  45.55 |  -0.04 | 0.92 | -0.6  |            250 |        -0.05 |
| E12 cup with handle                   |       221 |       0.02 |       -0.05 |       -0.2  | -0.09 |      148 |  45.95 |   0.01 | 1.01 |  0.05 |             51 |         0.01 |
| E13 NR7 breakout                      |     45983 |      -0.05 |       -0.05 |       -0.08 | -0.32 |    16649 |  21.68 |  -0.09 | 0.9  | -4.93 |           3800 |         0    |
| E14 inside day + NR4                  |     22002 |       0.01 |       -0.04 |       -0.05 | -0.15 |    10356 |  21.21 |  -0.13 | 0.86 | -5.36 |           2511 |        -0.08 |
| E15 thrust bar breakout               |      2351 |      -0.05 |       -0.07 |        0.06 |  0.08 |     2164 |  30.64 |   0.14 | 1.19 |  2.88 |            551 |         0.41 |
| E16 gap up on volume                  |       684 |       0.34 |        0.38 |        0.09 |  0.07 |      393 |  55.22 |   0.18 | 1.54 |  3.19 |            105 |         0.2  |
| E17 bullish engulfing in pullback     |      3060 |      -0.04 |       -0.13 |       -0.28 | -0.41 |     2706 |  30.23 |  -0.05 | 0.93 | -1.44 |            832 |        -0.05 |
| E18 hammer at 10-day low              |      3325 |      -0.06 |       -0.06 |        0    |  0    |     2383 |  33.78 |   0.08 | 1.11 |  1.84 |            396 |         0.08 |
| E19 outside-day key reversal          |      1400 |      -0.18 |       -0.28 |       -0.01 | -0.01 |     1338 |  37.67 |   0.15 | 1.23 |  2.65 |            210 |         0.13 |
| E20 stopping volume (climax low)      |      1101 |      -0.13 |       -0.18 |       -0.11 | -0.1  |      961 |  42.77 |   0.34 | 1.64 |  4.99 |             34 |        -0.19 |
| E21 no-supply pullback                |      8665 |       0.01 |        0.08 |        0.06 |  0.12 |     4883 |  25.93 |  -0.06 | 0.93 | -1.88 |           1089 |        -0.04 |
| E22 anchored-VWAP support             |     16161 |       0.08 |        0.07 |        0.1  |  0.3  |     6845 |  28.43 |   0.21 | 1.26 |  6.63 |             49 |        -0.56 |

## 2. Context filters

`fwd20% on/off` = raw 20-day forward return of all liquid ticker-days with the filter true/false. `avgR on/off` = baseline-exit result of all entry-setup trades split by the filter at signal time.

|                                  |   % days on |   fwd20% on |   fwd20% off |   excess20% |    t20 |   trades on |   avgR on |   avgR off |
|:---------------------------------|------------:|------------:|-------------:|------------:|-------:|------------:|----------:|-----------:|
| C01 market trend                 |       71.66 |        0.93 |         1.49 |      nan    | nan    |       79276 |      0.03 |      -0.06 |
| C02 market distribution days < 5 |       38.46 |        0.61 |         1.38 |      nan    | nan    |       43142 |     -0.06 |       0.06 |
| C03 stage 2 uptrend              |       41.03 |        0.82 |         1.27 |       -0    |  -0.03 |       57458 |      0    |       0.02 |
| C04 trend template               |       19.76 |        0.75 |         1.17 |        0.03 |   0.15 |       31277 |     -0.02 |       0.02 |
| C05 relative strength >= 70      |       27.46 |        1.18 |         1.05 |        0.13 |   0.76 |       38150 |      0.07 |      -0.03 |
| C06 within 15% of 52w high       |       60.1  |        0.83 |         1.47 |       -0.02 |  -0.14 |       74552 |      0    |       0.03 |
| C07 HH+HL swing structure        |       34.69 |        0.89 |         1.19 |       -0.01 |  -0.12 |       47931 |     -0.04 |       0.06 |
| C08 weekly trend up              |       60.78 |        0.84 |         1.46 |       -0.01 |  -0.05 |       87074 |     -0.01 |       0.16 |

## 3. Exit rules (all entry setups pooled)

| exit_rule                                   |   trades |   win% |   avgR |   PF |      t |   avg bars |
|:--------------------------------------------|---------:|-------:|-------:|-----:|-------:|-----------:|
| X00 baseline: setup stop + 20-bar time exit |   100666 |  30.24 |   0.01 | 1.01 |   1.45 |      10.78 |
| X01b ATR stop (2 ATR) instead of setup stop |    92885 |  44.5  |   0.06 | 1.12 |  13.67 |      15.05 |
| X03 fixed 2R target                         |   111674 |  37.84 |  -0.03 | 0.96 |  -5.86 |       7.24 |
| X04 half off at 1R, stop to breakeven       |   106592 |  49.85 |  -0.03 | 0.94 |  -7.67 |       8.97 |
| X05a trail: close below EMA10               |   109664 |  34.82 |  -0.03 | 0.95 |  -5.29 |       7.6  |
| X05b trail: chandelier 3 ATR                |    96044 |  27.76 |   0.02 | 1.03 |   3.04 |      13.31 |
| X06 stale exit: <0.5R after 5 bars          |   110286 |  35.56 |  -0.03 | 0.95 |  -4.94 |       7.15 |
| X07 climax exit: close > EMA20 + 3 ATR      |   104478 |  32.19 |  -0    | 0.99 |  -0.62 |       9.4  |
| X08 exit on strength: close > SMA5          |   127649 |  49.99 |  -0.06 | 0.81 | -26.84 |       2.42 |

### Average R by entry setup and exit rule

| rule                                  |   X00 |   X01b |   X03 |   X04 |   X05a |   X05b |   X06 |   X07 |   X08 |
|:--------------------------------------|------:|-------:|------:|------:|-------:|-------:|------:|------:|------:|
| E01 Holy Grail (ADX + EMA20 pullback) | -0.09 |  -0.02 | -0.06 | -0.11 |  -0.15 |  -0.04 | -0.17 | -0.05 | -0.12 |
| E02 first pullback to SMA50           |  0.27 |   0.17 |  0.15 |  0.16 |   0.14 |   0.36 |  0.2  |  0.24 |  0.06 |
| E03 Landry 3-7 bar pullback           | -0.03 |   0.06 | -0.06 | -0.06 |  -0.07 |  -0    | -0.07 | -0.04 | -0.1  |
| E04 High 2 (two-legged pullback)      | -0    |   0.04 |  0.01 | -0    |  -0.03 |   0    | -0.03 | -0.01 | -0.03 |
| E05 bull flag breakout                |  0.02 |   0.03 |  0.05 |  0.03 |  -0    |  -0.02 | -0.03 |  0    | -0.03 |
| E06 RSI(2) < 10 above SMA200          |  0.09 |   0.11 |  0.09 |  0.08 |   0.05 |   0.11 |  0.03 |  0.09 |  0.02 |
| E07 spring / Turtle Soup              |  0.17 |   0.16 |  0.06 |  0.07 |   0.11 |   0.17 |  0.11 |  0.16 | -0.01 |
| E08 breakout retest (throwback)       | -0.07 |  -0.02 | -0.05 | -0.07 |  -0.09 |  -0.06 | -0.08 | -0.07 | -0.06 |
| E09 52-week-high breakout on volume   |  0.04 |   0.06 | -0.02 |  0.01 |  -0.03 |   0.03 | -0    | -0.06 | -0.07 |
| E10 tight base (Darvas box) breakout  |  0.03 |   0.02 |  0.02 |  0.01 |  -0.03 |   0.02 | -0.03 |  0.02 | -0.04 |
| E11 volatility contraction (VCP)      | -0.04 |  -0.06 | -0.03 | -0.02 |  -0.06 |   0    | -0.03 |  0    | -0.06 |
| E12 cup with handle                   |  0.01 |   0.02 |  0.02 | -0.01 |  -0.05 |   0.08 | -0.02 | -0.06 | -0.07 |
| E13 NR7 breakout                      | -0.09 |   0.04 | -0.12 | -0.13 |  -0.12 |  -0.08 | -0.12 | -0.1  | -0.14 |
| E14 inside day + NR4                  | -0.13 |   0.01 | -0.14 | -0.15 |  -0.14 |  -0.12 | -0.13 | -0.12 | -0.14 |
| E15 thrust bar breakout               |  0.14 |   0.12 |  0.07 |  0.04 |   0.08 |   0.1  |  0.14 | -0.01 | -0.04 |
| E16 gap up on volume                  |  0.18 |   0.19 |  0.18 |  0.17 |   0.13 |   0.16 |  0.09 |  0.13 |  0    |
| E17 bullish engulfing in pullback     | -0.05 |   0.01 | -0.02 | -0.05 |  -0.05 |  -0.04 | -0.08 | -0.04 | -0.06 |
| E18 hammer at 10-day low              |  0.08 |   0.08 |  0.03 |  0.04 |   0.02 |   0.15 |  0.02 |  0.07 | -0    |
| E19 outside-day key reversal          |  0.15 |   0.09 |  0.08 |  0.07 |   0.02 |   0.12 |  0.02 |  0.11 | -0.02 |
| E20 stopping volume (climax low)      |  0.34 |   0.14 |  0.09 |  0.19 |   0.27 |   0.37 |  0.3  |  0.32 |  0.1  |
| E21 no-supply pullback                | -0.06 |   0.06 | -0.09 | -0.11 |  -0.12 |  -0.08 | -0.09 | -0.08 | -0.11 |
| E22 anchored-VWAP support             |  0.21 |   0.16 |  0.06 |  0.06 |   0.14 |   0.25 |  0.13 |  0.19 |  0.01 |
