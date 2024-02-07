from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from decouple import config
import torch
from pathlib import Path
from openai import OpenAI
import logging
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
import assemblyai as aai
from transformers import pipeline
from telegram import Update, ParseMode


# konfiguracja logów
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# słowa zablokowane
blocked_words = ['cat', 'block', 'test']
user_bad_word_count = {}

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
    help_command(update, context)

def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="See you later!")
    updater.stop()
    
# funkcja wysyłająca wiadomość
def send_message(update, context, text):
    return context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)

def save_all_messages(update, context):
    context.user_data.setdefault('all_messages', []).append(update.message.text)
    block_words(update, context)  # sprawdzenie słów blokowanych po zapisaniu wiadomości    
    
# funkcja generująca streszczenie za pomocą transformers
def generate_summary(update, context, text):
    summarization = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # dzielenie tekstu na fragmenty aby nie przekroczyć limitu rozmiau wiadomości
    chunks = [text[i:i + 4096] for i in range(0, len(text), 4096)]
    
    # generowanie podsumowań dla każdego fragmentu
    summaries = [summarization(chunk)[0]['summary_text'] for chunk in chunks]
    
    # łączenie podsumowań
    result_summary = ' '.join(summaries)
    
    return result_summary    

def summary(update, context):
    # pobieranie tekstu do streszczenia
    text_to_summarize = ' '.join(context.args) if context.args else ' '.join(context.user_data.get('all_messages', []))
    if text_to_summarize:
        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")

        
        summary_result = generate_summary(update, context, text_to_summarize)

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        if message_sent:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # wysłanie wyniku streszczenia
        send_message(update, context, f"Summary: {summary_result}")
    else:
        send_message(update, context,
                     "Provide text for summary after command /summary, "
                     "or use /summary_previous_one to summarize the previous message, "
                     "or /summary_previous_n to summarize the last N messages.")
        
def summary_speech(update, context):
    # pobieranie tekstu do streszczenia
    text_to_summarize = ' '.join(context.args) if context.args else ' '.join(context.user_data.get('all_messages', []))
    if text_to_summarize:
        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")

        
        summary_result = generate_summary(update, context, text_to_summarize)

        # generowanie mowy OpenAI na podstawie streszczenia
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=summary_result
        )
        
        # zapis odpowiedzi do pliku audio
        response.stream_to_file(speech_file_path)

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # wysłanie pliku audio do użytkownika
        context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))

    else:
        send_message(update, context,
                     "Provide the text for the summary after the /summary command, "
                     "or use /summary_previous_one to summarize the previous message, "
                     "or /summary_previous_n to summarize the last N messages.")

