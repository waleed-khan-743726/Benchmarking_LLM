from pathlib import Path

from backend.reporting import ReportGenerator


def base_experiment() -> dict:
    return {
        "id": "exp-test",
        "name": "Report test",
        "status": "completed",
        "created_at": "2026-10-26T00:00:00+05:00",
        "config": {"models": ["test:small"]},
        "results": [],
    }


def test_no_results_report_is_honest(tmp_path: Path) -> None:
    destination = ReportGenerator().generate_html(
        base_experiment(), tmp_path / "no-results.html"
    )
    content = destination.read_text(encoding="utf-8")
    assert "No results yet" in content
    assert "does not infer a best model" in content
    pdf = ReportGenerator().generate_pdf(base_experiment(), tmp_path / "no-results.pdf")
    assert pdf.read_bytes().startswith(b"%PDF")


def test_report_summarizes_failures(tmp_path: Path) -> None:
    experiment = base_experiment()
    experiment["results"] = [
        {
            "model": "test:small",
            "prompt_mode": "baseline",
            "success": True,
            "wall_time_ms": 100.0,
            "cache_hit": False,
        },
        {
            "model": "test:small",
            "prompt_mode": "baseline",
            "success": False,
            "wall_time_ms": 200.0,
            "cache_hit": False,
        },
    ]
    destination = ReportGenerator().generate_html(experiment, tmp_path / "report.html")
    content = destination.read_text(encoding="utf-8")
    assert "50.0%" in content
    assert "150.00 ms" in content
    assert "1</td><td>0" in content

