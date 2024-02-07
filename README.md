# NAI

Telegram bot project using artificial intelligence.   
The bot is supposed to improve communication in group conversations. 

In this project, we used models such as:  
M2m100 to translate text/speech into a language other than the one entered,  
OpenAI API to create TTS,  
AssemblyAI API to create STT,  
Telegram API to create and operate a bot,  
facebook/blenderbot-400M-distill to create conversational communications with the bot,  
model="facebook/bart-large-cnn to create user text summaries. 

Using the models considered above, we were able to such funfictions as: 

"/start" - Starts /help. 
"/stop"- Stops bot. 
"/help"- Displays a list of available commands and their description. 
"/summary [text]"- Generates a summary of the specified text. If no argument, uses previous messages. 
"/summary_all"- Generates a summary of the entire conversation. 
"/summary_previous_one"- Generates a summary of the last message. 
"/summary_previous_n [number]"- Generates a summary of the last N messages. 
"/summary_speech [text]"- Generates a summary of the specified text by speech. If no argument, uses previous messages. 
"/summary_all_speech"- Generates a summary of the entire conversation by speech. 
"/summary_previous_one_speech"- Generates a summary of the last message by voice. 
"/summary_previous_n_speech [number]"- Generates a summary of the last N messages by speech." 
"/conv [text]" -Conversation with blender bot. 
"/speech [text]" -Voice messages by text. 
“/bspeech [text] “-Conversation with blender bot returned as voice message. 
"/translate_plfr [text]" -Text translation from Polish to French. 
"/translate_frpl [text]" -Text translation from French to Polish. 
“/translate_plen [text]"- Text translation from Polish to English. 
“/translate_enpl [text]"- Text translation from English to Polish. 
“/speech_translate_plen [text]” -Text translation from Polish to English returned as a voice message. 
“/speech_translate_enpl [text]”- Text translation from English to Polish returned as a voice 		message. 
"stop [voice]"- Stops Blender bot. 
"show me instruction [voice]"- Displays a list of available commands and their description. 
"text talk with blender [voice]"- Conversation with blender bot. 
"voice talk with blender [voice]" - Conversation with blender bot returned as voice message. 
"translate to polish by voice [voice]"- Text translation from English to Polish. 
"translate to polish [voice]"- Text translation from English to Polish returned as a voice message. 

Installation:  

python-telegram-bot: It supports integration with Telegram. You can install it with pip install python-telegram-bot.  
transformers: This is a library for working with AI-based language models, such as BERT, GPT, etc. You can install it with pip install transformers.  
python-decouple: A library for loading environment variables from an .env file. You can install it with pip install python-decouple.  
torch: This is a library for tensor calculations, which is required by the transformers library. You can install it with pip install torch.  
pathlib: A library for handling file and directory paths in Python. It is usually built into the standard Python library and does not require a separate installation.  
assemblyai: A library for integrating with the AssemblyAI API, which provides speech processing services. You can install it with pip install assemblyai. 
