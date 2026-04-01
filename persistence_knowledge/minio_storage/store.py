"""
MinIO Object Storage — Repository for evidences and artifacts.
Manages storage of model checkpoints, session recordings, screenshots,
and other binary artifacts.
"""

import io
import logging
from pathlib import Path
from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

logger = logging.getLogger(__name__)

MODELS_BUCKET = "aspar-models"
SESSIONS_BUCKET = "aspar-sessions"
ARTIFACTS_BUCKET = "aspar-artifacts"


class MinioObjectStore:
    """Manages object storage in MinIO for artifacts and evidence."""

    def __init__(self, endpoint: str = "localhost:9000",
                 access_key: str = "minioadmin",
                 secret_key: str = "minioadmin",
                 secure: bool = False) -> None:
        self.client = Minio(endpoint, access_key=access_key,
                            secret_key=secret_key, secure=secure)
        self._ensure_buckets()

    def _ensure_buckets(self) -> None:
        """Create required buckets if they don't exist."""
        for bucket in [MODELS_BUCKET, SESSIONS_BUCKET, ARTIFACTS_BUCKET]:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
                logger.info("Created MinIO bucket: %s", bucket)

    def upload_model(self, model_name: str, model_version: str,
                     data: BinaryIO, size: int) -> str:
        """Upload a model checkpoint to MinIO."""
        object_name = f"{model_name}/v{model_version}/model.pt"
        self.client.put_object(MODELS_BUCKET, object_name, data, size)
        logger.info("Uploaded model: %s/%s", MODELS_BUCKET, object_name)
        return object_name

    def download_model(self, model_name: str, model_version: str) -> bytes:
        """Download a model checkpoint from MinIO."""
        object_name = f"{model_name}/v{model_version}/model.pt"
        response = self.client.get_object(MODELS_BUCKET, object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def upload_artifact(self, bucket: str, object_name: str,
                        file_path: Path) -> str:
        """Upload a file artifact to MinIO."""
        self.client.fput_object(bucket, object_name, str(file_path))
        logger.info("Uploaded artifact: %s/%s", bucket, object_name)
        return object_name

    def list_artifacts(self, bucket: str,
                       prefix: str = "") -> list[dict[str, str]]:
        """List artifacts in a bucket."""
        objects = self.client.list_objects(bucket, prefix=prefix, recursive=True)
        return [
            {
                "name": obj.object_name,
                "size": str(obj.size),
                "last_modified": obj.last_modified.isoformat() if obj.last_modified else "",
            }
            for obj in objects
        ]

    def delete_artifact(self, bucket: str, object_name: str) -> None:
        """Delete an artifact from MinIO."""
        self.client.remove_object(bucket, object_name)
        logger.info("Deleted artifact: %s/%s", bucket, object_name)
