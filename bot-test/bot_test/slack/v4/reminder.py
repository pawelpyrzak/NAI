from datetime import datetime

from bot_test.bot_config.db_config import *

# Przechowywanie danych w trakcie sesji
temp_data = {}


def save_reminder_to_db(user_id, selected_date, selected_hour, selected_minute, content, target, platform_id):
    conn = get_db_connection2()
    cursor = conn.cursor()

    # Formatujemy datę i godzinę
    reminder_time = f"{selected_date} {selected_hour}:{selected_minute}:00"
    reminder_time = datetime.strptime(reminder_time, "%Y-%m-%d %H:%M:%S")

    # Zapisz przypomnienie do tabeli
    cursor.execute(
        """
        INSERT INTO reminders (user_id, time, content, target, platform)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (user_id, reminder_time, content, target, "slack")
    )

    conn.commit()
    cursor.close()
    conn.close()


def create_reminder_flow(message, say):
    user_id = message["user"]

    # Initialize temporary data for the user
    temp_data[user_id] = {}

    say(
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Wypełnij formularz przypomnienia."}
            },
            {
                "type": "input",
                "block_id": "content_block",
                "label": {
                    "type": "plain_text",
                    "text": "Opis przypomnienia",
                    "emoji": True
                },
                "optional": False,
                "element": {
                    "type": "plain_text_input",
                    "action_id": "content_input",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Wpisz opis przypomnienia",
                        "emoji": True
                    }
                }
            },
            {
                "type": "input",
                "block_id": "time_block",
                "element": {
                    "type": "timepicker",
                    "action_id": "select_time",
                    "placeholder": {"type": "plain_text", "text": "Wybierz godzinę"},
                    "initial_time": "12:00"
                },
                "label": {"type": "plain_text", "text": "Godzina przypomnienia"}
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "datepicker",
                        "action_id": "select_date",
                        "placeholder": {"type": "plain_text", "text": "Wybierz datę"}
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Potwierdź"},
                        "action_id": "confirm_reminder",
                        "style": "primary"
                    }
                ]
            }
        ]
    )

def handle_content_input(ack, body):
    ack()
    print("content_input")
    user_id = body["user"]["id"]
    content = body["actions"][0]["value"]
    print(f"DEBUG: Content entered by user: {content}")  # Debugowanie
    if user_id not in temp_data:
        temp_data[user_id] = {}
    temp_data[user_id]["content"] = content

# Obsługa wyboru daty
def handle_date_selection(ack, body):
    ack()
    print("select_date")
    user_id = body["user"]["id"]
    selected_date = body["actions"][0]["selected_date"]
    if user_id not in temp_data:
        temp_data[user_id] = {}
    temp_data[user_id]["date"] = selected_date


# Obsługa wyboru godziny
def handle_time_selection(ack, body):
    ack()
    user_id = body["user"]["id"]
    print("select_time")
    selected_time = body["actions"][0]["selected_time"]
    if user_id not in temp_data:
        temp_data[user_id] = {}
    temp_data[user_id]["time"] = selected_time


def handle_confirm_reminder_2(ack, body, say):
    ack()
    user_id = body["user"]["id"]
    channel_id = body["channel"]["id"]
    # print(json.dumps(body, indent=2))  # Zobacz całą strukturę body w logach
    # Retrieve temporary data
    user_data = temp_data.get(user_id, {})
    selected_date = user_data.get("date")
    selected_time = user_data.get("time")
    content = user_data.get("content", "Brak opisu")
    platform_id = 1  # Slack platform ID
    print(content)
    print(selected_date)
    print(selected_time)
    if selected_date and selected_time:
        selected_hour, selected_minute = map(int, selected_time.split(":"))

        # Save to database
        save_reminder_to_db(user_id, selected_date, selected_hour, selected_minute, content, channel_id, platform_id)

        # Send confirmation
        say(
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Przypomnienie utworzone!*\n\n"
                                f"• *Data:* {selected_date}\n"
                                f"• *Godzina:* {selected_time}\n"
                                f"• *Opis:* {content}\n"
                                f"• *Kanał docelowy:* <#{channel_id}>\n"
                                f"• *Platforma:* Slack"
                    }
                }
            ]
        )

        # Clear temporary data
        del temp_data[user_id]
    else:
        say("Najpierw wybierz datę i godzinę, zanim potwierdzisz przypomnienie.")