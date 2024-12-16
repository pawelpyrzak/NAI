import discord
import io
import os
import psycopg2
import sys
from decouple import config
from discord.ext import commands
from discord.ui import Button, View
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
from transformers import BartForConditionalGeneration, BartTokenizer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bot_test.bot_config.methods import *

BOT_TOKEN = config("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

BANNED_WORDS = ["test", "block", "cat"]
# CHANNEL_ID = 1221141214745723002
CHANNEL_ID = 1221774231432466452

@bot.event
async def on_ready():
    print("Hello! bot is ready!")
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send("Hello!")

# Widok z przyciskami Tak i Nie
class ConfirmView(View):
    def __init__(self, message, attachment):
        super().__init__(timeout=60)
        self.message = message
        self.attachment = attachment

    @discord.ui.button(label="Tak", style=discord.ButtonStyle.success)
    async def confirm_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.message.author:
            await interaction.response.send_message("Tylko autor wiadomości może zatwierdzić plik.", ephemeral=True)
            return

        # Pobierz zawartość pliku jako bytes
        file_content = await self.attachment.read()
        file_name = self.attachment.filename

        # Zapisz plik do bazy danych
        save_file_to_db(file_name, file_content, str(interaction.channel_id))

        # Potwierdzenie i usunięcie przycisków
        await interaction.response.edit_message(content=f"Plik `{file_name}` został zapisany w bazie danych!",
                                                view=None)

    @discord.ui.button(label="Nie", style=discord.ButtonStyle.danger)
    async def cancel_button(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.message.author:
            await interaction.response.send_message("Tylko autor wiadomości może odrzucić plik.", ephemeral=True)
            return

        await interaction.response.edit_message(content="Anulowano zapis pliku.", view=None)


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.attachments:
        for attachment in message.attachments:
            view = ConfirmView(message, attachment)
            await message.channel.send(f"Czy chcesz zapisać plik `{attachment.filename}` w bazie danych?", view=view)
    await bot.process_commands(message)



@bot.command()
async def start(ctx):
    await ctx.send("message")
    # Upewnij się, że wiadomość nie jest z DM
    if isinstance(ctx.channel, discord.DMChannel):
        await ctx.send("Ta komenda nie jest dostępna w wiadomościach prywatnych.")
        return

    # Zapisz czat do bazy danych
    channel_id = ctx.channel.id
    channel_name = ctx.channel.name
    message = save_chat_to_db(str(channel_id), channel_name)

    # Wyślij wynik do użytkownika
    await ctx.send(message)


bot.run(BOT_TOKEN)
