# Critical UAT Scenario Matrix

Source boundary: `test-plan.md` §§16, 18–22, 27.1–27.2, 28, 29.4;
`implementation-roadmap.md` §§17.4–17.6, 27.3; `product-requirements.md` §§11–12;
`screen-spec.md` §13; `technical-architecture.md` §29.4.

The trusted spec is `sfpcl-lms/e2e/critical-uat-smoke.e2e.spec.ts`. It runs as one
order-independent tracer against a freshly migrated deterministic database. “Manual” means the
named source script remains a business-UAT step and is not falsely claimed as automated evidence.

| UAT | E2E | Mode | Source role / public evidence |
|---|---|---|---|
| 001 | E2E-001 | Automated | Finance/CFC: documentation-readiness fixture, SAP, initiation, independent authorisation, transfer success, active loan screenshot |
| 002 | E2E-002 | Manual | Company Secretary: repeat with demat/CDSL pledge and unpledge evidence |
| 003 | E2E-003 | Manual | Credit Manager: FPC profile, authorised signatory, beneficial-owner evidence |
| 004 | E2E-004 | Manual | Deputy Manager Finance: return and resolve named deficiencies |
| 005 | E2E-005 | Manual | Credit Manager: failed eligibility, rejection note, communication |
| 006 | E2E-006 | Automated | CFO: public approved ₹400,000 case retains the one-Director route; the inclusive ₹500,000 boundary is read from the canonical public matrix |
| 007 | E2E-006 | Automated configuration + manual decision | CFO/two Directors: public ₹500,000.01+ row requires two Directors; complete at/above decision execution remains manual UAT |
| 008 | E2E-007 | Automated negative + manual positive | Public permissible-limit exception route requires two Directors; a zero-authority actor is denied, while the valid exception decision remains manual UAT |
| 009 | E2E-008 | Manual | Non-conflicted Directors: abstention and general-meeting evidence |
| 010 | E2E-009 | Manual | Company Secretary: signature mismatch and bank-verification evidence |
| 011 | E2E-001 | Automated | Current checklist/document/security owner evidence consumed by readiness |
| 012 | E2E-010 | Automated | Completed SAP customer-code projection consumed by readiness |
| 013 | E2E-001 | Automated | Senior Finance/CFC public initiation, approval, transfer actions |
| 014 | E2E-011 | Automated | Direct receipt, principal-first allocation, exact-key replay, ledger balance |
| 015 | E2E-012 | Automated | Subsidiary receipt, verified tri-party evidence, pending-statement state, replay |
| 016 | E2E-013 | Automated | Public FY2026-27 interest-invoice generation |
| 017 | E2E-013 | Automated | DPD calculated from the seeded schedule and retained outstanding |
| 018 | E2E-014 | Automated | Missed principal opens the three-month grace-period default |
| 019 | E2E-014 | Automated negative + manual positive | Recovery is denied before an approved recovery case; authority completion remains manual UAT |
| 020 | E2E-015 | Automated | Premature canonical closure fails readiness; public lifecycle tracer proves a fully repaid loan closes |
| 021 | E2E-016 | Automated | Section 186 public calculation: higher limit ₹120, exposure ₹100, within limit |
| 022 | E2E-016 | Automated | NBFC public calculation: 51%/51%, registration trigger true |
| 023 | E2E-017 | Manual | Compliance Team: two-year re-KYC completion with updated documents |
| 024 | E2E-001/011/016 | Automated | Loan-portfolio row reconciles to ₹300,000 principal; idempotent export queues |
| 025 | E2E-018 | Automated | Audit API retains actors and state evidence for disbursement, repayment, default, compliance, and export, including the CFC approval reason digest |
| 026 | E2E-018 | Automated | Zero-permission user denied object/export/audit mutation; PAN/Aadhaar remain masked |

Retained browser outputs:

- `critical-uat-standard-loan.png`
- `critical-uat-permission-negative.png`
- `critical-uat-scenario-matrix.json`
- `critical-uat-seed-manifest.json`
- Playwright trace/logs from both independent trusted runs
