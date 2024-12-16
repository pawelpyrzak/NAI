import io
from decouple import config
import base64
import uuid
import pdfplumber
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams
import discord
from discord.ext import commands
from docx import Document

# Ładowanie zmiennych z pliku .env
DISCORD_BOT_TOKEN = config('DISCORD_TOKEN')
QDRANT_COLLECTION_NAME = "files_collection"

# Inicjalizacja klienta Qdrant
qdrant_client = QdrantClient(url="http://localhost:6333")  # Upewnij się, że Qdrant działa na tym porcie
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


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
@bot.command()
async def add_file(ctx):
    # Oczekiwanie na załącznik w wiadomości
    if not ctx.message.attachments:
        await ctx.send("Nie znaleziono pliku w wiadomości!")
        return

    attachment = ctx.message.attachments[0]
    file_name = attachment.filename
    file_id = str(uuid.uuid4())

    # Pobranie pliku
    file_content_base64 = await attachment.read()
    file_type = file_name.split('.')[-1].lower()

    # Obsługa różnych formatów plików
    text = None
    if file_type == 'pdf':
        text = extract_text_from_pdf(io.BytesIO(file_content_base64))
    elif file_type == 'docx':
        text = extract_text_from_docx(io.BytesIO(file_content_base64))
    elif file_type == 'txt':
        text = extract_text_from_txt(io.BytesIO(file_content_base64))
    else:
        await ctx.send(
            f"Obsługiwane formaty to PDF, DOCX i TXT. Plik '{file_name}' ma format {file_type}, który nie jest obsługiwany.")
        return

    if not text:
        await ctx.send(f"Nie udało się wydobyć tekstu z pliku '{file_name}'.")
        return

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
                    "file_binary": base64.b64encode(file_content_base64).decode('utf-8')
                }
            }]
        )
        await ctx.send(f"Plik '{file_name}' został pomyślnie dodany do Qdrant.")

    except Exception as e:
        await ctx.send(f"Wystąpił błąd: {e}")


# Funkcja do wyszukiwania pliku na podstawie zapytania
@bot.command()
async def search_file(ctx, *, query: str):
    try:
        # Zamiana zapytania na wektor
        query_vector = get_embedding(query)

        # Wyszukiwanie w Qdrant
        result = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=query_vector,
            limit=5
        )

        if result:
            response = "Znalezione pliki:\n"
            for res in result:
                file_name = res.payload.get("file_name")
                score = res.score  # Dla wyszukiwania wektorowego jest też wynik dopasowania
                response += f"Plik: {file_name}, Dopasowanie: {score}\n"
            await ctx.send(response)
        else:
            await ctx.send("Nie znaleziono plików pasujących do zapytania.")

    except Exception as e:
        await ctx.send(f"Wystąpił błąd: {e}")

@bot.command()
async def get_file(ctx, file_name: str):
    try:
        # Wyszukiwanie pliku za pomocą wektora (tutaj przyjmujemy pusty wektor)
        result = qdrant_client.search(
            collection_name=QDRANT_COLLECTION_NAME,
            query_vector=[0.0] * 384,  # Użyj odpowiedniego wektora
            limit=5  # Zwiększamy limit wyników, jeśli chcesz znaleźć więcej plików
        )
        if result:
            # Iterowanie po wynikach, aby znaleźć odpowiedni plik po file_name
            for point in result:
                if point.payload.get("file_name") == file_name:
                    file_content_base64 = point.payload.get("file_binary")
                    file_name = point.payload.get("file_name")

                    if not file_content_base64:
                        await ctx.send(f"Nie znaleziono pliku o nazwie '{file_name}'.")
                        return

                    # Zdekodowanie pliku
                    file_content = base64.b64decode(file_content_base64)

                    # Tworzenie pliku w pamięci i wysyłanie
                    file = discord.File(io.BytesIO(file_content), filename=file_name)
                    await ctx.send(f"Plik '{file_name}' został pobrany:", file=file)
                    return

            await ctx.send(f"Nie znaleziono pliku o nazwie '{file_name}'.")
        else:
            await ctx.send(f"Nie znaleziono wyników.")

    except Exception as e:
        await ctx.send(f"Wystąpił błąd: {e}")


@bot.command()
async def list_files(ctx):
    try:
        # Użycie search zamiast scroll z pustym wektorem
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
                    print(f"Nazwa: {file_name}")
                    if file_name:
                        files_list.append(f"Nazwa: {file_name}")

            if files_list:
                await ctx.send("\n".join(files_list))
            else:
                await ctx.send("Brak plików w kolekcji.")
        else:
            await ctx.send("Nie znaleziono plików.")

    except Exception as e:
        await ctx.send(f"Wystąpił błąd: {e}")


# Uruchomienie bota
bot.run(DISCORD_BOT_TOKEN)