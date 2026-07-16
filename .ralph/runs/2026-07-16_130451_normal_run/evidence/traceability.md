# Per-check Traceability

| Source requirement | Implemented checks | Verification |
|---|---|---|
| API §31.1 and R5-AC-005 return the complete pass/fail projection | All 23 stable ordered codes; aggregate is `all(pass)` | `test_incomplete_sources_return_every_ordered_safe_blocker_without_writes`, `test_all_current_owner_decisions_return_ready` |
| Functional M08 blockers: sanction, exception/GM, KYC, appraisal | `sanction_approved`, `exception_approval_complete`, `general_meeting_approval_complete`, `kyc_complete`, `appraisal_complete` | independent source-fact matrix |
| Integrations §9.4 account/checklist approvals | `loan_account_sanctioned`, `documentation_complete`, CS/Credit/Sanction approval codes | independent source-fact matrix |
| Legal/security terminal facts | package, PoA, Term Sheet, Loan Agreement, explicit SH-4/CDSL, blank cheque, signature codes | legal/security owner selectors plus independent matrix |
| Verified beneficiary bank and cancelled cheque | `cancelled_cheque_verified`, `bank_account_verified` | application bank owner plus independent matrix |
| M07-FR-010 / INT-SAP-005 exact active SAP binding | `sap_customer_code_present` | public SAP decision seam; cross-state matrix |
| Integrations §9.4 source account and amount | `source_bank_account_configured`, `amount_within_sanction` | A-126 fail-closed owner plus independent matrix |
| Auth §§12.9/15.6/15.7/26.5 | exact SMF/CFC role + permission + object scope | role/grant/scope/inactive/missing-id tests |
| Read-only and bounded owner coordination | no writes; coordinator imports owner selectors, not foreign models; at most 30 queries | zero-write tracer and `test_real_projection_is_query_bounded_and_coordinator_uses_owner_seams` |

Senior Manager Finance initiation/final verification and CFC authorisation are deliberately absent:
functional M08 and integrations §9 order them after readiness, and slices 009E/009F own them.

`test_stale_application_lifecycle_fails_the_sanction_check` additionally proves that an application
changed to the source rejected lifecycle cannot pass merely because an old case/decision remains approved.
