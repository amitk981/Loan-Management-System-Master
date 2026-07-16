# Readiness Contract Evidence

- Ordered checks: the public response retains all 23 codes in source order; see focused API log
  `terminal-logs/11-readiness-api-focused.log`.
- Approval current evidence: changed completion body and duplicate audit/workflow/version siblings
  fail the full ordered approval chain; RED/GREEN logs `01`/`02` and `09`/`10`.
- Required signers: missing PoA borrower, excess eligible Term Sheet Director, wrong/stale signers,
  malformed frozen approval facts, and changed genuine mismatch-resolution remarks fail closed;
  logs `03`/`04`, `23`, `24`, and `26`.
- Reader matrix: Senior Finance, Credit Manager, CFO, and audit-scoped Auditor succeed only within
  canonical scope; pre-009E CFC, intake-only, wrong role/grant, inactive, out-of-domain, missing,
  and cross-object reads remain nondisclosing; RED/GREEN logs `05`/`06` and final log `25`.
- Deep interface: readiness-specific process pass-throughs fail the structural RED probe and are
  absent in GREEN; logs `07`/`08`.
- Genuine owners: the real approval/legal/security/bank/SAP/loan path reaches only A-126, writes no
  business rows, stays at or below 250 queries, and returns all 23 passes only with the governed
  source-bank seam; logs `12` and `13`.
