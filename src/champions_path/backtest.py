import json
import math
import random
from dataclasses import asdict
from pathlib import Path

from champions_path.calibration import (
    Metrics,
    Parameters,
    evaluate,
    evaluate_detailed,
    structural_candidates,
)
from champions_path.data import load_historical_season
from champions_path.domain import HistoricalMatch


Prediction = tuple[HistoricalMatch, tuple[float, float, float]]


def metrics_from_predictions(predictions: list[Prediction]) -> Metrics:
    if not predictions:
        raise ValueError("At least one prediction is required")
    log_loss = brier = 0.0
    correct = 0
    for match, probabilities in predictions:
        actual = match.outcome
        log_loss -= math.log(max(1e-12, probabilities[actual]))
        targets = tuple(1.0 if actual == index else 0.0 for index in range(3))
        brier += sum((probability - target) ** 2 for probability, target in zip(probabilities, targets)) / 3
        correct += int(max(range(3), key=probabilities.__getitem__) == actual)
    count = len(predictions)
    return Metrics(count, log_loss / count, brier / count, correct / count)


def constant_predictions(
    matches: list[HistoricalMatch], probabilities: tuple[float, float, float]
) -> list[Prediction]:
    if abs(sum(probabilities) - 1.0) > 1e-12:
        raise ValueError("Outcome probabilities must sum to one")
    return [(match, probabilities) for match in matches]


def empirical_probabilities(matches: list[HistoricalMatch]) -> tuple[float, float, float]:
    # Laplace smoothing keeps all classes strictly positive.
    counts = [1, 1, 1]
    for match in matches:
        counts[match.outcome] += 1
    total = sum(counts)
    return tuple(count / total for count in counts)


def calibration_bins(predictions: list[Prediction], bin_count: int = 10) -> list[dict[str, float | int]]:
    buckets: list[list[tuple[float, int]]] = [[] for _ in range(bin_count)]
    for match, probabilities in predictions:
        for outcome, probability in enumerate(probabilities):
            index = min(bin_count - 1, int(probability * bin_count))
            buckets[index].append((probability, int(match.outcome == outcome)))
    result: list[dict[str, float | int]] = []
    for index, bucket in enumerate(buckets):
        if not bucket:
            continue
        result.append(
            {
                "lower": index / bin_count,
                "upper": (index + 1) / bin_count,
                "count": len(bucket),
                "mean_probability": sum(item[0] for item in bucket) / len(bucket),
                "observed_rate": sum(item[1] for item in bucket) / len(bucket),
            }
        )
    return result


def block_bootstrap_intervals(
    predictions: list[Prediction],
    samples: int = 2_000,
    seed: int = 20_261_106,
) -> dict[str, list[float]]:
    by_matchday: dict[int, list[Prediction]] = {}
    for prediction in predictions:
        by_matchday.setdefault(prediction[0].matchday, []).append(prediction)
    blocks = list(by_matchday.values())
    rng = random.Random(seed)
    log_losses: list[float] = []
    briers: list[float] = []
    for _ in range(samples):
        sample = [prediction for _ in blocks for prediction in rng.choice(blocks)]
        metrics = metrics_from_predictions(sample)
        log_losses.append(metrics.log_loss)
        briers.append(metrics.brier_score)

    def percentile(values: list[float], probability: float) -> float:
        ordered = sorted(values)
        position = (len(ordered) - 1) * probability
        lower = int(position)
        upper = min(len(ordered) - 1, lower + 1)
        fraction = position - lower
        return ordered[lower] * (1 - fraction) + ordered[upper] * fraction

    return {
        "log_loss_95": [percentile(log_losses, 0.025), percentile(log_losses, 0.975)],
        "brier_score_95": [percentile(briers, 0.025), percentile(briers, 0.975)],
    }


def paired_bootstrap_difference(
    reference: list[Prediction],
    candidate: list[Prediction],
    samples: int = 2_000,
    seed: int = 20_261_106,
) -> dict[str, object]:
    if [item[0] for item in reference] != [item[0] for item in candidate]:
        raise ValueError("Paired predictions must contain the same ordered matches")
    matchdays = sorted({item[0].matchday for item in reference})
    indices = {
        matchday: [index for index, item in enumerate(reference) if item[0].matchday == matchday]
        for matchday in matchdays
    }
    rng = random.Random(seed)
    log_loss_differences: list[float] = []
    brier_differences: list[float] = []
    for _ in range(samples):
        selected = [index for _ in matchdays for index in indices[rng.choice(matchdays)]]
        reference_metrics = metrics_from_predictions([reference[index] for index in selected])
        candidate_metrics = metrics_from_predictions([candidate[index] for index in selected])
        log_loss_differences.append(candidate_metrics.log_loss - reference_metrics.log_loss)
        brier_differences.append(candidate_metrics.brier_score - reference_metrics.brier_score)

    def interval(values: list[float]) -> list[float]:
        ordered = sorted(values)
        return [ordered[int(0.025 * (len(ordered) - 1))], ordered[int(0.975 * (len(ordered) - 1))]]

    return {
        "interpretation": "negative values favour calibrated",
        "log_loss_delta": sum(log_loss_differences) / len(log_loss_differences),
        "log_loss_delta_95": interval(log_loss_differences),
        "brier_delta": sum(brier_differences) / len(brier_differences),
        "brier_delta_95": interval(brier_differences),
    }


