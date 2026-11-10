FROM python:3.12-slim

WORKDIR /srv

# JDK 17 for the honest "local" Java execution mode: candidate code compiles
# and runs inside this container as an isolated subprocess. (The "docker"
# mode would need a sibling executor container, which hosts like Render
# cannot provide; "local" keeps execution real without faking it.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests

# Non-root runtime user.
RUN useradd --create-home gym && chown -R gym:gym /srv
USER gym

# The SQLite data directory must be writable (volume-mounted for persistence).
ENV PYTHONUNBUFFERED=1
VOLUME ["/srv/data"]

EXPOSE 8000
# Render injects PORT; locally the default 8000 applies.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
