from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from decouple import config
import torch
from pathlib import Path
from openai import OpenAI
import logging
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import assemblyai as aai

# konfiguracja logów
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ścieżka do audio
speech_file_path = Path(__file__).parent / "speech.mp3"

# inicjalizacja OpenAI
openai_api_key = ""
openai_client = OpenAI(api_key=openai_api_key)

# inicjalizacja facebook/blenderbot-400M-distill
blender_bot_tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
blender_bot_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

#inicjalizacja m2m100
m2m100_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
m2m100_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

#inicjalizacja assemblyai
aai.settings.api_key = ""
transcriber = aai.Transcriber()

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Witaj! Zaczynamy rozmowę.")

def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Do zobaczenia!")
    updater.stop()
    
def transcription(update, context):    
# Pobierz plik audio z wiadomości głosowej
    voice_message = update.message.voice
    file_id = voice_message.file_id
    file = context.bot.get_file(file_id)
    file_path = file.file_path

    # pobieranie nazwy użytkownika
    user_name = update.effective_user.username
    
    # Pobierz transkrypcję za pomocą assemblyai
    transcript = transcribe_audio(file_path)


    # Wyślij transkrypcję do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user_name} nagrał wiadomość głosową: {transcript}")

def transcribe_audio(audio_file_path):
    # Utwórz instancję transkrybera z użyciem assemblyai
    transcriber = aai.Transcriber()

    # Pobierz transkrypcję z pliku audio
    transcript = transcriber.transcribe(audio_file_path)

    return transcript.text
    
def translate_text_pl_fr(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("fr"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
    
def translate_text_fr_pl(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("fr"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
        
def translate_text_en_pl(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "en"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("pl"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
    
    
def translate_text_pl_en(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("en"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])

    
def generate_response(update, context):
    # Extract user input from the update
    user_input = update.message.text
    
    if user_input.startswith('/conv'):
        user_input = ' '.join(user_input.split(' ')[1:]).strip()

    # Rest of your code to generate the response
    input_ids = blender_bot_tokenizer.encode(user_input, return_tensors="pt")
    
    with torch.no_grad():
        output = blender_bot_model.generate(input_ids)

    response = blender_bot_tokenizer.decode(output[0], skip_special_tokens=True)

    # Send the generated response back to the user
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

    # Zapis odpowiedzi do pliku audio
    response.stream_to_file(speech_file_path)

    # Wysyłanie pliku audio do użytkownika
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
def generate_speech_response(update, context):
    user_input = update.message.text
    # ignorowanie /bspeach jako wiadomość do modelu
    if user_input.startswith('/bspeach'):
        user_input = ' '.join(user_input.split(' ')[1:]).strip()

    # generowanie odpowiedzi tekstowej z modelu Blender
    input_ids = blender_bot_tokenizer.encode(user_input, return_tensors="pt")
    
    with torch.no_grad():
        output = blender_bot_model.generate(input_ids)

    response_text = blender_bot_tokenizer.decode(output[0], skip_special_tokens=True)


    # generowanie mowy OpenAI na podstawie odpowiedzi Blendera
    response_audio = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=response_text
    )

    # zapis odpowiedzi do głosówki
    response_audio.stream_to_file(speech_file_path)

    # wysyłanie głosówki do użytkownika
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
def generate_translate_speech_pl_en(update, context):
    # Pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # Ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka angielskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("en"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
    
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
    m2m100_tokenizer.src_lang = "en"

    # Tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # Ustawienie forced_bos_token_id dla języka polskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("pl"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
    
    # Generowanie mowy OpenAI
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=translated_text[0]
    )

    response.stream_to_file(speech_file_path)
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
     
def main():
    telegram_bot_token = config("TELEGRAM_API_KEY")
    global updater
    updater = Updater(token=telegram_bot_token, use_context=True)

    dp = updater.dispatcher

    # komendy start/stop
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    
    # obsługa transkrypcji wiadomości głosowej
    dp.add_handler(MessageHandler(Filters.voice & ~Filters.command, transcription))

    # obsługa wiadomości głosowych
    dp.add_handler(CommandHandler("speech", generate_speech))
    
    # obsługa konwersacji z botem
    dp.add_handler(CommandHandler("conv", generate_response))

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
