# Risk Register

| ID | Risk | Area | Severity | Likelihood | Mitigation | Related Slice/ADR | Status |
|---|---|---|---|---|---|---|---|
| R-001 | Mock frontend behavior may drift from source-doc business rules. | Prototype/API | High | Medium | Replace mock data one vertical slice at a time with contracts and tests. | Future API slices | Open |
| R-002 | No backend/database code exists yet. | Architecture | High | High | Treat backend introduction as planned high-control slices with ADRs and tests. | Future backend slices | Open |
| R-003 | Missing lint/typecheck/unit test scripts reduce validation strength. | Quality | Medium | High | Add testing-enablement slice before risky product work. | Slice 001/future testing slice | Open |
| R-004 | Financial, disbursement, recovery, and compliance rules are high impact. | Business controls | High | Medium | Require source refs, tests, audit evidence, and human review for high-risk changes. | Future lifecycle slices | Open |
