#!/bin/bash
set -e

echo "=== RepoGuardian - Starting on HuggingFace Spaces ==="

# Ensure writable directories
mkdir -p "${WORK_DIR:-/tmp/repoguardian/work}"
mkdir -p "${STATE_DIR:-/tmp/repoguardian/state}"
mkdir -p "${STATUS_SITE_DIR:-/tmp/repoguardian/status-site}"

echo "Running RepoGuardian daily check..."
repoguardian run-daily || echo "Daily run completed with warnings"

echo "Generating status site..."
repoguardian publish-site

echo "=== RepoGuardian complete ==="

# If a web server is needed, serve the status site
if [ "${SERVE_DASHBOARD:-false}" = "true" ]; then
    echo "Serving dashboard on port ${PORT:-7860}..."
    cd "${STATUS_SITE_DIR:-/tmp/repoguardian/status-site}"
    python -m http.server "${PORT:-7860}"
fi
