# Champions Path backtest

Training: `2024-25` — untouched validation: `2025-26`

| Model | Matches | Log loss | Brier | Accuracy | LL skill vs raw Elo | Brier skill vs raw Elo |
|---|---:|---:|---:|---:|---:|---:|
| uniform | 144 | 1.0986 | 0.2222 | 49.3% | -10.0% | -11.9% |
| historical_frequency | 144 | 1.0271 | 0.2064 | 49.3% | -2.8% | -3.9% |
| raw_elo | 144 | 0.9989 | 0.1986 | 50.7% | 0.0% | 0.0% |
| calibrated | 144 | 0.9667 | 0.1899 | 55.6% | 3.2% | 4.3% |

## Rolling-origin selection on the training season

Evaluated 72 held-out matches: log loss `0.8748`, Brier `0.1700`, accuracy `62.5%`.

## Paired matchday bootstrap

Calibrated minus raw Elo log-loss delta: `-0.0323` (95% interval `-0.0597` to `-0.0080`).
Brier delta: `-0.0087` (95% interval `-0.0150` to `-0.0030`).
