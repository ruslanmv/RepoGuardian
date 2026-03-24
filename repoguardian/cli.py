from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from repoguardian.inventory.huggingface_discovery import HuggingFaceDiscovery
from repoguardian.inventory.org_discovery import GitHubOrgDiscovery
from repoguardian.logging import configure_logging
from repoguardian.main import check_single_repo, run_daily
from repoguardian.site.generator import generate_site
from repoguardian.settings import get_settings

app = typer.Typer(add_completion=False, help="RepoGuardian CLI")
console = Console()


@app.callback()
def _callback() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)


@app.command("discover")
def discover() -> None:
    settings = get_settings()
    repos = GitHubOrgDiscovery(settings).list_repositories() + HuggingFaceDiscovery(settings).list_repositories()
    table = Table(title="Repositories")
    table.add_column("Platform")
    table.add_column("Name")
    table.add_column("Default branch")
    for repo in repos:
        table.add_row(repo.platform, repo.full_name, repo.default_branch)
    console.print(table)


@app.command("run")
@app.command("run-daily")
def run_daily_cmd() -> None:
    settings = get_settings()
    reports = run_daily(settings)
    console.print(f"Processed {len(reports)} repositories")


@app.command("publish-site")
def publish_site() -> None:
    settings = get_settings()
    generate_site(settings)
    console.print("Status site generated")


@app.command("check-repo")
def check_repo(repo_name: str) -> None:
    settings = get_settings()
    repos = GitHubOrgDiscovery(settings).list_repositories() + HuggingFaceDiscovery(settings).list_repositories()
    repo = next((r for r in repos if r.name == repo_name or r.full_name == repo_name), None)
    if repo is None:
        raise typer.Exit(f"Repository not found: {repo_name}")
    report = check_single_repo(repo, settings)
    console.print_json(data=report.model_dump(mode="json"))


if __name__ == "__main__":
    app()
