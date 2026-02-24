# Django Employee Cache App

This project provides:
- PostgreSQL-backed `employee` model via Django ORM.
- Redis-backed read-through caching for employee list page.
- Celery worker + Celery Beat using Redis as broker and backend.
- Checkpoint logging in `progress.log` for resume-after-restart cache refresh tasks.

## Structure

```text
application/
  config/
    settings.py
    urls.py
    celery.py
  employees/
    models.py
    repository.py
    cache_service.py
    progress_tracker.py
    tasks.py
    views.py
    templates/employees/employee_list.html
```

## Setup

```powershell
cd application
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run migrations

```powershell
python manage.py migrate
```

## Run services

```powershell
# Django app
python manage.py runserver

# Celery worker
celery -A config worker -l info

# Celery beat
celery -A config beat -l info
```

## Behavior

- First `GET /` request reads employees from PostgreSQL and stores them in Redis.
- Later `GET /` requests return data from Redis cache.
- Celery Beat periodically triggers `employees.tasks.refresh_employee_cache`.
- Task checkpoints append JSON lines to `progress.log`.
- On app/worker startup, unfinished jobs are detected and resumed from last checkpoint.
