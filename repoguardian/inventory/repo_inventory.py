from __future__ import annotations

import json

from repoguardian.models import RepoRef
from repoguardian.settings import Settings


def save_inventory(settings: Settings, repos: list[RepoRef]) -> None:
    settings.state_dir.mkdir(parents=True, exist_ok=True)
    payload = {"items": [repo.model_dump(mode="json") for repo in repos]}
    (settings.state_dir / "repo_inventory.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
