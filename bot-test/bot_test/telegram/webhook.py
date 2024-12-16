# from telegram import Update
# from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
# from decouple import config
# import logging
#
# # Enable logging
# logging.basicConfig(
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     level=logging.INFO
# )
# logger = logging.getLogger(__name__)
#
# # Webhook URL and bot token
# WEBHOOK_URL = "https://angry-melons-crash.loca.lt/weebhook"
# telegram_bot_token = config("TELEGRAM_API_KEY")
#
# # Initialize the Telegram bot application
# app = ApplicationBuilder().token(telegram_bot_token).build()
#
# # Set up the webhook and run the application in webhook mode
# app.run_webhook(
#     listen="0.0.0.0",          # Listen on all network interfaces
#     port=5000,                 # Port to listen on
#     webhook_url=WEBHOOK_URL    # Webhook URL for Telegram
# )

import requests
from decouple import config

# Replace with your bot token
YOUR_BOT_TOKEN = config("TELEGRAM_API_KEY")
WEBHOOK_URL = "https://angry-melons-crash.loca.lt/weebhook"

# Construct the URL for setting the webhook
url = f"https://api.telegram.org/bot{YOUR_BOT_TOKEN}/setWebhook?url={WEBHOOK_URL}"

# Send the GET request to set the webhook
response = requests.get(url)

# Read and print the JSON response
json_response = response.json()

# Print the response in a readable format
print(json_response)