# funkcja streszczająca poprzednią wiadomość
def summary_previous_one(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")

        summary_result = generate_summary(update, context, all_messages[-1])

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        send_message(update, context, f"Summary of previous message: {summary_result}")
    else:
        send_message(update, context, "No past messages available for summary..")

def summary_previous_one_speech(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")
        
        # streszczenie ostatniej wiadomości
        summary_result = generate_summary(update, context, all_messages[-1])

        # generowanie mowy OpenAI na podstawie streszczenia
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=summary_result
        )
    
        # zapis odpowiedzi do pliku audio
        response.stream_to_file(speech_file_path)

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # wysłanie pliku audio do użytkownika
        context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    else:
        send_message(update, context, "No past messages available for summary..")   

# funkcja streszczająca ostatnie N wiadomości
def summary_previous_n(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages and context.args and context.args[0].isdigit():
        n = int(context.args[0])

        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")

        text_to_summarize = ' '.join(all_messages[-n:])
        summary_result = generate_summary(update, context, text_to_summarize)

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        send_message(update, context, f"Summary of recent{n} past messages: {summary_result}")
    else:
        send_message(update, context, "Specify the number of messages to summarize after the /summary_previous_n command.")

def summary_previous_n_speech(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages and context.args and context.args[0].isdigit():
        n = int(context.args[0])
        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")

        text_to_summarize = ' '.join(all_messages[-n:])
        summary_result = generate_summary(update, context, text_to_summarize) 
        
        # generowanie mowy OpenAI na podstawie streszczenia
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=summary_result
        )
        
        # zapis odpowiedzi do pliku audio
        response.stream_to_file(speech_file_path)

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # wysłanie pliku audio do użytkownika
        context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    else:
        send_message(update, context, "No past messages available for summary..")   
        
# funkcja streszczająca wszystkie zapisane wiadomości
def summary_all(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")

        text_to_summarize = ' '.join(all_messages)
        summary_result = generate_summary(update, context, text_to_summarize)

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        send_message(update, context, f"Summary of all saved messages: {summary_result}")
    else:
        send_message(update, context, "No saved messages to summarize.")
        
def summary_all_speech(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Summary in process please wait")

        text_to_summarize = ' '.join(all_messages)
        summary_result = generate_summary(update, context, text_to_summarize)
        
        # generowanie mowy OpenAI na podstawie streszczenia
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=summary_result
        )
        # zapis odpowiedzi do pliku audio
        response.stream_to_file(speech_file_path)

        # usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # wysłanie pliku audio do użytkownika
        context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    else:
        send_message(update, context, "No past messages available for summary..") 
        
# blokowanie wiadomości zawierające zablokowane słowa
def block_words(update, context):
    message_text = update.message.text.lower()

    if any(word in message_text.split() for word in blocked_words):
        user_id = update.effective_user.id
        user_bad_word_count[user_id] = user_bad_word_count.get(user_id, 0) + 1

        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

        context.bot.send_message(chat_id=update.effective_chat.id,
        text=f'The message contains a blocked word. Please avoid using such words.\n'
        f'Number of bad words:{user_bad_word_count[user_id]}')
        if user_bad_word_count[user_id] >= 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
            text=f'User {update.effective_user.username} has been blocked for abuse')

# funkcja obsługująca komendę /help
def help_command(update, context):
    commands_info = [
        ("/start", "Starts /help."),
        ("/stop",""),
        ("/help", "Displays a list of available commands and their description."),
        ("/summary [text]", "Generates a summary of the specified text. If no argument, uses previous messages."),
        ("/summary_all", "Generates a summary of the entire conversation."),
        ("/summary_previous_one", "Generates a summary of the last message."),
        ("/summary_previous_n [number]", "Generates a summary of the last N messages."),
        ("/summary_speech",""),
        ("/summary_all_speech",""),
        ("/summary_previous_one_speech",""),
        ("/summary_previous_n_speech",""),
        ("/conv", "")
        ("/speech",""),
        ("/bspeech",""),
        ("/translate_plfr",""),
        ("/translate_frpl",""),
        ("/translate_plen",""),
        ("/translate_enpl",""),
        ("/speech_translate_plen",""),
        ("/",""),
        ("voice messages", )
    ]

    message = "Available commands:\n\n"
    for cmd, description in commands_info:
        message += f"{cmd}: {description}\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)
                                            
def transcription(update, context):    
# pobiernaie pliku audio z wiadomości głosowej
    voice_message = update.message.voice
    file_id = voice_message.file_id
    file = context.bot.get_file(file_id)
    file_path = file.file_path

    # pobieranie nazwy użytkownika
    user_name = update.effective_user.username
    
    # pobieranie transkrypcji za pomocą assemblyai
    transcript = transcribe_audio(file_path)
    
    if 'translate to polish by voice' in transcript.lower():
        start_index = transcript.lower().index('translate to polish by voice') + len('translate to polish by voice')
        text_to_translate = transcript[start_index:].strip()
        
        m2m100_tokenizer.src_lang = "en"

        # tokenizacja i generowanie tłumaczenia
        model_inputs = m2m100_tokenizer(text_to_translate, return_tensors="pt")

        # ustawienie forced_bos_token_id dla języka polskiego
        gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("pl"))
    
        translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
    
        # generowanie mowy OpenAI
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=translated_text[0]
        )

    response.stream_to_file(speech_file_path)
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
    if 'translate to polish' in transcript.lower():
        start_index = transcript.lower().index('translate to polish') + len('translate to polish')
        text_to_translate = transcript[start_index:].strip()
        
        # Ustawienie źródłowego języka w tokenizatorze na angielski
        m2m100_tokenizer.src_lang = "en"

        # Tokenizacja i generowanie tłumaczenia
        model_inputs = m2m100_tokenizer(text_to_translate, return_tensors="pt")

        # Ustawienie forced_bos_token_id dla języka polskiego
        gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("pl"))
        
        translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

        # Wysłanie przetłumaczonego tekstu
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user_name}, przetłumaczono na język polski: {translated_text[0]}")
    
    if 'cat' in transcript.lower():
        user_id = update.effective_user.id
        user_bad_word_count[user_id] = user_bad_word_count.get(user_id, 0) + 1

        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

        context.bot.send_message(chat_id=update.effective_chat.id,
        text=f'The message contains a blocked word. Please avoid using such words.\n'
        f'Number of bad words:{user_bad_word_count[user_id]}')
        
        if user_bad_word_count[user_id] >= 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
            text=f'User {update.effective_user.username} has been blocked for abuse')
    
    
    if 'test' in transcript.lower():
        user_id = update.effective_user.id
        user_bad_word_count[user_id] = user_bad_word_count.get(user_id, 0) + 1

        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

        context.bot.send_message(chat_id=update.effective_chat.id,
        text=f'The message contains a blocked word. Please avoid using such words.\n'
        f'Number of bad words:{user_bad_word_count[user_id]}')
        
        if user_bad_word_count[user_id] >= 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
            text=f'User {update.effective_user.username} has been blocked for abuse')

    if 'blocked' in transcript.lower():
        user_id = update.effective_user.id
        user_bad_word_count[user_id] = user_bad_word_count.get(user_id, 0) + 1

        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

        context.bot.send_message(chat_id=update.effective_chat.id,
        text=f'The message contains a blocked word. Please avoid using such words.\n'
        f'Number of bad words:{user_bad_word_count[user_id]}')
        
        if user_bad_word_count[user_id] >= 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
            text=f'User {update.effective_user.username} has been blocked for abuse')
    else:
        # wysyłanie transkrypcji do użytkownika
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"{user_name} recorded a voice message: {transcript}")
    

