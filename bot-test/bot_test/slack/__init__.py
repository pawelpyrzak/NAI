import  requests
from decouple import config


DISCORD_TOKEN=config("DISCORD_TOKEN")
send_discord_message(DISCORD_TOKEN, "1221774231432466452", "<KEY> <KEY>")