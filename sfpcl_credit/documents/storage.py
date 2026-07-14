import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePath
from urllib.parse import urlencode

from django.conf import settings
from django.utils import timezone


LOCAL_STORAGE_PROVIDER = "local"


@dataclass(frozen=True)
class StoredFile:
    storage_provider: str
    storage_key: str
    file_size_bytes: int
    checksum_sha256: str


class LocalDocumentStorage:
    """Local filesystem adapter for dev/test document bytes."""

    storage_provider = LOCAL_STORAGE_PROVIDER

    def __init__(self, root=None):
        self.root = Path(root or settings.DOCUMENT_STORAGE_ROOT)

    def store(self, uploaded_file):
        safe_name = safe_file_name(uploaded_file.name)
        storage_key = f"document-files/{uuid.uuid4()}/{safe_name}"
        target_path = self.root / storage_key
        target_path.parent.mkdir(parents=True, exist_ok=True)

        checksum = hashlib.sha256()
        size = 0
        with target_path.open("wb") as target:
            for chunk in uploaded_file.chunks():
                checksum.update(chunk)
                size += len(chunk)
                target.write(chunk)

        return StoredFile(
            storage_provider=self.storage_provider,
            storage_key=storage_key,
            file_size_bytes=size,
            checksum_sha256=checksum.hexdigest(),
        )

    def delete(self, stored_file):
        target_path = self.root / stored_file.storage_key
        target_path.unlink(missing_ok=True)
        parent = target_path.parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()

    def read_verified(self, document):
        root = self.root.resolve()
        target_path = (root / document.storage_key).resolve()
        if root not in target_path.parents:
            raise ValueError("Document storage key escapes the configured root.")
        content = target_path.read_bytes()
        checksum = hashlib.sha256(content).hexdigest()
        if checksum != document.checksum_sha256 or len(content) != document.file_size_bytes:
            raise ValueError("Document bytes do not match retained metadata.")
        return content

    def download_descriptor(self, document):
        ttl_minutes = getattr(settings, "DOCUMENT_DOWNLOAD_URL_TTL_MINUTES", 15)
        expires_at = timezone.now() + timezone.timedelta(minutes=ttl_minutes)
        expires_value = expires_at.isoformat().replace("+00:00", "Z")
        query = urlencode({"expires_at": expires_value})
        return {
            "download_url": (
                f"/api/v1/local-document-files/{document.document_id}/download/?{query}"
            ),
            "expires_at": expires_value,
        }


def safe_file_name(raw_name):
    name = PurePath(raw_name or "uploaded-file").name
    return name.replace(os.sep, "_") or "uploaded-file"
