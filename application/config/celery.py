import os

from celery import Celery
from celery.signals import worker_ready


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@worker_ready.connect
def queue_resume_on_worker_start(sender=None, **kwargs):
    from employees.tasks import queue_resume_if_needed

    queue_resume_if_needed()
