# import time
# import re
# from apscheduler.schedulers.background import BackgroundScheduler
# from slack_sdk import WebClient as SlackClient
# from telegram import Bot as TelegramBot
# from telegram.ext import Updater, CommandHandler
#
# # Twój token Slacka i Telegrama
# SLACK_TOKEN = 'xoxb-XXXXXXXXXXXX-XXXXXXXXXXXX-XXXXXXXXXXXXXXXXXXXXXXXX'
# TELEGRAM_TOKEN = 'XXXXXXXXXXXXXX:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
#
# # Inicjalizacja klientów
# slack_client = SlackClient(token=SLACK_TOKEN)
# telegram_client = TelegramBot(token=TELEGRAM_TOKEN)
#
# # Inicjalizacja harmonogramu
# scheduler = BackgroundScheduler()
# scheduler.start()
#
# # Funkcja wysyłająca przypomnienie do Slacka
# def send_slack_reminder(user_id, reminder_text):
#     try:
#         response = slack_client.chat_postMessage(
#             channel=user_id,
#             text=f"Przypomnienie: {reminder_text} 😊"
#         )
#         print(f"Wiadomość wysłana do Slacka: {response['message']['text']}")
#     except Exception as e:
#         print(f"Błąd wysyłania wiadomości do Slacka: {str(e)}")
#
# # Funkcja wysyłająca przypomnienie do Telegrama
# def send_telegram_reminder(chat_id, reminder_text):
#     try:
#         telegram_client.send_message(chat_id=chat_id, text=f"Przypomnienie: {reminder_text} 😊")
#         print(f"Wiadomość wysłana do Telegrama: {reminder_text}")
#     except Exception as e:
#         print(f"Błąd wysyłania wiadomości do Telegrama: {str(e)}")
#
# # Funkcja parsująca czas
# def parse_time(time_str):
#     match = re.match(r"(\d+)([smhd])", time_str)
#     if match:
#         value = int(match.group(1))
#         unit = match.group(2)
#
#         # Konwersja na sekundy
#         if unit == "s":
#             return value
#         elif unit == "m":
#             return value * 60
#         elif unit == "h":
#             return value * 3600
#         elif unit == "d":
#             return value * 86400
#     return None
#
# # Funkcja ustawiająca przypomnienie
# def schedule_reminder(platform, user_id, reminder_text, time_str):
#     delay_seconds = parse_time(time_str)
#     if delay_seconds is None:
#         print("Niepoprawny format czasu!")
#         return
#
#     if platform == 'slack':
#         scheduler.add_job(
#             send_slack_reminder, 'date', run_date=time.time() + delay_seconds,
#             args=[user_id, reminder_text]
#         )
#     elif platform == 'telegram':
#         scheduler.add_job(
#             send_telegram_reminder, 'date', run_date=time.time() + delay_seconds,
#             args=[user_id, reminder_text]
#         )
#     else:
#         print("Nieobsługiwana platforma")
#
#     print(f"Przypomnienie na {platform} zostało zaplanowane na {time_str}.")
#
# # Funkcja interakcyjna z użytkownikiem
# def prompt_user_input():
#     platform = input("Wybierz platformę (slack/telegram): ").lower()
#     user_id = input("Podaj ID użytkownika lub chat ID: ")
#     reminder_text = input("Wpisz tekst przypomnienia: ")
#     time_str = input("Podaj czas w formacie (np. 10m, 2h, 1d): ")
#
#     schedule_reminder(platform, user_id, reminder_text, time_str)
#
# # Uruchomienie programu
# while True:
#     prompt_user_input()
#     time.sleep(1)
