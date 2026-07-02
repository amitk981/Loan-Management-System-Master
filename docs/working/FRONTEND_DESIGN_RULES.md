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

## Owner-approved design amendments (the only exception)
The owner may change the approved design itself — a label, colour, layout, or visual element — but only through a `ui-change` change request (`docs/change-requests/`, maintenance stage) whose Source Document Reference contains the phrase "owner approved". Intake enforces this mechanically. When implementing such a CR slice, change exactly what the request names and nothing else; every hard rule above still applies to everything the request does not name.

## States and evidence
Follow `docs/working/VISUAL_ACCEPTANCE.md`: loading/empty/error/unauthorized/validation/success states using existing patterns (e.g., existing alert/empty styles), screenshots saved to the run's evidence folder. Screenshots must be visually indistinguishable from the prototype's design language.
