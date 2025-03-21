import logging

from django.utils import timezone

from ..models import Reminder, Notification

logger = logging.getLogger('scheduler')


def process_reminders_and_create_notifications():
    reminders = Reminder.objects.filter(time__lte=timezone.now(), sent_at__isnull=True)
    if len(reminders) > 0:
        logger.info("Rozpoczęcie zadania reminder_dispatcher")
        for reminder in reminders:
            Notification.objects.create(
                user=reminder.user,
                type='reminder',
                title=reminder.title,
                message=reminder.content
            )
            logger.info("Notification created")
            reminder.sent_at = timezone.now()
            reminder.save()
        logger.info("Zakończenie zadania create_notifications")

