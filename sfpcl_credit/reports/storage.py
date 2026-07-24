import hashlib
from dataclasses import dataclass
from pathlib import Path

from django.conf import settings


@dataclass(frozen=True)
class StoredExport:
    storage_key: str
    file_size_bytes: int
    checksum_sha256: str


class LocalReportExportStorage:
    """Local development/test adapter; storage keys never become public URLs."""

    def __init__(self, root=None):
        configured = root or getattr(
            settings,
            "REPORT_EXPORT_STORAGE_ROOT",
            Path(settings.DOCUMENT_STORAGE_ROOT) / "report-exports",
        )
        self.root = Path(configured)

    def store(self, *, export_job_id, export_format, content):
        storage_key = f"report-exports/{export_job_id}.{export_format}"
        target = self._resolve(storage_key)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return StoredExport(
            storage_key=storage_key,
            file_size_bytes=len(content),
            checksum_sha256=hashlib.sha256(content).hexdigest(),
        )

    def read(self, *, storage_key, checksum_sha256, file_size_bytes):
        content = self._resolve(storage_key).read_bytes()
        if (
            len(content) != file_size_bytes
            or hashlib.sha256(content).hexdigest() != checksum_sha256
        ):
            raise ValueError("Report export bytes do not match retained metadata.")
        return content

    def delete(self, storage_key):
        self._resolve(storage_key).unlink(missing_ok=True)

    def _resolve(self, storage_key):
        root = self.root.resolve()
        target = (root / storage_key).resolve()
        if root not in target.parents:
            raise ValueError("Report export storage key escapes the configured root.")
        return target
