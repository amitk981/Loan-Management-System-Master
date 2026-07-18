# Risk Assessment

Risk level: Low for this review's mutations; Critical product finding.

- Selected slice: architecture-review
- Mode: architecture_review
- Review range: `fb380227...e3d965ad`
- Production code changed: no
- Database/schema changed: no
- Protected files or `docs/source/` changed: no

## Material Findings

- Critical: a valid queued H5 advice job can be downgraded by communications migration 0008 and
  make migration 0009 abort. This can block deployment from the retained 0007 state.
- High: a crash on the final allowed worker attempt is requeued, so the next claim can violate the
  `attempts <= max_attempts` database constraint and strand the job.
- High: an accepted SMS job crosses the Email adapter with no SMS-specific sensitive-content
  guard and can be falsely marked sent.
- Medium/Low: the source facade, replay envelope, immutable generic provider evidence, exception
  queue, API working contract, and thin-task boundaries remain partial.

## Controls and Disposition

- No defect was repaired in architecture-review mode; the review changed documentation, Ralph
  state, evidence, and corrective slice contracts only.
- The independent probes are retained as failing evidence, not fabricated passing tests.
- Corrective slices `009H9A`, `009H9B`, and `009H9C` are concrete, High-risk, dependency-ordered,
  and placed before `009I2`/`009J`.
- Forty-three focused retained backend tests pass, limiting the findings to the newly exercised
  paths. The orchestrator remains responsible for authoritative full coverage and validation.
- No new architecture decision was invented; the corrective requirements are fixed by cited source
  sections, so no ADR is required.

Manual review is recommended for the three corrective slice contracts and the Critical migration
finding before promotion of `staging` to `main`.
