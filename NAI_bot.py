from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from decouple import config
import torch
from pathlib import Path
from openai import OpenAI
import logging

# konfiguracja logów
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ścieżka do audio
speech_file_path = Path(__file__).parent / "speech.mp3"

# inicjalizacja OpenAI
openai_api_key = config("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

# inicjalizacja facebook/blenderbot-400M-distill
tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Witaj! Zaczynamy rozmowę.")

def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Do zobaczenia!")
    updater.stop()

def generate_response(user_input):
    # Tokenize the user input
    input_ids = tokenizer.encode(user_input, return_tensors="pt")

    # Generate response from the model
    with torch.no_grad():
        output = model.generate(input_ids)

    # Decode and return the generated response
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response

def echo(update, context):
    user_input = update.message.text
    response = generate_response(user_input)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

def generate_speech(update, context):
    # Pobieranie tekstu z wiadomości
    user_text = " ".join(context.args)

    # Generowanie mowy OpenAI
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=user_text
    )

    # Zapis odpowiedzi do głosówki
    response.stream_to_file(speech_file_path)

    # Wysyłanie głosówki do użytkownika
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))

def main():
    telegram_bot_token = config("TELEGRAM_API_KEY")
    global updater
    updater = Updater(token=telegram_bot_token, use_context=True)

    dp = updater.dispatcher

    # komendy start/stop
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    # obsługa wiadomości tekstowych
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # obsługa wiadomości głosowych
    dp.add_handler(CommandHandler("speech", generate_speech))

    # nasłuchiwanie wiadomości
    updater.start_polling()

    # bot działa aż do ręcznego zatrzymania
    updater.idle()

if __name__ == '__main__':
    main()
