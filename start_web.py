"""
Railway web-service entry point.

1. Loads Employee CSV data into PostgreSQL (idempotent).
2. Runs Django migrations.
3. Collects static files.
4. Starts gunicorn on 0.0.0.0:$PORT.
"""
import os
import subprocess
import sys


def run(cmd: list[str], cwd: str | None = None, critical: bool = True) -> None:
    """Run a command. If critical=False, log failures but continue."""
    print(f">>> {' '.join(cmd)}", flush=True)
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        msg = f"Command failed with exit code {result.returncode}"
        if critical:
            print(msg, flush=True)
            sys.exit(result.returncode)
        else:
            print(f"WARNING: {msg} (non-critical, continuing...)", flush=True)


def main() -> int:
    port = os.getenv("PORT", "8000")
    app_dir = "/app/application"

    # Step 1 — Apply Django migrations (creates auth tables, sessions, etc.)
    run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=app_dir, critical=False)

    # Step 2 — Create employees table + load CSV data into PostgreSQL
    run([sys.executable, "/app/main.py"], critical=False)

    # Step 3 — Collect static files
    run([sys.executable, "manage.py", "collectstatic", "--noinput"], cwd=app_dir)

    # Step 4 — Start gunicorn
    print(f">>> Starting gunicorn on 0.0.0.0:{port}", flush=True)
    cmd = [
        "gunicorn",
        "config.wsgi:application",
        "--bind", f"0.0.0.0:{port}",
        "--workers", os.getenv("WEB_CONCURRENCY", "2"),
        "--timeout", "120",
        "--access-logfile", "-",
        "--error-logfile", "-",
    ]
    return subprocess.call(cmd, cwd=app_dir)


if __name__ == "__main__":
    raise SystemExit(main())