def transcribe_audio(audio_file_path):
    # tworzenie instancji transkrybera z użyciem assemblyai
    transcriber = aai.Transcriber()

    # pobieranie transkrypcji z pliku audio
    transcript = transcriber.transcribe(audio_file_path)

    return transcript.text

def translate_text_pl_fr(update, context):
    # pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("fr"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
    
def translate_text_fr_pl(update, context):
    # pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("fr"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # Wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
        
def translate_text_en_pl(update, context):
    # pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "en"

    # tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("pl"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])
    
    
def translate_text_pl_en(update, context):
    # pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # ustawienie forced_bos_token_id dla języka francuskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("en"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    # wysyłanie przetłumaczonego tekstu do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=translated_text[0])

    
def generate_response(update, context):
   
    user_input = update.message.text
    
    if user_input.startswith('/conv'):
        user_input = ' '.join(user_input.split(' ')[1:]).strip()

    # generowanie odpowiedzi
    input_ids = blender_bot_tokenizer.encode(user_input, return_tensors="pt")
    
    with torch.no_grad():
        output = blender_bot_model.generate(input_ids)

    response = blender_bot_tokenizer.decode(output[0], skip_special_tokens=True)

    # wysyłanie wygenerowanej odpowiedzi z powrotem do użytkownika
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def generate_speech(update, context):
    # pobieranie tekstu z wiadomości
    user_text = " ".join(context.args)

    # generowanie mowy OpenAI
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=user_text
    )

    # zapis odpowiedzi do pliku audio
    response.stream_to_file(speech_file_path)

    # wysyłanie pliku audio do użytkownika
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
def generate_speech_response(update, context):
    user_input = update.message.text
    # ignorowanie /bspeech jako wiadomość do modelu
    if user_input.startswith('/bspeech'):
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
    # pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "pl"

    # tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # ustawienie forced_bos_token_id dla języka angielskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("en"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
    
    # generowanie mowy OpenAI
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=translated_text[0]
    )
    
    
    response.stream_to_file(speech_file_path)
    context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    
def generate_translate_speech_enpl(update, context):
    # pobieranie tekstu do przetłumaczenia z wiadomości
    user_text = " ".join(context.args)

    # ustawienie źródłowego języka w tokenizatorze na polski
    m2m100_tokenizer.src_lang = "en"

    # tokenizacja i generowanie tłumaczenia
    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    # ustawienie forced_bos_token_id dla języka polskiego
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id("pl"))
    
    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)
    
    # generowanie mowy OpenAI
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

    # komendy start/stop/help
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("help", help_command))
    
    # obsługa transkrypcji wiadomości głosowej
    dp.add_handler(MessageHandler(Filters.voice & ~Filters.command, transcription))
    
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_all_messages))

    dp.add_handler(CommandHandler("summary", summary, pass_args=True))
    
    dp.add_handler(CommandHandler("summary_speech", summary_speech, pass_args=True))

    # obsługa streszczenia wszystkich zapisane wiadomości
    dp.add_handler(CommandHandler("summary_all", summary_all))
    
    # obsługa streszczenia wszystkich zapisanych wiadomości i zwaracanie ich w formie głosówki 
    dp.add_handler(CommandHandler("summary_all_speech", summary_all_speech))
    
    # obsługa streszczenia ostatniej wiadomości
    dp.add_handler(CommandHandler("summary_previous_one", summary_previous_one))
    
    # obsługa streszczenia ostatniej wiadomości i zwracanie jej w formie głosówki
    dp.add_handler(CommandHandler("summary_previous_one_speech", summary_previous_one_speech))
    
    # obsługa streszczenia n wiadomości
    dp.add_handler(CommandHandler("summary_previous_n", summary_previous_n))
    
    # obsługa streszczenia n wiadomości i zwracanie ich w formie głosówki
    dp.add_handler(CommandHandler("summary_previous_n_speech", summary_previous_n_speech))

    # obsługa wiadomości głosowych
    dp.add_handler(CommandHandler("speech", generate_speech))
    
    # obsługa konwersacji z botem
    dp.add_handler(CommandHandler("conv", generate_response))

    # obsługa wiadomości głosowych generowanych przez blenderbot
    dp.add_handler(CommandHandler("bspeech", generate_speech_response))
    
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
