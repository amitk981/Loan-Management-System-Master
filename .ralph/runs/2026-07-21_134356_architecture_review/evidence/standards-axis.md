# Standards Axis

Review boundary: product commits `00e537d3`, `9d4fa144`, `7574cd6b`, and `283d9767` after `5c0aba87`. Orchestration-only commits were excluded.

## High

- The 010MA frontend owns a non-atomic capture/SAP/allocation workflow. An exact capture replay returns immediately with `allocation: null`; a prior SAP failure is never resumed. This is a financial workflow-owner defect under `ROOT-010-SERVICING-OWNER-SEAM`.
- The 010K3 reminder check and provider call are separated by a committed transaction boundary. The permanent test covers repayment before worker execution, not repayment after the final check.
- 010K3 repeatable-read MIS generation freezes a coherent present view but not historical status truth; invoice selection uses invoice date while serialization uses the current mutable status.

## Medium

- Statement export replay has no concurrent equal-key ownership proof and ignores scheduler creation ownership after an unlocked existing-job read.
- Portal collections truncate at the first 100 rows without continuation truth.
- New servicing tests continue to call other `TestCase.setUp` methods; reminder batch coverage does not prove 1/100/101 behavior.
- Availability remains partly derived in frontend role/permission logic instead of being wholly projected by the backend.

## Closed

- 010K3's DPD constraints and public capitalisation source close the carried cross-account pointer and double-classification root in the focused closure set.
