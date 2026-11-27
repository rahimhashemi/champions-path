# Champions Path

[![CI](https://github.com/rahimhashemi/champions-path/actions/workflows/ci.yml/badge.svg)](https://github.com/rahimhashemi/champions-path/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.11%2B-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Reproducible Monte Carlo forecasts for the UEFA Champions League and Europa
League league phases and their complete knockout paths.

| Competition | Snapshot | Model status | Included report |
|---|---|---|---|
| Champions League (`ucl`) | 2026/27 after Matchday 5 | Backtested `v5-bayesian` | [`reports/forecast.md`](reports/forecast.md) |
| Europa League (`uel`) | 2026/27 after Matchday 5 | Provisional UEL adapter | [`reports/europa_forecast.md`](reports/europa_forecast.md) |

The Champions League match layer was trained on the 2024/25 league phase and
validated without retuning on 2025/26. Europa League support uses the same
tournament engine with an independent schedule, results, preseason-strength
snapshot and UEFA coefficients. Its match-layer parameters remain provisional
until a dedicated UEL backtest is added.

## Quick start

```bash
python -m pip install -e ".[dev]"

# Champions League
champions-path simulate --competition ucl --sims 300000 --output ucl.csv

# Europa League
champions-path simulate --competition uel --sims 300000 --output uel.csv
```

## What it reports

For all 36 teams the simulation estimates expected league-phase points and the
probability of each league and knockout outcome, from a top-eight finish through
to winning the competition. Percentages are Monte Carlo estimates rather than
certainties. A displayed `0.0%` can represent a non-zero probability below the
reporting precision.

## Model architecture

### Calibrated match layer

The match model is calibrated on all 144 league-phase matches from 2024/25.
Structural parameters are selected by minimising `log loss + Brier score`.
Dixon-Coles rho is selected in a separate, four-value search so it does not
multiply the structural grid on a small dataset. The final model is evaluated
without retuning on all 144 matches from 2025/26.

| Parameter | Selected value |
|---|---:|
| Elo home advantage | 55 |
| Elo K-factor | 32 |
| Expected total goals | 3.3 |
| Margin-of-victory weight | 0.55 |
| Dixon-Coles rho | 0.00 |

Forecasts for every match in a matchday are calculated before the model learns
any result from that matchday. This prevents within-matchday future leakage.

### Current-season power layer

Each 2026/27 competition snapshot combines current European form, preseason
strength and five-season UEFA coefficient history with a precision-weighted
Bayesian blend. Form uncertainty falls as matches accumulate: early forecasts
rely more on priors, while later forecasts learn more from current form. Attack
and defence estimates are shrunk toward the competition average so five matches
cannot dominate the long-run strength signal.

### Match and knockout simulation

- correlated Poisson score generation with an optional Dixon-Coles low-score
  correction;
- calibrated home advantage and goal environment;
- UEFA paired-position playoff and round-of-16 paths;
- two-legged ties, extra time and penalties;
- neutral single-match final.

League standings use points, goal difference and goals scored. Any unresolved
tie receives a deterministic-seed random ordering because the remaining UEFA
tie-break inputs are not fully represented by the score-only model.

## Backtest results

| Model | Matches | Log loss | Brier score | Accuracy |
|---|---:|---:|---:|---:|
| Uniform baseline | 144 | 1.0986 | 0.2222 | 49.3% |
| Historical-frequency baseline | 144 | 1.0271 | 0.2064 | 49.3% |
| Raw Elo baseline | 144 | 0.9989 | 0.1986 | 50.7% |
| Calibrated model | 144 | 0.9667 | 0.1899 | 55.6% |

Against raw Elo on the untouched 2025/26 season, the calibrated model improves
log loss by 3.2% and Brier score by 4.3%. The repository also reports paired
matchday-bootstrap intervals and a rolling-origin selection result instead of
presenting point estimates alone.

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
champions-path simulate --competition ucl --sims 300000 --seed 20261106 \
  --output forecast.csv
```

Run the Europa League snapshot after Matchday 5:

```bash
champions-path simulate --competition uel --sims 300000 --seed 20261127 \
  --output europa.csv --markdown reports/europa_forecast.md \
  --html reports/europa_forecast.html
```

Generate presentation-friendly output at the same time:

```bash
champions-path simulate --output forecast.csv \
  --markdown reports/forecast.md --html reports/forecast.html
```

| Option | Default | Description |
|---|---:|---|
| `--sims` | `300000` | Number of tournament simulations |
| `--seed` | `20261106` | Reproducible random seed |
| `--competition` | `ucl` | `ucl` or `uel` |
| `--power-model` | `bayesian` | `bayesian` or legacy `fixed` blend |
| `--dixon-coles-rho` | calibrated | Override the fitted low-score correction |
| `--form-snapshot` | unset | Optional uniform domestic/xG snapshot |

The former `CHAMPIONS_PATH_*` environment variables remain supported for
backward compatibility. For a quick run, pass `--sims 10000`.

## Reproduce calibration

```bash
champions-path calibrate
```

This evaluates 144 structural combinations and four sequential Dixon-Coles
candidates on the 2024/25 Champions League. The 2025/26 Champions League is
used only for out-of-sample reporting. It does not yet calibrate UEL separately.

## Compare baselines and calibration

```bash
champions-path backtest
```

This creates JSON, Markdown and HTML reports plus an SVG reliability plot under
`reports/`. Baselines include uniform probabilities, historical outcome
frequencies and a raw, untuned Elo model. Hyperparameter stability is checked
with rolling-origin matchday folds, and uncertainty with paired block bootstrap.

## Optional domestic-form/xG snapshot

External features are opt-in because the project does not fabricate missing xG.
A snapshot must include exactly the same 36 teams and provenance metadata:

```json
{
  "provider": "licensed-provider-or-open-source-name",
  "as_of": "2026-11-23",
  "teams": {
    "Arsenal": {
      "domestic_elo_delta": 42.0,
      "xg_difference_per_90": 0.71,
      "matches": 12
    }
  }
}
```

Partial coverage is rejected to prevent stronger data coverage in one domestic
league from silently biasing the tournament forecast.

## Test

```bash
python -m pytest -q
```

Tests cover complete UCL and UEL snapshots, probability partitions,
deterministic backtesting, all 36 teams in each competition, monotonic
knockout-stage reach and total championship probability mass.

## Project structure

```text
data/historical/                   CC0 historical match snapshots
src/champions_path/data.py         Historical-data parser
src/champions_path/domain.py       Typed historical match model
src/champions_path/calibration.py  Time-ordered parameter calibration
src/champions_path/backtest.py     Baselines, rolling CV and bootstrap
src/champions_path/probability.py  Correlated Poisson and Dixon-Coles
src/champions_path/ratings.py      Bayesian power blending
src/champions_path/features.py     Optional form/xG snapshot contract
src/champions_path/europa.py       Europa League teams, fixtures and results
src/champions_path/reporting.py    Markdown, HTML and SVG reports
src/champions_path/cli.py          Command-line interface
src/champions_path/simulation.py   League and knockout simulation
tests/                             Calibration and simulation invariants
```

## Data provenance

- Historical match snapshots: [OpenFootball Champions League](https://github.com/openfootball/champions-league), CC0.
- 2026/27 fixtures, results and format: [UEFA Champions League](https://www.uefa.com/uefachampionsleague/fixtures-results/) and [UEFA Europa League](https://www.uefa.com/uefaeuropaleague/fixtures-results/).
- Five-season coefficients: [UEFA methodology](https://www.uefa.com/nationalassociations/uefarankings/club/about/) and [Kassiesa tables](https://kassiesa.net/uefa/data/method5/trank2026.html).

Raw historical files are committed so calibration remains reproducible if an
upstream page changes.

## Known limitations

- Uniform xG and domestic-form data are not bundled; the optional adapter rejects
  incomplete team coverage.
- Injury, suspension and expected-lineup data are not yet included.
- Preseason ratings are model inputs rather than outputs of this repository.
- Only two completed seasons exist under the 36-team league-phase format.
- Europa League currently reuses the UCL-calibrated match layer; its tournament
  results are useful model estimates but not yet independently backtested.
- Bayesian blend variance assumptions are documented heuristics until more
  completed seasons are available for direct calibration.
- Squad changes can make five-season coefficients slow to reflect current team
  quality.

Missing inputs are not fabricated. Parameter uncertainty partly represents
their impact, but is not a replacement for complete data.

## Roadmap

- add a dedicated historical UEL dataset and out-of-sample calibration;
- calibrate Bayesian prior variances as more seasons arrive;
- add licensed, uniformly available xG and domestic-form adapters;
- add optional injury and suspension snapshots;
- automate result ingestion while retaining immutable snapshots;
- add bookmaker-implied probabilities only if a legal reproducible snapshot is
  available.

## Disclaimer

This is an analytical and educational project. Its probabilities are uncertain
model estimates and are **not betting or financial advice**.

## License

Code is MIT licensed. Historical OpenFootball snapshots are provided under CC0
by their upstream project.
