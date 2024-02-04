from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from decouple import config
import torch
from pathlib import Path
from openai import OpenAI
import logging
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# konfiguracja logów
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ścieżka do audio
speech_file_path = Path(__file__).parent / "speech.mp3"

# inicjalizacja OpenAI
openai_api_key = ""
openai_client = OpenAI(api_key=openai_api_key)

# inicjalizacja facebook/blenderbot-400M-distill
tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

#inicjalizacja m2m100
model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Witaj! Zaczynamy rozmowę.")

def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Do zobaczenia!")
    updater.stop()
    
def translate_text_pl_fr(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = model.generate(**model_inputs, forced_bos_token_id=tokenizer.get_lang_id("fr"))
    
    translated_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
    
def translate_text_fr_pl(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = model.generate(**model_inputs, forced_bos_token_id=tokenizer.get_lang_id("fr"))
    
    translated_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
        
def translate_text_en_pl(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    tokenizer.src_lang = "en"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = model.generate(**model_inputs, forced_bos_token_id=tokenizer.get_lang_id("pl"))
    
    translated_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
    
    
def translate_text_pl_en(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = model.generate(**model_inputs, forced_bos_token_id=tokenizer.get_lang_id("en"))
    
    translated_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])

    
def generate_response(user_input):
    # Tokenize the user input
    input_ids = tokenizer.encode(user_input, return_tensors="pt")

    # Generate response from the model
    with torch.no_grad():
        output = model.generate(input_ids)

    # Decode and return the generated response
    response = tokenizer.decode(output[0], skip_special_tokens=True)
    return response


def generate_speech(update, context):
    # Pobieranie tekstu z wiadomości
    user_text = " ".join(context.args)

    # Generowanie mowy OpenAI
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=user_text
    )

    # Zapis odpowiedzi do pliku audio
    response.stream_to_file(speech_file_path)

    # Wysyłanie pliku audio do użytkownika
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
    
def generate_translate_speech_pl_en(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka angielskiego
    gen_tokens = model.generate(**model_inputs, forced_bos_token_id=tokenizer.get_lang_id("en"))
    
    translated_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
    
    # Generowanie mowy OpenAI
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=translated_text[0]
    )
    
    
    response.stream_to_file(speech_file_path)
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
def generate_translate_speech_enpl(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    tokenizer.src_lang = "en"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka polskiego
    gen_tokens = model.generate(**model_inputs, forced_bos_token_id=tokenizer.get_lang_id("pl"))
    
    translated_text = tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
    
    # Generowanie mowy OpenAI
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=translated_text[0]
    )

    response.stream_to_file(speech_file_path)
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
    
def generate_speech_response(update, context):
    # Pobieranie tekstu z wiadomości
    user_text = " ".join(context.args)

    # Generowanie odpowiedzi tekstowej z modelu Blenderbot
    response_text = generate_response(user_text)

    # Generowanie mowy OpenAI na podstawie odpowiedzi tekstowej
    response_audio = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=response_text
    )

    # Zapis odpowiedzi do głosówki
    response_audio.stream_to_file(speech_file_path)

    # Wysyłanie głosówki do użytkownika
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))

def echo(update, context):
    user_input = update.message.text
    response = generate_response(user_input)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)
    
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
    
    # obsługa wiadomości głosowych generowanych przez blenderbot
    dp.add_handler(CommandHandler("bspeach", generate_speech_response))
    
    # obsługa tłumaczenia z polskiego na francuski
    dp.add_handler(CommandHandler("translate_plfr", translate_text_pl_fr))
    
     # obsługa tłumaczenia z francuskiego na polski
    dp.add_handler(CommandHandler("translate_frpl", translate_text_fr_pl))
    
     # obsługa tłumaczenia z polskiego na angielski
    dp.add_handler(CommandHandler("translate_plen", translate_text_pl_en))
    
     # obsługa tłumaczenia z angielskiego na polski
    dp.add_handler(CommandHandler("translate_enpl", translate_text_en_pl))
    
      # obsługa tłumaczenia głosowego z polskiego na angielski
    dp.add_handler(CommandHandler("speach_translate_plen",  generate_translate_speech_pl_en))
    
     # obsługa tłumaczenia głosowego z polskiego na angielski
    dp.add_handler(CommandHandler("speach_translate_enpl", generate_translate_speech_enpl))
    
    # nasłuchiwanie wiadomości
    updater.start_polling()

    # bot działa aż do ręcznego zatrzymania
    updater.idle()

if __name__ == '__main__':
    main()
