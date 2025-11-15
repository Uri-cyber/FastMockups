"""
Cloud storage integration for mockups
Supports AWS S3, Google Cloud Storage, Azure Blob Storage
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
import os
from abc import ABC, abstractmethod


class CloudStorageProvider(ABC):
    """
    Abstract base class for cloud storage providers
    """

    @abstractmethod
    def upload_file(
        self, local_path: Path, remote_path: str, metadata: Optional[Dict] = None
    ) -> bool:
        """Upload a file to cloud storage"""
        pass

    @abstractmethod
    def download_file(self, remote_path: str, local_path: Path) -> bool:
        """Download a file from cloud storage"""
        pass

    @abstractmethod
    def list_files(self, prefix: str = "") -> List[str]:
        """List files in cloud storage"""
        pass

    @abstractmethod
    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from cloud storage"""
        pass

    @abstractmethod
    def get_public_url(self, remote_path: str) -> Optional[str]:
        """Get public URL for a file"""
        pass


class S3Storage(CloudStorageProvider):
    """
    AWS S3 storage provider
    """

    def __init__(
        self,
        bucket_name: str,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        region: str = "us-east-1",
    ):
        self.bucket_name = bucket_name
        self.region = region

        try:
            import boto3

            # Initialize S3 client
            if aws_access_key_id and aws_secret_access_key:
                self.s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    region_name=region,
                )
            else:
                # Use default credentials (from ~/.aws/credentials or environment)
                self.s3_client = boto3.client("s3", region_name=region)

            self.available = True
        except ImportError:
            print("boto3 not installed. Install with: pip install boto3")
            self.available = False
        except Exception as e:
            print(f"Failed to initialize S3 client: {e}")
            self.available = False

    def upload_file(
        self, local_path: Path, remote_path: str, metadata: Optional[Dict] = None
    ) -> bool:
        if not self.available:
            return False

        try:
            extra_args = {}
            if metadata:
                extra_args["Metadata"] = metadata

            # Set content type based on file extension
            content_type = self._get_content_type(local_path)
            if content_type:
                extra_args["ContentType"] = content_type

            self.s3_client.upload_file(
                str(local_path), self.bucket_name, remote_path, ExtraArgs=extra_args
            )
            print(f"Uploaded to S3: s3://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            print(f"S3 upload failed: {e}")
            return False

    def download_file(self, remote_path: str, local_path: Path) -> bool:
        if not self.available:
            return False

        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(self.bucket_name, remote_path, str(local_path))
            print(f"Downloaded from S3: {remote_path}")
            return True
        except Exception as e:
            print(f"S3 download failed: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        if not self.available:
            return []

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except Exception as e:
            print(f"S3 list failed: {e}")
            return []

    def delete_file(self, remote_path: str) -> bool:
        if not self.available:
            return False

        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=remote_path)
            print(f"Deleted from S3: {remote_path}")
            return True
        except Exception as e:
            print(f"S3 delete failed: {e}")
            return False

    def get_public_url(self, remote_path: str) -> Optional[str]:
        if not self.available:
            return None

        return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{remote_path}"

    def _get_content_type(self, file_path: Path) -> Optional[str]:
        """Get content type based on file extension"""
        ext = file_path.suffix.lower()
        content_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".pdf": "application/pdf",
            ".gif": "image/gif",
        }
        return content_types.get(ext)


class GCSStorage(CloudStorageProvider):
    """
    Google Cloud Storage provider
    """

    def __init__(
        self,
        bucket_name: str,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None,
    ):
        self.bucket_name = bucket_name

        try:
            from google.cloud import storage

            # Initialize GCS client
            if credentials_path:
                self.storage_client = storage.Client.from_service_account_json(
                    credentials_path
                )
            else:
                self.storage_client = storage.Client(project=project_id)

            self.bucket = self.storage_client.bucket(bucket_name)
            self.available = True
        except ImportError:
            print("google-cloud-storage not installed. Install with: pip install google-cloud-storage")
            self.available = False
        except Exception as e:
            print(f"Failed to initialize GCS client: {e}")
            self.available = False

    def upload_file(
        self, local_path: Path, remote_path: str, metadata: Optional[Dict] = None
    ) -> bool:
        if not self.available:
            return False

        try:
            blob = self.bucket.blob(remote_path)

            if metadata:
                blob.metadata = metadata

            blob.upload_from_filename(str(local_path))
            print(f"Uploaded to GCS: gs://{self.bucket_name}/{remote_path}")
            return True
        except Exception as e:
            print(f"GCS upload failed: {e}")
            return False

    def download_file(self, remote_path: str, local_path: Path) -> bool:
        if not self.available:
            return False

        try:
            local_path.parent.mkdir(parents=True, exist_ok=True)
            blob = self.bucket.blob(remote_path)
            blob.download_to_filename(str(local_path))
            print(f"Downloaded from GCS: {remote_path}")
            return True
        except Exception as e:
            print(f"GCS download failed: {e}")
            return False

    def list_files(self, prefix: str = "") -> List[str]:
        if not self.available:
            return []

        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"GCS list failed: {e}")
            return []

    def delete_file(self, remote_path: str) -> bool:
        if not self.available:
            return False

        try:
            blob = self.bucket.blob(remote_path)
            blob.delete()
            print(f"Deleted from GCS: {remote_path}")
            return True
        except Exception as e:
            print(f"GCS delete failed: {e}")
            return False

    def get_public_url(self, remote_path: str) -> Optional[str]:
        if not self.available:
            return None

        blob = self.bucket.blob(remote_path)
        return blob.public_url


class CloudStorageManager:
    """
    Unified manager for cloud storage operations
    """

    def __init__(self):
        self.providers: Dict[str, CloudStorageProvider] = {}

    def add_provider(self, name: str, provider: CloudStorageProvider):
        """Add a cloud storage provider"""
        self.providers[name] = provider
        print(f"Added cloud storage provider: {name}")

    def upload_mockups(
        self,
        local_folder: Path,
        provider_name: str,
        remote_folder: str = "mockups",
        file_pattern: str = "*.png",
    ) -> Dict[str, bool]:
        """
        Upload all mockups from a folder to cloud storage

        Args:
            local_folder: Local folder containing mockups
            provider_name: Name of provider to use
            remote_folder: Remote folder path
            file_pattern: Glob pattern for files to upload

        Returns:
            Dict mapping filename to upload success status
        """
        if provider_name not in self.providers:
            print(f"Provider '{provider_name}' not found")
            return {}

        provider = self.providers[provider_name]
        results = {}

        for file_path in local_folder.glob(file_pattern):
            remote_path = f"{remote_folder}/{file_path.name}"
            success = provider.upload_file(file_path, remote_path)
            results[file_path.name] = success

        return results

    def get_provider(self, name: str) -> Optional[CloudStorageProvider]:
        """Get a cloud storage provider by name"""
        return self.providers.get(name)

    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self.providers.keys())


# Convenience factory functions
def create_s3_storage(bucket_name: str, **kwargs) -> S3Storage:
    """Create S3 storage provider"""
    return S3Storage(bucket_name, **kwargs)


def create_gcs_storage(bucket_name: str, **kwargs) -> GCSStorage:
    """Create GCS storage provider"""
    return GCSStorage(bucket_name, **kwargs)
