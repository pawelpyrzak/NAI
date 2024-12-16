import base64
import uuid

from PyPDF2 import PdfReader
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import MatchAny, PointIdsList
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, HasIdCondition
from qdrant_client.models import Filter, FieldCondition, Match

from ..models import UploadedFile

QDRANT_COLLECTION_NAME = "files"
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')
qdrant_client = QdrantClient(host="localhost", port=6333)


def extract_text_from_file(file):
    if file.name.endswith('.txt'):
        return file.read().decode('utf-8')
    elif file.name.endswith('.pdf'):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    elif file.name.endswith('.docx'):
        doc = Document(file)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    else:
        raise ValueError("Nieobsługiwany typ pliku")


def generate_vector_from_text(text):
    return model.encode(text).tolist()


def process_and_store_file(file, group_id):
    file_content = extract_text_from_file(file)

    vector = generate_vector_from_text(file_content)

    file_binary = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
    qdrant_id = str(uuid.uuid4())
    qdrant_client.upsert(
        collection_name="files",
        points=[
            {
                "id": qdrant_id,
                "vector": vector,
                "payload": {
                    "file_name": file.name,
                    "file_binary": file_binary,
                },
            }
        ],
    )

    return qdrant_id


def get_all_files(group_id):
    group_files = UploadedFile.objects.filter(group_id=group_id)
    qdrant_ids = [file.qdrant_id for file in group_files]
    result = qdrant_client.retrieve(
        collection_name=QDRANT_COLLECTION_NAME,
        ids=qdrant_ids,
    )
    return result

def search_files_in_group(query, group_id, top_k=10):
    query_vector = generate_vector_from_text(query)
    group_files = UploadedFile.objects.filter(group_id=group_id)
    ids = [file.qdrant_id for file in group_files]
    filter_condition = Filter(
            must=[
                HasIdCondition(has_id=ids),
            ],
        )

    results = qdrant_client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=filter_condition,
    )

    return results




def get_file_from_qdrant(qdrant_id):
    result = qdrant_client.retrieve(
        collection_name=QDRANT_COLLECTION_NAME,
        ids=[str(qdrant_id)]
    )

    if not result:
        raise FileNotFoundError(f"Plik o ID {qdrant_id} nie został znaleziony w Qdrant.")

    point = result[0]

    file_name = point.payload.get("file_name")
    file_binary_base64 = point.payload.get("file_binary")

    # Dekodowanie zawartości pliku z base64
    file_binary = base64.b64decode(file_binary_base64)

    return {
        "file_name": file_name,
        "file_binary": file_binary
    }
def file_delete(file_id):
    try:
        qdrant_client.delete(
            collection_name=QDRANT_COLLECTION_NAME,
            points_selector=PointIdsList(points=[file_id])
        )
        print(f"File with ID {file_id} successfully deleted from Qdrant.")
    except Exception as e:
        print(f"Error deleting file with ID {file_id}: {e}")