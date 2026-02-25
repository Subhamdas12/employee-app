"""
Railway/local Celery beat entry point.
"""
import subprocess
import sys
from pathlib import Path


def resolve_app_dir() -> str:
    if Path("/app/application").exists():
        return "/app/application"
    return str((Path(__file__).resolve().parent / "application"))


def main() -> int:
    app_dir = resolve_app_dir()
    cmd = ["celery", "-A", "config", "beat", "-l", "info"]
    print(f">>> {' '.join(cmd)} (cwd={app_dir})", flush=True)
    return subprocess.call(cmd, cwd=app_dir)


if __name__ == "__main__":
    raise SystemExit(main())
