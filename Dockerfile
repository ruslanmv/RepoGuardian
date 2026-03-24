FROM python:3.11-slim AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY repoguardian/ repoguardian/
RUN pip install --no-cache-dir -e ".[all]"

FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 guardian

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin/repoguardian /usr/local/bin/repoguardian
COPY --from=builder /app /app

USER guardian

HEALTHCHECK --interval=60s --timeout=5s \
  CMD python -c "import repoguardian; print('ok')" || exit 1

ENTRYPOINT ["repoguardian"]
CMD ["run-daily"]
