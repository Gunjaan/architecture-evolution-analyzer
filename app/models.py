from pydantic import BaseModel, Field


class FileMetrics(BaseModel):
    path: str
    language: str
    lines: int
    functions: int
    classes: int
    imports: int
    branches: int
    max_nesting: int


class SnapshotMetrics(BaseModel):
    commit: str
    short_sha: str
    message: str
    timestamp: str

    files: int
    lines: int
    functions: int
    classes: int
    imports: int
    branches: int

    dependency_edges: int
    dependency_cycles: int

    file_metrics: list[FileMetrics] = Field(
        default_factory=list
    )


class FileEvolution(BaseModel):
    path: str
    language: str

    snapshots_present: int

    first_lines: int
    latest_lines: int

    first_functions: int
    latest_functions: int

    first_branches: int
    latest_branches: int

    line_change_percent: float
    function_change_percent: float
    branch_change_percent: float

    max_lines: int
    max_branches: int

    score: float


class DriftEvent(BaseModel):
    type: str
    severity: str
    commit: str
    message: str

    before: float | None = None
    after: float | None = None
    change_percent: float | None = None


class EvolutionReport(BaseModel):
    repository: str

    total_commits: int
    commits_analyzed: int
    snapshots_analyzed: int

    supported_files: int

    unsupported_extensions: dict[str, int] = Field(
        default_factory=dict
    )

    languages: dict[str, int] = Field(
        default_factory=dict
    )

    snapshots: list[SnapshotMetrics]

    file_evolution: list[FileEvolution]

    drift_events: list[DriftEvent]

    hotspots: list[FileEvolution]

    ai_explanation: str | None = None