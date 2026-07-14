# Ralph Handoff

## Last Run

2026-07-15_004202_normal_run

## Current Status

008I3 is complete. All executable `security_instruments` code is free of approvals/legal imports.
Public security views now call `processes.security_instrument_evidence`, which resolves canonical
sanction/read scope and locked legal/checklist facts, then issues an immutable narrow access object
to the security owner. Caller-supplied evidence access fails before lookup; the temporary
`legal_documents.modules.power_of_attorney` alias is deleted. Historical migrations and Django
string FK labels remain only to preserve retained tables and relations.

Security applicability, exact ₹500 PoA activation, maker-checker, custody, pledge, replay, terminal
state, and masked read policy remain local. Package/PoA/SH-4/CDSL ordinary evidence uses one
recursively redacting recorder with role/team/request/network attribution. Tri-party changed
verification now detects observed-versus-locked races while exact replay retains one action.

## Validation

Evidence is in `.ralph/runs/2026-07-15_004202_normal_run/evidence/`. Dependency, recorder-redaction,
and forged-authority RED/GREEN logs are retained. The 39 focused public/boundary tests passed. PoA,
tri-party, SH-4, and CDSL ran 10 PostgreSQL race tests twice with one material winner and zero loser
success evidence. Backend check/migration sync passed; all 832 backend tests passed with 36 expected
SQLite skips at 92% coverage. Frontend lint/typecheck/build and all 293 tests passed.

## Next Run

Run sharpened 008I4. Extend the coordinator for nullable pending CDSL evidence, install independent
versioned authenticated encryption plus central sensitive reveal ownership, and preserve I3's
ordinary evidence recorder and twice-run races. Then run sharpened 008J through the same coordinator
and encryption/reveal seams. A-101 still blocks the complete real Term-Sheet path.
