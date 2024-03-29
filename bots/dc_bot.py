import discord
from decouple import config
from discord.ext import commands
from transformers import pipeline

BOT_TOKEN = config("DISCORD_TOKEN")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

BANNED_WORDS = ["test", "block", "cat"]
CHANNEL_ID=1221141214745723002

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


bot.run(BOT_TOKEN)