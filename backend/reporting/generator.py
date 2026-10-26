# ruff: noqa: E501 -- HTML/CSS template lines are kept readable as rendered markup.

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from html import escape
from pathlib import Path
from statistics import mean
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class ReportGenerator:
    def generate_html(self, experiment: dict[str, Any], destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        rows = experiment.get("results", [])
        summary = self._summary(rows)
        if rows:
            evidence_html = self._evidence_table(summary)
            status_note = (
                "This report summarizes stored experimental observations. Failed runs remain in all "
                "success-rate denominators."
            )
        else:
            evidence_html = (
                '<div class="empty"><h2>No results yet</h2><p>This experiment contains no recorded '
                "model runs. No findings or comparisons can be calculated.</p></div>"
            )
            status_note = "This is a no-results report. It contains no model-performance claims."

        generated = datetime.now().astimezone().isoformat(timespec="seconds")
        html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>{escape(experiment['name'])} · Robot Navigation Research Report</title>
<style>
body{{font:16px/1.55 Arial,sans-serif;color:#1c2925;margin:0;background:#eef3f1}}
main{{max-width:1050px;margin:30px auto;background:white;padding:48px;border-radius:14px}}
h1,h2{{color:#10241d}}.meta{{color:#60746d}}.notice,.empty{{padding:18px;border-left:4px solid #2b8b69;background:#eef8f4}}
table{{border-collapse:collapse;width:100%;margin:20px 0}}th,td{{padding:10px;border:1px solid #d9e3df;text-align:left}}
th{{background:#edf4f1}}code{{background:#edf3f0;padding:2px 5px}}@media print{{body{{background:white}}main{{margin:0;padding:20px}}}}
</style></head><body><main>
<p class="meta">COST EFFECTIVE OPTIMIZATION OF OPEN SOURCE LLM AGENTS FOR SYSTEM LEVEL TASK</p>
<h1>Robot Navigation Experiment Report</h1>
<p><strong>Experiment:</strong> {escape(experiment['name'])}<br>
<strong>Status:</strong> {escape(experiment['status'])}<br>
<strong>Created:</strong> {escape(experiment['created_at'])}<br>
<strong>Report generated:</strong> {escape(generated)}<br>
<strong>Application version:</strong> 0.1.0</p>
<div class="notice">{escape(status_note)}</div>
<h2>Executive summary</h2>
<p>{self._executive_summary(rows, summary)}</p>
<h2>System overview</h2>
<p>A local language model interprets an instruction into a validated task. Deterministic A* then plans
the four-directional route, and an independent validator checks every cell and transition. Dynamic map
changes are replanned without another language-model call.</p>
<h2>Experimental configuration</h2>
<pre>{escape(str(experiment.get('config', {})))}</pre>
<h2>Model comparison</h2>{evidence_html}
<h2>Methodology and interpretation</h2>
<p>Success requires both a correct structured interpretation and a validator-approved route. Latency is
reported in milliseconds. Cache hits are counted explicitly. Results from offline deterministic tests
are not included as language-model observations.</p>
<h2>Limitations</h2>
<p>Local inference performance depends on the tested machine, model quantization, warm-up state, and
scenario set. Small samples must not be generalized. Missing resource observations are shown as absent,
not as zero.</p>
<h2>Reproducibility</h2>
<p>Use the stored experiment ID <code>{escape(experiment['id'])}</code>, configuration above, versioned
scenario files, prompt versions, and raw JSON/CSV exports to inspect or repeat this experiment.</p>
</main></body></html>"""
        destination.write_text(html, encoding="utf-8")
        return destination

    def generate_pdf(self, experiment: dict[str, Any], destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        rows = experiment.get("results", [])
        summary = self._summary(rows)
        styles = getSampleStyleSheet()
        document = SimpleDocTemplate(
            str(destination),
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title="Robot Navigation Experiment Report",
            author="NavLab",
        )
        story = [
            Paragraph("Robot Navigation Experiment Report", styles["Title"]),
            Spacer(1, 6 * mm),
            Paragraph(f"<b>Experiment:</b> {escape(experiment['name'])}", styles["BodyText"]),
            Paragraph(f"<b>Status:</b> {escape(experiment['status'])}", styles["BodyText"]),
            Paragraph("<b>Application version:</b> 0.1.0", styles["BodyText"]),
            Spacer(1, 5 * mm),
            Paragraph("Executive summary", styles["Heading2"]),
            Paragraph(self._executive_summary(rows, summary), styles["BodyText"]),
            Spacer(1, 4 * mm),
        ]
        if summary:
            table_data = [["Model", "Mode", "Runs", "Success", "Mean latency", "Failures"]]
            for item in summary:
                latency = "-" if item["mean_latency"] is None else f"{item['mean_latency']:.2f} ms"
                table_data.append(
                    [
                        item["model"],
                        item["mode"],
                        str(item["runs"]),
                        f"{item['success_rate']:.1f}%",
                        latency,
                        str(item["failures"]),
                    ]
                )
            table = Table(table_data, repeatRows=1)
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1d725a")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#c9d8d2")),
                        ("FONTSIZE", (0, 0), (-1, -1), 8),
                        ("PADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.extend([Paragraph("Model comparison", styles["Heading2"]), table])
        else:
            story.extend(
                [
                    Paragraph("No results yet", styles["Heading2"]),
                    Paragraph(
                        "No model observations are stored, so no comparison or best-model claim is "
                        "included.",
                        styles["BodyText"],
                    ),
                ]
            )
        story.extend(
            [
                Spacer(1, 5 * mm),
                Paragraph("Methodology", styles["Heading2"]),
                Paragraph(
                    "Success requires a correct structured interpretation and a validator-approved "
                    "A* route. Failures remain in denominators. Offline tests are not model results.",
                    styles["BodyText"],
                ),
                Paragraph("Limitations", styles["Heading2"]),
                Paragraph(
                    "Results depend on the tested hardware, exact model tag, quantization, warm-up "
                    "state, scenarios, and sample size.",
                    styles["BodyText"],
                ),
                Paragraph("Reproducibility", styles["Heading2"]),
                Paragraph(
                    f"Experiment ID: {escape(experiment['id'])}. Inspect JSON/CSV exports and "
                    "versioned scenarios for raw evidence.",
                    styles["BodyText"],
                ),
            ]
        )
        document.build(story)
        return destination

    @staticmethod
    def _summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[(row["model"], row["prompt_mode"])].append(row)
        summary = []
        for (model, mode), values in sorted(grouped.items()):
            latencies = [row["wall_time_ms"] for row in values if row["wall_time_ms"] is not None]
            summary.append(
                {
                    "model": model,
                    "mode": mode,
                    "runs": len(values),
                    "success_rate": 100 * sum(bool(row["success"]) for row in values) / len(values),
                    "mean_latency": mean(latencies) if latencies else None,
                    "failures": sum(not bool(row["success"]) for row in values),
                    "cache_hits": sum(bool(row["cache_hit"]) for row in values),
                }
            )
        return summary

    @staticmethod
    def _evidence_table(summary: list[dict[str, Any]]) -> str:
        rendered_rows = []
        for row in summary:
            latency = (
                "-" if row["mean_latency"] is None else f"{row['mean_latency']:.2f} ms"
            )
            rendered_rows.append(
                "<tr>"
                f"<td>{escape(row['model'])}</td><td>{escape(row['mode'])}</td>"
                f"<td>{row['runs']}</td><td>{row['success_rate']:.1f}%</td>"
                f"<td>{latency}</td><td>{row['failures']}</td>"
                f"<td>{row['cache_hits']}</td></tr>"
            )
        body = "".join(rendered_rows)
        return (
            "<table><thead><tr><th>Model</th><th>Configuration</th><th>Runs</th>"
            "<th>Success rate</th><th>Mean wall latency</th><th>Failures</th>"
            f"<th>Cache hits</th></tr></thead><tbody>{body}</tbody></table>"
        )

    @staticmethod
    def _executive_summary(
        rows: list[dict[str, Any]], summary: list[dict[str, Any]]
    ) -> str:
        if not rows:
            return (
                "No benchmark has been completed for this experiment. The report intentionally does "
                "not infer a best model or fabricate performance values."
            )
        successful = sum(bool(row["success"]) for row in rows)
        return escape(
            f"The experiment recorded {len(rows)} runs across {len(summary)} model/configuration "
            f"groups. {successful} runs met both interpretation and route-validity criteria. Detailed "
            "rows, including failures, remain available in JSON and CSV exports."
        )

