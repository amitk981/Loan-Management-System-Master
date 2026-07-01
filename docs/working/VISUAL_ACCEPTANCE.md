# Visual Acceptance

## Prototype Reference
`sfpcl-lms/` is the current visual reference for future frontend slices.

## Match Level
Preserve domain-specific layout, navigation, role-aware workflows, status indicators, tables, and action density unless a slice explicitly improves them. Do not convert operational screens into marketing-style pages.

## Responsive Expectations
- Staff app must remain usable on desktop and tablet widths.
- Member portal screens must remain usable on mobile widths.
- Text must not overlap controls or cards.
- Fixed-format elements should use stable dimensions to avoid layout shift.

## Required States
Frontend slices should cover relevant loading, empty, error, unauthorized, validation, and success states.

## Evidence
For frontend slices, save screenshots to `.ralph/runs/<run-id>/evidence/screenshots/` before marking the slice complete.
