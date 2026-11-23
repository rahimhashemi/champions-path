import math


def dixon_coles_factor(
    home_goals: int,
    away_goals: int,
    home_mean: float,
    away_mean: float,
    rho: float,
) -> float:
    """Return the Dixon-Coles low-score correction factor."""
    if home_goals == 0 and away_goals == 0:
        return 1 - home_mean * away_mean * rho
    if home_goals == 0 and away_goals == 1:
        return 1 + home_mean * rho
    if home_goals == 1 and away_goals == 0:
        return 1 + away_mean * rho
    if home_goals == 1 and away_goals == 1:
        return 1 - rho
    return 1.0


def bivariate_poisson_score_matrix(
    home_mean: float,
    away_mean: float,
    rho: float = 0.0,
    maximum: int = 10,
    shared_cap: float = 0.10,
) -> list[list[float]]:
    """Build a normalised correlated-Poisson score matrix.

    ``home_mean`` and ``away_mean`` are marginal goal means. A small shared
    Poisson component models score correlation. Dixon-Coles then reweights the
    four low-score cells without changing the rest of the score grid.
    """
    shared = min(shared_cap, min(home_mean, away_mean) * 0.35)
    home_only = max(1e-12, home_mean - shared)
    away_only = max(1e-12, away_mean - shared)
    common = max(0.0, shared)
    base = math.exp(-(home_only + away_only + common))

    matrix: list[list[float]] = []
    for home_goals in range(maximum + 1):
        row: list[float] = []
        for away_goals in range(maximum + 1):
            probability = 0.0
            for shared_goals in range(min(home_goals, away_goals) + 1):
                probability += (
                    home_only ** (home_goals - shared_goals)
                    * away_only ** (away_goals - shared_goals)
                    * common**shared_goals
                    / (
                        math.factorial(home_goals - shared_goals)
                        * math.factorial(away_goals - shared_goals)
                        * math.factorial(shared_goals)
                    )
                )
            correction = dixon_coles_factor(home_goals, away_goals, home_mean, away_mean, rho)
            row.append(max(0.0, base * probability * correction))
        matrix.append(row)

    total = sum(sum(row) for row in matrix)
    if total <= 0:
        raise ValueError("Score probability matrix has no positive mass")
    return [[probability / total for probability in row] for row in matrix]


def outcome_probabilities_from_means(
    home_mean: float,
    away_mean: float,
    rho: float = 0.0,
    maximum: int = 10,
) -> tuple[float, float, float]:
    matrix = bivariate_poisson_score_matrix(home_mean, away_mean, rho, maximum)
    home_win = draw = away_win = 0.0
    for home_goals, row in enumerate(matrix):
        for away_goals, probability in enumerate(row):
            if home_goals > away_goals:
                home_win += probability
            elif home_goals == away_goals:
                draw += probability
            else:
                away_win += probability
    return home_win, draw, away_win
