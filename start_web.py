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


def run(cmd: list[str], cwd: str | None = None) -> None:
    print(f">>> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"Command failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def main() -> int:
    port = os.getenv("PORT", "8000")
    app_dir = "/app/application"

    # Step 1 — Load CSV data into PostgreSQL (creates tables + imports if needed)
    run([sys.executable, "/app/main.py"])

    # Step 2 — Apply Django migrations
    run([sys.executable, "manage.py", "migrate", "--noinput"], cwd=app_dir)

    # Step 3 — Collect static files
    run([sys.executable, "manage.py", "collectstatic", "--noinput"], cwd=app_dir)

    # Step 4 — Start gunicorn
    print(f">>> Starting gunicorn on 0.0.0.0:{port}")
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
