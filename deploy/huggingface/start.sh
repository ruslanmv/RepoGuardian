#!/bin/bash
set -e

echo "=== RepoGuardian Enterprise Web UI ==="
echo "Starting on port ${PORT:-7860}..."

# Ensure writable directories
mkdir -p "${WORK_DIR:-/tmp/repoguardian/work}"
mkdir -p "${STATE_DIR:-/tmp/repoguardian/state}"
mkdir -p "${STATUS_SITE_DIR:-/tmp/repoguardian/status-site}"

# Start the FastAPI web application
exec uvicorn webapp.main:app \
    --host "${HOST:-0.0.0.0}" \
    --port "${PORT:-7860}" \
    --workers 1 \
    --log-level info
