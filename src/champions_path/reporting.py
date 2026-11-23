import csv
import html
from pathlib import Path


def _percentage(value: str | float) -> str:
    return f"{float(value):.1f}%"


def write_forecast_markdown(csv_path: Path, output_path: Path) -> None:
    with csv_path.open(encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))
    headers = (
        "Team",
        "Expected points",
        "Top 8",
        "9-24",
        "Eliminated",
        "Round of 16",
        "Quarter-final",
        "Semi-final",
        "Final",
        "Champion",
    )
    keys = (
        "team",
        "expected_points",
        "top_8_pct",
        "rank_9_24_pct",
        "eliminated_pct",
        "round_of_16_pct",
        "quarterfinal_pct",
        "semifinal_pct",
        "final_pct",
        "champion_pct",
    )
    lines = ["# Champions Path forecast", "", "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        values = [row[key] if key in ("team", "expected_points") else _percentage(row[key]) for key in keys]
        lines.append("| " + " | ".join(values) + " |")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_forecast_html(csv_path: Path, output_path: Path) -> None:
    with csv_path.open(encoding="utf-8") as input_file:
        rows = list(csv.DictReader(input_file))
    columns = (
        ("team", "Team"),
        ("expected_points", "Expected points"),
        ("top_8_pct", "Top 8"),
        ("rank_9_24_pct", "9-24"),
        ("eliminated_pct", "Eliminated"),
        ("round_of_16_pct", "Round of 16"),
        ("quarterfinal_pct", "Quarter-final"),
        ("semifinal_pct", "Semi-final"),
        ("final_pct", "Final"),
        ("champion_pct", "Champion"),
    )
    head = "".join(f"<th>{html.escape(label)}</th>" for _, label in columns)
    body = []
    for row in rows:
        cells = []
        for key, _ in columns:
            value = row[key] if key in ("team", "expected_points") else _percentage(row[key])
            cells.append(f"<td>{html.escape(value)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    document = f"""<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Champions Path forecast</title>
<style>body{{font:14px system-ui;margin:2rem;background:#0b1020;color:#e8ecf6}}table{{border-collapse:collapse;width:100%;background:#131a2d}}th,td{{padding:.65rem;border-bottom:1px solid #2b3550;text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{position:sticky;top:0;background:#1c2742}}tr:hover{{background:#19233b}}</style>
<h1>Champions Path forecast</h1><table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table></html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")


def write_backtest_markdown(report: dict[str, object], output_path: Path) -> None:
    models = report["models"]
    lines = [
        "# Champions Path backtest",
        "",
        f"Training: `{report['training_season']}` — untouched validation: `{report['validation_season']}`",
        "",
        "| Model | Matches | Log loss | Brier | Accuracy | LL skill vs raw Elo | Brier skill vs raw Elo |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, values in models.items():
        lines.append(
            f"| {name} | {values['matches']} | {values['log_loss']:.4f} | "
            f"{values['brier_score']:.4f} | {values['accuracy']:.1%} | "
            f"{values['log_loss_skill_vs_raw_elo']:.1%} | {values['brier_skill_vs_raw_elo']:.1%} |"
        )
    if "rolling_origin" in report:
        metrics = report["rolling_origin"]["metrics"]
        lines.extend(
            [
                "",
                "## Rolling-origin selection on the training season",
                "",
                f"Evaluated {metrics['matches']} held-out matches: log loss `{metrics['log_loss']:.4f}`, "
                f"Brier `{metrics['brier_score']:.4f}`, accuracy `{metrics['accuracy']:.1%}`.",
            ]
        )
    comparison = report["calibrated_vs_raw_elo"]
    lines.extend(
        [
            "",
            "## Paired matchday bootstrap",
            "",
            f"Calibrated minus raw Elo log-loss delta: `{comparison['log_loss_delta']:.4f}` "
            f"(95% interval `{comparison['log_loss_delta_95'][0]:.4f}` to `{comparison['log_loss_delta_95'][1]:.4f}`).",
            f"Brier delta: `{comparison['brier_delta']:.4f}` "
            f"(95% interval `{comparison['brier_delta_95'][0]:.4f}` to `{comparison['brier_delta_95'][1]:.4f}`).",
        ]
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_calibration_svg(report: dict[str, object], output_path: Path, model: str = "calibrated") -> None:
    bins = report["models"][model]["calibration_bins"]
    size = 560
    margin = 55
    plot = size - 2 * margin

    def point(x: float, y: float) -> tuple[float, float]:
        return margin + x * plot, size - margin - y * plot

    points = " ".join(f"{point(item['mean_probability'], item['observed_rate'])[0]:.1f},{point(item['mean_probability'], item['observed_rate'])[1]:.1f}" for item in bins)
    circles = "".join(
        f'<circle cx="{point(item["mean_probability"], item["observed_rate"])[0]:.1f}" cy="{point(item["mean_probability"], item["observed_rate"])[1]:.1f}" r="5"/>'
        for item in bins
    )
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">
<rect width="100%" height="100%" fill="#fff"/><g stroke="#d1d5db"><line x1="{margin}" y1="{size-margin}" x2="{size-margin}" y2="{margin}" stroke-dasharray="6 6"/><line x1="{margin}" y1="{margin}" x2="{margin}" y2="{size-margin}"/><line x1="{margin}" y1="{size-margin}" x2="{size-margin}" y2="{size-margin}"/></g>
<g fill="none" stroke="#2563eb" stroke-width="3"><polyline points="{points}"/></g><g fill="#2563eb">{circles}</g>
<g font-family="system-ui" font-size="14" fill="#111827"><text x="{size/2}" y="{size-12}" text-anchor="middle">Predicted probability</text><text x="16" y="{size/2}" transform="rotate(-90 16 {size/2})" text-anchor="middle">Observed frequency</text><text x="{size/2}" y="28" text-anchor="middle" font-size="18">Calibration — {html.escape(model)}</text></g></svg>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")


def write_backtest_html(report: dict[str, object], output_path: Path) -> None:
    models = report["models"]
    rows = "".join(
        f"<tr><td>{html.escape(name)}</td><td>{values['matches']}</td><td>{values['log_loss']:.4f}</td>"
        f"<td>{values['brier_score']:.4f}</td><td>{values['accuracy']:.1%}</td>"
        f"<td>{values['log_loss_skill_vs_raw_elo']:.1%}</td><td>{values['brier_skill_vs_raw_elo']:.1%}</td></tr>"
        for name, values in models.items()
    )
    document = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Champions Path backtest</title><style>body{{font:15px system-ui;max-width:1050px;margin:2rem auto;padding:0 1rem;color:#172033}}table{{border-collapse:collapse;width:100%}}th,td{{padding:.7rem;border-bottom:1px solid #d7dce5;text-align:right}}th:first-child,td:first-child{{text-align:left}}th{{background:#eef2ff}}</style>
<h1>Champions Path backtest</h1><p>Training: <b>{report['training_season']}</b> · untouched validation: <b>{report['validation_season']}</b></p>
<table><thead><tr><th>Model</th><th>Matches</th><th>Log loss</th><th>Brier</th><th>Accuracy</th><th>LL skill</th><th>Brier skill</th></tr></thead><tbody>{rows}</tbody></table></html>"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
