from datetime import datetime, timedelta

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from decouple import config
from psycopg2.extras import RealDictCursor

from db_config import get_db_connection2

slack_bot_token = config("SLACK_BOT_TOKEN")
telegram_bot_token = config("TELEGRAM_BOT_TOKEN")
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
        print("Wiadomość wysłana pomyślnie:", response.json())
    else:
        print("Błąd podczas wysyłania:", response.status_code, response.text)


def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{telegram_bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, json=payload)
    print("Wysłano wiadomość:", response.json())


def send_slack_message(channel, text):
    url = "https://slack.com/api/chat.postMessage"
    headers = {
        "Authorization": f"Bearer {slack_bot_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "channel": channel,
        "text": "przypomninie: " + text
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        print("Wysłano wiadomość:", response.json())
    else:
        print("Błąd podczas wysyłania wiadomości:", response.status_code, response.text)


# Pobieranie przypomnień gotowych do wysłania
def get_pending_reminders():
    conn = get_db_connection2()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    now = datetime.now()
    cursor.execute("SELECT * FROM reminders WHERE time <= %s AND sent_at IS NULL", (now,))
    reminders = cursor.fetchall()
    conn.close()
    return reminders


# Wysyłanie danych do odpowiednich botów
def send_to_bot(platform, target, content):
    if platform == 'slack':
        send_slack_message(target, content)
    elif platform == 'telegram':
        send_telegram_message(target, content)
    elif platform == 'discord':
        send_discord_message(target, content)


# Aktualizacja statusu przypomnienia po wysłaniu
def mark_as_sent(reminder_id):
    conn = get_db_connection2()
    cursor = conn.cursor()
    now = datetime.now()
    cursor.execute("UPDATE reminders SET sent_at = %s WHERE id = %s", (now, reminder_id))
    conn.commit()
    conn.close()


def delete_old_reminders():
    conn = get_db_connection2()
    cursor = conn.cursor()
    cutoff = datetime.now() - timedelta(days=1)
    cursor.execute("DELETE FROM reminders WHERE sent_at IS NOT NULL AND sent_at < %s", (cutoff,))
    conn.commit()
    conn.close()


# Główna funkcja schedulera
def scheduler_task():
    print("start scheduler task")
    reminders = get_pending_reminders()
    for reminder in reminders:
        send_to_bot(reminder['platform'], reminder['target'], reminder['content'])
        mark_as_sent(reminder['id'])
        print(f"Sent reminder: {reminder['content']} to {reminder['platform']} -> {reminder['target']}")
    delete_old_reminders()
    print("end scheduler task")


# Uruchomienie schedulera
if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(scheduler_task, 'interval', minutes=5)
    scheduler_task()
    scheduler.start()
