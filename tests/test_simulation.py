import csv
import os
import subprocess
import sys


def test_probability_invariants(tmp_path):
    output = tmp_path / "forecast.csv"
    env = os.environ.copy()
    env["CHAMPIONS_PATH_SIMS"] = "1000"
    env["CHAMPIONS_PATH_OUTPUT"] = str(output)
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
