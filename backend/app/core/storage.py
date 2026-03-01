import asyncio
from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

_s3_client = None


def get_s3_client():
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.aws_endpoint_url,
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
    return _s3_client


def ensure_bucket_exists() -> None:
    s3 = get_s3_client()
    try:
        s3.head_bucket(Bucket=settings.aws_s3_bucket)
    except ClientError as e:
        code = e.response["Error"]["Code"]
        if code in ("404", "NoSuchBucket"):
            s3.create_bucket(Bucket=settings.aws_s3_bucket)
            # Make bucket public-read so presigned GET URLs work from the browser
            s3.put_bucket_policy(
                Bucket=settings.aws_s3_bucket,
                Policy=f"""{{
                    "Version":"2012-10-17",
                    "Statement":[{{
                        "Effect":"Allow",
                        "Principal":"*",
                        "Action":"s3:GetObject",
                        "Resource":"arn:aws:s3:::{settings.aws_s3_bucket}/*"
                    }}]
                }}""",
            )
        else:
            raise


async def generate_presigned_put_url(key: str, content_type: str, expires: int = 900) -> str:
    s3 = get_s3_client()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: s3.generate_presigned_url(
            "put_object",
            Params={"Bucket": settings.aws_s3_bucket, "Key": key, "ContentType": content_type},
            ExpiresIn=expires,
        )
    )


async def generate_presigned_get_url(key: str, expires: int = 900) -> str:
    s3 = get_s3_client()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.aws_s3_bucket, "Key": key},
            ExpiresIn=expires,
        )
    )

async def generate_presigned_upload_url(s3_key: str, expires_in: int = 3600) -> str:
    """Legacy alias"""
    return await generate_presigned_put_url(s3_key, "application/octet-stream", expires_in)

async def generate_presigned_download_url(s3_key: str, expires_in: int = 3600) -> str:
     """Legacy alias"""
     return await generate_presigned_get_url(s3_key, expires_in)


async def upload_bytes(key: str, data: bytes, content_type: str = "application/octet-stream") -> None:
    s3 = get_s3_client()
    loop = asyncio.get_event_loop()
    def _upload():
        s3.put_object(
            Bucket=settings.aws_s3_bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
    await loop.run_in_executor(None, _upload)


async def download_bytes(key: str) -> bytes:
    s3 = get_s3_client()
    loop = asyncio.get_event_loop()
    def _download():
        response = s3.get_object(Bucket=settings.aws_s3_bucket, Key=key)
        return response["Body"].read()
    return await loop.run_in_executor(None, _download)


async def delete_object(key: str) -> None:
    s3 = get_s3_client()
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: s3.delete_object(Bucket=settings.aws_s3_bucket, Key=key))


async def object_exists(key: str) -> bool:
    s3 = get_s3_client()
    loop = asyncio.get_event_loop()
    def _exists():
        try:
            s3.head_object(Bucket=settings.aws_s3_bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise
    return await loop.run_in_executor(None, _exists)
