from __future__ import annotations

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


def run_healing_loop(report: RepoHealthReport, repo_dir: Path, settings: Settings) -> RepoHealthReport:
    gitpilot = GitPilotClient(settings)
    llm = OllaBridgeClient(settings)

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

        if llm.available():
            suggestion = llm.suggest_repair(report, str(repo_dir))
            if suggestion:
                report.notes.append(f"llm_suggestion={suggestion[:200]}")

        if gitpilot.available():
            gitpilot.run_headless(report.repo.full_name, build_fix_prompt(report, str(repo_dir)), report.branch_name)

        changed = apply_fixes(report, repo_dir)
        report.changed_files = sorted(set(report.changed_files + changed))
        report.notes.append(f"attempt {attempt}: applied {classify_failure(report)} local fixes")
