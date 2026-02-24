from __future__ import annotations

from celery import shared_task

from .cache_service import (
    PAGE_SIZE,
    cache_page_if_missing,
)
from .progress_tracker import ProgressTracker
from .repository import fetch_employee_page


JOB_NAME = "employee_cache_refresh"
DEFAULT_BATCH_SIZE = PAGE_SIZE


@shared_task(bind=True, name="employees.tasks.refresh_employee_cache")
def refresh_employee_cache(self, start_after_id: int | None = None, batch_size: int = DEFAULT_BATCH_SIZE) -> dict:
    print("This is working and refreshing cache",start_after_id,batch_size)
    batch_size = max(int(batch_size), 1)
    tracker = ProgressTracker()

    if start_after_id is None:
        start_after_id = tracker.get_resume_checkpoint(JOB_NAME)

    start_after_id = int(start_after_id or 0)
    tracker.write(JOB_NAME, "STARTED", checkpoint=start_after_id, task_id=self.request.id)

    processed_count = start_after_id
    page_number = (start_after_id // batch_size) + 1

    while True:
        batch = fetch_employee_page(page_number, batch_size)
        if not batch:
            break

        cache_inserted = cache_page_if_missing(page_number, batch)
        processed_count += len(batch)
        tracker.write(
            JOB_NAME,
            "CHECKPOINT",
            checkpoint=processed_count,
            processed_count=processed_count,
            page=page_number,
            cache_inserted=cache_inserted,
            task_id=self.request.id,
        )
        page_number += 1

    tracker.write(JOB_NAME, "COMPLETED", checkpoint=processed_count, processed_count=processed_count)
    tracker.clear()
    return {"processed_count": processed_count, "last_checkpoint": processed_count}


def queue_resume_if_needed() -> None:
    tracker = ProgressTracker()
    if not tracker.has_incomplete_job(JOB_NAME):
        return

    checkpoint = tracker.get_resume_checkpoint(JOB_NAME)
    tracker.write(JOB_NAME, "RESUME_QUEUED", checkpoint=checkpoint)
    refresh_employee_cache.delay(start_after_id=checkpoint)
