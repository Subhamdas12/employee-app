import os
import subprocess
import sys


def main() -> int:
    port = os.getenv("PORT", "8000")
    cmd = [
        sys.executable,
        "/app/application/manage.py",
        "runserver",
        f"0.0.0.0:{port}",
    ]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
