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
blocked_words = ['ban', 'block', 'test']
user_bad_word_count = {}

# ścieżka do audio
speech_file_path = Path(__file__).parent / "speech.mp3"

# inicjalizacja OpenAI
openai_api_key = "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"
openai_client = OpenAI(api_key=openai_api_key)

# inicjalizacja facebook/blenderbot-400M-distill
blender_bot_tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
blender_bot_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

#inicjalizacja m2m100
m2m100_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
m2m100_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

#inicjalizacja assemblyai
aai.settings.api_key = "b94a066bd92d470fb52b4171688a7720"
transcriber = aai.Transcriber()

def start(update, context):
    help_command(update, context)

def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Do zobaczenia!")
    updater.stop()
    
# Funkcja wysyłająca wiadomość
def send_message(update, context, text):
    return context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)

def save_all_messages(update, context):
    context.user_data.setdefault('all_messages', []).append(update.message.text)
    block_words(update, context)  # Sprawdzenie słów blokowanych po zapisaniu wiadomości    
    
# Funkcja generująca streszczenie za pomocą transformers
def generate_summary(update, context, text):
    summarization = pipeline("summarization", model="facebook/bart-large-cnn")
    
    # Split the text into chunks of 4096 characters (to stay within Telegram message size limit)
    chunks = [text[i:i + 4096] for i in range(0, len(text), 4096)]
    
    # Generate summaries for each chunk
    summaries = [summarization(chunk)[0]['summary_text'] for chunk in chunks]
    
    # Concatenate the summaries
    result_summary = ' '.join(summaries)
    
    return result_summary    

def summary(update, context):
    # Pobierz tekst do streszczenia
    text_to_summarize = ' '.join(context.args) if context.args else ' '.join(context.user_data.get('all_messages', []))
    if text_to_summarize:
        # Wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Streszczanie proszę czekać")

        # Domyślnie używamy transformers do streszczenia
        summary_result = generate_summary(update, context, text_to_summarize)

        # Usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        if message_sent:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # Wysłanie wyniku streszczenia
        send_message(update, context, f"Streszczenie: {summary_result}")
    else:
        send_message(update, context,
                     "Podaj tekst do streszczenia po komendzie /summary, "
                     "lub użyj /summary_previous_one, aby streszczyć poprzednią wiadomość, "
                     "lub /summary_previous_n, aby streszczyć ostatnie N wiadomości.")


