# Risk Assessment

Risk level: High.

This slice exposes financial lifecycle truth to borrowers and adds a one-use download capability
for finalized advice. The principal risks are cross-member disclosure, false success from stale
financial ledgers, full bank/SAP/UTR leakage, replayable advice access, and audit retention of the
capability or advice content.

Controls implemented:

- Portal scope is derived only from the active `PortalAccount.member_id`; cross-member and missing
  applications share the same 404 response, while staff and invalid sessions retain shared denial
  contracts.
- The projection composes current sanction, initiation, authorisation, post-transfer, and finalized
  communications owner decisions. Drift falls back to the last safely provable stage or blocked
  copy and the status GET is zero-write.
- Only last-four bank values and fixed borrower labels leave the API. Tests reject raw UTR, SAP,
  recipient, checksum, communication, outbox, actor, and evidence vocabulary.
- Capabilities bind portal/member/application/account/advice/file/checksum/version, expire in 15
  minutes, replace prior grants, and consume once under a row lock. Issued, accepted, and denied
  audits use safe identities without token or content retention.

Residual risk: browser screenshots could not be produced because this sandbox exposed no browser
backend and denied localhost listeners. Real authenticated envelopes and all component states are
saved; the external Ralph browser gate must complete visual acceptance. The advice artifact is a
deterministic text copy of the retained finalized communication under A-099 until governance owns a
PDF template.
