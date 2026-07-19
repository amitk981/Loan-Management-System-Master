# Specification Review

Fixed point: `f8eb78be`; reviewed product commit: `3b31edc4`.

- High: requirements 2-3 require exact eligible identities before count/offset. Loan Account, S37,
  and CFC branches count queryable supersets, then perform stricter scalar evidence checks after the
  offset. Five retained review probes reproduce incorrect totals or a wrong portal stage.
- High: requirement 1 names every downstream consumer. The portal stage at
  `portal_disbursement_status.py:462-472` accepts another application's coherent current member
  completion because it omits the application/customer-code edge.
- Medium carried forward: requirement 5's 1/21/101 staff-workspace, downstream-consumer,
  action/mutation, transport, and independent error matrices remain materially absent. New backend
  tests cover only Loan Account reads; workspace coverage remains one-row.
- Low carried forward: the exact PostgreSQL label remains an empty discovered subclass, so the same
  inherited races still run twice.

No material scope creep was found. The member/account facade divergence itself is closed, as is the
full-portfolio Python page walk; the exact selector and all-consumer promises remain open.
