import assemblyai as aai
import logging
import os
import psycopg2
import re
import signal
import sys
import torch
from collections import defaultdict, deque
from datetime import datetime
from decouple import config
from gtts import gTTS
from openai import OpenAI
from pathlib import Path
from psycopg2.extras import RealDictCursor
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, ApplicationBuilder, MessageHandler, filters, CallbackContext
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, M2M100ForConditionalGeneration, M2M100Tokenizer, pipeline

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conf.db_config import get_db_connection

forbidden_words = ["spam", "kurde", "ban", "blocked", "test", "cat"]
user_violations = defaultdict(int)
last_messages = deque(maxlen=5)

speech_file_path = Path(__file__).parent / "speech.mp3"

openai_api_key = config("OPENAI_API_KEY")
openai_client = OpenAI(api_key=openai_api_key)

blender_bot_tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
blender_bot_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

m2m100_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
m2m100_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

aai.settings.api_key = config("AAI_API_KEY")


# Funkcja obsługująca komendę /auth
async def auth(update: Update, context: CallbackContext):
    if len(context.args) < 2:
        await update.message.reply_text('Użycie: /auth <users_id> <user_key>')
        return
    try:
        users_id = int(context.args[0])
        user_key = context.args[1]
    except (IndexError, ValueError):
        await update.message.reply_text('Użycie: /auth <users_id> <user_key>')
        return

    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        # Sprawdzenie, czy użytkownik istnieje
        cursor.execute("SELECT * FROM users WHERE id = %s AND auth_key = %s", (users_id, user_key))
        user = cursor.fetchone()

        if user:
            telegram_user_id = update.effective_user.id
            telegram_username = update.effective_user.username

            chatuser = check_chat_user(telegram_user_id)
            if not telegram_username:
                if update.effective_user.last_name:
                    telegram_username = f"{update.effective_user.first_name} {update.effective_user.last_name}"
                else:
                    telegram_username = update.effective_user.first_name

            if not chatuser:
                cursor.execute("INSERT INTO chat_users (id, username, users_id) VALUES (%s, %s, %s)",
                               (telegram_user_id, telegram_username, users_id))
            db.commit()

            await update.message.reply_text(f"Użytkownik {telegram_username} został dodany do bazy danych.")
        else:
            await update.message.reply_text("Nie znaleziono użytkownika o podanym ID i kluczu.")

    except psycopg2.OperationalError as e:
        await update.message.reply_text("Wystąpił błąd podczas dodawania użytkownika do bazy danych.")
        print(e)
    except Exception as e:
        await update.message.reply_text("Wystąpił nieoczekiwany błąd.")
        print(e)
    finally:
        cursor.close()
        db.close()


def check_chat_user(telegram_user_id: int) -> dict:
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM chat_users WHERE id = %s", (telegram_user_id,))
        chat_user = cursor.fetchone()
        return chat_user
    finally:
        cursor.close()
        db.close()


async def create_chat_if_not_exist(chat_id: int, chat_name: str) -> dict:
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM Chats WHERE id = %s", (chat_id,))
        chat = cursor.fetchone()

        if not chat:
            cursor.execute("INSERT INTO Chats (id, name, chat_platforms_id) VALUES (%s, %s, %s)",
                           (chat_id, chat_name, 1))
            db.commit()
            cursor.execute("SELECT * FROM Chats WHERE id = %s", (chat_id,))
            chat = cursor.fetchone()
    finally:
        cursor.close()
        db.close()


