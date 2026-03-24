from __future__ import annotations

from typing import Protocol

from repoguardian.models import RepoRef


class RepositoryProvider(Protocol):
    def list_repositories(self) -> list[RepoRef]: ...
