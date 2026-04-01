from minio import Minio
import os
import io

class MinioStorageClient:
    """
    Interface for MinIO Object Storage.
    Stores meshes, binaries, and large artifact files.
    """
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str = "aero-artifacts"):
        self.client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.bucket = bucket_name
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def upload_file(self, object_name: str, file_path: str):
        """
        Uploads a local file to storage.
        """
        self.client.fput_object(self.bucket, object_name, file_path)
        return f"minio://{self.bucket}/{object_name}"

    def upload_stream(self, object_name: str, data_stream: io.BytesIO, length: int):
        """
        Uploads data from an in-memory stream.
        """
        self.client.put_object(self.bucket, object_name, data_stream, length)
        return f"minio://{self.bucket}/{object_name}"

    def download_file(self, object_name: str, local_path: str):
        """
        Downloads an object to a local file.
        """
        self.client.fget_object(self.bucket, object_name, local_path)
        return local_path

if __name__ == "__main__":
    # client = MinioStorageClient("localhost:9000", "minioadmin", "minioadmin")
    print("MinIO Client initialized (Skeleton)")
