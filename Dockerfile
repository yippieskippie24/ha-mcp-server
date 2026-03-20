FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

# ── Layer 1: dependencies ────────────────────────────────────────────────────
# Install only the third-party deps first so this layer is cached and only
# rebuilds when the dependency versions in pyproject.toml change.
# Keep this list in sync with [project.dependencies] in pyproject.toml.
COPY pyproject.toml README.md ./
RUN uv pip install --system --no-cache \
    "mcp[cli]>=1.2.0" \
    "httpx>=0.27.0" \
    "websockets>=12.0" \
    "pydantic-settings>=2.5.0"

# ── Layer 2: package ─────────────────────────────────────────────────────────
# src/ is now present, so hatchling can build a real wheel.
# --no-deps skips re-resolving the deps we already installed above.
COPY src/ src/
RUN uv pip install --system --no-cache --no-deps .

EXPOSE 8080

CMD ["python", "-m", "ha_mcp"]
