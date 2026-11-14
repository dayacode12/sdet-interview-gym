"""Application configuration via environment variables (.env supported)."""
from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "SDET Interview Gym"
    candidate_name: str = "Daya Sagar"

    # "auto" tries docker -> local -> disabled. Explicit modes override.
    java_execution_mode: str = "auto"
    java_docker_image: str = "sdet-gym-java:latest"
    java_local_enabled: bool = True
    java_timeout_seconds: int = 25
    java_max_output_chars: int = 20000

    # Optional LLM evaluation (OpenAI-compatible chat completions).
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"

    # In-app interview assistant (Groq, OpenAI-compatible chat completions).
    # The key is read from the environment / .env and never sent to the client.
    groq_api_key: str = ""
    groq_base_url: str = "https://api.groq.com/openai/v1"
    groq_model: str = "openai/gpt-oss-120b"
    # Dictation uploads are transcribed by Groq Whisper (audio never reaches
    # the browser's built-in speech service).
    groq_whisper_model: str = "whisper-large-v3-turbo"

    # Password for the private area (Admiral playbook + assistant). Empty means
    # the gate is off, which is what local development wants. Set it on the
    # hosted backend so the public site cannot read those endpoints.
    private_area_password: str = ""

    # SQLite by default; PostgreSQL in docker-compose via DATABASE_URL.
    database_url: str = f"sqlite:///{(BACKEND_DIR / 'data' / 'sdet_gym.db').as_posix()}"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()


def detect_java_mode() -> str:
    """Resolve the effective Java execution mode honestly.

    auto  -> docker if available, else local if enabled, else disabled
    The UI always shows which mode is active; execution is never faked.
    """
    mode = os.environ.get("JAVA_EXECUTION_MODE", settings.java_execution_mode).lower()
    if mode not in {"auto", "docker", "local", "disabled"}:
        mode = "auto"
    if mode == "auto":
        if _docker_available():
            return "docker"
        if settings.java_local_enabled and _java_available():
            return "local"
        return "disabled"
    if mode == "docker":
        return "docker" if _docker_available() else "disabled"
    if mode == "local":
        return "local" if _java_available() else "disabled"
    return "disabled"


def _docker_available() -> bool:
    import shutil
    import subprocess

    docker = shutil.which("docker")
    if not docker:
        return False
    try:
        subprocess.run(
            [docker, "info"],
            capture_output=True,
            timeout=10,
            check=True,
        )
        return True
    except Exception:
        return False


def _java_available() -> bool:
    import shutil
    import subprocess

    java = shutil.which("java")
    javac = shutil.which("javac")
    if not (java and javac):
        return False
    try:
        subprocess.run([javac, "-version"], capture_output=True, timeout=10, check=True)
        return True
    except Exception:
        return False


JAVA_MODE = detect_java_mode()
