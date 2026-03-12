from __future__ import annotations

import mimetypes
import os
import uuid
from functools import lru_cache

import boto3
from fastapi import HTTPException, UploadFile

from app.core.config import get_settings


class ImageStorage:
    def __init__(self) -> None:
        s = get_settings()
        if s.storage_provider.lower() != "s3":
            raise RuntimeError("Only S3-compatible storage is supported for now (STORAGE_PROVIDER=s3).")

        if not s.s3_bucket:
            raise RuntimeError("S3_BUCKET is not configured.")

        session_kwargs: dict = {}
        client_kwargs: dict = {"region_name": s.s3_region}

        if s.s3_access_key_id and s.s3_secret_access_key:
            session_kwargs["aws_access_key_id"] = s.s3_access_key_id
            session_kwargs["aws_secret_access_key"] = s.s3_secret_access_key

        if s.s3_endpoint_url:
            client_kwargs["endpoint_url"] = s.s3_endpoint_url

        session = boto3.session.Session(**session_kwargs)
        self.client = session.client("s3", **client_kwargs)
        self.bucket = s.s3_bucket
        self.public_base = s.s3_public_base_url

    async def upload_image(self, file: UploadFile) -> str:
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")

        ext = mimetypes.guess_extension(file.content_type.split(";")[0].strip()) or ""
        key = f"ideas/{uuid.uuid4().hex}{ext}"

        try:
            self.client.upload_fileobj(
                file.file,
                self.bucket,
                key,
                ExtraArgs={"ContentType": file.content_type, "ACL": "public-read"},
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error uploading image: {e}") from e

        if self.public_base:
            return f"{self.public_base.rstrip('/')}/{key}"

        # Fallback: S3-style URL
        s = get_settings()
        region = s.s3_region or "us-east-1"
        return f"https://{self.bucket}.s3.{region}.amazonaws.com/{key}"


@lru_cache
def get_image_storage() -> ImageStorage:
    return ImageStorage()

