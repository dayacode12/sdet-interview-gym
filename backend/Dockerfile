FROM python:3.12-slim

WORKDIR /srv

# JDK 21 (Debian trixie's packaged LTS) for the honest "local" Java execution
# mode: candidate code compiles and runs inside this container as an isolated
# subprocess. (The "docker" mode would need a sibling executor container,
# which hosts like Render cannot provide; "local" keeps execution real
# without faking it.)
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-21-jdk-headless \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY tests ./tests

# Non-root runtime user. /srv/data exists (gym-owned) for the SQLite fallback;
# on Render DATABASE_URL points at managed PostgreSQL instead.
RUN useradd --create-home gym \
    && mkdir -p /srv/data \
    && chown -R gym:gym /srv
USER gym

ENV PYTHONUNBUFFERED=1

EXPOSE 8000
# Render injects PORT; locally the default 8000 applies.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
