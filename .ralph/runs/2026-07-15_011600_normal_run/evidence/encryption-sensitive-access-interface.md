# Encryption and Sensitive-Access Evidence

- Production reversible owner: `sfpcl_credit.shared.encryption.FieldEncryption`.
- Algorithm: AES-256-GCM through pinned `cryptography==46.0.3`; 96-bit random nonce.
- Authenticated metadata: field name, format version, key version, length, and last four.
- Dedicated configuration: current/previous field key versions, key reference, and lookup-HMAC key;
  no Django `SECRET_KEY` fallback.
- Reveal owner: `sfpcl_credit.documents.modules.sensitive_data_access`.
- CDSL supplies encrypted object facts only; the process resolves canonical scope and locks the row.
- Ordinary security evidence remains masked/redacted and separate from sensitive success/denial audit.
- Retained `seal:v1` code exists only in migration `0004` and is absent from production paths.
