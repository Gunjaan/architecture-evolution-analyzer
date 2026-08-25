from app.models import EvolutionReport


def build_evidence(report: EvolutionReport) -> str:

    lines = [
        f"Repository: {report.repository}",
        f"Total commits: {report.total_commits}",
        f"Historical snapshots analyzed: {report.snapshots_analyzed}",
        f"Supported files: {report.supported_files}",
        f"Languages: {report.languages}",
        "",
        "Repository evolution:",
    ]

    # --------------------------------
    # Historical repository metrics
    # --------------------------------

    for snapshot in report.snapshots:
        lines.append(
            f"- {snapshot.short_sha}: "
            f"lines={snapshot.lines}, "
            f"files={snapshot.files}, "
            f"functions={snapshot.functions}, "
            f"classes={snapshot.classes}, "
            f"branches={snapshot.branches}, "
            f"imports={snapshot.imports}, "
            f"dependency_edges={snapshot.dependency_edges}, "
            f"dependency_cycles={snapshot.dependency_cycles}"
        )

    # --------------------------------
    # File evolution
    # --------------------------------

    lines.extend(
        [
            "",
            "Top evolving files:",
        ]
    )

    for file in report.hotspots[:10]:
        lines.append(
            f"- {file.path} "
            f"[{file.language}]: "
            f"appeared_in={file.snapshots_present}/"
            f"{report.snapshots_analyzed} snapshots, "
            f"lines={file.first_lines}->"
            f"{file.latest_lines} "
            f"({file.line_change_percent:+.1f}%), "
            f"functions={file.first_functions}->"
            f"{file.latest_functions} "
            f"({file.function_change_percent:+.1f}%), "
            f"branches={file.first_branches}->"
            f"{file.latest_branches} "
            f"({file.branch_change_percent:+.1f}%), "
            f"max_lines={file.max_lines}, "
            f"max_branches={file.max_branches}, "
            f"risk_score={file.score}"
        )

    # --------------------------------
    # Drift events
    # --------------------------------

    lines.extend(
        [
            "",
            "Detected drift events:",
        ]
    )

    if not report.drift_events:
        lines.append("- None detected.")

    else:
        for event in report.drift_events:
            lines.append(
                f"- {event.severity}: "
                f"{event.type} at "
                f"{event.commit[:8]} — "
                f"{event.message}"
            )

    return "\n".join(lines)


def build_fallback_explanation(report: EvolutionReport) -> str:
    """Build a helpful report when the optional LLM provider is unavailable."""

    lines = [
        "## Architectural interpretation",
        "",
        (
            "The optional AI provider is temporarily unavailable. "
            "This deterministic summary is based on the collected repository metrics."
        ),
        "",
        "## Repository profile",
        (
            f"{report.total_commits} commits were sampled into "
            f"{report.snapshots_analyzed} historical snapshots, covering "
            f"{report.supported_files} supported source files."
        ),
    ]

    if report.hotspots:
        lines.extend(["", "## Top hotspots"])
        for hotspot in report.hotspots[:5]:
            lines.append(
                f"- `{hotspot.path}`: {hotspot.latest_lines} lines, "
                f"{hotspot.line_change_percent:+.1f}% line growth, "
                f"risk score {hotspot.score}."
            )

    lines.extend(["", "## Drift signals"])
    if report.drift_events:
        for event in report.drift_events[:5]:
            lines.append(f"- {event.severity.title()}: {event.message}")
    else:
        lines.append("- No configured architectural drift thresholds were crossed.")

    return "\n".join(lines)
