"""Review-only probe for source-bank rationale audit redaction."""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")

import django

django.setup()

from sfpcl_credit.configurations.modules.source_bank_governance import (  # noqa: E402
    _clean_reason,
)


unsafe_reasons = (
    "Move treasury funds to account 1234-5678-9012.",
    "Investigate unrelated field:v2:k9:secret-ciphertext-token.",
)
accepted = []
for reason in unsafe_reasons:
    try:
        accepted.append(_clean_reason(reason))
    except Exception as exc:  # pragma: no cover - review output only
        print(f"rejected={reason!r}; exception={type(exc).__name__}")

print(f"unsafe_reason_count={len(unsafe_reasons)}")
print(f"accepted_unsafe_reasons={accepted!r}")
if accepted:
    raise SystemExit(
        "REPRODUCED: formatted bank numbers and unrelated field-encryption tokens "
        "pass the rationale validator and can enter audit/version evidence."
    )
