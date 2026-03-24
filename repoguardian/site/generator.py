from __future__ import annotations

import json
from pathlib import Path

from repoguardian.models import RepoHealthReport
from repoguardian.reporting.incident_builder import incidents_from_reports
from repoguardian.reporting.infra_status import default_infra_status
from repoguardian.reporting.repo_status import to_repo_item
from repoguardian.reporting.status_builder import build_summary
from repoguardian.settings import Settings


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if hasattr(data, "model_dump"):
        payload = data.model_dump(mode="json")
    elif isinstance(data, list):
        payload = [d.model_dump(mode="json") if hasattr(d, "model_dump") else d for d in data]
    else:
        payload = data
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def generate_site(settings: Settings) -> None:
    """Generate status-site JSON data from latest_status.json."""
    settings.ensure_directories()
    latest = settings.state_dir / "latest_status.json"

    reports: list[RepoHealthReport] = []
    if latest.exists():
        raw = json.loads(latest.read_text(encoding="utf-8"))
        for item in raw.get("items", []):
            reports.append(RepoHealthReport.model_validate(item))

    data_dir = settings.status_site_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    summary = build_summary(settings.site_title, settings.site_description, reports)
    _write_json(data_dir / "summary.json", summary)
    _write_json(data_dir / "repos.json", [to_repo_item(r) for r in reports])
    _write_json(data_dir / "incidents.json", incidents_from_reports(reports))
    _write_json(data_dir / "infra.json", default_infra_status())
