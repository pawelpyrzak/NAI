import uuid
from io import BytesIO

import fitz
import openpyxl
import torch
from PIL import Image
from PyPDF2 import PdfReader
from docx import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import PointIdsList, PointStruct
from qdrant_client.models import Filter
from qdrant_client.models import HasIdCondition
from qdrant_client.models import VectorParams
from sentence_transformers import SentenceTransformer
from transformers import CLIPModel, CLIPProcessor

from ..models import UploadedFile

QDRANT_COLLECTION_NAME_IMG = "images"
QDRANT_COLLECTION_NAME = "files"

qdrant_client = QdrantClient(host="localhost", port=6333)
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def extract_text_from_file(file, mime_type):
    print(f"Detected MIME type: {mime_type}")

    try:
        if mime_type == "text/plain":  # Plik TXT
            print("Processing TXT file...")
            return file.read().decode('utf-8')

        elif mime_type == "application/pdf":  # Plik PDF
            print("Processing PDF file...")

            #  PyMuPDF (lepsze wydobywanie tekstu)
            try:
                pdf = fitz.open(stream=file.read(), filetype="pdf")
                file.seek(0)  # Reset wskaźnika
                text = "\n".join(page.get_text() for page in pdf)
                if text.strip():
                    return text
            except Exception:
                pass

            # PyPDF2
            reader = PdfReader(file)
            text = "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
            return text if text.strip() else None

        elif mime_type in [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword"
        ]:  # Pliki DOCX i DOC
            print("Processing DOCX file...")
            doc = Document(file)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])

        elif mime_type in [
            "application/vnd.ms-excel",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ]:  # Pliki XLS i XLSX
            print("Processing Excel file...")
            workbook = openpyxl.load_workbook(file)
            sheet = workbook.active
            return "\n".join(" ".join(str(cell.value) for cell in row if cell.value) for row in sheet.iter_rows())

    except Exception as e:
        print(f"Błąd przetwarzania pliku: {e}")

    return None


def generate_vector_384_from_text(text):
    return model.encode(text).tolist()

def generate_vector_512_from_text(text):
    return clip_model.get_text_features(**clip_processor(text=text, return_tensors="pt")).squeeze().tolist()

def is_valid_id(value):
    if isinstance(value, int) and value >= 0:
        return True
    try:
        uuid.UUID(str(value))
        return True
    except ValueError:
        return False


def get_all_files(group_id):
    group_files = UploadedFile.objects.filter(group_id=group_id)
    qdrant_ids = [file.qdrant_id for file in group_files]

    # Filter invalid IDs
    valid_ids = [qid for qid in qdrant_ids if is_valid_id(qid)]
    invalid_ids = set(qdrant_ids) - set(valid_ids)
    if invalid_ids:
        print(f"Invalid qdrant_ids: {invalid_ids}")

    if not valid_ids:
        print("No valid IDs found.")
        return []

    result = qdrant_client.retrieve(
        collection_name=QDRANT_COLLECTION_NAME,
        ids=valid_ids,
    )
    result2 = qdrant_client.retrieve(
        collection_name=QDRANT_COLLECTION_NAME_IMG,
        ids=valid_ids,
    )
    return result + result2


def search_files_in_group(query, ids, limit=5, offset=0):
    query_vector = generate_vector_384_from_text(query)
    query_vector_512= generate_vector_512_from_text(query)
    filter_condition = Filter(
        must=[
            HasIdCondition(has_id=ids),
        ],
    )

    results = qdrant_client.search(
        collection_name=QDRANT_COLLECTION_NAME,
        query_vector=query_vector,
        query_filter=filter_condition,
        limit=limit,  # Liczba wyników
        offset=offset
    )
    results2 = qdrant_client.search(
        collection_name=QDRANT_COLLECTION_NAME_IMG,
        query_vector=query_vector_512,
        query_filter=filter_condition,
        limit=limit,  # Liczba wyników
        offset=offset
    )

    combined_results = results + results2
    print(combined_results)
    sorted_results = sorted(combined_results, key=lambda x: x.score, reverse=True)
    return sorted_results


def file_delete(file_id,is_img):
    if is_img:
        QDRANT_COLLECTION = QDRANT_COLLECTION_NAME_IMG
    else:
        QDRANT_COLLECTION = QDRANT_COLLECTION_NAME
    try:
        qdrant_client.delete(
            collection_name=QDRANT_COLLECTION,
            points_selector=PointIdsList(points=[file_id])
        )
        print(f"File with ID {file_id} successfully deleted from Qdrant.")
    except Exception as e:
        print(f"Error deleting file with ID {file_id}: {e}")


def add_to_qdrant(vector, bucket_name, file_path, file_name,is_img):
    if is_img:
        QDRANT_COLLECTION=QDRANT_COLLECTION_NAME_IMG
    else:
        QDRANT_COLLECTION=QDRANT_COLLECTION_NAME
    print(is_img)
    print(QDRANT_COLLECTION)
    file_uuid = str(uuid.uuid4())
    point = PointStruct(
        id=file_uuid,
        vector=vector,
        payload={
            "file_name": file_name,
            "minio_path": f"{bucket_name}/{file_path}"
        }
    )
    qdrant_client.upsert(collection_name=QDRANT_COLLECTION, points=[point])
    return file_uuid

def extract_image_embedding(image_bytes):
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        image_embedding = model.get_image_features(**inputs)
    return image_embedding.squeeze().tolist()

def generate_image_vector(image_file):
    image = Image.open(image_file)
    if image.mode != "RGB":
        image = image.convert("RGB")

    inputs = clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        outputs = clip_model.get_image_features(**inputs)

    vector = outputs.squeeze().tolist()
    return vector