def load_calibrated_parameters(path: Path | None = None) -> Parameters:
    source = path or Path(__file__).with_name("calibrated_params.json")
    values = json.loads(source.read_text(encoding="utf-8"))["parameters"]
    return Parameters(**values)


def train_then_validate(
    training: list[HistoricalMatch],
    validation: list[HistoricalMatch],
    parameters: Parameters,
) -> tuple[Metrics, list[Prediction]]:
    _, end_ratings = evaluate(training, parameters)
    carried = {team: 1500 + 0.75 * (rating - 1500) for team, rating in end_ratings.items()}
    metrics, _, predictions = evaluate_detailed(validation, parameters, carried)
    return metrics, predictions


def rolling_origin_cv(
    matches: list[HistoricalMatch],
    minimum_training_matchdays: int = 4,
) -> tuple[Metrics, list[dict[str, object]]]:
    candidates = structural_candidates()
    predictions: list[Prediction] = []
    folds: list[dict[str, object]] = []
    matchdays = sorted({match.matchday for match in matches})
    for matchday in matchdays:
        if matchday <= minimum_training_matchdays:
            continue
        training = [match for match in matches if match.matchday < matchday]
        validation = [match for match in matches if match.matchday == matchday]
        scored: list[tuple[float, Parameters, dict[str, float]]] = []
        for candidate in candidates:
            metrics, ratings = evaluate(training, candidate)
            scored.append((metrics.log_loss + metrics.brier_score, candidate, ratings))
        _, selected, ratings = min(scored, key=lambda item: item[0])
        _, _, fold_predictions = evaluate_detailed(validation, selected, ratings)
        predictions.extend(fold_predictions)
        folds.append({"matchday": matchday, "parameters": asdict(selected), "matches": len(validation)})
    return metrics_from_predictions(predictions), folds


def build_backtest_report(include_rolling: bool = True) -> dict[str, object]:
    training = load_historical_season("2024-25")
    validation = load_historical_season("2025-26")
    calibrated = load_calibrated_parameters()
    raw_elo = Parameters(65.0, 20.0, 3.0, 0.0, 0.0)

    uniform_predictions = constant_predictions(validation, (1 / 3, 1 / 3, 1 / 3))
    frequency_predictions = constant_predictions(validation, empirical_probabilities(training))
    raw_metrics, raw_predictions = train_then_validate(training, validation, raw_elo)
    calibrated_metrics, calibrated_predictions = train_then_validate(training, validation, calibrated)

    model_data = {
        "uniform": (metrics_from_predictions(uniform_predictions), uniform_predictions),
        "historical_frequency": (metrics_from_predictions(frequency_predictions), frequency_predictions),
        "raw_elo": (raw_metrics, raw_predictions),
        "calibrated": (calibrated_metrics, calibrated_predictions),
    }
    raw_log_loss = raw_metrics.log_loss
    raw_brier = raw_metrics.brier_score
    models: dict[str, object] = {}
    for name, (metrics, predictions) in model_data.items():
        values = asdict(metrics)
        values["log_loss_skill_vs_raw_elo"] = 1 - metrics.log_loss / raw_log_loss
        values["brier_skill_vs_raw_elo"] = 1 - metrics.brier_score / raw_brier
        values["calibration_bins"] = calibration_bins(predictions)
        values["bootstrap_intervals"] = block_bootstrap_intervals(predictions)
        models[name] = values

    report: dict[str, object] = {
        "training_season": "2024-25",
        "validation_season": "2025-26",
        "baseline_reference": "raw_elo",
        "calibrated_parameters": asdict(calibrated),
        "models": models,
        "calibrated_vs_raw_elo": paired_bootstrap_difference(raw_predictions, calibrated_predictions),
    }
    if include_rolling:
        rolling_metrics, folds = rolling_origin_cv(training)
        report["rolling_origin"] = {"metrics": asdict(rolling_metrics), "folds": folds}
    return report
