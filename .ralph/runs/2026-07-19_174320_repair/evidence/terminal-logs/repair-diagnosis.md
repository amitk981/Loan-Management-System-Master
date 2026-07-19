# Repair Diagnosis

## Red Feedback Loop

The prior independent trusted run executed the declared Epic 009 Playwright spec with the Ralph venv
and a fresh run-1 evidence directory. It reached the real Django authorisation and transfer endpoints.
Authorisation returned HTTP 200; transfer returned HTTP 400:

`disbursed_at: Must not be before CFC authorisation.`

The run captured six screenshots before stopping, which rules out fixture startup, real login, owned
API reachability, and the first six state assertions as the demonstrated cause.

## Ranked Hypotheses and Result

1. Confirmed: transfer evidence was derived from the browser clock rather than the server-owned CFC
   authorisation instant. Django correctly compares it with `row.authorised_at`.
2. Subsumed by 1: browser/server timezone or clock differences can make the browser-derived instant
   earlier even when the UI value is described as the next minute.
3. Rejected: `--prepare-transfer` only creates the restricted evidence document/notification and does
   not mutate `authorised_at`.
4. Rejected: the transfer reached the expected row and failed only the chronological field validation,
   not current-evidence or workspace-coherence checks.

## Repair

The spec now retains `authorised_at` from the successful real Django response, converts the next
representable local input minute from that instant inside the same browser context, and round-trips the
value to an ISO instant. A pre-submit assertion requires that instant to be strictly later than the
returned authorisation time. Product workflow validation is unchanged.

## Local Browser Constraint

The focused local browser attempt started Django/Vite but Chrome closed at launch with
`browserType.launch: Target page, context or browser has been closed`. This is the documented sandbox
Chromium restriction, not a product verdict. Playwright collection passes; Ralph's outside-sandbox
contract remains the authoritative run and will execute twice.
