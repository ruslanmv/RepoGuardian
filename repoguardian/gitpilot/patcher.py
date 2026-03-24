from __future__ import annotations

from pathlib import Path

from repoguardian.models import RepoHealthReport
from repoguardian.standards.health_test_rules import ensure_health_test
from repoguardian.standards.makefile_rules import ensure_makefile
from repoguardian.standards.pyproject_rules import ensure_pyproject
from repoguardian.standards.huggingface_rules import ensure_huggingface_metadata


def apply_safe_local_fixes(report: RepoHealthReport, repo_dir: Path) -> list[str]:
    changed: list[str] = []
    _, c1 = ensure_makefile(repo_dir)
    _, c2 = ensure_pyproject(repo_dir, report.repo.name)
    _, c3 = ensure_health_test(repo_dir)
    _, c4 = ensure_huggingface_metadata(repo_dir, report.repo)
    changed.extend(c1 + c2 + c3 + c4)
    return sorted(set(changed))
