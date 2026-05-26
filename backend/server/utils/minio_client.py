import uuid
from pathlib import Path
from minio import Minio
from minio.error import S3Error
from server.config import get_settings

settings = get_settings()

_client: Minio | None = None


def get_minio_client() -> Minio:
    global _client
    if _client is None:
        _client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        bucket = settings.MINIO_BUCKET
        if not _client.bucket_exists(bucket):
            _client.make_bucket(bucket)
    return _client


async def upload_avatar(file_bytes: bytes, file_ext: str) -> str:
    client = get_minio_client()
    bucket = settings.MINIO_BUCKET
    object_name = f"avatars/{uuid.uuid4()}{file_ext}"
    content_type = "image/jpeg"
    if file_ext == ".png":
        content_type = "image/png"
    elif file_ext == ".webp":
        content_type = "image/webp"
    elif file_ext == ".gif":
        content_type = "image/gif"
    client.put_object(
        bucket,
        object_name,
        data=__import__("io").BytesIO(file_bytes),
        length=len(file_bytes),
        content_type=content_type,
    )
    public_url = settings.MINIO_PUBLIC_URL.rstrip("/")
    return f"{public_url}/{bucket}/{object_name}"


ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def validate_image_ext(filename: str) -> str | None:
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_EXTENSIONS:
        return ext
    return None
