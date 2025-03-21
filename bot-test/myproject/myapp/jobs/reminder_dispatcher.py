import logging
from datetime import timedelta

import requests

from ..models import Reminder

logger = logging.getLogger('scheduler')
from django.utils import timezone

from decouple import config

slack_bot_token = config("SLACK_BOT_TOKEN")
telegram_bot_token = config("TELEGRAM_API_KEY")
DISCORD_TOKEN = config("DISCORD_TOKEN")


def send_discord_message(channel_id, content):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    headers = {
        "Authorization": f"Bot {DISCORD_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"content": content}

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Wiadomość wysłana pomyślnie:", response.json())
    else:
        logger.exception("Błąd podczas wysyłania:", response.status_code, response.text)


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    logger.info("Wysłano wiadomość:", response.json())


def send_slack_message(channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_bot_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": "Przypomnienie: " + text
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        logger.info("Wysłano wiadomość:", response.json())
    else:
        logger.exception("Błąd podczas wysyłania wiadomości:", response.status_code, response.text)


def send_to_bot(platform, target, content):
    if platform == 'Slack':
        send_slack_message(target, content)
    elif platform == 'Telegram':
        send_telegram_message(target, content)
    elif platform == 'Discord':
        send_discord_message(target, content)


def mark_as_sent(reminder):
    reminder.sent_at = timezone.now()
    reminder.save()


def delete_old_reminders():
    cutoff = timezone.now() - timedelta(days=7)
    Reminder.objects.filter(sent_at__isnull=False, sent_at__lt=cutoff).delete()


def reminder_dispatcher():
    reminders = Reminder.objects.filter(time__lte=timezone.now(), sent_at__isnull=True, channel__isnull=False)
    if len(reminders) > 0:
        logger.info("Rozpoczęcie zadania reminder_dispatcher")
        for reminder in reminders:
            try:
                send_to_bot(reminder.channel.platform.name, reminder.channel.channel_id, reminder.content)
                mark_as_sent(reminder)
                logger.info(f"Wysłano przypomnienie: {reminder.content} na {reminder.channel.platform.name} -> {reminder.channel.name}")
            except Exception as e:
                logger.error(f"Błąd podczas wysyłania przypomnienia: {reminder.content}, błąd: {e}")

        delete_old_reminders()
        logger.info("Zakończenie zadania reminder_dispatcher")
