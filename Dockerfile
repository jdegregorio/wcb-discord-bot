FROM ghcr.io/astral-sh/uv:0.10.3 AS uv

FROM python:3.14-slim-bookworm@sha256:416f0db2a2b561945630cef9877a7ea0581b27449eb9fd9df42f03e1b74b5b63

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid app --home-dir /app app

COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md LICENSE ./
COPY src ./src

RUN uv sync --locked --no-dev --no-editable \
    && chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD ["trubot-healthcheck"]

CMD ["trubot"]
