import logging
from decouple import config
from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from transformers import pipeline

# Konfiguracja logowania
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Słowa zablokowane
blocked_words = ['ban', 'block', 'test']
user_bad_word_count = {}


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

# Funkcja obsługująca komendę /summary
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


# Funkcja obsługująca komendę /start
def start(update, context):
    help_command(update, context)


# Funkcja zatrzymująca bota
def stop(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Do zobaczenia!")
    updater.stop()


# Funkcja główna
def main():
    bot_token = config("TELEGRAM_API_KEY")
    global updater
    updater = Updater(token=bot_token, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    dp.add_handler(CommandHandler("summary", summary, pass_args=True))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_all_messages))
    dp.add_handler(CommandHandler("summary_all", summary_all))
    dp.add_handler(CommandHandler("summary_previous_one", summary_previous_one))
    dp.add_handler(CommandHandler("summary_previous_n", summary_previous_n))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
