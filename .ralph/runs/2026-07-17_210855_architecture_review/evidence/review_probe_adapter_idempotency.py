"""Review-only probe: a stable provider key must identify one logical email."""

import os
import uuid

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sfpcl_credit.config.settings")

import django

django.setup()

from sfpcl_credit.communications.adapters import (  # noqa: E402
    EmailDeliveryPayload,
    ManualEmailDeliveryAdapter,
)


intent_id = uuid.UUID("eddf42df-078f-49fd-9a9a-9c41ef03028b")
key = f"disbursement-advice:{intent_id}"
base = dict(
    communication_id=intent_id,
    recipient_email="borrower@example.test",
    subject="Disbursement advice",
    related_entity_type="disbursement",
    related_entity_id=uuid.UUID("79b0deef-9c38-45b5-8364-bfba51c279fc"),
)

first = ManualEmailDeliveryAdapter().send_email(
    EmailDeliveryPayload(body_text="Original retained content", **base), key
)
retry_after_unretained_acceptance = ManualEmailDeliveryAdapter().send_email(
    EmailDeliveryPayload(body_text="Changed content after crash", **base), key
)

print(f"idempotency_key={key}")
print(f"first_external_message_id={first.external_message_id}")
print(
    "retry_external_message_id="
    f"{retry_after_unretained_acceptance.external_message_id}"
)
print(
    "same_logical_provider_identity="
    f"{first.external_message_id == retry_after_unretained_acceptance.external_message_id}"
)

if first.external_message_id != retry_after_unretained_acceptance.external_message_id:
    raise SystemExit(
        "REPRODUCED: one stable idempotency key can identify two provider messages "
        "when acceptance precedes durable receipt retention."
    )
