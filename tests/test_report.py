from app.models import EvolutionReport
from app.report import build_fallback_explanation


def test_fallback_explanation_never_exposes_provider_error() -> None:
    report = EvolutionReport(
        repository="example",
        total_commits=5,
        commits_analyzed=5,
        snapshots_analyzed=5,
        supported_files=2,
        snapshots=[],
        file_evolution=[],
        drift_events=[],
        hotspots=[],
    )

    explanation = build_fallback_explanation(report)

    assert "temporarily unavailable" in explanation
    assert "No configured architectural drift" in explanation
    assert "HfHubHTTPError" not in explanation
