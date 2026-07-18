# Risk Assessment

Risk level: High

- Selected slice: 009H9D-communications-provenance-and-operator-boundary-closure
- Mode: normal_run
- Standing approval: confirmed; no veto exists in `HIGH_RISK_APPROVALS.md`.

## Material Risks

- Historical-data risk: communications migration `0008` is corrected in place at the only state
  where 0007 queued snapshot/job relationships still coexist. A false positive could claim
  provenance that never existed; a false negative could block a legitimate queued advice job.
- Authorisation risk: exception collection/detail/resolution expose operational failure evidence.
  A union-of-permissions check could disclose or mutate the opposite job kind, while stale owner or
  job evidence could permit an invalid resolution write.
- Migration risk: retained exception rows stored dotted adapter identities. Normalizing them must
  preserve every job, retry, assignment, audit, workflow, and resolution fact.
- Runtime risk: moving adapter selection and task iteration behind the communications interface
  could regress retry, lease, provider replay, cross-channel idempotency, or advice finalization.

## Mitigations and Evidence

- The independent three-probe review suite and retained copies failed before production changes;
  see `red-review-contract-probes.log` and `red-retained-contract-probes.log`.
- Recomputed-checksum drift is covered for every frozen template fact, plus malformed variable
  collections and the genuine queued forward/reverse/reapply identity; see
  `green-provenance-matrix.log` and `final-provenance-regression.log`.
- Public HTTP tests cover exact/opposite/revoked permission, inactive/cross-owner operators,
  stale version, changed job evidence, strict 105-row pagination, provider vocabulary, and
  redaction. Denied paths assert zero resolution audit/write.
- Migration `0013` derives `email`/`sms` from the retained source job channel and its regression
  compares every other exception column before/after normalization.
- Executable seam tests prove process/Celery delegators do not select channels or read
  communications models; existing Email/SMS, retry, lease, replay, provider-evidence, and advice
  tests remain green.
- PostgreSQL `CommunicationWorkerClaimRaceTests` passed twice, 6/6 each, in
  `postgresql-races-1.log` and `postgresql-races-2.log`.

## Residual Risk

The orchestrator must still run the authoritative complete backend suite under coverage and its
independent migration/race validation. No frontend production file changed. No external provider,
network communication, real personal data, deployment, or git operation occurred.
