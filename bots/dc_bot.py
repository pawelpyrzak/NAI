import io
import discord
from decouple import config
from discord.ext import commands
from docx import Document
from transformers import BartForConditionalGeneration, BartTokenizer
from db_config import get_db_connection  # Import połączenia z bazą danych

BOT_TOKEN = config("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

BANNED_WORDS = ["test", "block", "cat"]
CHANNEL_ID = 1221141214745723002

# Połączenie z bazą danych MySQL
db = get_db_connection()
cursor = db.cursor()

# Funkcja do dodawania wiadomości do bazy danych
def add_message(user_id, user_name, content):
    cursor.execute('INSERT INTO messages (user_id, user_name, content) VALUES (%s, %s, %s)',
                   (user_id, user_name, content))
    db.commit()


@bot.command()
async def important(ctx, *, message: str):
    user_id = ctx.author.id
    user_name = str(ctx.author)
    add_message(user_id, user_name, message)
    await ctx.send(f'Message from {user_name} has been marked as important and saved.')
@bot.event
async def on_ready():
    print("Start!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello!")

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
