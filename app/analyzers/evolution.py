from collections import defaultdict

from app.models import FileEvolution, DriftEvent


def pct_change(before, after):
    if before == 0:
        return 100.0 if after else 0.0

    return ((after - before) / before) * 100.0


def build_file_evolution(snapshots):

    history = defaultdict(list)

    for snapshot in snapshots:

        for metric in snapshot.file_metrics:

            history[metric.path].append(
                (snapshot, metric)
            )

    result = []

    for path, entries in history.items():

        if len(entries) < 2:
            continue

        first_snapshot, first = entries[0]
        last_snapshot, last = entries[-1]

        line_change = pct_change(
            first.lines,
            last.lines
        )

        function_change = pct_change(
            first.functions,
            last.functions
        )

        branch_change = pct_change(
            first.branches,
            last.branches
        )

        # -----------------------------
        # Growth signal
        # -----------------------------

        growth_score = (
            max(line_change, 0) * 0.15
            + max(function_change, 0) * 0.10
            + max(branch_change, 0) * 0.15
        )

        # -----------------------------
        # Absolute complexity
        # -----------------------------

        complexity_score = (
            last.lines * 0.10
            + last.branches * 4
            + last.imports * 2
            + last.max_nesting * 8
        )

        # -----------------------------
        # Persistence
        # -----------------------------

        persistence_score = (
            len(entries)
            / len(snapshots)
        ) * 20

        # -----------------------------
        # Final score
        # -----------------------------

        score = (
            growth_score
            + complexity_score
            + persistence_score
        )

        result.append(
            FileEvolution(

                path=path,

                language=last.language,

                snapshots_present=len(entries),

                first_lines=first.lines,

                latest_lines=last.lines,

                first_functions=first.functions,

                latest_functions=last.functions,

                first_branches=first.branches,

                latest_branches=last.branches,

                line_change_percent=round(
                    line_change,
                    2
                ),

                function_change_percent=round(
                    function_change,
                    2
                ),

                branch_change_percent=round(
                    branch_change,
                    2
                ),

                max_lines=max(
                    metric.lines
                    for _, metric in entries
                ),

                max_branches=max(
                    metric.branches
                    for _, metric in entries
                ),

                score=round(
                    score,
                    2
                ),
            )
        )

    return sorted(
        result,
        key=lambda x: x.score,
        reverse=True
    )


def detect_drift(snapshots):

    events = []

    for before, after in zip(
        snapshots,
        snapshots[1:]
    ):

        checks = [

            (
                "repository_complexity_growth",
                before.branches,
                after.branches,
                40
            ),

            (
                "repository_code_growth",
                before.lines,
                after.lines,
                60
            ),

            (
                "dependency_growth",
                before.dependency_edges,
                after.dependency_edges,
                50
            ),
        ]

        for (
            kind,
            old,
            new,
            threshold
        ) in checks:

            change = pct_change(
                old,
                new
            )

            if change >= threshold:

                events.append(
                    DriftEvent(

                        type=kind,

                        severity=(
                            "critical"
                            if change >= threshold * 2
                            else "warning"
                        ),

                        commit=after.commit,

                        message=(
                            f"{kind.replace('_', ' ').title()} "
                            f"changed from {old} to {new}."
                        ),

                        before=float(old),

                        after=float(new),

                        change_percent=round(
                            change,
                            2
                        ),
                    )
                )

        if (
            after.dependency_cycles
            > before.dependency_cycles
        ):

            events.append(
                DriftEvent(

                    type="dependency_cycle",

                    severity="critical",

                    commit=after.commit,

                    message=(
                        "Dependency cycles increased "
                        f"from {before.dependency_cycles} "
                        f"to {after.dependency_cycles}."
                    ),

                    before=float(
                        before.dependency_cycles
                    ),

                    after=float(
                        after.dependency_cycles
                    ),
                )
            )

    return events