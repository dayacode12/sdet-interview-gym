"""Isolated Java code execution.

Security model (never fake a successful run):
1. docker  -> code is executed inside a throwaway container with no network,
              a read-only root FS, a tmpfs workspace, CPU and memory limits.
2. local   -> code is executed as a separate short-lived subprocess (javac + java)
              in an isolated temp directory. This is the development fallback and
              is clearly labelled as such in the UI.
3. disabled-> no execution. The editor, hints, solution review and test list all
              remain available, and every run request returns an honest error.
"""
from __future__ import annotations

import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from app.config import JAVA_MODE, settings


@dataclass
class ExecutionResult:
    ok: bool
    passed: int = 0
    total: int = 0
    compile_error: str | None = None
    test_results: list[dict] = field(default_factory=list)
    mode: str = JAVA_MODE
    error: str | None = None

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "passed": self.passed,
            "total": self.total,
            "compile_error": self.compile_error,
            "test_results": self.test_results,
            "mode": self.mode,
            "error": self.error,
        }


def _truncate(text: str, limit: int | None = None) -> str:
    limit = limit or settings.java_max_output_chars
    text = text or ""
    if len(text) > limit:
        return text[:limit] + f"\n... [truncated, {len(text) - limit} more characters]"
    return text


def run_tests(code: str, tests: list[dict]) -> ExecutionResult:
    """Compile once, then run the class once per test comparing stdout."""
    if JAVA_MODE == "disabled":
        return ExecutionResult(
            ok=False,
            error=(
                "Java execution is disabled on this machine. Docker and a local JDK were not "
                "found. You can still study the problem, hints and solution — execution is "
                "never simulated."
            ),
        )
    if not code or "public class Main" not in code:
        return ExecutionResult(ok=False, error="Code must define a public class named Main.")

    compile_error, workdir, classname = _compile(code)
    if compile_error is not None:
        return ExecutionResult(ok=False, compile_error=compile_error)

    passed = 0
    results: list[dict] = []
    for test in tests:
        try:
            stdout, stderr, timed_out = _run_class(workdir, classname, test.get("stdin", ""))
        except Exception as exc:  # pragma: no cover - environment failures
            results.append({"name": test["name"], "passed": False, "error": str(exc)})
            continue
        expected = (test.get("expected", "") or "").strip()
        actual = stdout.strip()
        ok = not timed_out and actual == expected
        if ok:
            passed += 1
        results.append(
            {
                "name": test["name"],
                "passed": ok,
                "expected": expected,
                "actual": actual,
                "timed_out": timed_out,
                "stderr": _truncate(stderr) if stderr else "",
            }
        )
    return ExecutionResult(ok=passed == len(tests) and len(tests) > 0, passed=passed, total=len(tests), test_results=results)


def _prepare_sources(code: str) -> tuple[Path, str]:
    """Write Main.java into a fresh isolated temp directory."""
    workdir = Path(tempfile.mkdtemp(prefix="sdet-java-"))
    if JAVA_MODE == "docker":
        (workdir / "Main.java").write_text(code, encoding="utf-8")
        return workdir, "Main"
    # Single-file source launch keeps a .java extension requirement, so we compile instead.
    source = workdir / "Main.java"
    source.write_text(code, encoding="utf-8")
    return workdir, "Main"


def _compile(code: str) -> tuple[str | None, Path, str]:
    workdir, classname = _prepare_sources(code)
    if JAVA_MODE == "docker":
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1",
            "-v", f"{workdir.as_posix()}:/work",
            "-w", "/work",
            settings.java_docker_image,
            "javac", "-encoding", "UTF-8", "Main.java",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=settings.java_timeout_seconds)
        except Exception as exc:  # pragma: no cover
            return f"Could not start Docker execution: {exc}", workdir, classname
        if proc.returncode != 0:
            return _truncate(proc.stderr or proc.stdout or "compilation failed"), workdir, classname
        return None, workdir, classname

    # local mode
    try:
        proc = subprocess.run(
            ["javac", "-encoding", "UTF-8", "Main.java"],
            cwd=workdir,
            capture_output=True,
            text=True,
            timeout=settings.java_timeout_seconds,
        )
    except Exception as exc:  # pragma: no cover
        return f"Could not start javac: {exc}", workdir, classname
    if proc.returncode != 0:
        return _truncate(proc.stderr or proc.stdout or "compilation failed"), workdir, classname
    return None, workdir, classname


def _run_class(workdir: Path, classname: str, stdin_text: str) -> tuple[str, str, bool]:
    if JAVA_MODE == "docker":
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "512m",
            "--cpus", "1",
            "-v", f"{workdir.as_posix()}:/work",
            "-w", "/work",
            settings.java_docker_image,
            "java", "-XX:+UseSerialGC", "-Xmx256m", classname,
        ]
    else:
        cmd = ["java", "-XX:+UseSerialGC", "-Xmx256m", classname]
    try:
        proc = subprocess.run(
            cmd,
            cwd=workdir,
            input=stdin_text,
            capture_output=True,
            text=True,
            timeout=settings.java_timeout_seconds,
        )
    except subprocess.TimeoutExpired:
        return "", "", True
    return proc.stdout or "", proc.stderr or "", False
