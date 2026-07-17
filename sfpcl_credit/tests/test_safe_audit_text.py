from django.test import SimpleTestCase


class SafeAuditTextTests(SimpleTestCase):
    def test_accepts_reviewable_text_and_rejects_sensitive_or_invalid_text(self):
        from sfpcl_credit.shared.audit_text import (
            SAFE_AUDIT_TEXT_ERROR,
            UnsafeAuditText,
            safe_audit_text,
        )

        self.assertEqual(
            safe_audit_text(
                "  Move settlement routing to the verified operating account.  ",
                max_length=500,
            ),
            "Move settlement routing to the verified operating account.",
        )

        protected_values = (
            "field:v2:k2:current-bank-token",
            "current-bank-hash",
        )
        unsafe_values = (
            "   ",
            "x" * 501,
            "Unsafe\ncontrol character",
            "Account 123456789012",
            "Account 1234-5678-9012",
            "Account 1234 5678 9012",
            "Account 1234/5678/9012",
            "Use field:v1:k1:legacy-token",
            "Use field:v2:k9:other-module-token",
            "Use field:v37:k9:future-token",
            "Use enc:v2:legacy-token",
            "Use AES-GCM protected content",
            "Use ciphertext:protected-content",
            "Use 17f8b6a94f7bcafbcf0a8f73364d4a86eaa20b2eb8e6318104ff87cb7f1703b4",
            "Use current-bank-hash in the ticket",
        )
        for value in unsafe_values:
            with self.subTest(value=value[:40]):
                with self.assertRaisesRegex(
                    UnsafeAuditText, f"^{SAFE_AUDIT_TEXT_ERROR}$"
                ) as raised:
                    safe_audit_text(
                        value,
                        max_length=500,
                        protected_values=protected_values,
                    )
                if value.strip():
                    self.assertNotIn(value.strip(), str(raised.exception))
