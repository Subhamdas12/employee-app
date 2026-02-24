from django.apps import AppConfig
from django.conf import settings
import sys


class EmployeesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "employees"

    def ready(self):
        # Avoid duplicate startup actions caused by Django autoreload parent process.
        if settings.DEBUG and settings.__dict__.get("_resume_checked", False):
            return

        try:
            from .tasks import queue_resume_if_needed, refresh_employee_cache

            queue_resume_if_needed()
            # Trigger one immediate refresh on web app startup; periodic refresh remains on Celery Beat.
            if "runserver" in sys.argv:
                refresh_employee_cache.delay()
            settings._resume_checked = True
        except Exception:
            # Startup should not fail if broker/database is unavailable.
            pass
