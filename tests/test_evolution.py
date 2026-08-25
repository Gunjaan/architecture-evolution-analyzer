from app.analyzers.evolution import build_file_evolution, detect_drift, pct_change
from app.models import FileMetrics, SnapshotMetrics


def snapshot(commit: str, lines: int, branches: int, edges: int) -> SnapshotMetrics:
    """Create a minimal snapshot with one source file for evolution tests."""

    return SnapshotMetrics(
        commit=commit * 40,
        short_sha=commit * 8,
        message="test commit",
        timestamp="2026-01-01T00:00:00+00:00",
        files=1,
        lines=lines,
        functions=1,
        classes=0,
        imports=1,
        branches=branches,
        dependency_edges=edges,
        dependency_cycles=0,
        file_metrics=[
            FileMetrics(
                path="app/example.py",
                language="python",
                lines=lines,
                functions=1,
                classes=0,
                imports=1,
                branches=branches,
                max_nesting=1,
            )
        ],
    )


def test_pct_change_handles_zero_baseline() -> None:
    assert pct_change(0, 0) == 0.0
    assert pct_change(0, 5) == 100.0
    assert pct_change(20, 30) == 50.0


def test_build_file_evolution_tracks_growth() -> None:
    evolution = build_file_evolution([snapshot("a", 10, 1, 1), snapshot("b", 20, 2, 2)])

    assert len(evolution) == 1
    assert evolution[0].path == "app/example.py"
    assert evolution[0].line_change_percent == 100.0
    assert evolution[0].latest_branches == 2


def test_detect_drift_reports_large_growth() -> None:
    events = detect_drift([snapshot("a", 10, 1, 1), snapshot("b", 20, 2, 2)])

    assert {event.type for event in events} == {
        "repository_complexity_growth",
        "repository_code_growth",
        "dependency_growth",
    }
