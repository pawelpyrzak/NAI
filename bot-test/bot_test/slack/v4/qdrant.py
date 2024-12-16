import base64
import io
import logging
import uuid

import pdfplumber
import requests
from decouple import config
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
from sentence_transformers import SentenceTransformer
from slack_bolt import App, Ack
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)

# Ładowanie zmiennych z pliku .env
SLACK_BOT_TOKEN = config('SLACK_BOT_TOKEN')
QDRANT_COLLECTION_NAME = "files_collection"
SLACK_APP_TOKEN = config("SLACK_APP_TOKEN")
# Inicjalizacja klienta Qdrant
qdrant_client = QdrantClient(url="http://localhost:6333")  # Upewnij się, że Qdrant działa na tym porcie
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
client = WebClient(token=SLACK_BOT_TOKEN)

# Inicjalizacja aplikacji Slack
app = App(token=SLACK_BOT_TOKEN)

ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}  # Modify this as needed


# Funkcja, która zamienia dane binarne na base64
def encode_file_to_base64(file_path):
    with open(file_path, "rb") as f:
        file_content = f.read()
    return base64.b64encode(file_content).decode('utf-8')


def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text


# Funkcja do ekstrakcji tekstu z pliku DOCX
def extract_text_from_docx(file):
    doc = Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text


# Funkcja do ekstrakcji tekstu z pliku TXT
def extract_text_from_txt(file):
    text = file.read().decode('utf-8')
    return text


# Funkcja do konwertowania tekstu na wektor
def get_embedding(text):
    return model.encode(text).tolist()  # Zamiana na listę, aby mogło być zapisane w Qdrant


# Funkcja do dodawania pliku do Qdrant
def add_file_to_qdrant(file_content, file_name, file_type):
    file_id = str(uuid.uuid4())

    # Obsługa różnych formatów plików
    text = None
    if file_type == 'pdf':
        text = extract_text_from_pdf(io.BytesIO(file_content))
    elif file_type == 'docx':
        text = extract_text_from_docx(io.BytesIO(file_content))
    elif file_type == 'txt':
        text = extract_text_from_txt(io.BytesIO(file_content))

    if not text:
        return f"Nie udało się wydobyć tekstu z pliku '{file_name}'."

    # Konwertowanie tekstu na wektor
    vector = get_embedding(text)

    # Dodanie do kolekcji Qdrant
    try:
        # Sprawdzenie, czy kolekcja istnieje
        if not qdrant_client.collection_exists(QDRANT_COLLECTION_NAME):
            # Tworzenie nowej kolekcji, jeśli nie istnieje
            qdrant_client.create_collection(
                collection_name=QDRANT_COLLECTION_NAME,
                vectors_config=VectorParams(size=384, distance="Cosine")  # Przykład konfiguracji
            )

        # Wstawianie pliku do kolekcji
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=[{
                "id": file_id,
                "vector": vector,
                "payload": {
                    "file_name": file_name,
                    "file_binary": base64.b64encode(file_content).decode('utf-8')
                }
            }]
        )
        return f"Plik '{file_name}' został pomyślnie dodany do Qdrant."
    except Exception as e:
        return f"Wystąpił błąd: {e}"


# Funkcja do wyszukiwania pliku na podstawie zapytania
def search_file(query):
    try:
        # Zamiana zapytania na wektor
        query_vector = get_embedding(query)

        # Wyszukiwanie w Qdrant
        result = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=5  # Zwrócenie 5 najlepszych wyników
        )

        if result:
            response = "Znalezione pliki:\n"
            for res in result:
                file_name = res.payload.get("file_name")
                score = res.score  # Dla wyszukiwania wektorowego jest też wynik dopasowania
                response += f"Plik: {file_name}, Dopasowanie: {score}\n"
            return response
        else:
            return "Nie znaleziono plików pasujących do zapytania."
    except Exception as e:
        return f"Wystąpił błąd: {e}"


# Funkcja do wysyłania pliku
def send_file(channel_id, file_content, file_name):
    try:
        # Tworzenie pliku w pamięci i wysyłanie
        response = app.client.files_upload(
            channels=channel_id,
            file=io.BytesIO(file_content),
            filename=file_name
        )
        return response
    except SlackApiError as e:
        return f"Błąd podczas wysyłania pliku: {e.response['error']}"


