from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="W czym mogę Ci pomóc?")
# /stop
def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Do zobaczenia!")
    updater.stop()

# obsługa wiadomości
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

def main():
    bot_token = "6864763120:AAGeJliLEswXvnFBl8Th7fZZZxHVuuVJGDg"
    updater = Updater(token=bot_token, use_context=True)

    
    dp = updater.dispatcher

    # komendy start/stop
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))
    

    
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    #nasłuchiwanie wiadomości
    updater.start_polling()

    #bot działa aż do ręcznego zatrzymania
    updater.idle()

if __name__ == '__main__':
    main()