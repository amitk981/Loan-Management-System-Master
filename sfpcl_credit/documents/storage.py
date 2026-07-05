import hashlib
import os
import uuid
from dataclasses import dataclass
from pathlib import Path, PurePath

from django.conf import settings


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


def safe_file_name(raw_name):
    name = PurePath(raw_name or "uploaded-file").name
    return name.replace(os.sep, "_") or "uploaded-file"
