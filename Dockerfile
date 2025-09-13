# To build, run: docker build -t <name of the Docker image> .
# Optionally change this URL to build from a different repository, or a specific commit
# by doing instead: `docker build --build-arg GITHUB_URL=<the new URL> -t <name of the Docker image> .`
# You can also specify a commit or branch by passing --build-arg GIT_REVISION=<...>

FROM python:3.12-slim-trixie

ARG GITHUB_URL="https://github.com/akoyamp/geopolrisk-py"
ARG GIT_REVISION="main"

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates git

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app
RUN git clone ${GITHUB_URL}

WORKDIR /app/geopolrisk-py

RUN git checkout ${GIT_REVISION} && uv venv

RUN uv pip install -r pyproject.toml

CMD ["uv", "run", "fastapi", "run", "src/geopolrisk/assessment/api.py", "--port", "8000"]