# Funkcja do wylistowania wszystkich plików z Qdrant
@app.message("!listfiles")
def list_files(ack, say):
    try:
        # Wyszukiwanie plików w kolekcji Qdrant
        result = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=[0.0] * 384,  # Pusty wektor jako zapytanie
            limit=100  # Limit wyników
        )

        if result:
            files_list = []
            for point in result:
                if hasattr(point, 'payload'):
                    file_name = point.payload.get("file_name")
                    if file_name:
                        files_list.append(f"Nazwa: {file_name}")

            if files_list:
                say("\n".join(files_list))
            else:
                say("Brak plików w kolekcji.")
        else:
            say("Nie znaleziono plików.")

        ack()

    except Exception as e:
        say(f"Wystąpił błąd: {e}")
        ack()


@app.message("!getfile")
def handle_get_file(ack, say, message):
    # Pobieranie nazwy pliku z wiadomości
    file_name = message.get('text', '').replace('!getfile', '').strip()

    if not file_name:
        say("Proszę podać nazwę pliku.")
        ack()
        return

    say(f"Retrieving the file: {file_name}")

    try:
        # Wyszukiwanie pliku w Qdrant
        result = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=[0.0] * 384,  # Pusty wektor jako zapytanie
            limit=5
        )

        # Sprawdzenie, czy znaleziono plik o podanej nazwie
        file_found = False
        for point in result:
            if point.payload.get("file_name") == file_name:
                file_content_base64 = point.payload.get("file_binary")
                if not file_content_base64:
                    say(f"Plik o nazwie '{file_name}' nie zawiera danych binarnych.")
                    ack()
                    return

                file_content = base64.b64decode(file_content_base64)

                # Tworzenie pliku w pamięci i wysyłanie do Slacka przy użyciu files.upload_v2
                response = app.client.files_upload_v2(
                    channel=message['channel'],  # Zmieniamy z 'channels' na 'channel'
                    file=io.BytesIO(file_content),
                    filename=file_name
                )

                if response["ok"]:
                    say(f"Plik '{file_name}' został wysłany.")
                else:
                    say(f"Nie udało się wysłać pliku '{file_name}': {response['error']}")
                file_found = True
                break

        if not file_found:
            say(f"Plik o nazwie '{file_name}' nie został znaleziony.")
        ack()

    except Exception as e:
        say(f"Wystąpił błąd podczas pobierania pliku: {e}")
        ack()


def handle_file_message_events(event, say):
    files = event['files']
    print(len(files))
    for file in files:
        file_id = file['id']
        file_name = file['name']
        file_type = file_name.split('.')[-1].lower()
        print("file_name:", file_name)

        if not file_type in ALLOWED_EXTENSIONS:
            say(text=f"Sorry, the file '{file_name}' has an unsupported extension. Supported extensions are: PDF, DOCX, TXT.", )
            continue
        say(
            text=f"Would you like to save the file '{file_name}'?",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Would you like to save the file '{file_name}'?*"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Yes"},
                            "value": f"{file_id}:{file_name}:{file_type}",
                            "action_id": "save_file_yes"
                        },
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "No"},
                            "value": file_id,
                            "action_id": "save_file_no"
                        }
                    ]
                }
            ]
        )
        print("say yes/no")

def update_message(channel_id, ts, confirmation_text):
    client.chat_update(
        channel=channel_id,
        ts=ts,
        text=confirmation_text,
        blocks=[
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": confirmation_text}
            }
        ]
    )


@app.action("save_file_yes")
def handle_save_file_yes(ack: Ack, body, say):
    ack()
    value = body['actions'][0]['value']
    file_id, file_name, file_type = value.split(":")

    try:
        # Get detailed file information
        file_info_response = client.files_info(file=file_id)
        file_url = file_info_response['file']['url_private_download']

        # Download the file
        headers = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
        download_response = requests.get(file_url, headers=headers)

        if download_response.status_code == 200:
            file_content = download_response.content

            confirmation_text = add_file_to_qdrant(file_content, file_name, file_type)
        else:
            confirmation_text = f"Error downloading the file: {download_response.status_code}"

    except SlackApiError as e:
        confirmation_text = f"Error processing the file: {e.response['error']}"

    update_message(body['channel']['id'], body['message']['ts'], confirmation_text)


# Handle "No" button click to discard the file
@app.action("save_file_no")
def handle_save_file_no(ack: Ack, body, say):
    ack()
    update_message(body['channel']['id'], body['message']['ts'], "The file was not saved.")


if __name__ == "__main__":
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
