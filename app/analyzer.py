import os
from collections import Counter
from collections.abc import Callable
from pathlib import Path

from .analyzers.code_parser import CodeParser
from .analyzers.dependencies import DependencyAnalyzer
from .analyzers.evolution import (
    build_file_evolution,
    detect_drift,
)
from .git_history import GitHistory
from .models import EvolutionReport, SnapshotMetrics
from .report import build_evidence, build_fallback_explanation


def analyze_repository(
    repo_path: str | Path,
    snapshot_count: int = 30,
    use_llm: bool = True,
    progress: Callable[[float, str], None] | None = None,
) -> EvolutionReport:

    history = GitHistory(repo_path)

    total_commits = history.total_commits()

    commits = history.sampled_commits(snapshot_count)

    if not commits:
        raise RuntimeError("Repository has no commits.")

    original_ref = history.current_ref()

    parser = CodeParser()
    dependency = DependencyAnalyzer()

    snapshots: list[SnapshotMetrics] = []

    unsupported: Counter[str] = Counter()

    try:
        for index, commit in enumerate(commits, 1):
            history.checkout(commit.hexsha)

            metrics, unsupported_here = parser.analyze_repo(history.path)

            commit_message = commit.message
            if isinstance(commit_message, bytes):
                commit_message = commit_message.decode("utf-8", errors="replace")

            unsupported.update(unsupported_here)

            graph = dependency.build_graph(history.path)

            snapshot = SnapshotMetrics(
                commit=commit.hexsha,
                short_sha=commit.hexsha[:8],
                message=commit_message.strip().split("\n")[0],
                timestamp=(commit.committed_datetime.isoformat()),
                files=len(metrics),
                lines=sum(m.lines for m in metrics),
                functions=sum(m.functions for m in metrics),
                classes=sum(m.classes for m in metrics),
                imports=sum(m.imports for m in metrics),
                branches=sum(m.branches for m in metrics),
                dependency_edges=(graph.number_of_edges()),
                dependency_cycles=(dependency.cycle_count(graph)),
                file_metrics=metrics,
            )

            snapshots.append(snapshot)

            if progress:
                progress(
                    index / len(commits),
                    (f"Analyzing {index}/{len(commits)} — {commit.hexsha[:8]}"),
                )

    finally:
        history.restore(original_ref)

    latest = snapshots[-1]

    languages: Counter[str] = Counter(metric.language for metric in latest.file_metrics)

    file_evolution = build_file_evolution(snapshots)

    report = EvolutionReport(
        repository=str(history.path),
        total_commits=total_commits,
        commits_analyzed=len(commits),
        snapshots_analyzed=len(snapshots),
        supported_files=len(latest.file_metrics),
        unsupported_extensions=dict(unsupported),
        languages=dict(languages),
        snapshots=snapshots,
        file_evolution=file_evolution,
        drift_events=detect_drift(snapshots),
        hotspots=file_evolution[:10],
    )

    # -----------------------------
    # Hugging Face explanation
    # -----------------------------

    if use_llm and os.getenv("HF_TOKEN"):
        try:
            from .llm.explainer import HuggingFaceExplainer

            explainer = HuggingFaceExplainer()

            report.ai_explanation = explainer.explain(build_evidence(report))

        except Exception:
            report.ai_explanation = build_fallback_explanation(report)

    elif use_llm:
        report.ai_explanation = "HF_TOKEN is not configured."

    return report
