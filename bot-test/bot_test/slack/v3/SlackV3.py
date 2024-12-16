from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from bot_test.slack.v3.callFunctions import *
from bot_test.slack.v3.intentDetector import *

SLACK_APP_TOKEN = config("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = config("SLACK_BOT_TOKEN")
app = App(token=SLACK_BOT_TOKEN)


# Obsługa wiadomości z Slacka
@app.message("")
def handle_message(message, say, client):
    user_message = message["text"]
    loading_message = say(
        text="Pracuję nad odpowiedzią...",  # Fallback text
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Pracuję nad odpowiedzią... :hourglass_flowing_sand:"}
            }
        ]
    )["ts"]
    intent = detect_intent(user_message,0.6)
    if intent == "todayTasks":
        response = get_tasks_for_today()
    elif intent == "upcomingTasks":
        response = get_upcoming_tasks()
    elif intent == "upcomingMeetings":
        response = get_static_meetings()
    elif intent == "TodayMeetings":
        response = get_meetings_for_today()
    elif intent == "scheduleToday":
        response = get_schedule_for_today()
    else:
        response = "Nie rozumiem wiadomości"
    # Finalna odpowiedź
    client.chat_update(
        channel=message["channel"],
        ts=loading_message,
        text=response,  # Fallback text
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"{response}"}
            }
        ]
    )


# Uruchomienie aplikacji Slack w trybie socket mode
if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
