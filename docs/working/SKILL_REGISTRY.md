# Skill Registry

| Stage | Skill | When to use | Input Files | Output Expected | Stop Condition |
|---|---|---|---|---|---|
| Setup | `setup-matt-pocock-skills` | Only if repo skills are missing | Repo root | Skills available | Already configured or install fails |
| Requirement clarification | `grill-with-docs` | Source docs conflict or slice is ambiguous | `docs/source/`, current slice | Clarified requirements | High-risk ambiguity remains |
| Slice creation | `to-issues` or manual slicing | After requirements are stable | `CONTEXT.md`, source refs | Small vertical slices | Slice spans too much work |
| Triage | `triage` | Before implementation when slice needs sharpening | Current slice | Agent-ready brief | Missing source truth |
| TDD | `tdd` | During implementation at testable seams | Current slice, relevant code | Tests and implementation | No viable test seam |
| Diagnosis | `diagnosing-bugs` | Tests fail or behavior is broken | Logs, failing tests | Root cause and fix | Repeated failure |
| Handoff | `handoff` | End of run | Changed files, logs | Updated handoff | Required artifact missing |
| Architecture | `improve-codebase-architecture` | Every 3 to 5 completed slices | Repo, ADRs, slices | ADRs/refactor slices | Risky auto-refactor proposed |

Skills must be stage-based. Do not use skills randomly or install internet skills without review.
