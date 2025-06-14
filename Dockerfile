FROM python:3.12
WORKDIR /python

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY . ./

# Install the project and its dependencies
RUN uv sync

# Set the PATH to include the virtual environment
ENV PATH="/python/.venv/bin:$PATH"
ENV VIRTUAL_ENV="/python/.venv"