async def important(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    telegram_user_id = update.effective_user.id
    current_time = datetime.now()
    chat_user = check_chat_user(telegram_user_id)

    if not chat_user:
        await update.message.reply_text("Najpierw musisz użyć komendy /auth {id} {key}.")
        return

    try:

        chat_id = update.message.chat_id
        chat_name = update.message.chat.title or update.message.chat.username
        message_content = ' '.join(context.args)
        await create_chat_if_not_exist(chat_id, chat_name)
        cursor.execute("SELECT * FROM user_chat_mapping WHERE Chats_id = %s AND chat_users_id = %s",
                       (chat_id, chat_user['id']))
        mapping = cursor.fetchone()

        if not mapping:
            cursor.execute("INSERT INTO user_chat_mapping (chats_id, chat_users_id) VALUES (%s, %s)",
                           (chat_id, chat_user['id']))
            db.commit()
            cursor.execute("SELECT * FROM user_chat_mapping WHERE chats_id = %s AND chat_users_id = %s",
                           (chat_id, chat_user['id']))
            mapping = cursor.fetchone()

        cursor.execute("INSERT INTO Messages (content, user_chat_mapping_id,timestamp) VALUES (%s, %s, %s)",
                       (message_content, mapping['id']), current_time)
        db.commit()
        await update.message.reply_text("Wiadomość została dodana jako ważna.")

    except psycopg2.OperationalError as e:
        await update.message.reply_text("Wystąpił błąd podczas dodawania wiadomości do bazy danych.")
        print(e)
    except Exception as e:
        await update.message.reply_text("Wystąpił nieoczekiwany błąd.")
        print(e)
    finally:
        cursor.close()
        db.close()


async def add_to_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Użycie: /add_to_group <group_id>")
        return

    group_id = int(context.args[0])

    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM Groups WHERE id = %s", (group_id,))
        existing_group = cursor.fetchone()
        db.commit()
        if not existing_group or group_id <= 0:
            await update.message.reply_text(f"Grupa o id {group_id} nie istnieje.")
            return

        chat_id = update.message.chat_id
        chat_name = update.message.chat.title or update.message.chat.username
        await create_chat_if_not_exist(chat_id, chat_name)
        cursor.execute("INSERT INTO Messages (content, user_chat_mapping_id,timestamp) VALUES (%s, %s, %s)",
                       (message_content, mapping['id']), current_time)
        db.commit()
        await update.message.reply_text(f"Aktualizowano group_id dla grupy o id {group_id}.")

    except psycopg2.OperationalError as e:
        await update.message.reply_text("Wystąpił błąd podczas przetwarzania komendy.")
        print(e)
    except Exception as e:
        await update.message.reply_text("Wystąpił nieoczekiwany błąd.")
        print(e)
    finally:
        cursor.close()
        db.close()


async def transcription(update: Update, context: CallbackContext) -> None:
    # pobiernaie pliku audio z wiadomości głosowej
    voice_message = update.message.voice
    file_id = voice_message.file_id
    file = context.bot.get_file(file_id)
    file_path = file.file_path
    user_name = update.effective_user.username

    transcriber = aai.Transcriber()
    # pobieranie transkrypcji z pliku audio
    transcript = transcriber.transcribe(file_path)

    if await check_forbidden_words(transcript.lower(), update, context):
        return

    if 'show me instruction' in transcript.lower():
        await update.message.reply_text(get_help_commands())

    if 'text talk with blender' in transcript.lower():
        start_index = transcript.lower().index('text talk with blender') + len('text talk with blender')
        text_to_translate = transcript[start_index:].strip()

        if text_to_translate:
            response = await return_response(text_to_translate)
            await update.message.reply_text(response)

    if 'voice talk with blender' in transcript.lower():
        start_index = transcript.lower().index('voice talk with blender') + len('voice talk with blender')
        text_to_translate = transcript[start_index:].strip()

        if text_to_translate:
            response_text = await return_response(text_to_translate)
            await gen_speech_gTTS(update, response_text)
            # await gen_speech_openAi(update,response_text)

    if 'translate to polish by voice' in transcript.lower():
        start_index = transcript.lower().index('translate to polish by voice') + len('translate to polish by voice')
        text_to_translate = transcript[start_index:].strip()
        translated_text = perform_translation("pl", "en", text_to_translate)

        await gen_speech_gTTS(update, translated_text)

    if 'translate to polish' in transcript.lower():
        start_index = transcript.lower().index('translate to polish') + len('translate to polish')
        text_to_translate = transcript[start_index:].strip()
        translated_text = perform_translation("pl", "en", text_to_translate)
        await update.message.reply_text(f"{user_name}, {translated_text[0]}")

    update.message.reply_text(f"{user_name} recorded a voice message: {transcript}")
    last_messages.append(transcript)


def perform_translation(tgt_lang: str, src_lang: str, user_text: str) -> str:
    supported_languages = ["pl", "fr", "en"]

    if src_lang not in supported_languages or tgt_lang not in supported_languages:
        return f"Języki {src_lang} lub {tgt_lang} nie są obsługiwane."

    m2m100_tokenizer.src_lang = src_lang

    model_inputs = m2m100_tokenizer(user_text, return_tensors="pt")

    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id(tgt_lang))

    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    end_text = f"Tłumaczenie z {src_lang} na {tgt_lang}: {translated_text[0]}"
    return end_text


