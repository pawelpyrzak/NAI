import atexit
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver


logger = logging.getLogger('scheduler')


class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from .jobs.reminder_dispatcher import reminder_dispatcher
        from .jobs.create_notifications import process_reminders_and_create_notifications
        from .jobs.jira_task_update import update_or_create_tasks_from_jira

        scheduler = BackgroundScheduler()
        # scheduler.add_job(reminder_dispatcher, 'interval', minutes=1)
        # scheduler.add_job(process_reminders_and_create_notifications, 'interval', minutes=1)
        scheduler.add_job(update_or_create_tasks_from_jira, 'interval', minutes=1)

        scheduler.start()
        atexit.register(lambda: scheduler.shutdown(wait=False))


@receiver(post_migrate)
def create_default_platforms(sender, **kwargs):
    from .models import Platform
    from .models import ProjectPlatform
    default_platforms = [
        {'name': 'Slack'},
        {'name': 'Discord'},
        {'name': 'Telegram'},
    ]
    default_platforms2 = [
        {'name': 'Jira'},
    ]
    for platform_data in default_platforms:
        Platform.objects.get_or_create(name=platform_data['name'], defaults=platform_data)

    for platform_data in default_platforms2:
        ProjectPlatform.objects.get_or_create(name=platform_data['name'], defaults=platform_data)
