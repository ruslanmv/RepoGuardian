FROM python:3.11-slim

LABEL maintainer="RepoGuardian"
LABEL description="RepoGuardian - Autonomous Repository Health & Repair"

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY repoguardian/ repoguardian/

RUN pip install --no-cache-dir -e ".[all]"

# HF Spaces expects port 7860
ENV PORT=7860
ENV WORK_DIR=/tmp/repoguardian/work
ENV STATE_DIR=/tmp/repoguardian/state
ENV STATUS_SITE_DIR=/tmp/repoguardian/status-site

COPY deploy/huggingface/start.sh /app/start.sh
RUN chmod +x /app/start.sh

HEALTHCHECK --interval=30s --timeout=5s \
  CMD python -c "import repoguardian; print('ok')" || exit 1

CMD ["/app/start.sh"]