async def translate_text(update: Update, context: CallbackContext) -> None:
    args = context.args
    if not args or len(args) < 3:
        update.message.reply_text("Za mało argumentów. Użyj: /translate {tgt_lang} {src_lang} {text}")
        return

    tgt_lang = args[0].lower()
    src_lang = args[1].lower()
    user_text = " ".join(args[2:]).strip()

    translated_text = perform_translation(tgt_lang, src_lang, user_text)

    await update.message.reply_text(translated_text)


# dodać if sv
async def generate_summary(update: Update, text: str) -> str:
    message = await update.message.reply_text("Summary in process please wait")
    summarization = pipeline("summarization", model="facebook/bart-large-cnn")
    chunks = [text[i:i + 4096] for i in range(0, len(text), 4096)]
    summaries = [summarization(chunk)[0]['summary_text'] for chunk in chunks]
    await message.delete()
    await update.message.reply_text(f"Summary: {' '.join(summaries)}")
    return ' '.join(summaries)


async def summary(update: Update, context: CallbackContext) -> None:
    args = context.args
    if not args:
        update.message.reply_text("Brak argumentów")
        return
    send_voice = False
    number_flag = 0
    if '-sv' in args:
        send_voice = True
        args.remove('-sv')
    for arg in args:
        if re.match(r'^-n[1-9]$', arg):
            number_flag = int(arg[2:])
            args.remove(f'-n{number_flag}')

    if 0 < number_flag < len(last_messages):
        if last_messages:
            summary_result = await generate_summary(update, last_messages[-number_flag])
        else:
            await update.message.reply_text("No past messages available for summary..")
            return
    else:
        text_to_summarize = ' '.join(context.args)
        summary_result = await generate_summary(update, text_to_summarize)
    if send_voice:
        await gen_speech_gTTS(update, summary_result)


# async def summary_previous(update: Update, context: CallbackContext) -> None:
#     if not context.args:
#         update.message.reply_text("Brak argumentów")
#         return
#     if last_messages:
#         await generate_summary(update, last_messages[-1])
#     else:
#         await update.message.reply_text("No past messages available for summary..")


async def return_response(user_input) -> str:
    # Generowanie odpowiedzi
    input_ids = blender_bot_tokenizer.encode(user_input, return_tensors="pt")

    with torch.no_grad():
        output = blender_bot_model.generate(input_ids)

    response_text = blender_bot_tokenizer.decode(output[0], skip_special_tokens=True)
    return response_text


async def generate_response(update: Update, context: CallbackContext) -> None:
    args = context.args
    if not args:
        update.message.reply_text("Brak argumentów")
        return
    send_voice = False
    if '-sv' in args:
        send_voice = True
        args.remove('-sv')

    user_input = ' '.join(args).strip()

    response_text = await return_response(user_input)
    if send_voice:
        await gen_speech_gTTS(update, response_text)
    else:
        await update.message.reply_text(response_text)


async def check_forbidden_words(message_text: str, update: Update, context: CallbackContext) -> bool:
    for word in forbidden_words:
        if re.search(rf"\b{re.escape(word)}\b", message_text):
            user_id = update.effective_user.id
            user_violations[user_id] += 1
            await update.message.delete()
            await update.message.reply_text(
                f"Twoja wiadomość została usunięta, ponieważ zawiera zakazane słowo."
                f"\nLiczba wykroczeń: {user_violations[user_id]}")
            return True
    return False


