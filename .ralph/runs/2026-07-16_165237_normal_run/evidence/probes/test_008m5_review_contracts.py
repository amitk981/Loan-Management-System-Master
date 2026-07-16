"""Failing-first architecture-review probes selected for corrective slice 008M5."""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[5]


class ReviewContractProbes(unittest.TestCase):
    def test_required_poa_path_has_an_explicit_governed_decision(self):
        source = (
            ROOT / "sfpcl_credit/security_instruments/modules/staff_workspace_actions.py"
        ).read_text()
        if "attorney = None" in source:
            self.fail("required PoA creation is unreachable and no blocker is projected")
        self.assertIn("governed_attorney_unconfigured", source)

    def test_upload_and_correction_use_durable_owner_workflows(self):
        source = (
            ROOT / "sfpcl_credit/legal_documents/modules/staff_workspace_actions.py"
        ).read_text()
        self.assertNotIn("def _execute_upload_signed_copy", source)
        self.assertNotIn("def _execute_workspace_record", source)
        self.assertIn("documentation_actions.upload_signed_copy", source)
        self.assertIn("documentation_actions.record_review_action", source)


if __name__ == "__main__":
    unittest.main(verbosity=2)
