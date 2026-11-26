from champions_path.probability import (
    bivariate_poisson_score_matrix,
    outcome_probabilities_from_means,
)
from champions_path.ratings import bayesian_power_rating, blend_weights


def test_correlated_score_matrix_is_probability_partition():
    matrix = bivariate_poisson_score_matrix(1.7, 1.2, rho=-0.08)
    assert abs(sum(sum(row) for row in matrix) - 1.0) < 1e-12
    assert all(probability >= 0 for row in matrix for probability in row)


def test_dixon_coles_outcomes_are_probability_partition():
    probabilities = outcome_probabilities_from_means(1.7, 1.2, rho=-0.08)
    assert abs(sum(probabilities) - 1.0) < 1e-12
    assert all(0 < probability < 1 for probability in probabilities)


def test_bayesian_form_weight_grows_with_evidence():
    first = blend_weights(1)
    fourth = blend_weights(4)
    seventh = blend_weights(7)
    assert first[2] < fourth[2] < seventh[2]
    assert abs(sum(fourth) - 1.0) < 1e-12
    rating = bayesian_power_rating(1900, 1800, 2000, 4)
    assert 1800 < rating < 2000
