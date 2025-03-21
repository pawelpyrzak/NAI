import uuid
from decouple import config
import boto3
from django.core.exceptions import ValidationError
from io import BytesIO

# Konfiguracja MinIO (boto3)
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = config("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = config("MINIO_SECRET_KEY")

s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=MINIO_ACCESS_KEY,
    aws_secret_access_key=MINIO_SECRET_KEY
)


def upload_to_minio(file, group_id):
    """Wgrywa plik do MinIO przy użyciu boto3."""
    bucket_name = f"group-{group_id}"

    try:
        # Sprawdzanie, czy bucket istnieje (boto3 nie ma `bucket_exists`, trzeba obsłużyć wyjątek)
        s3_client.head_bucket(Bucket=bucket_name)
    except Exception:
        try:
            s3_client.create_bucket(Bucket=bucket_name)
        except Exception as e:
            raise ValidationError(f"Błąd przy tworzeniu bucketu: {e}")

    file_uuid = str(uuid.uuid4())
    file_path = f"{file_uuid}/{file.name}"

    try:
        s3_client.put_object(Bucket=bucket_name, Key=file_path, Body=file, ContentType=file.content_type)
    except Exception as e:
        raise ValidationError(f"Błąd przy wgrywaniu pliku do MinIO: {e}")

    return bucket_name, file_path


def get_file_from_minio(file):
    """Pobiera plik z MinIO jako BytesIO."""
    bucket_name = f"group-{file.group.id}"
    file_path = file.minio_path

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=file_path)
        return BytesIO(response["Body"].read())
    except Exception as e:
        raise ValidationError(f"Błąd przy pobieraniu pliku z MinIO: {e}")


def delete_file_from_minio(group_id, minio_path):
    """Usuwa plik z MinIO."""
    bucket_name = f"group-{group_id}"

    try:
        s3_client.delete_object(Bucket=bucket_name, Key=minio_path)
    except Exception as e:
        raise ValidationError(f"Błąd przy usuwaniu pliku z MinIO: {e}")
