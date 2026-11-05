# Champions Path

[![CI](https://github.com/rahimhashemi/champions-path/actions/workflows/ci.yml/badge.svg)](https://github.com/rahimhashemi/champions-path/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Reproducible Monte Carlo forecasts for the UEFA Champions League league phase
and complete knockout path.

> **Current model:** `v4-calibrated`
>
> **Forecast snapshot:** 2026/27 after league-phase matchday 4
>
> **Historical training:** 2024/25 league phase
>
> **Out-of-sample validation:** 2025/26 league phase

## What it reports

For all 36 teams the simulation estimates expected league-phase points and the
probability of each league and knockout outcome, from a top-eight finish through
to winning the competition. Percentages are Monte Carlo estimates rather than
certainties. A displayed `0.0%` can represent a non-zero probability below the
reporting precision.

## Model architecture

### Calibrated match layer

The match model is calibrated on all 144 league-phase matches from 2024/25.
Candidate parameters are selected by minimising `log loss + Brier score`, then
evaluated without retuning on all 144 matches from 2025/26.

| Parameter | Selected value |
|---|---:|
| Elo home advantage | 55 |
| Elo K-factor | 32 |
| Expected total goals | 3.3 |
| Margin-of-victory weight | 0.55 |

Forecasts for every match in a matchday are calculated before the model learns
any result from that matchday. This prevents within-matchday future leakage.

### Current-season power layer

The 2026/27 snapshot combines 50% current Champions League form, 30% preseason
strength and 20% five-season UEFA coefficient history. Attack and defence form
are shrunk toward the competition average so four games cannot dominate the
prior. Each tournament simulation also draws persistent uncertainty for team
strength, attack and defence.

### Match and knockout simulation

- correlated Poisson score generation;
- calibrated home advantage and goal environment;
- UEFA paired-position playoff and round-of-16 paths;
- two-legged ties, extra time and penalties;
- neutral single-match final.

League standings use points, goal difference and goals scored. Any unresolved
tie receives a deterministic-seed random ordering because the remaining UEFA
tie-break inputs are not fully represented by the score-only model.

## Backtest results

| Dataset | Matches | Log loss | Brier score | Accuracy |
|---|---:|---:|---:|---:|
| 2024/25 training | 144 | 0.9267 | 0.1821 | 60.4% |
| 2025/26 validation | 144 | 0.9646 | 0.1898 | 55.6% |

Accuracy is included for readability, but parameter selection uses proper
probabilistic scoring rules rather than accuracy.

## Installation

```bash
git clone https://github.com/rahimhashemi/champions-path.git
cd champions-path
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

On Windows PowerShell use `.venv\Scripts\Activate.ps1`.

## Run a forecast

```bash
CHAMPIONS_PATH_OUTPUT=forecast.csv python -m champions_path.simulation
```

| Variable | Default | Description |
|---|---:|---|
| `CHAMPIONS_PATH_SIMS` | `300000` | Number of tournament simulations |
| `CHAMPIONS_PATH_SEED` | `20261106` | Reproducible random seed |
| `CHAMPIONS_PATH_OUTPUT` | unset | Optional CSV output path |

For a quick run, set `CHAMPIONS_PATH_SIMS=10000`.

## Reproduce calibration

```bash
python -m champions_path.calibration
```

This evaluates 144 parameter combinations on 2024/25 and overwrites the bundled
calibration report. The 2025/26 season is used only for out-of-sample reporting.

## Test

```bash
python -m pytest -q
```

Tests cover complete historical snapshots, probability partitions,
deterministic backtesting, all 36 forecast teams, monotonic knockout-stage reach
and total championship probability mass.

## Project structure

```text
data/historical/                   CC0 historical match snapshots
src/champions_path/data.py         Historical-data parser
src/champions_path/domain.py       Typed historical match model
src/champions_path/calibration.py  Time-ordered calibration and backtest
src/champions_path/simulation.py   League and knockout simulation
tests/                             Calibration and simulation invariants
```

## Data provenance

- Historical match snapshots: OpenFootball Champions League, CC0.
- Competition results and format cross-check: UEFA.
- Five-season coefficients: UEFA methodology and Kassiesa tables.

Raw historical files are committed so calibration remains reproducible if an
upstream page changes.

## Known limitations

- Uniform xG, injury, suspension, expected-lineup and domestic-form data are not
  yet included.
- Preseason ratings are model inputs rather than outputs of this repository.
- Only two completed seasons exist under the 36-team league-phase format.
- The current-season 50/30/20 power blend is not independently calibrated; v4
  calibrates the match layer, home advantage, goals and Elo updates.
- Squad changes can make five-season coefficients slow to reflect current team
  quality.

Missing inputs are not fabricated. Parameter uncertainty partly represents
their impact, but is not a replacement for complete data.

## Roadmap

- calibrate the preseason/current-form/history blend as more seasons arrive;
- add licensed, uniformly available xG and domestic-form adapters;
- add optional injury and suspension snapshots;
- automate result ingestion while retaining immutable snapshots;
- publish forecast comparisons and confidence intervals.

## Disclaimer

This is an analytical and educational project. Its probabilities are uncertain
model estimates and are **not betting or financial advice**.

## License

Code is MIT licensed. Historical OpenFootball snapshots are provided under CC0
by their upstream project.
