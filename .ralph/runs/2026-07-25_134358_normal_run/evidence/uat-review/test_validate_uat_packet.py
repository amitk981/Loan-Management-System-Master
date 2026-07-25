import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate_uat_packet.py"
EXPECTED_COMMIT = "767b1f29c4dae0634a8af8c01513f57ec81dedef"


def run_validator(repo_root, index, packet, as_of="2026-07-25T14:00:00+05:30"):
    return subprocess.run(
        [
            sys.executable,
            str(VALIDATOR),
            "--repo-root",
            str(repo_root),
            "--index",
            str(index),
            "--packet",
            str(packet),
            "--expected-commit",
            EXPECTED_COMMIT,
            "--as-of",
            as_of,
        ],
        check=False,
        capture_output=True,
        text=True,
    )


def valid_index(evidence):
    return {
        "schema_version": 1,
        "candidate_commit": EXPECTED_COMMIT,
        "generated_at": "2026-07-25T14:00:00+05:30",
        "engineering_readiness": "NOT_READY",
        "business_approval": "NOT_APPROVED",
        "uat": [],
        "gates": [],
        "defects": [],
        "signoffs": [],
        "evidence": evidence,
    }


class UatPacketValidatorTests(unittest.TestCase):
    def test_missing_evidence_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            index = repo_root / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "candidate_commit": EXPECTED_COMMIT,
                        "generated_at": "2026-07-25T14:00:00+05:30",
                        "engineering_readiness": "NOT_READY",
                        "business_approval": "NOT_APPROVED",
                        "uat": [],
                        "gates": [],
                        "defects": [],
                        "signoffs": [],
                        "evidence": [
                            {
                                "id": "E-MISSING",
                                "path": "missing.log",
                                "sha256": "0" * 64,
                                "source_commit": EXPECTED_COMMIT,
                                "produced_at": "2026-07-25T13:45:00+05:30",
                                "expires_at": "2026-07-26T13:45:00+05:30",
                                "producer": "Ralph",
                                "result": "PASS",
                                "counts": {"passed": 1, "failed": 0, "skipped": 0},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--repo-root",
                    str(repo_root),
                    "--index",
                    str(index),
                    "--packet",
                    str(packet),
                    "--expected-commit",
                    EXPECTED_COMMIT,
                    "--as-of",
                    "2026-07-25T14:00:00+05:30",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("MISSING_FILE", completed.stdout)

    def test_changed_evidence_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            evidence_file = repo_root / "evidence.log"
            evidence_file.write_text("changed evidence\n", encoding="utf-8")
            index = repo_root / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "candidate_commit": EXPECTED_COMMIT,
                        "generated_at": "2026-07-25T14:00:00+05:30",
                        "engineering_readiness": "NOT_READY",
                        "business_approval": "NOT_APPROVED",
                        "uat": [],
                        "gates": [],
                        "defects": [],
                        "signoffs": [],
                        "evidence": [
                            {
                                "id": "E-TAMPERED",
                                "path": "evidence.log",
                                "sha256": "0" * 64,
                                "source_commit": EXPECTED_COMMIT,
                                "produced_at": "2026-07-25T13:45:00+05:30",
                                "expires_at": "2026-07-26T13:45:00+05:30",
                                "producer": "Ralph",
                                "result": "PASS",
                                "counts": {"passed": 1, "failed": 0, "skipped": 0},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--repo-root",
                    str(repo_root),
                    "--index",
                    str(index),
                    "--packet",
                    str(packet),
                    "--expected-commit",
                    EXPECTED_COMMIT,
                    "--as-of",
                    "2026-07-25T14:00:00+05:30",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("HASH_MISMATCH", completed.stdout)

    def test_wrong_candidate_commit_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            evidence_file = repo_root / "evidence.log"
            evidence_file.write_text("retained evidence\n", encoding="utf-8")
            index = repo_root / "index.json"
            index.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "candidate_commit": "1" * 40,
                        "generated_at": "2026-07-25T14:00:00+05:30",
                        "engineering_readiness": "NOT_READY",
                        "business_approval": "NOT_APPROVED",
                        "uat": [],
                        "gates": [],
                        "defects": [],
                        "signoffs": [],
                        "evidence": [
                            {
                                "id": "E-VALID",
                                "path": "evidence.log",
                                "sha256": hashlib.sha256(
                                    evidence_file.read_bytes()
                                ).hexdigest(),
                                "source_commit": EXPECTED_COMMIT,
                                "produced_at": "2026-07-25T13:45:00+05:30",
                                "expires_at": "2026-07-26T13:45:00+05:30",
                                "producer": "Ralph",
                                "result": "PASS",
                                "counts": {"passed": 1, "failed": 0, "skipped": 0},
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--repo-root",
                    str(repo_root),
                    "--index",
                    str(index),
                    "--packet",
                    str(packet),
                    "--expected-commit",
                    EXPECTED_COMMIT,
                    "--as-of",
                    "2026-07-25T14:00:00+05:30",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("WRONG_CANDIDATE_COMMIT", completed.stdout)

    def test_expired_evidence_fails_closed(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            evidence_file = repo_root / "evidence.log"
            evidence_file.write_text("retained evidence\n", encoding="utf-8")
            index = repo_root / "index.json"
            index.write_text(
                json.dumps(
                    valid_index(
                        [
                            {
                                "id": "E-EXPIRED",
                                "path": "evidence.log",
                                "sha256": hashlib.sha256(
                                    evidence_file.read_bytes()
                                ).hexdigest(),
                                "source_commit": EXPECTED_COMMIT,
                                "produced_at": "2026-07-24T12:00:00+05:30",
                                "expires_at": "2026-07-25T12:00:00+05:30",
                                "producer": "Ralph",
                                "result": "PASS",
                                "counts": {"passed": 1, "failed": 0, "skipped": 0},
                            }
                        ]
                    )
                ),
                encoding="utf-8",
            )

            completed = run_validator(repo_root, index, packet)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("STALE_EVIDENCE", completed.stdout)

    def test_duplicate_or_unmapped_uat_script_fails_reconciliation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            index_data = valid_index([])
            index_data["uat"] = [
                {
                    "id": "UAT-001",
                    "status": "MISSING",
                    "actor": "Credit Manager",
                    "owner": "Product/Business",
                    "reason": "Not executed",
                    "evidence_ids": [],
                },
                {
                    "id": "UAT-001",
                    "status": "MISSING",
                    "actor": "Credit Manager",
                    "owner": "Product/Business",
                    "reason": "Duplicate mapping",
                    "evidence_ids": [],
                },
                {
                    "id": "UAT-999",
                    "status": "MISSING",
                    "actor": "Unknown",
                    "owner": "Product/Business",
                    "reason": "Unmapped script",
                    "evidence_ids": [],
                },
            ]
            index = repo_root / "index.json"
            index.write_text(json.dumps(index_data), encoding="utf-8")

            completed = run_validator(repo_root, index, packet)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("UAT_RECONCILIATION", completed.stdout)

    def test_unmapped_qa_gate_fails_reconciliation(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            index_data = valid_index([])
            index_data["gates"] = [
                {
                    "id": "QA-UNKNOWN",
                    "status": "MISSING",
                    "mandatory": True,
                    "owner": "QA",
                    "reason": "Not a mapped source gate",
                    "evidence_ids": [],
                }
            ]
            index = repo_root / "index.json"
            index.write_text(json.dumps(index_data), encoding="utf-8")

            completed = run_validator(repo_root, index, packet)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("GATE_RECONCILIATION", completed.stdout)

    def test_ready_claim_rejects_gate_defect_and_signoff_blockers(self):
        cases = {
            "mandatory skip": (
                {
                    "gates": [
                        {
                            "id": "QA-ENTRY-BUILD",
                            "status": "SKIPPED",
                            "mandatory": True,
                            "owner": "QA",
                            "reason": "Mandatory gate was skipped",
                            "evidence_ids": [],
                        }
                    ]
                },
                "MANDATORY_GATE",
            ),
            "failed critical gate": (
                {
                    "gates": [
                        {
                            "id": "QA-EXIT-SECURITY",
                            "status": "FAIL",
                            "mandatory": True,
                            "owner": "Security",
                            "reason": "Critical security test failed",
                            "evidence_ids": [],
                        }
                    ]
                },
                "MANDATORY_GATE",
            ),
            "open severity one defect": (
                {
                    "defects": [
                        {
                            "id": "DEF-001",
                            "severity": "SEV1",
                            "status": "OPEN",
                            "owner": "Engineering",
                            "accepted_by": None,
                            "workaround": None,
                        }
                    ]
                },
                "BLOCKING_DEFECT",
            ),
            "absent signoff": ({"signoffs": []}, "SIGNOFF_RECONCILIATION"),
        }

        for name, (changes, expected_failure) in cases.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary_directory:
                repo_root = Path(temporary_directory)
                packet = repo_root / "packet.md"
                packet.write_text("# UAT packet\n", encoding="utf-8")
                index_data = valid_index([])
                index_data["engineering_readiness"] = "READY"
                index_data.update(changes)
                index = repo_root / "index.json"
                index.write_text(json.dumps(index_data), encoding="utf-8")

                completed = run_validator(repo_root, index, packet)

                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(expected_failure, completed.stdout)

    def test_packet_redaction_rejects_sensitive_values_and_signed_urls(self):
        sensitive_samples = {
            "credential": "access_token=live-secret-value",
            "bearer token": "Authorization: Bearer live-token-value",
            "JWT": "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ1c2VyIn0.signaturepart",
            "PAN": "PAN ABCDE1234F",
            "Aadhaar": "Aadhaar 1234 5678 9012",
            "bank": "bank account 123456789012",
            "cheque": "cheque number 123456",
            "BO account": "BO account 1234567890123456",
            "signed URL": "https://storage.invalid/file?X-Amz-Signature=abc123",
        }
        for name, sample in sensitive_samples.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temporary_directory:
                repo_root = Path(temporary_directory)
                packet = repo_root / "packet.md"
                packet.write_text(f"# UAT packet\n{sample}\n", encoding="utf-8")
                index = repo_root / "index.json"
                index.write_text(json.dumps(valid_index([])), encoding="utf-8")

                completed = run_validator(repo_root, index, packet)

                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("SENSITIVE_VALUE", completed.stdout)

    def test_manifest_detects_tampered_human_packet(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\nNOT READY\n", encoding="utf-8")
            index = repo_root / "index.json"
            index.write_text(json.dumps(valid_index([])), encoding="utf-8")
            manifest = repo_root / "evidence-hashes.sha256"
            manifest.write_text(
                f"{hashlib.sha256(packet.read_bytes()).hexdigest()}  packet.md\n"
                f"{hashlib.sha256(index.read_bytes()).hexdigest()}  index.json\n",
                encoding="utf-8",
            )
            packet.write_text("# UAT packet\nREADY\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(VALIDATOR),
                    "--repo-root",
                    str(repo_root),
                    "--index",
                    str(index),
                    "--packet",
                    str(packet),
                    "--manifest",
                    str(manifest),
                    "--expected-commit",
                    EXPECTED_COMMIT,
                    "--as-of",
                    "2026-07-25T14:00:00+05:30",
                ],
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("MANIFEST_HASH_MISMATCH", completed.stdout)

    def test_pass_status_requires_mapped_current_passing_evidence(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            index_data = valid_index([])
            index_data["uat"] = [
                {
                    "id": "UAT-001",
                    "status": "PASS",
                    "actor": "Credit Manager",
                    "owner": "Product/Business",
                    "reason": "Claimed pass without evidence",
                    "evidence_ids": [],
                }
            ]
            index = repo_root / "index.json"
            index.write_text(json.dumps(index_data), encoding="utf-8")

            completed = run_validator(repo_root, index, packet)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("UNMAPPED_PASS", completed.stdout)

    def test_business_approval_requires_signed_business_slot(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            repo_root = Path(temporary_directory)
            packet = repo_root / "packet.md"
            packet.write_text("# UAT packet\n", encoding="utf-8")
            index_data = valid_index([])
            index_data["business_approval"] = "APPROVED"
            index = repo_root / "index.json"
            index.write_text(json.dumps(index_data), encoding="utf-8")

            completed = run_validator(repo_root, index, packet)

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("BUSINESS_APPROVAL_MISMATCH", completed.stdout)


if __name__ == "__main__":
    unittest.main()
