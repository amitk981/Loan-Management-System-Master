from datetime import date
from types import SimpleNamespace
from unittest import TestCase
from uuid import uuid4

from sfpcl_credit.applications.modules.nominee_validation import evaluate_nominee_selection


class NomineeValidationModuleTests(TestCase):
    def test_valid_adult_same_member_nominee_is_accepted_through_public_interface(self):
        member_id = uuid4()
        nominee = SimpleNamespace(
            member_id=member_id,
            minor_flag=False,
            age_at_application=42,
            date_of_birth=None,
        )
        member = SimpleNamespace(member_id=member_id)

        result = evaluate_nominee_selection(nominee, member, on_date=date(2026, 7, 10))

        self.assertEqual(result.status, "valid")
        self.assertIsNone(result.field_error)

    def test_public_interface_preserves_missing_cross_member_minor_and_evidence_errors(self):
        member_id = uuid4()
        member = SimpleNamespace(member_id=member_id)
        cases = (
            (None, "pending", "An adult nominee must be selected."),
            (
                self._nominee(member_id=uuid4(), age=42),
                "pending",
                "Selected nominee must belong to the application member.",
            ),
            (
                self._nominee(member_id=member_id, age=16, minor=True),
                "minor",
                "Selected nominee must be at least 18 years old.",
            ),
            (
                self._nominee(member_id=member_id, age=None),
                "pending",
                "Selected nominee requires age or date-of-birth evidence.",
            ),
        )

        for nominee, status, field_error in cases:
            with self.subTest(status=status, field_error=field_error):
                result = evaluate_nominee_selection(
                    nominee,
                    member,
                    on_date=date(2026, 7, 10),
                )
                self.assertEqual(result.status, status)
                self.assertEqual(result.field_error, field_error)

    @staticmethod
    def _nominee(*, member_id, age, minor=False):
        return SimpleNamespace(
            member_id=member_id,
            minor_flag=minor,
            age_at_application=age,
            date_of_birth=None,
        )
