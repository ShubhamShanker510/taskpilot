# from __future__ import absolute_import
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskpilot.settings')
app = Celery('taskpilot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule={
    'send-task-reminders-daily':{
        'task':'tasks.tasks.send_due_soon_reminders',
        'schedule': crontab(minute='*/1')
    }
}