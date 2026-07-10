import importlib.util
import tempfile
import unittest
from pathlib import Path


VERIFIER_PATH = Path(__file__).with_name("verify_postgresql_acceptance.py")
SPEC = importlib.util.spec_from_file_location("postgresql_acceptance_verifier", VERIFIER_PATH)
VERIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VERIFIER)


class PostgreSQLAcceptanceVerifierTests(unittest.TestCase):
    def write_log(self, content):
        handle = tempfile.NamedTemporaryFile(mode="w", delete=False)
        self.addCleanup(Path(handle.name).unlink, missing_ok=True)
        with handle:
            handle.write(content)
        return Path(handle.name)

    def test_accepts_exactly_two_complete_five_test_postgresql_runs(self):
        complete = """Found 5 test(s).
database_backend=postgresql ordering=winner -> loser
Ran 5 tests in 1.000s
OK
"""

        VERIFIER.verify_acceptance_logs(
            [self.write_log(complete), self.write_log(complete)]
        )

    def test_rejects_incomplete_skipped_failed_or_non_postgresql_packets(self):
        invalid_packets = (
            "Found 5 test(s).\n",
            "Found 5 test(s).\nRan 5 tests in 1.000s\nOK (skipped=5)\n",
            "Found 5 test(s).\nconnection refused\nRan 0 tests\nFAILED\n",
            "Found 5 test(s).\nRan 5 tests in 1.000s\nOK\n",
        )

        for content in invalid_packets:
            with self.subTest(content=content):
                with self.assertRaises(VERIFIER.AcceptanceEvidenceError):
                    VERIFIER.verify_acceptance_logs(
                        [self.write_log(content), self.write_log(content)]
                    )

    def test_rejects_any_count_other_than_two_logs(self):
        complete = """Found 5 test(s).
database_backend=postgresql ordering=winner -> loser
Ran 5 tests in 1.000s
OK
"""

        for logs in ([], [self.write_log(complete)]):
            with self.subTest(log_count=len(logs)):
                with self.assertRaises(VERIFIER.AcceptanceEvidenceError):
                    VERIFIER.verify_acceptance_logs(logs)


if __name__ == "__main__":
    unittest.main()
