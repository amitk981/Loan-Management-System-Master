# Ralph Handoff

## Last Run

2026-07-14_234031_architecture_review

## Current Status

The independent architecture review covered 008G2, 008F2, 008H, and 008I from `e046a9d3` through
`bacc285d`. Standards found three High and one Medium issue; Spec found three High and one Medium
issue. The principal defects are a forwarding-shell/reversed security dependency, missing source
read roles, missing exact ₹500 PoA validation, nullable CDSL evidence causing a 500, custom
`SECRET_KEY`-derived reversible crypto/direct reveal policy, and incomplete exact-winner race
evidence. Focused public-path regressions reproduced the ₹1 PoA activation and null-evidence CDSL
failure. No production code changed.

Corrective slices are queued in strict order: 008I2 moves real PoA ownership and fixes stamp/read
contracts; 008I3 restores the legal/security dependency seam and complete race evidence; 008I4
installs central independently keyed encryption/sensitive access and fixes nullable CDSL evidence.
008J now depends on I4 so cheque custody cannot copy the wrong sensitive-data seam. 008K and 012E3
were sharpened from already-opened source material. No ADR was needed because the source architecture
already decides these ownership boundaries.

## Validation

Review evidence is in `.ralph/runs/2026-07-14_234031_architecture_review/evidence/`. It contains
separate Standards and Spec reports, both failing regression reproductions, queue/protected-path
checks, and configured frontend/backend gate results. The review packet is the authoritative compact
summary.

## Next Run

Run 008I2, then 008I3, then 008I4 before 008J. Preserve retained ids/tables/routes, terminal legal
evidence, package locks, masked projections, and strict exclusion of invocation, unpledge,
disbursement, file authority, balance changes, and readiness. A-101 still blocks the complete real
Term-Sheet path.
