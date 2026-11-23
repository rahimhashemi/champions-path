from champions_path.backtest import build_backtest_report


def test_backtest_compares_calibrated_model_with_raw_elo():
    report = build_backtest_report(include_rolling=False)
    models = report["models"]
    assert set(models) == {"uniform", "historical_frequency", "raw_elo", "calibrated"}
    assert models["calibrated"]["log_loss"] < models["raw_elo"]["log_loss"]
    assert models["calibrated"]["brier_score"] < models["raw_elo"]["brier_score"]
    assert report["calibrated_vs_raw_elo"]["log_loss_delta"] < 0
