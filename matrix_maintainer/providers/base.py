from __future__ import annotations

from typing import Protocol

from matrix_maintainer.models import RepoRef


class RepositoryProvider(Protocol):
    def list_repositories(self) -> list[RepoRef]: ...
