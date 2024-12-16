import logging
import os
import re
import requests
import sys
import uuid
from decouple import config
from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot_test.bot_config.methods import *

SLACK_APP_TOKEN = config("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = config("SLACK_BOT_TOKEN")


app = App(token=SLACK_BOT_TOKEN, name="Joke Bot")
logger = logging.getLogger(__name__)

client = WebClient(token=config("SLACK_BOT_TOKEN"))


@app.message("!hello")
def message_hello(message, say):
    user = message['user']
    say(f"Hello there, <@{user}>!")


@app.event("app_mention")
def handle_app_mention_events(body, say):
    user = body['event']['user']
    text = body['event']['text']

    # Respond to the mention
    say(f"Hello <@{user}>, you mentioned me saying: '{text}'")


@app.message(re.compile("^!start$", re.IGNORECASE))
def handle_start_command(message, say):
    channel_id = message['channel']

    try:
        response = client.conversations_info(channel=channel_id)
        channel_info = response['channel']

        if not channel_info.get('is_im'):
            channel_name = channel_info.get('name')
            say(save_chat_to_db(channel_id, channel_name))

    except SlackApiError as e:
        print(f"Błąd: {e.response['error']}")


@app.event("message")
def handle_file_message_events(body, say):
    event = body.get("event", {})

    if 'files' in event:
        chat_id = event['channel']
        files = event['files']

        for file in files:
            file_id = file['id']
            file_name = file['name']

            # Display confirmation buttons before saving the file
            say(
                text=f"Would you like to save the file '{file_name}'?",
                blocks=[
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Would you like to save the file '{file_name}'?*"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "Yes"},
                                "value": f"{file_id}:{file_name}:{chat_id}",
                                "action_id": "save_file_yes"
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": "No"},
                                "value": file_id,
                                "action_id": "save_file_no"
                            }
                        ]
                    }
                ]
            )


def update_message(channel_id, ts, confirmation_text):
    client.chat_update(
        channel=channel_id,
        ts=ts,
        text=confirmation_text,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": confirmation_text}
            }
        ]
    )


@app.action("save_file_yes")
def handle_save_file_yes(ack: Ack, body, say):
    ack()
    value = body['actions'][0]['value']
    file_id, file_name, chat_id = value.split(":")

    try:
        # Get detailed file information
        file_info_response = client.files_info(file=file_id)
        file_url = file_info_response['file']['url_private_download']

        # Download the file
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        download_response = requests.get(file_url, headers=headers)

        if download_response.status_code == 200:
            file_content = download_response.content
            save_file_to_db(file_name, file_content, chat_id)
            confirmation_text = f"File '{file_name}' has been saved to the database!"
        else:
            confirmation_text = f"Error downloading the file: {download_response.status_code}"

    except SlackApiError as e:
        logger.error(f"Slack API Error: {e.response['error']}")
        confirmation_text = f"Error processing the file: {e.response['error']}"

    update_message(body['channel']['id'], body['message']['ts'], confirmation_text)


# Handle "No" button click to discard the file
@app.action("save_file_no")
def handle_save_file_no(ack: Ack, body, say):
    ack()
    update_message(body['channel']['id'], body['message']['ts'], "The file was not saved.")


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
