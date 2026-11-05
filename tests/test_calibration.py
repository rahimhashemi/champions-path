from pathlib import Path

from champions_path.calibration import Parameters, evaluate, outcome_probabilities
from champions_path.data import parse_openfootball_league_phase, project_root


def test_historical_snapshots_contain_complete_league_phases():
    for season in ("2024-25", "2025-26"):
        path = project_root() / "data" / "historical" / f"{season}-cl.txt"
        matches = parse_openfootball_league_phase(path, season)
        assert len(matches) == 144
        assert {match.matchday for match in matches} == set(range(1, 9))


def test_outcome_probabilities_form_partition():
    parameters = Parameters(65, 24, 3.0, 0.35)
    probabilities = outcome_probabilities(1550, 1500, parameters)
    assert abs(sum(probabilities) - 1.0) < 1e-12
    assert all(0 < probability < 1 for probability in probabilities)


def test_evaluation_is_deterministic_and_finite():
    fixture = Path(__file__).parent / "fixtures" / "mini-season.txt"
    matches = parse_openfootball_league_phase(fixture, "test")
    parameters = Parameters(65, 24, 3.0, 0.35)
    first, _ = evaluate(matches, parameters)
    second, _ = evaluate(matches, parameters)
    assert first == second
    assert first.matches == 4
    assert first.log_loss > 0
    assert 0 <= first.accuracy <= 1
