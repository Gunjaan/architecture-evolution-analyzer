from pathlib import Path

from git import InvalidGitRepositoryError, Repo
from git.objects.commit import Commit


class GitHistory:
    def __init__(self, repo_path: str | Path) -> None:
        self.path = Path(repo_path).expanduser().resolve()

        try:
            self.repo = Repo(self.path)
        except InvalidGitRepositoryError as exc:
            raise ValueError(f"Not a Git repository: {self.path}") from exc

    def total_commits(self) -> int:
        return sum(1 for _ in self.repo.iter_commits())

    def sampled_commits(self, snapshot_count: int = 30) -> list[Commit]:
        """
        Select snapshots evenly across the ENTIRE Git history.

        Example:
        299 commits + 30 snapshots
        -> approximately every 10 commits
        """

        all_commits = list(self.repo.iter_commits())

        if not all_commits:
            return []

        count = min(snapshot_count, len(all_commits))

        if count == 1:
            return [all_commits[-1]]

        indexes = [
            round(i * (len(all_commits) - 1) / (count - 1)) for i in range(count)
        ]

        # Git returns newest -> oldest.
        # Reverse so analysis is oldest -> newest.
        return [all_commits[i] for i in reversed(indexes)]

    def checkout(self, sha: str) -> None:
        self.repo.git.checkout(sha, "--force")

    def current_ref(self) -> str:
        """Return a branch name or SHA that can restore the original checkout."""

        try:
            return self.repo.active_branch.name
        except TypeError:
            return self.repo.head.commit.hexsha

    def restore(self, ref: str) -> None:
        self.repo.git.checkout(ref, "--force")
