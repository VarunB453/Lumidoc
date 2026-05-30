"""AWS S3 client wrapper for file storage operations."""
from __future__ import annotations

import aioboto3

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger("s3_client")


def _get_session() -> aioboto3.Session:
    """Create an aioboto3 session."""
    return aioboto3.Session(
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID or None,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY or None,
        region_name=settings.AWS_REGION,
    )


async def upload_file(
    file_bytes: bytes,
    key: str,
    content_type: str = "application/octet-stream",
    bucket: str | None = None,
) -> str:
    """Upload a file to S3 and return the key."""
    bucket = bucket or settings.S3_BUCKET_NAME
    session = _get_session()
    async with session.client("s3") as s3:
        await s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=file_bytes,
            ContentType=content_type,
        )
    logger.info("s3_file_uploaded", key=key, bucket=bucket)
    return key


async def generate_presigned_url(
    key: str,
    bucket: str | None = None,
    expires_in: int | None = None,
) -> str:
    """Generate a presigned URL for downloading a file."""
    bucket = bucket or settings.S3_BUCKET_NAME
    expires_in = expires_in or settings.S3_PRESIGNED_URL_TTL
    session = _get_session()
    async with session.client("s3") as s3:
        url = await s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": key},
            ExpiresIn=expires_in,
        )
    return url


async def delete_file(key: str, bucket: str | None = None) -> None:
    """Delete a file from S3."""
    bucket = bucket or settings.S3_BUCKET_NAME
    session = _get_session()
    async with session.client("s3") as s3:
        await s3.delete_object(Bucket=bucket, Key=key)
    logger.info("s3_file_deleted", key=key, bucket=bucket)


async def file_exists(key: str, bucket: str | None = None) -> bool:
    """Check if a file exists in S3."""
    bucket = bucket or settings.S3_BUCKET_NAME
    session = _get_session()
    try:
        async with session.client("s3") as s3:
            await s3.head_object(Bucket=bucket, Key=key)
        return True
    except Exception:
        return False
