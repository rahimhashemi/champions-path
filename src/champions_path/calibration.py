import argparse
import itertools
import json
import math
from collections import defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path

from champions_path.data import load_historical_season, project_root
from champions_path.domain import HistoricalMatch
from champions_path.probability import outcome_probabilities_from_means


@dataclass(frozen=True, slots=True)
class Parameters:
    home_advantage: float
    k_factor: float
    total_goals: float
    margin_weight: float
    dixon_coles_rho: float = 0.0


@dataclass(frozen=True, slots=True)
class Metrics:
    matches: int
    log_loss: float
    brier_score: float
    accuracy: float


def outcome_probabilities(home_rating: float, away_rating: float, parameters: Parameters) -> tuple[float, float, float]:
    gap = home_rating + parameters.home_advantage - away_rating
    ratio = 10 ** (gap / 400)
    home_mean = parameters.total_goals * ratio / (1 + ratio)
    away_mean = parameters.total_goals / (1 + ratio)
    return outcome_probabilities_from_means(home_mean, away_mean, parameters.dixon_coles_rho)


def update_ratings(ratings: dict[str, float], match: HistoricalMatch, parameters: Parameters) -> None:
    home_rating = ratings[match.home]
    away_rating = ratings[match.away]
    expected = 1 / (1 + 10 ** (-(home_rating + parameters.home_advantage - away_rating) / 400))
    actual = 1.0 if match.home_goals > match.away_goals else 0.5 if match.home_goals == match.away_goals else 0.0
    margin = abs(match.home_goals - match.away_goals)
    multiplier = 1 + parameters.margin_weight * math.log1p(margin) if margin else 1.0
    change = parameters.k_factor * multiplier * (actual - expected)
    ratings[match.home] += change
    ratings[match.away] -= change


def evaluate(
    matches: list[HistoricalMatch],
    parameters: Parameters,
    initial_ratings: dict[str, float] | None = None,
) -> tuple[Metrics, dict[str, float]]:
    metrics, ratings, _ = evaluate_detailed(matches, parameters, initial_ratings)
    return metrics, ratings


def evaluate_detailed(
    matches: list[HistoricalMatch],
    parameters: Parameters,
    initial_ratings: dict[str, float] | None = None,
) -> tuple[Metrics, dict[str, float], list[tuple[HistoricalMatch, tuple[float, float, float]]]]:
    teams = {match.home for match in matches} | {match.away for match in matches}
    ratings = defaultdict(lambda: 1500.0)
    if initial_ratings:
        ratings.update(initial_ratings)
    for team in teams:
        ratings[team]

    log_loss = brier = 0.0
    correct = 0
    all_predictions: list[tuple[HistoricalMatch, tuple[float, float, float]]] = []
    matchdays = sorted({match.matchday for match in matches})
    for matchday in matchdays:
        current = [match for match in matches if match.matchday == matchday]
        predictions: list[tuple[HistoricalMatch, tuple[float, float, float]]] = []
        for match in current:
            probabilities = outcome_probabilities(ratings[match.home], ratings[match.away], parameters)
            predictions.append((match, probabilities))
            all_predictions.append((match, probabilities))
            actual = match.outcome
            log_loss -= math.log(max(1e-12, probabilities[actual]))
            targets = (1.0 if actual == 0 else 0.0, 1.0 if actual == 1 else 0.0, 1.0 if actual == 2 else 0.0)
            brier += sum((probability - target) ** 2 for probability, target in zip(probabilities, targets)) / 3
            correct += int(max(range(3), key=probabilities.__getitem__) == actual)
        # All forecasts for a matchday are made before any result from that matchday is learned.
        for match, _ in predictions:
            update_ratings(ratings, match, parameters)

    count = len(matches)
    metrics = Metrics(count, log_loss / count, brier / count, correct / count)
    return metrics, dict(ratings), all_predictions


def structural_candidates() -> list[Parameters]:
    return [
        Parameters(*values)
        for values in itertools.product(
            (40.0, 55.0, 70.0, 85.0),
            (16.0, 24.0, 32.0),
            (2.7, 2.9, 3.1, 3.3),
            (0.0, 0.35, 0.55),
        )
    ]


def calibrate() -> dict[str, object]:
    training = load_historical_season("2024-25")
    validation = load_historical_season("2025-26")
    candidates = structural_candidates()

    scored: list[tuple[float, Parameters, Metrics, dict[str, float]]] = []
    for parameters in candidates:
        metrics, ratings = evaluate(training, parameters)
        score = metrics.log_loss + metrics.brier_score
        scored.append((score, parameters, metrics, ratings))
    _, base_best, _, _ = min(scored, key=lambda item: item[0])

    # Tune the single Dixon-Coles parameter only after the structural grid is
    # selected. This avoids multiplying the full search space on a small sample.
    rho_candidates = (-0.12, -0.08, -0.04, 0.0)
    rho_scored: list[tuple[float, Parameters, Metrics, dict[str, float]]] = []
    for rho in rho_candidates:
        parameters = Parameters(
            base_best.home_advantage,
            base_best.k_factor,
            base_best.total_goals,
            base_best.margin_weight,
            rho,
        )
        metrics, ratings = evaluate(training, parameters)
        rho_scored.append((metrics.log_loss + metrics.brier_score, parameters, metrics, ratings))
    _, best, training_metrics, end_ratings = min(rho_scored, key=lambda item: item[0])

    # Regress last season's ratings toward the mean before the unseen season.
    carried = {team: 1500 + 0.75 * (rating - 1500) for team, rating in end_ratings.items()}
    validation_metrics, _ = evaluate(validation, best, carried)
    return {
        "model_version": "v5-bayesian",
        "training_season": "2024-25",
        "validation_season": "2025-26",
        "selection_objective": "log_loss_plus_brier",
        "parameters": asdict(best),
        "training_metrics": asdict(training_metrics),
        "validation_metrics": asdict(validation_metrics),
        "candidates_evaluated": len(candidates) + len(rho_candidates),
        "structural_candidates": len(candidates),
        "dixon_coles_candidates": list(rho_candidates),
        "carryover_shrinkage": 0.75,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate and backtest the Champions Path match model")
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root() / "src" / "champions_path" / "calibrated_params.json",
    )
    arguments = parser.parse_args()
    result = calibrate()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
