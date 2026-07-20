# Specification Review

Fixed point: `016a3a893fbbda1a3d32ca5daa4b36e4da40e212`

Product commits: `28f8e19d` (010E4), `600e9742` (010H2), `c6175bf3` (010I), and
`b7e802ff` (010J).

## Findings

- High: approved `InterestInvoiceConfiguration` remains mutable and deletable before first
  consumption, contrary to 010H2 AC-INT-6's approval-time immutability.
- High: capitalisation can add the full unpaid invoice to principal while subtracting only the
  available account/schedule interest, rather than reconciling exactly or failing zero-write under
  AC-INT-4.
- High: reminder eligibility uses `days_past_due >= 365`, not the approved calendar-anniversary
  boundary required by 010J requirement 1 and M11-FR-006/BR-069.
- Medium: a later still-overdue DPD pointer can invalidate a quarter reminder whose retained
  eligibility remains valid.
- Medium: a quarter batch can retain earlier queue side effects and then report one later missing
  contact/template as a request-level failure without an honest per-loan result contract.

010E4's stated source behavior is otherwise implemented, but the effective/current-date owner
still fails the standards-axis production ownership test. No unrelated scope creep was found.
