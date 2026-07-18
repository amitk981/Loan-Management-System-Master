# Risk Assessment

Risk level: Low for this review run; High product risks were found and queued.

- Selected slice: architecture-review
- Mode: architecture_review
- Manual review required: no blocking manual action.

## Mutation Scope

- No production code, migration, runtime configuration, protected file, or `docs/source/` file was
  modified.
- Changes are limited to review records, assumptions/reference repair, queue dependencies, five
  corrective slice specifications, Ralph bookkeeping, and run evidence.
- Review probes are isolated under this run's `evidence/` directory and intentionally do not form
  part of the product test suite.

## Product Risk Found

- High: queued advice has no deployed worker discovery/scheduling or dead-worker recovery, while
  the default manual adapter can record sent without delivery.
- High: the dispatcher lacks the source generic send/explicit idempotency contract and retains a
  hidden disbursement/process cycle.
- High: legacy advice provenance is reconstructed from a mutable later template and labelled
  verified.
- High: MP14 omits exact SAP/stage truth, fabricates timestamps, and makes an order-dependent
  application choice in the browser.
- Medium: migration exception fingerprint, visual reuse/evidence, and durable assumption IDs had
  integrity gaps.

These risks are not silently accepted: 009G6, 009H6, 009H7, 009H8, and 009I2 are concrete and
dependency-ordered before 009J. No ADR was created because the cited source already decides the
required behavior.

## Validation Risk

Focused retained tests are green. Five deliberately adversarial probes are red and retained as
evidence for the corrective queue. The orchestrator remains responsible for authoritative complete
coverage and gates; this run intentionally did not run the full backend suite.
