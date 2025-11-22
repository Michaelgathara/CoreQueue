import io
from pathlib import Path
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from apps.api.core.config import Settings
from apps.api.core.paths import safe_filename
from apps.api.storage.base import StorageProvider


class LocalStorage(StorageProvider):
    def __init__(self, root_dir: str):
        self.root = Path(root_dir)

    def write(self, path: str, data: bytes | BinaryIO) -> str:
        full_path = self.root / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, "wb") as f:
            if isinstance(data, bytes):
                f.write(data)
            else:
                f.write(data.read())
        return str(full_path)

    def read(self, path: str) -> bytes:
        full_path = self.root / path
        if not full_path.exists():
            return b""
        return full_path.read_bytes()

    def list(self, prefix: str) -> list[str]:
        target = self.root / prefix
        if not target.exists():
            return []
        if target.is_file():
            return [target.name]

        results = []
        for p in target.iterdir():
            if p.is_file():
                results.append(p.name)
        return sorted(results)

    def exists(self, path: str) -> bool:
        return (self.root / path).exists()


class S3Storage(StorageProvider):
    def __init__(self, settings: Settings):
        self.bucket = settings.s3_bucket_name
        self.client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
            region_name=settings.s3_region,
        )

    def write(self, path: str, data: bytes | BinaryIO) -> str:
        if isinstance(data, bytes):
            fileobj = io.BytesIO(data)
        else:
            fileobj = data  # type: ignore

        self.client.upload_fileobj(fileobj, self.bucket, path)
        return path

    def read(self, path: str) -> bytes:
        try:
            buffer = io.BytesIO()
            self.client.download_fileobj(self.bucket, path, buffer)
            buffer.seek(0)
            return buffer.read()
        except ClientError:
            return b""

    def list(self, prefix: str) -> list[str]:
        # S3 is flat, so we list by prefix here
        if not prefix.endswith("/"):
            prefix += "/"

        try:
            response = self.client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)
            if "Contents" not in response:
                return []

            results = []
            for obj in response["Contents"]:
                key = obj["Key"]
                name = key[len(prefix) :]
                if name:
                    results.append(name)
            return sorted(results)
        except ClientError:
            return []

    def exists(self, path: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=path)
            return True
        except ClientError:
            return False


def get_storage(settings: Settings) -> StorageProvider:
    if settings.storage_backend == "s3":
        return S3Storage(settings)
    return LocalStorage(settings.data_root)


def write_artifact(settings: Settings, job_id: str, filename: str, data: bytes) -> str:
    storage = get_storage(settings)
    path = f"artifacts/{job_id}/{safe_filename(filename)}"
    return storage.write(path, data)


def list_artifacts(settings: Settings, job_id: str) -> list[str]:
    storage = get_storage(settings)
    path = f"artifacts/{job_id}"
    return storage.list(path)


def read_artifact(settings: Settings, job_id: str, filename: str) -> bytes:
    storage = get_storage(settings)
    path = f"artifacts/{job_id}/{safe_filename(filename)}"
    return storage.read(path)
