# Frontend Design Rules (binding for every frontend change)

The prototype in `sfpcl-lms/` is the approved visual system. These rules are owner requirements (2026-07-02) and are not negotiable per slice.

## Hard rules
- No colour changes.
- No typography changes.
- No spacing/layout redesign.
- No new card design.
- No new badge design.
- No new table/queue pattern.
- Only change: labels, sample/real row data, visibility, and role/action logic.
- Do not redesign existing screens.
- Reuse the existing dashboard layout, sidebar, header, alert components, metric cards, badges, queue cards, links, spacing, colours, typography, and existing component patterns.
- Do not introduce new styling, new visual systems, or new components unless absolutely required — and "absolutely required" means no existing component or composition of existing components can express the function. Record any such case in ASSUMPTIONS.md with the reason.

## Gap-closure duty (documents > prototype)
If `docs/source/` requires functionality that has no screen in the prototype, building that screen IS the slice's responsibility — a backend without a reachable UI does not satisfy the documents. Process:
1. Check `docs/working/PROTOTYPE_INVENTORY.md` and `docs/working/PROTOTYPE_GAP_REPORT.md` for the closest existing screen.
2. Compose the new screen ONLY from existing pieces: `AppShell`/`Sidebar`/`Header` shell, `KPICard`, `StatusBadge`, `AlertBanner`, `Modal`, `Tabs`, `StageStepper`, and the loan components (`ApprovalPanel`, `AuditTimeline`, `DocumentChecklist`, `DocumentPackModal`, `EligibilityChecklist`, `LoanLimitCalculator`, `RepaymentLedger`), plus the table/queue/detail patterns already used in `src/pages/`.
3. Copy the structure of the most similar existing page (same header pattern, same card grid, same table classes) and change only labels, data wiring, visibility, and role/action logic.
4. Wire it to the real backend API — no new mock data. Route it in the existing router and sidebar following the role rules.
5. Update `PROTOTYPE_INVENTORY.md` (new screen) and `PROTOTYPE_GAP_REPORT.md` (gap closed) in the same run.

## Mock-surface ratchet and ownership (2026-07-11)
Rules (from PRODUCTION_COMPLETION_BLUEPRINT.md §6.4):
1. The total mock/fixture surface may never grow: no slice may add a `mockData` import, an inline business fixture, or a runtime business calculation to a production path. Controlled vocabularies, display metadata, and test fixtures are legitimate when explicitly identified as such.
2. Each file below has exactly one final-removal owner. That slice must leave the file with no `src/data/mockData.ts` import and no inline business fixtures, and must add a regression test asserting it.
3. A production screen may not calculate server-owned money, eligibility, approval, state, or permission decisions locally.

| File (sfpcl-lms/src/) | Final-removal owner |
|---|---|
| `App.tsx` | 006H5 |
| `pages/applications/CompletenessWorkbench.tsx` | 005E2 |
| `pages/sanction/SanctionWorkbench.tsx` | 007I |
| `pages/settings/SettingsHub.tsx` | 007J (matrix panel) / 007J2 (all remaining panels) |
| `pages/documentation/DocumentationHub.tsx` | 008M |
| `components/loan/DocumentChecklist.tsx` | 008M |
| `components/loan/DocumentPackModal.tsx` | 008M |
| `components/loan/AuditTimeline.tsx` | 008M |
| `pages/disbursement/DisbursementHub.tsx` | 009K |
| `pages/disbursement/PaymentAuthorisationHub.tsx` | 009K |
| `pages/loan-accounts/LoanAccount360.tsx` | 010M (initial wiring 009J) |
| `pages/repayments/RepaymentsHub.tsx` | 010M |
| `pages/monitoring/MonitoringDashboard.tsx` | 010M |
| `components/loan/RepaymentLedger.tsx` | 010M |
| `pages/search/GlobalSearchResults.tsx` | 010N |
| `components/layout/Header.tsx` | 010O (search paths 010N) |
| `pages/compliance/ComplianceDashboard.tsx` | 011P |
| `pages/compliance/GrievancesHub.tsx` | 011P |
| `pages/compliance/AuditArchiveHub.tsx` | 011P |
| `pages/registers/RegistersHub.tsx` | 012DA (S23/S25 views 007J) |
| `pages/reports/ReportsMIS.tsx` | 012DA |
| `components/loan/ApprovalPanel.tsx` (inline ₹5,00,000 matrix + client authority) | 007I |
| `pages/borrower/portal/applications/MP05_NewApplication.tsx` | client money math removed 2026-07-11; 006Z2 owns the server limit projection |
| `pages/borrower/portal/auth/MP00_Login.tsx` + `App.tsx` demo-login fallback | fixed 2026-07-11 (005FA2 Complete, regression-tested) |

This table reflects the 20 production files importing `mockData` as of 2026-07-11 plus SettingsHub's inline fixtures. If a slice finds a mock read in a file not listed here, it must add the file to this table with an owner in the same run.

## Owner-approved design amendments (the only exception)
The owner may change the approved design itself — a label, colour, layout, or visual element — but only through a `ui-change` change request (`docs/change-requests/`, maintenance stage) whose Source Document Reference contains the phrase "owner approved". Intake enforces this mechanically. When implementing such a CR slice, change exactly what the request names and nothing else; every hard rule above still applies to everything the request does not name.

## States and evidence
Follow `docs/working/VISUAL_ACCEPTANCE.md`: loading/empty/error/unauthorized/validation/success states using existing patterns (e.g., existing alert/empty styles), screenshots saved to the run's evidence folder. Screenshots must be visually indistinguishable from the prototype's design language.
