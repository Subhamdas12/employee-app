from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from django.conf import settings


TERMINAL_STATES = {"COMPLETED", "FAILED"}


@dataclass
class ProgressState:
    state: str
    checkpoint: int | None
    payload: dict[str, Any]


class ProgressTracker:
    def __init__(self, log_path: Path | None = None):
        self.log_path = Path(log_path or settings.PROGRESS_LOG_PATH)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()

    def write(self, job_name: str, state: str, checkpoint: int | None = None, **kwargs) -> None:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "job_name": job_name,
            "state": state,
            "checkpoint": checkpoint,
            "payload": kwargs,
        }
        with self.log_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(event) + "\n")

    def clear(self) -> None:
        with self.log_path.open("w", encoding="utf-8"):
            pass

    def get_latest_state(self, job_name: str) -> ProgressState | None:
        latest_event: dict[str, Any] | None = None
        with self.log_path.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("job_name") == job_name:
                    latest_event = event

        if not latest_event:
            return None

        return ProgressState(
            state=latest_event.get("state", "UNKNOWN"),
            checkpoint=latest_event.get("checkpoint"),
            payload=latest_event.get("payload", {}),
        )

    def get_resume_checkpoint(self, job_name: str) -> int | None:
        latest_state = self.get_latest_state(job_name)
        if latest_state is None:
            return None
        if latest_state.state in TERMINAL_STATES:
            return None
        return int(latest_state.checkpoint or 0)

    def has_incomplete_job(self, job_name: str) -> bool:
        latest_state = self.get_latest_state(job_name)
        if latest_state is None:
            return False
        return latest_state.state not in TERMINAL_STATES
