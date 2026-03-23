# RepoGuardian

RepoGuardian is a production-ready foundation for continuously verifying, repairing, and maintaining repository health across **GitHub** and **Hugging Face**.

It discovers repositories, clones them into isolated workspaces, runs install/test/start verification, applies safe local repairs, validates the result, and prepares a repair branch that is ready to become a pull request.

## What it does

- Discovers repositories from a GitHub org or user and a Hugging Face namespace
- Detects repository type and basic health signals
- Verifies install, test, and startup flows
- Applies safe automated fixes for common repo hygiene issues
- Generates a repair plan and branch name for human review
- Publishes JSON and HTML status artifacts for dashboards

## Current repair coverage

RepoGuardian currently focuses on the safest production bootstrap fixes:

- missing `Makefile`
- missing `pyproject.toml`
- missing `tests/test_health.py`
- missing Hugging Face README front matter
- missing Python 3.11 and `tool.uv` markers in `pyproject.toml`

This gives you a solid base repo that can be extended with language-specific and platform-specific repair strategies.

## Platforms

### GitHub

- org-wide or user-wide repository discovery
- branch naming for repair proposals
- ready for PR workflows after branch push

### Hugging Face

- model, dataset, and Space discovery
- repo metadata validation
- branch-ready repair workflow for Hub repositories

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Configuration

Copy the example environment file and set the namespaces you want to manage:

```bash
cp .env.example .env
```

Key variables:

- `GITHUB_ORG` or `GITHUB_USER`
- `HF_NAMESPACE`
- `GITHUB_TOKEN`
- `HF_TOKEN`
- `DRY_RUN=true` for safe local validation without pushing branches

## CLI

```bash
repoguardian discover
repoguardian run
repoguardian check-repo owner/repo
repoguardian publish-site
```

`matrix-maintainer` remains as a compatibility alias.

## How the production flow works

1. Discover repositories
2. Clone into `work/`
3. Analyze layout and metadata
4. Run install / test / start verification
5. Apply safe repairs if needed
6. Re-run verification
7. Mark healthy, degraded, or down
8. Prepare a repair branch and site artifacts

## Branches and PR readiness

When a repository becomes healthy after fixes, RepoGuardian prepares a branch named like:

```text
repoguardian/repair/<repo-name>
```

In `DRY_RUN=true` mode it records the intended push without pushing upstream. Set `DRY_RUN=false` to allow real branch pushes.

## Status artifacts

RepoGuardian writes:

- `state/repo_inventory.json`
- `state/latest_status.json`
- `state/history_index.json`
- `status-site/data/*.json`
- `status-site/index.html`

## Test suite

```bash
pytest
```

## Recommended next production steps

- add GitHub PR creation through the API
- add Hugging Face discussion / PR publishing
- add repo-type-specific validators for Node, Rust, model cards, datasets, and Spaces
- run execution in containers instead of direct local subprocesses
- add allowlists, deny lists, and approval policies

## License

Apache-2.0
