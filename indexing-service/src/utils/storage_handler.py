# src/utils/storage_handler.py
import os
from typing import Optional
_logger = None
try:
    from minio import Minio
    from minio.error import S3Error
except Exception:
    Minio = None
    S3Error = Exception

if _logger is None:
    from .logger import setup_logger
    _logger = setup_logger(__name__)


class StorageHandler:
    """
    Minimal wrapper around Minio. If minio client not available, fallback to local filesystem
    under /tmp/minio_fallback (or env MINIO_FALLBACK_DIR).
    """

    def __init__(self, endpoint: Optional[str] = None, access_key: Optional[str] = None,
                 secret_key: Optional[str] = None, secure: bool = False):
        self._logger = _logger
        self._use_minio = False
        if Minio and endpoint and access_key and secret_key:
            try:
                self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)
                self._use_minio = True
                self._logger.debug("Using Minio storage backend")
            except Exception:
                self._logger.warning("Could not initialize Minio client, falling back to local storage")
                self.client = None
        else:
            self.client = None
            self._logger.debug("Minio client not configured - using local fallback")

        self._fallback_dir = os.getenv("MINIO_FALLBACK_DIR", "/tmp/minio_fallback")
        os.makedirs(self._fallback_dir, exist_ok=True)

    def upload_file(self, bucket: str, object_name: str, file_path: str) -> bool:
        if self._use_minio and self.client:
            try:
                # ensure bucket exists
                if not self.client.bucket_exists(bucket):
                    self.client.make_bucket(bucket)
                self.client.fput_object(bucket, object_name, file_path)
                return True
            except Exception as e:
                self._logger.exception("Minio upload failed: %s", e)
                return False
        else:
            dest_dir = os.path.join(self._fallback_dir, bucket)
            os.makedirs(dest_dir, exist_ok=True)
            dest = os.path.join(dest_dir, object_name)
            try:
                with open(file_path, "rb") as fr, open(dest, "wb") as fw:
                    fw.write(fr.read())
                return True
            except Exception:
                self._logger.exception("Local file copy failed")
                return False

    def download_file(self, bucket: str, object_name: str, dest_path: str) -> bool:
        if self._use_minio and self.client:
            try:
                self.client.fget_object(bucket, object_name, dest_path)
                return True
            except Exception:
                self._logger.exception("Minio download failed")
                return False
        else:
            src = os.path.join(self._fallback_dir, bucket, object_name)
            try:
                with open(src, "rb") as fr, open(dest_path, "wb") as fw:
                    fw.write(fr.read())
                return True
            except Exception:
                self._logger.exception("Local download failed")
                return False
