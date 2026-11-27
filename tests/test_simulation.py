import csv
import os
import subprocess
import sys

import pytest

from champions_path.europa import COEFFICIENTS, FIXED, GAMES, PLAYED_ROUNDS, PRESEASON


def test_europa_snapshot_is_complete():
    assert len(PRESEASON) == 36
    assert set(PRESEASON) == set(COEFFICIENTS)
    assert len(GAMES) == 144
    assert len(set(GAMES)) == 144
    assert len(PLAYED_ROUNDS) == 5
    assert all(len(round_results) == 18 for round_results in PLAYED_ROUNDS)
    assert len(FIXED) == 90


@pytest.mark.parametrize("competition", ("ucl", "uel"))
def test_probability_invariants(tmp_path, competition):
    output = tmp_path / "forecast.csv"
    env = os.environ.copy()
    env["CHAMPIONS_PATH_SIMS"] = "1000"
    env["CHAMPIONS_PATH_OUTPUT"] = str(output)
    env["CHAMPIONS_PATH_POWER_MODEL"] = "bayesian"
    env["CHAMPIONS_PATH_COMPETITION"] = competition
    subprocess.run(
        [sys.executable, "-m", "champions_path.simulation"],
        check=True,
        env=env,
        capture_output=True,
        text=True,
    )

    with output.open(encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))

    assert len(rows) == 36
    assert abs(sum(float(row["top_8_pct"]) for row in rows) - 800) < 5
    assert abs(sum(float(row["champion_pct"]) for row in rows) - 100) < 2
    for row in rows:
        league_total = sum(float(row[key]) for key in ("top_8_pct", "rank_9_24_pct", "eliminated_pct"))
        assert abs(league_total - 100) <= 0.2
        stages = [float(row[key]) for key in (
            "round_of_16_pct", "quarterfinal_pct", "semifinal_pct", "final_pct", "champion_pct"
        )]
        assert stages == sorted(stages, reverse=True)
