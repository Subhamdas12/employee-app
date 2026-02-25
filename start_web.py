"""
Railway/local web-service entry point.

1. Runs Django migrations.
2. Loads Employee CSV data into PostgreSQL (idempotent).
3. Collects static files.
4. Starts gunicorn on Railway, runserver locally.
"""
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: str | None = None, critical: bool = True) -> None:
    """Run a command. If critical=False, log failures but continue."""
    print(f">>> {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        msg = f"Command failed with exit code {result.returncode}"
        if critical:
            print(msg, flush=True)
            sys.exit(result.returncode)
        print(f"WARNING: {msg} (non-critical, continuing...)", flush=True)


def resolve_paths() -> tuple[str, str]:
    """Resolve app and loader paths for both local and container execution."""
    script_dir = Path(__file__).resolve().parent

    app_dir_env = os.getenv("APP_DIR")
    if app_dir_env:
        app_dir = Path(app_dir_env)
    elif Path("/app/application").exists():
        app_dir = Path("/app/application")
    else:
        app_dir = script_dir / "application"

    main_py = script_dir / "main.py"
    if not main_py.exists() and Path("/app/main.py").exists():
        main_py = Path("/app/main.py")

    return str(app_dir), str(main_py)


def main() -> int:
    port = os.getenv("PORT", "8000")
    app_dir, main_py = resolve_paths()

    # Step 1 - Apply Django migrations (creates auth tables, sessions, etc.).
    run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=app_dir, critical=False)

    # Step 2 - Create employees table + load CSV data into PostgreSQL.
    run([sys.executable, main_py], critical=False)

    # Step 3 - Collect static files.
    run([sys.executable, "manage.py", "collectstatic", "--noinput"], cwd=app_dir)

    # Step 4 - Start server (Railway: gunicorn, local: runserver).
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PUBLIC_DOMAIN"):
        print(f">>> Starting gunicorn on 0.0.0.0:{port}", flush=True)
        cmd = [
            "gunicorn",
            "config.wsgi:application",
            "--bind",
            f"0.0.0.0:{port}",
            "--workers",
            os.getenv("WEB_CONCURRENCY", "2"),
            "--timeout",
            "120",
            "--access-logfile",
            "-",
            "--error-logfile",
            "-",
        ]
    else:
        print(f">>> Starting Django runserver on 127.0.0.1:{port}", flush=True)
        cmd = [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}"]

    return subprocess.call(cmd, cwd=app_dir)


if __name__ == "__main__":
    raise SystemExit(main())
