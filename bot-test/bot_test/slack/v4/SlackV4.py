import os
import sys

from CreateTask import *
from qdrant import *
from reminder import *

SLACK_APP_TOKEN = config("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = config("SLACK_BOT_TOKEN")

app = App(token=SLACK_BOT_TOKEN)
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}  # Modify this as needed

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@app.message("!searchfile")
def search_file_command(ack, say, message):
    query = message.get('text', '')
    result = search_file(query)
    say(result)
    ack()


@app.message("!getfile")
def get_file(ack, say, message):
    handle_get_file(ack, say, message)


@app.message("!bot")
def handle_bot_commands(message, say):
    # Pobierz pełny tekst wiadomości
    command_text = message['text']

    # Usuń prefix "!bot"
    command_args = command_text[5:].strip()  # Usuwamy "!bot " z początku

    # Rozdziel pierwsze słowo (komendę) od reszty
    parts = command_args.split(' ', 1)
    command = parts[0].lower()  # Komenda (np. "utwórz")
    args = parts[1] if len(parts) > 1 else ""  # Argumenty (np. "przypomnienie")

    # Obsługa komend
    if command == "utwórz":
        handle_create_command(args, message, say)
    elif command == "pokaż":
        handle_show_command(args, message, say)
    else:
        say(f"Nieznana komenda: {command}. Dostępne komendy: `utwórz`, `pokaż`.")


def handle_create_command(args, message, say):
    if args.startswith("przypomnienie"):
        create_reminder_flow(message, say)
    elif args.startswith("zadanie"):
        checkPattern(message, say)
    else:
        say("Nie rozumiem, co chcesz utworzyć. Użyj `przypomnienie` lub `zadanie`.")


def handle_show_command(args, message, say):
    if args.startswith("zadania"):
        show_tasks(message, say)
    else:
        say(f"Nie rozumiem, co chcesz pokazać. Użyj `zadania`.")


def show_tasks(message, say):
    say("Oto lista zadań: ...")


# Reminder functions
@app.action("select_time")
def action_select_time(ack, body):
    handle_time_selection(ack, body)


@app.action("select_date")
def action_select_date(ack, body):
    handle_date_selection(ack, body)


@app.action("content_input")
def action_content_input(ack, body):
    handle_content_input(ack, body)


@app.action("confirm_reminder")
def handle_confirm_reminder(ack, body, say):
    handle_confirm_reminder_2(ack, body, say)


@app.event("message")
def handle_message(body, say):
    event = body.get("event", {})

    if 'files' in event:
        handle_file_message_events(event, say)


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)  # App-Level Token
    handler.start()
