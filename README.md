# Telegram AI Bot Project

## Introduction
This project aims to improve communication in group conversations on Telegram using artificial intelligence models. It integrates various AI models to provide features such as text summarization, translation, speech-to-text, text-to-speech, and conversational interactions with the BlenderBot.

## Features
- `/start`: Initiates the bot.
- `/stop`: Stops the bot.
- `/help`: Displays available commands and their descriptions.
- `/summary [text]`: Generates a summary of the specified text or previous messages.
- `/summary_all`: Generates a summary of the entire conversation.
- `/summary_previous_one`: Generates a summary of the last message.
- `/summary_previous_n [number]`: Generates a summary of the last N messages.
- `/summary_speech [text]`: Generates a summary of the specified text by speech.
- `/summary_all_speech`: Generates a summary of the entire conversation by speech.
- `/summary_previous_one_speech`: Generates a summary of the last message by voice.
- `/summary_previous_n_speech [number]`: Generates a summary of the last N messages by speech.
- `/conv [text]`: Initiates a conversation with BlenderBot.
- `/speech [text]`: Converts text to voice messages.
- `/bspeech [text]`: Initiates a conversation with BlenderBot and returns it as a voice message.
- `/translate_plfr [text]`: Translates text from Polish to French.
- `/translate_frpl [text]`: Translates text from French to Polish.
- `/translate_plen [text]`: Translates text from Polish to English.
- `/translate_enpl [text]`: Translates text from English to Polish.
- `/speech_translate_plen [text]`: Translates text from Polish to English and returns as a voice message.
- `/speech_translate_enpl [text]`: Translates text from English to Polish and returns as a voice message.
- `stop [voice]`: Stops BlenderBot conversation.
- `show me instruction [voice]`: Displays available commands and their descriptions.
- `text talk with blender [voice]`: Initiates a conversation with BlenderBot.
- `voice talk with blender [voice]`: Initiates a conversation with BlenderBot and returns it as a voice message.
- `translate to polish by voice [voice]`: Translates text from English to Polish.
- `translate to polish [voice]`: Translates text from English to Polish and returns as a voice message.

## Installation
To run the bot, ensure you have the following dependencies installed:
- `python-telegram-bot`: Install with `pip install python-telegram-bot`.
- `transformers`: Install with `pip install transformers`.
- `python-decouple`: Install with `pip install python-decouple`.
- `torch`: Install with `pip install torch`.
- `assemblyai`: Install with `pip install assemblyai`.
- `pathlib`: Usually built into Python standard library.

