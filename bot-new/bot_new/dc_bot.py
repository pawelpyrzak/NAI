import io

import discord
from decouple import config
from discord.ext import commands
from docx import Document
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from transformers import BartForConditionalGeneration, BartTokenizer

from db_config import get_db_connection  # Import połączenia z bazą danych

BOT_TOKEN = config("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

BANNED_WORDS = ["test", "block", "cat"]
# CHANNEL_ID = 1221141214745723002
CHANNEL_ID = 1221774231432466452
# Połączenie z bazą danych MySQL
db = get_db_connection()
cursor = db.cursor()

@bot.event
async def on_ready():
    print("Hello! Study bot is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello!")

# @bot.event
# async def on_message(message):
#     if not message.author.bot:  # Sprawdź, czy autor wiadomości nie jest botem, aby uniknąć pętli
#         for word in BANNED_WORDS:
#             if word.lower() in message.content.lower():
#                 await message.delete()
#                 await message.channel.send(f"{message.author.mention}, nie możesz używać tego słowa!")
#                 break  # Zakończ pętlę po pierwszym zbanowanym słowie
#
#     await bot.process_commands(message)


@bot.command()
async def say(ctx, *, message):
    await ctx.send(message)

def check_chat_user(discord_user_id):
    db = get_db_connection()
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM ChatUsers WHERE id = %s", (discord_user_id,))
        chat_user = cursor.fetchone()
        return chat_user
    finally:
        cursor.close()


@bot.command()
async def auth(ctx, users_id: int, user_key: str):
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        # Sprawdzenie, czy użytkownik istnieje
        cursor.execute("SELECT * FROM users WHERE id = %s AND auth_key = %s", (users_id, user_key))
        user = cursor.fetchone()

        if user:
            discord_user_id = ctx.author.id
            discord_username = ctx.author.name
            chatuser = check_chat_user(discord_user_id)

            if not chatuser:
                cursor.execute("INSERT INTO chatusers (id, username, users_id) VALUES (%s, %s, %s)",
                               (discord_user_id, discord_username, users_id))
            db.commit()
            await ctx.send(f"Użytkownik {discord_username} został dodany do bazy danych.")
        else:
            await ctx.send("Nie znaleziono użytkownika o podanym ID i kluczu.")

    except OperationalError as e:
        await ctx.send("Wystąpił błąd podczas dodawania użytkownika do bazy danych.")
        print(e)
    except Exception as e:
        await ctx.send("Wystąpił nieoczekiwany błąd.")
        print(e)
    finally:
        cursor.close()
        db.close()


def create_chat_if_not_exist(server_id, server_name, group_id):
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM Chats WHERE id = %s", (server_id,))
        chat = cursor.fetchone()

        if not chat:
            # Chat does not exist, create it
            cursor.execute("INSERT INTO Chats (id, name, groups_id) VALUES (%s, %s, %s)",
                           (server_id, server_name, group_id))
            db.commit()
            cursor.execute("SELECT * FROM Chats WHERE id = %s", (server_id,))
            chat = cursor.fetchone()

        if 0 < group_id != chat['groups_id']:
            cursor.execute("UPDATE Chats SET groups_id = %s WHERE id = %s", (group_id, server_id))
            db.commit()

        return chat
    finally:
        cursor.close()
        db.close()


@bot.command()
async def important(ctx, *, message_content: str):
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    discord_user_id = ctx.author.id
    print(discord_user_id)
    # Check if ChatUser exists
    chat_user = check_chat_user(discord_user_id)

    if not chat_user:
        await ctx.send("Najpierw musisz użyć komendy !auth {id} {key}.")
        return

    try:
        server_name = ctx.guild.name
        server_id = ctx.guild.id
        # Check if chat exists, if not, create it
        create_chat_if_not_exist(server_id, server_name, 0)
        cursor.execute("SELECT * FROM UserChatMapping WHERE Chats_id = %s AND ChatUsers_id = %s",
                       (server_id, chat_user['id']))
        mapping = cursor.fetchone()

        if not mapping:
            # Create UserChatMapping if it doesn't exist
            cursor.execute("INSERT INTO UserChatMapping (Chats_id, ChatUsers_id) VALUES (%s, %s)",
                           (server_id, chat_user['id']))
            db.commit()
            cursor.execute("SELECT * FROM UserChatMapping WHERE Chats_id = %s AND ChatUsers_id = %s",
                           (server_id, chat_user['id']))
            mapping = cursor.fetchone()

        # Insert message into Messages table
        cursor.execute("INSERT INTO Messages (content, UserChatMapping_id) VALUES (%s, %s)",
                       (message_content, mapping['id']))
        db.commit()
        await ctx.send("Wiadomość została dodana jako ważna.")

    except OperationalError as e:
        await ctx.send("Wystąpił błąd podczas dodawania wiadomości do bazy danych.")
        print(e)
    except Exception as e:
        await ctx.send("Wystąpił nieoczekiwany błąd.")
        print(e)

    finally:
        cursor.close()
        db.close()


@bot.command()
async def add_to_group(ctx, group_id: int):
    db = get_db_connection()
    cursor = db.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("SELECT * FROM Groups WHERE id = %s", (group_id,))
        existing_group = cursor.fetchone()

        if not existing_group or group_id <= 0:
            await ctx.send(f"Grupa o id {group_id} nie istnieje.")
            return

        server_name = ctx.guild.name
        server_id = ctx.guild.id
        create_chat_if_not_exist(server_id, server_name, group_id)
        await ctx.send(f"Aktualizowano group_id dla grupy o id {group_id}.")

    except OperationalError as e:
        await ctx.send("Wystąpił błąd podczas przetwarzania komendy.")
        print(e)
    except Exception as e:
        await ctx.send("Wystąpił nieoczekiwany błąd.")
        print(e)

    finally:
        cursor.close()
        db.close()


@bot.event
async def on_ready():
    print("Start!")
    # channel = bot.get_channel(CHANNEL_ID)
    # await channel.send("Hello!")


@bot.command()
async def generate_summary(ctx, text):
    message = await ctx.send("Streszczanie...")
    tokenizer = BartTokenizer.from_pretrained('facebook/bart-large-cnn')

    # Tokenizacja i kodowanie tekstu wejściowego
    inputs = tokenizer(text, return_tensors='pt', max_length=1024, truncation=True)

    # Model BART
    model = BartForConditionalGeneration.from_pretrained('facebook/bart-large-cnn')

    # Generowanie podsumowania
    summary_ids = model.generate(inputs['input_ids'], num_beams=4, min_length=30, max_length=100, early_stopping=True)

    # Dekodowanie podsumowania
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    await message.delete()
    await ctx.send(summary)


@bot.command()
async def search(ctx, file_name):
    async for message in ctx.channel.history(limit=None):
        if message.attachments:
            for attachment in message.attachments:
                if attachment.filename == file_name:
                    try:
                        file_content = await attachment.read()
                        if attachment.filename.endswith('.txt'):
                            file_content = file_content.decode('utf-8')
                        elif attachment.filename.endswith('.docx'):
                            file_content = extract_text_from_docx(file_content)
                        await generate_summary(ctx, file_content)  # Wywołaj funkcję generate_summary
                        return
                    except Exception as e:
                        print(f'Błąd podczas czytania pliku {file_name}: {e}')
                        await ctx.send(f'Wystąpił błąd podczas czytania pliku {file_name}.')


def extract_text_from_docx(file_content):
    doc = Document(io.BytesIO(file_content))
    full_text = []
    for paragraph in doc.paragraphs:
        full_text.append(paragraph.text)
    return '\n'.join(full_text)


bot.run(BOT_TOKEN)
