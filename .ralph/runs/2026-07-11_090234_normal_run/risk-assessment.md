# Risk Assessment

Risk level: High.

- Selected slice: 006G3-sanction-handoff-dependency-and-evidence-ownership
- Mode: normal_run
- Changes sanction transaction ownership, durable evidence, dependencies, and concurrency-critical
  behavior. Controls are atomic writes, conservative legacy linking, forced rollback tests, static
  dependency tests, two five-race PostgreSQL runs, and all configured gates.
- Legacy cases without exactly one reason-linked event remain explicitly unlinked rather than
  guessed. New cases cannot complete without storing the created event.
- No protected paths, source docs, dependencies, external services, or frontend visuals changed.
