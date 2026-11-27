import argparse
import json
import os
from pathlib import Path
import runpy
import tempfile

from champions_path.backtest import build_backtest_report
from champions_path.calibration import calibrate
from champions_path.reporting import (
    write_backtest_html,
    write_backtest_markdown,
    write_calibration_svg,
    write_forecast_html,
    write_forecast_markdown,
)


def _simulate(arguments: argparse.Namespace) -> None:
    temporary: tempfile.NamedTemporaryFile[str] | None = None
    output = arguments.output
    if output is None and (arguments.markdown or arguments.html):
        temporary = tempfile.NamedTemporaryFile(suffix=".csv", delete=False)
        temporary.close()
        output = Path(temporary.name)
    os.environ["CHAMPIONS_PATH_SIMS"] = str(arguments.sims)
    os.environ["CHAMPIONS_PATH_SEED"] = str(arguments.seed)
    os.environ["CHAMPIONS_PATH_COMPETITION"] = arguments.competition
    os.environ["CHAMPIONS_PATH_POWER_MODEL"] = arguments.power_model
    os.environ["CHAMPIONS_PATH_DIXON_COLES_RHO"] = str(arguments.dixon_coles_rho)
    if arguments.form_snapshot:
        os.environ["CHAMPIONS_PATH_FORM_SNAPSHOT"] = str(arguments.form_snapshot)
    if output:
        os.environ["CHAMPIONS_PATH_OUTPUT"] = str(output)
    runpy.run_module("champions_path.simulation", run_name="__main__")
    if arguments.markdown:
        write_forecast_markdown(output, arguments.markdown, arguments.competition)
    if arguments.html:
        write_forecast_html(output, arguments.html, arguments.competition)
    if temporary:
        Path(temporary.name).unlink(missing_ok=True)


def _backtest(arguments: argparse.Namespace) -> None:
    report = build_backtest_report(include_rolling=not arguments.no_rolling)
    arguments.json.parent.mkdir(parents=True, exist_ok=True)
    arguments.json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if arguments.markdown:
        write_backtest_markdown(report, arguments.markdown)
    if arguments.html:
        write_backtest_html(report, arguments.html)
    if arguments.calibration_plot:
        write_calibration_svg(report, arguments.calibration_plot)


def _calibrate(arguments: argparse.Namespace) -> None:
    result = calibrate()
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="champions-path")
    commands = parser.add_subparsers(dest="command", required=True)

    simulate = commands.add_parser("simulate", help="run the league and knockout Monte Carlo model")
    simulate.add_argument("--sims", type=int, default=300_000)
    simulate.add_argument("--seed", type=int, default=20_261_106)
    simulate.add_argument("--competition", choices=("ucl", "uel"), default="ucl")
    simulate.add_argument("--output", type=Path)
    simulate.add_argument("--markdown", type=Path)
    simulate.add_argument("--html", type=Path)
    simulate.add_argument("--power-model", choices=("fixed", "bayesian"), default="bayesian")
    simulate.add_argument("--dixon-coles-rho", type=float, default=None)
    simulate.add_argument("--form-snapshot", type=Path)
    simulate.set_defaults(handler=_simulate)

    backtest = commands.add_parser("backtest", help="compare baselines and generate calibration reports")
    backtest.add_argument("--json", type=Path, default=Path("reports/backtest.json"))
    backtest.add_argument("--markdown", type=Path, default=Path("reports/backtest.md"))
    backtest.add_argument("--html", type=Path, default=Path("reports/backtest.html"))
    backtest.add_argument("--calibration-plot", type=Path, default=Path("reports/calibration.svg"))
    backtest.add_argument("--no-rolling", action="store_true")
    backtest.set_defaults(handler=_backtest)

    calibration = commands.add_parser("calibrate", help="fit calibrated match-model parameters")
    calibration.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("calibrated_params.json"),
    )
    calibration.set_defaults(handler=_calibrate)
    return parser


def main() -> None:
    arguments = build_parser().parse_args()
    if arguments.command == "simulate" and arguments.dixon_coles_rho is None:
        from champions_path.backtest import load_calibrated_parameters

        arguments.dixon_coles_rho = load_calibrated_parameters().dixon_coles_rho
    arguments.handler(arguments)


if __name__ == "__main__":
    main()
