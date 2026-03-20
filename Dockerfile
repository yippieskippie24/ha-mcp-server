FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Install dependencies first (layer-cached separately from source)
# README.md must be present because pyproject.toml references it and hatchling validates it
COPY pyproject.toml README.md ./
RUN uv pip install --system --no-cache .

# Copy application source
COPY src/ src/

EXPOSE 8080

CMD ["python", "-m", "ha_mcp"]
