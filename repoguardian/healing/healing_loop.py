from __future__ import annotations

import logging
from pathlib import Path

from repoguardian.analyzers.repo_analyzer import analyze_repo_layout
from repoguardian.gitpilot.client import GitPilotClient
from repoguardian.gitpilot.planner import build_fix_prompt, build_repair_plan
from repoguardian.healing.failure_classifier import classify_failure
from repoguardian.healing.fix_strategies import apply_fixes
from repoguardian.healing.retry_policy import should_retry
from repoguardian.llm.ollabridge_client import OllaBridgeClient
from repoguardian.matrixlab.verifier import verify_repo
from repoguardian.models import RepoHealthReport
from repoguardian.settings import Settings

logger = logging.getLogger(__name__)


def run_healing_loop(report: RepoHealthReport, repo_dir: Path, settings: Settings) -> RepoHealthReport:
    gitpilot = GitPilotClient(settings)
    ollabridge = OllaBridgeClient(settings) if settings.ollabridge_enabled else None

    attempt = 0
    while True:
        analyze_repo_layout(report, repo_dir)
        report.repair_plan = build_repair_plan(report)
        verify_repo(report, repo_dir, settings)
        if report.status == "healthy":
            return report

        if not should_retry(attempt, settings.max_fix_attempts):
            report.notes.append(f"max fix attempts reached ({settings.max_fix_attempts})")
            report.finalize_status()
            return report

        report.fix_attempts += 1
        attempt += 1

        # Try LLM-assisted repair via OllaBridge if available
        if ollabridge and ollabridge.available():
            try:
                prompt = build_fix_prompt(report, str(repo_dir))
                suggestion = ollabridge.chat(prompt)
                report.notes.append(f"ollabridge suggestion received ({len(suggestion)} chars)")
            except Exception as exc:
                logger.warning("OllaBridge repair suggestion failed: %s", exc)

        if gitpilot.available():
            gitpilot.run_headless(report.repo.full_name, build_fix_prompt(report, str(repo_dir)), report.branch_name)

        changed = apply_fixes(report, repo_dir)
        report.changed_files = sorted(set(report.changed_files + changed))
        report.notes.append(f"attempt {attempt}: applied {classify_failure(report)} local fixes")
