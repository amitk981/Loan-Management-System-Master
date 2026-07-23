# KYC Correction Permission and State Matrix

| Scenario | Expected result | Focused proof |
|---|---|---|
| Active portal account uploads restricted self-attested PAN evidence | Accepted for its own member only | `test_member_submits_owned_evidence_without_mutating_verified_kyc` |
| Portal account submits PAN correction with owned evidence | `submitted`; member and KYC profile remain verified and unchanged | same test; `backend-green-01-submission.log` |
| Portal account claims another member on submit | `403 OBJECT_ACCESS_DENIED`; zero correction/identity-change writes; denial audited | `test_cross_member_submit_is_blocked_and_audited_without_writes`; `backend-green-02-own-scope.log` |
| Portal account claims another member on read | `403 OBJECT_ACCESS_DENIED`; denial audited | same test; `backend-final-focused.log` |
| Staff without `members.member.update` | Queue denied with `403` | `test_staff_queue_enforces_permission_and_member_scope` |
| Staff with permission but no member scope | Queue returns no foreign rows | same test; `backend-green-05-staff-queue.log` |
| Scoped reviewer starts review | `under_review` with internal notes retained only in staff projection | approve/reject tests |
| Reviewer attempts approval before 004H document verification | `409 INVALID_STATE_TRANSITION`; member/history unchanged | approval test; `backend-final-focused.log` |
| KYC verifier verifies registered correction evidence | Existing `POST /kyc-documents/{id}/verify/` records verifier, time, remarks, profile/member status, and audit | approval test; `backend-final-integration.log` |
| Scoped identity approver approves locked PAN correction | Existing governance applies masked history, increments member version, resets KYC to `pending` | `test_staff_approval_applies_locked_identity_through_governed_reverification`; `backend-green-03-approve.log` |
| Reviewer rejects without borrower reason | `400 VALIDATION_ERROR`; no member/history change | `test_staff_rejection_requires_borrower_reason_and_hides_internal_notes` |
| Reviewer rejects with borrower reason | `rejected`; reason visible to borrower; internal notes absent | same test; `backend-green-04-reject.log` |

All fixtures use synthetic identities. Full PAN/Aadhaar values are absent from audit and history
assertions; portal projections expose only masks.
