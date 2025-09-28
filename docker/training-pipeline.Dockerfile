# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install build tools and CMake
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    && rm -rf /var/lib/apt/lists/*

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Copy monorepo services first so uv can resolve local packages during the deps step
COPY services /app/services

# Install the project's dependencies using the lockfile and settings (deps only)
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Now add the rest of the repo and install the project itself
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# Put venv on PATH
ENV PATH="/app/.venv/bin:$PATH"

# Don’t override with uv entrypoint; use CMD to run the trainer
ENTRYPOINT []
CMD ["uv", "run", "/app/services/predictor/src/predictor/train.py"]

# Debug alternative:
# CMD ["/bin/bash", "-c", "sleep 999999"]
