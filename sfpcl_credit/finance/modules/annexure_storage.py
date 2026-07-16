"""Encrypted-at-rest storage boundary for restricted SAP Annexure-I workbooks."""

import base64
import binascii

from django.core.files.uploadedfile import SimpleUploadedFile

from sfpcl_credit.documents.storage import LocalDocumentStorage
from sfpcl_credit.shared.encryption import FieldEncryption, InvalidCiphertext


_ENCRYPTION_CONTEXT = "finance.sap_request.annexure_i"


class EncryptedAnnexureStorage:
    """Store ciphertext physically while exposing verified XLSX bytes to Finance."""

    def __init__(self, backend=None):
        self.backend = backend or LocalDocumentStorage()

    def store(self, uploaded_file):
        plaintext = b"".join(uploaded_file.chunks())
        encoded = base64.urlsafe_b64encode(plaintext).decode("ascii")
        ciphertext = FieldEncryption.encrypt(_ENCRYPTION_CONTEXT, encoded).encode("ascii")
        encrypted_upload = SimpleUploadedFile(
            uploaded_file.name,
            ciphertext,
            content_type="application/octet-stream",
        )
        return self.backend.store(encrypted_upload)

    def delete(self, stored_file):
        self.backend.delete(stored_file)

    def read_verified(self, document):
        token = self.backend.read_verified(document)
        try:
            encoded = FieldEncryption.decrypt(
                _ENCRYPTION_CONTEXT, token.decode("ascii")
            )
            return base64.b64decode(encoded, altchars=b"-_", validate=True)
        except (UnicodeDecodeError, InvalidCiphertext, binascii.Error) as exc:
            raise ValueError("Encrypted Annexure-I bytes failed verification.") from exc
