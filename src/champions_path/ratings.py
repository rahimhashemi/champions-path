from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class BayesianBlendConfig:
    preseason_sigma: float = 109.0
    history_sigma: float = 134.0
    form_initial_sigma: float = 180.0
    form_floor_sigma: float = 60.0
    form_decay_matches: float = 1.8


def form_sigma(matches_played: int, config: BayesianBlendConfig = BayesianBlendConfig()) -> float:
    if matches_played < 0:
        raise ValueError("matches_played cannot be negative")
    initial_variance = config.form_initial_sigma**2
    floor_variance = config.form_floor_sigma**2
    variance = floor_variance + (initial_variance - floor_variance) * math.exp(
        -matches_played / config.form_decay_matches
    )
    return math.sqrt(variance)


def bayesian_power_rating(
    preseason: float,
    history: float,
    form: float,
    matches_played: int,
    config: BayesianBlendConfig = BayesianBlendConfig(),
) -> float:
    sigmas = (
        config.preseason_sigma,
        config.history_sigma,
        form_sigma(matches_played, config),
    )
    values = (preseason, history, form)
    precisions = tuple(1 / sigma**2 for sigma in sigmas)
    return sum(value * precision for value, precision in zip(values, precisions)) / sum(precisions)


def blend_weights(
    matches_played: int,
    config: BayesianBlendConfig = BayesianBlendConfig(),
) -> tuple[float, float, float]:
    precisions = (
        1 / config.preseason_sigma**2,
        1 / config.history_sigma**2,
        1 / form_sigma(matches_played, config) ** 2,
    )
    total = sum(precisions)
    return tuple(precision / total for precision in precisions)
