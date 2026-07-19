# Independent Spec Review

Boundary: `git diff 0b5be35c...HEAD` for the 010A–010D slices, Epic 010 digest, and cited source
sections. This pass was read-only and independent of the Standards pass.

## Findings

- High: `RepaymentAllocator` does not reject `manual_match_exception`, bypassing 010D's explicit
  deferral of M09-FR-009 financial allocation to 010C2 terminal approval.
- High: account/ledger balances can accept the full allocation while `_apply_to_schedules` silently
  exhausts insufficient schedule capacity; empty/insufficient/multi-line cases are absent.
- High: M09-FR-010 and flow §27 order balances after posting, but current allocation tests use a
  newly captured SAP-pending receipt.
- High: M09-FR-007 requires borrower name and application number for subsidiary matching; the generic
  matcher accepts any one account/application/borrower identifier and the working contract repeats it.
- High: direct capture accepts a nonexistent statement UUID, which then blocks genuine reconciliation.
- Medium: statement listing is global and import-time auto-match searches all repayments without the
  manual-match object-scope boundary.

## Clean Areas

No material scope creep was found. 010A has exact read/permission/constraint assertions; 010B has
strong duplicate/idempotency races; 010C arithmetic and one-effect contention are substantive; and
010D correctly supplies M09-FR-008's unmatched queue, safe projections, replay controls, and a
one-counterpart PostgreSQL race.