# Funkcja streszczająca poprzednią wiadomość
def summary_previous_one(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # Wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Streszczanie proszę czekać")

        summary_result = generate_summary(update, context, all_messages[-1])

        # Usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        send_message(update, context, f"Streszczenie poprzedniej wiadomości: {summary_result}")
    else:
        send_message(update, context, "Brak dostępnych poprzednich wiadomości do streszczenia.")

def summary_previous_one_speech(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # Wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Streszczanie proszę czekać")
        
        # Streszczenie ostatniej wiadomości
        summary_result = generate_summary(update, context, all_messages[-1])

        # Generowanie mowy OpenAI na podstawie streszczenia
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=summary_result
        )
    
    # Zapis odpowiedzi do pliku audio
        response.stream_to_file(speech_file_path)

        # Usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # Wysłanie pliku audio do użytkownika
        context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    else:
        send_message(update, context, "Brak dostępnych poprzednich wiadomości do streszczenia.")   
     
# Funkcja streszczająca ostatnie N wiadomości
def summary_previous_n(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages and context.args and context.args[0].isdigit():
        n = int(context.args[0])

        # Wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Streszczanie proszę czekać")

        text_to_summarize = ' '.join(all_messages[-n:])
        summary_result = generate_summary(update, context, text_to_summarize)

        # Usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        send_message(update, context, f"Streszczenie ostatnich {n} poprzednich wiadomości: {summary_result}")
    else:
        send_message(update, context,
                     "Podaj liczbę wiadomości do streszczenia po komendzie /summary_previous_n.")

def summary_previous_n_speech(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages and context.args and context.args[0].isdigit():
        n = int(context.args[0])
         # Wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Streszczanie proszę czekać")

        text_to_summarize = ' '.join(all_messages[-n:])
        summary_result = generate_summary(update, context, text_to_summarize) 
        
        # Generowanie mowy OpenAI na podstawie streszczenia
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=summary_result
        )
        
         # Zapis odpowiedzi do pliku audio
        response.stream_to_file(speech_file_path)

        # Usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # Wysłanie pliku audio do użytkownika
        context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    else:
        send_message(update, context, "Brak dostępnych poprzednich wiadomości do streszczenia.")   
              
# Funkcja streszczająca wszystkie zapisane wiadomości
def summary_all(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # Wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Streszczanie proszę czekać")

        text_to_summarize = ' '.join(all_messages)
        summary_result = generate_summary(update, context, text_to_summarize)

        # Usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        send_message(update, context, f"Streszczenie wszystkich zapisanych wiadomości: {summary_result}")
    else:
        send_message(update, context, "Brak zapisanych wiadomości do streszczenia.")
        
def summary_all_speech(update, context):
    all_messages = context.user_data.get('all_messages', [])
    if all_messages:
        # Wysłanie informacji o rozpoczęciu
        message_sent = send_message(update, context, "Streszczanie proszę czekać")

        text_to_summarize = ' '.join(all_messages)
        summary_result = generate_summary(update, context, text_to_summarize)
        
         # Generowanie mowy OpenAI na podstawie streszczenia
        response = openai_client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=summary_result
        )
             # Zapis odpowiedzi do pliku audio
        response.stream_to_file(speech_file_path)

        # Usunięcie lub zmiana wiadomości "streszczanie proszę czekać"
        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)

        # Wysłanie pliku audio do użytkownika
        context.bot.send_voice(chat_id=update.effective_chat.id, voice=open(speech_file_path, 'rb'))
    else:
        send_message(update, context, "Brak dostępnych poprzednich wiadomości do streszczenia.") 
        
# Funkcja blokująca wiadomości zawierające zablokowane słowa
def block_words(update, context):
    message_text = update.message.text.lower()

    if any(word in message_text.split() for word in blocked_words):
        user_id = update.effective_user.id
        user_bad_word_count[user_id] = user_bad_word_count.get(user_id, 0) + 1

        context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f'Wiadomość zawiera zablokowane słowo. Proszę unikać używania takich słów.\n'
                                      f'Liczba złych słów: {user_bad_word_count[user_id]}')
        if user_bad_word_count[user_id] >= 3:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f'Użytkownik {update.effective_user.username} został zablokowany za nadużywanie.')

# Funkcja obsługująca komendę /help
def help_command(update, context):
    commands_info = [
        ("/start", "Uruchamia /help."),
        ("/help", "Wyświetla listę dostępnych komend i ich opis."),
        ("/summary [tekst]",
         "Generuje streszczenie podanego tekstu. Jeśli brak argumentu, używa poprzednich wiadomości."),
        ("/summary_all", "Generuje streszczenie całej konwersacji."),
        ("/summary_previous_one", "Generuje streszczenie ostatniej wiadomości."),
        ("/summary_previous_n [liczba]", "Generuje streszczenie ostatnich N wiadomości."),
    ]

    message = "Dostępne komendy:\n\n"
    for cmd, description in commands_info:
        message += f"{cmd}: {description}\n"

    send_message(update, context, message)
                                            
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

    # komendy start/stop/help
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("help", help_command))
    
    # obsługa transkrypcji wiadomości głosowej
    dp.add_handler(MessageHandler(Filters.voice & ~Filters.command, transcription))
    
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_all_messages))

    dp.add_handler(CommandHandler("summary", summary, pass_args=True))
     
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
