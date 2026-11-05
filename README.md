# Champions Path

Reproducible Monte Carlo forecasts for the 2026/27 UEFA Champions League.

The current v3 snapshot simulates the remaining league-phase fixtures and the
complete knockout path for all 36 teams. It reports expected points and the
probability of finishing in the top eight, positions 9–24, being eliminated,
reaching every knockout round, and winning the competition.

## Model

The power estimate blends:

- 50% current Champions League form, with more weight on recent matchdays;
- 30% preseason team strength;
- 20% exact five-season UEFA coefficient history (2021/22–2025/26).

Matches use a correlated Poisson score model with home advantage and persistent
per-simulation uncertainty in team strength, attack, and defence. The knockout
simulation includes paired-position draws, two-legged ties, extra time,
penalties, and a neutral single-match final.

## Run

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
CHAMPIONS_PATH_OUTPUT=forecast.csv python -m champions_path.simulation
```

The default run uses 300,000 simulations and a deterministic seed. For a quick
run:

```bash
CHAMPIONS_PATH_SIMS=10000 python -m champions_path.simulation
```

## Test

```bash
pytest -q
```

The invariant test verifies all 36 teams, league-phase probability partitions,
the 100% championship probability mass, and monotonic knockout-stage reach.

## Data status

The repository currently contains a dated, reproducible matchday-four snapshot.
Fixtures, results, and coefficient inputs are kept in source so a historical run
can always be reproduced. Automated source ingestion is planned for the next
version.

Uniform xG, injury, suspension, and domestic-form data are not yet available for
all 36 teams. The project does not fabricate them; missing information is partly
represented through parameter uncertainty.

## Sources

- [UEFA Champions League](https://www.uefa.com/uefachampionsleague/)
- [UEFA club coefficients](https://www.uefa.com/nationalassociations/uefarankings/club/)
- [Kassiesa five-year coefficient tables](https://kassiesa.net/uefa/data/method5/trank2026.html)

## License

MIT
