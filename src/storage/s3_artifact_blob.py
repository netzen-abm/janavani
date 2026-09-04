"""S3-compatible artifact blob provider.

The provider is optional and keeps object-storage details outside
JanaVani document and case capabilities.
"""
from __future__ import annotations

import hashlib
import io
import os
from typing import Any, BinaryIO

from src.storage.artifact_blob import StoredArtifact


class S3ArtifactBlobStore:
    """Store artifacts through any S3-compatible object-storage service."""

    def __init__(
        self,
        bucket: str | None = None,
        *,
        prefix: str | None = None,
        client: Any = None,
        endpoint_url: str | None = None,
    ) -> None:
        self.bucket = bucket or os.getenv("JANAVANI_ARTIFACT_S3_BUCKET")
        if not self.bucket:
            raise ValueError("S3 artifact provider requires a bucket")
        self.prefix = (prefix or os.getenv("JANAVANI_ARTIFACT_S3_PREFIX", "artifacts")).strip("/")
        self.client = client or self._build_client(endpoint_url)

    @staticmethod
    def _build_client(endpoint_url: str | None) -> Any:
        try:
            import boto3
        except ImportError as exc:
            raise RuntimeError(
                "S3 artifact provider requires the optional boto3 dependency"
            ) from exc
        return boto3.client("s3", endpoint_url=endpoint_url)

    def _key(self, storage_key: str) -> str:
        clean = storage_key.lstrip("/")
        return f"{self.prefix}/{clean}" if self.prefix else clean

    def put(
        self,
        storage_key: str,
        content: bytes | BinaryIO,
        *,
        media_type: str,
    ) -> StoredArtifact:
        if isinstance(content, bytes):
            payload = content
        else:
            payload = content.read()
        digest = hashlib.sha256(payload).hexdigest()
        key = self._key(storage_key)
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=payload,
            ContentType=media_type,
            Metadata={"sha256": digest},
        )
        return StoredArtifact(
            storage_ref=f"s3://{self.bucket}/{key}",
            content_sha256=digest,
            size_bytes=len(payload),
            media_type=media_type,
        )

    def open(self, storage_ref: str) -> BinaryIO:
        bucket, key = self._parse_ref(storage_ref)
        response = self.client.get_object(Bucket=bucket, Key=key)
        return io.BytesIO(response["Body"].read())

    def delete(self, storage_ref: str) -> None:
        bucket, key = self._parse_ref(storage_ref)
        self.client.delete_object(Bucket=bucket, Key=key)

    @staticmethod
    def _parse_ref(storage_ref: str) -> tuple[str, str]:
        prefix = "s3://"
        if not storage_ref.startswith(prefix):
            raise ValueError("Invalid S3 artifact storage reference")
        value = storage_ref[len(prefix):]
        bucket, separator, key = value.partition("/")
        if not bucket or not separator or not key:
            raise ValueError("Invalid S3 artifact storage reference")
        return bucket, key