async def get_words(update: Update, context: CallbackContext) -> None:
    message_text = update.message.text.lower()
    if update.message.from_user.id == context.bot.id:
        return

    if await check_forbidden_words(message_text, update, context):
        return

    last_messages.append(update.message.text)


async def send_voice_message(update: Update, context) -> None:
    if not context.args:
        update.message.reply_text("Brak argumentów")
        return
    text = " ".join(context.args).strip()
    await gen_speech_gTTS(text, update)


def get_help_commands() -> str:
    commands_info = [
        ("/start", "Starts /help."),
        ("/stop", "Stops Blender bot."),
        ("/help", "Displays a list of available commands and their description."),
        ("/summary [text]", "Generates a summary of the specified text. If no argument, uses previous messages."),
        ("/summary_previous", "Generates a summary of the last message."),
        # ("/summary_previous_n [number]", "Generates a summary of the last N messages."),
        ("/summary_speech [text]",
         "Generates a summary of the specified text by speech. If no argument, uses previous messages."),
        ("/summary_previous_speech", "Generates a summary of the last message by voice."),
        # ("/summary_previous_n_speech [number]", "Generates a summary of the last N messages by speech."),
        ("/conv [text]", "Conversation with blender bot."),
        ("/speech [text]", "Voice messages by text."),
        ("/bspeech [text]", "Conversation with blender bot returned as voice message."),
        ("/translate_plfr [text]", "Text translation from Polish to French."),
        ("/translate_frpl [text]", "Text translation from French to Polish."),
        ("/translate_plen [text]", "Text translation from Polish to English"),
        ("/translate_enpl [text]", "Text translation from English to Polish"),
        ("/speech_translate_plen [text]", "Text translation from Polish to English returned as a voice message"),
        ("/speech_translate_enpl [text]", "Text translation from English to Polish returned as a voice message"),
        ("stop [voice]", "Stops Blender bot."),
        ("show me instruction [voice]", "Displays a list of available commands and their description."),
        ("text talk with blender [voice]", "Conversation with blender bot."),
        ("voice talk with blender [voice]", "Conversation with blender bot returned as voice message."),
        ("translate to polish by voice [voice]", "Text translation from English to Polish"),
        ("translate to polish [voice]", "Text translation from English to Polish returned as a voice message"),
        ("WARNING- U CAN'T USE WORDS LIKE:CAT, TEST, BLOCK IN TEXT/VOICE MESSAGES",
         "MESSAGES CONTAINING THESE WORDS WILL BE DELETED")
    ]
    commands_list = "\n".join([f"{command}: {description}" for command, description in commands_info])
    return "Available commands:\n\n" + commands_list


async def gen_speech_openAi(update: Update, text: str) -> None:
    response = openai_client.audio.speech.create(model="tts-1", voice="alloy", input=text)
    response.stream_to_file(speech_file_path)
    update.message.reply_voice(voice=open(speech_file_path, 'rb'))


async def gen_speech_gTTS(update: Update, text: str) -> None:
    try:
        if text:
            file_path = "voice_message.ogg"
            tts = gTTS(text=text, lang='pl')
            tts.save(file_path)
            with open(file_path, 'rb') as audio_file:
                await update.message.reply_voice(voice=audio_file)
            os.remove(file_path)
        else:
            await update.message.reply_text("Podaj tekst wiadomości do zamiany na głos.")
    except Exception as e:
        await update.message.reply_text(f"Wystąpił błąd: {e}")


async def show_help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(get_help_commands())


async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')


def signal_handler(sig, frame):
    print('Zatrzymanie bota...')
    sys.exit(0)


telegram_bot_token = config("TELEGRAM_API_KEY")
app = ApplicationBuilder().token(telegram_bot_token).build()
app.add_handler(CommandHandler("auth", auth))
app.add_handler(CommandHandler("important", important))

app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("help", show_help_command))

app.add_handler(CommandHandler("summary", summary))
app.add_handler(CommandHandler("send_voice", send_voice_message))

# app.add_handler(CommandHandler("summary_previous", summary_previous))

signal.signal(signal.SIGINT, signal_handler)
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), get_words))

print("start")
app.run_polling()
