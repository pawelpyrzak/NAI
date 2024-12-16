from telegram.ext import Application, CommandHandler, ContextTypes
from decouple import config
import asyncio
import requests
import nest_asyncio

telegram_bot_token = config("TELEGRAM_API_KEY")

WEBHOOK_URL = "https://angry-melons-crash.loca.lt/weebhook"

# Funkcja obsługująca /start
async def start(update, context):
    await update.message.reply_text("Hello! I'm running")

async def after_polling_start(application):
    print("Bot has started! Performing post-startup tasks...")
    await asyncio.sleep(5)  # Przykład działania
    await application.bot.delete_webhook()
    print("Post-startup tasks completed.")
    url = f"https://api.telegram.org/bot{telegram_bot_token}/setWebhook?url={WEBHOOK_URL}"
    response = requests.get(url)
    json_response = response.json()
    print(json_response)
    print("Bot is fully running, and additional code is executing now.")



async def run_bot():
    # Tworzenie aplikacji
    application = Application.builder().token(telegram_bot_token).build()
    # Dodawanie handlerów
    application.add_handler(CommandHandler("start", start))

    # Funkcja dodatkowa uruchamiana po starcie polling
    asyncio.create_task(after_polling_start(application))

    # Uruchamianie polling
    application.run_polling()

if __name__ == "__main__":
    nest_asyncio.apply()
    try:
        asyncio.get_event_loop().run_until_complete(run_bot())
    except RuntimeError as e:
        print(f"Runtime error: {e}")