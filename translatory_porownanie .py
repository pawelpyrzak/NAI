from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from sklearn.metrics import precision_score, recall_score, f1_score
from decouple import config
from deep_translator import GoogleTranslator
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer
from testdata import test_data 
from translate import Translator

src_lang = "pl"
target_lang = "en"
m2m100_model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
m2m100_tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

def translate_text_pl_fr_bing(text,context,update):
    translator = Translator(from_lang=src_lang, to_lang=target_lang)
    translated_text = translator.translate(text)
    return translated_text

# Funkcja tłumaczenia PL->FR
def translate_text_m2m100(text,context,update):
    m2m100_tokenizer.src_lang = src_lang
    model_inputs = m2m100_tokenizer(text, return_tensors="pt")
    gen_tokens = m2m100_model.generate(**model_inputs, forced_bos_token_id=m2m100_tokenizer.get_lang_id(target_lang))

    translated_text = m2m100_tokenizer.batch_decode(gen_tokens, skip_special_tokens=True)

    return translated_text[0]

# Funkcja tłumaczenia za pomocą Google Translate
def translate_text_GoogleTranslator(text,context,update):   
    # Tutaj umieść kod dla tłumaczenia za pomocą Google Translate
    translated_text = GoogleTranslator(source=src_lang, target=target_lang).translate(text)
    return translated_text

# Funkcja do oceny tłumaczeń
def evaluate_translation(translated_texts, target_texts):
    # Precyzja
    precision = precision_score(target_texts, translated_texts, average='weighted')
    
    # Odwołanie
    recall = recall_score(target_texts, translated_texts, average='weighted')
    
    # Miara F1
    f1 = f1_score(target_texts, translated_texts, average='weighted')
    
    return precision, recall, f1

# Funkcja do porównania tłumaczeń
def compare_translations(translator_func1, translator_func2, translator_func3, test_data, update, context):
    translated_texts_func1 = []
    translated_texts_func2 = []
    translated_texts_func3 = []
    target_texts = []
    i=1
    for source_text, target_text in test_data:
        message_sent= context.bot.send_message(chat_id=update.effective_chat.id, text=f"Aktualny test: {i}/50")
        # Tłumaczenie za pomocą pierwszej funkcji
        translated_text_func1 = translator_func1(source_text,context,update)
        translated_texts_func1.append(translated_text_func1)
        
        # Tłumaczenie za pomocą drugiej funkcji
        translated_text_func2 = translator_func2(source_text,context,update)
        translated_texts_func2.append(translated_text_func2)
        
        # Tłumaczenie za pomocą trzeciej funkcji
        translated_text_func3 = translator_func3(source_text,context,update)
        translated_texts_func3.append(translated_text_func3)
        i += 1
        target_texts.append(target_text)
        if message_sent:
            context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message_sent.message_id)
    
    # Ocena pierwszej funkcji tłumaczenia
    precision1, recall1, f1_score1 = evaluate_translation(translated_texts_func1, target_texts)
    
    # Ocena drugiej funkcji tłumaczenia
    precision2, recall2, f1_score2 = evaluate_translation(translated_texts_func2, target_texts)
    
    # Ocena trzeciej funkcji tłumaczenia
    precision3, recall3, f1_score3 = evaluate_translation(translated_texts_func3, target_texts)
    return {
        "M2m100": {"Precision": precision1*100, "Recall": recall1*100, "F1 Score": f1_score1*100},
        "Google translator": {"Precision": precision2*100, "Recall": recall2*100, "F1 Score": f1_score2*100},
        "Bing": {"Precision": precision3*100, "Recall": recall3*100, "F1 Score": f1_score3*100}
    }

# Funkcja obsługi polecenia /test
def test_translator(update, context):
    # Porównanie tłumaczeń
    evaluation_results = compare_translations(translate_text_m2m100, translate_text_GoogleTranslator, translate_text_pl_fr_bing, test_data, update, context)
    
    # Wyświetlenie wyników
    message = ""
    for method, metrics in evaluation_results.items():
        message += f"\n{method}:\n"
        for metric, value in metrics.items():
            message += f"{metric}: {value}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    # Inicjalizacja Updatera
    updater = Updater(config('TELEGRAM_API_KEY'))

    # Uzyskanie dyspozytora, aby zarejestrować obsługę poleceń
    dispatcher = updater.dispatcher

    # Rejestracja obsługi poleceń
    dispatcher.add_handler(CommandHandler("test_translator", test_translator))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
