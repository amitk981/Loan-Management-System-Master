# Review Traceability

## Boundary

- Fixed point: `220f3038`
- Reviewed head: `e1698e87`
- Commits: `59095ada` (007R), `95709705` (007S), `d95d5d53` (008A2), `e1698e87` (008B)
- Review modes: independent Standards and Spec passes

## Finding to Correction

| Finding | Evidence boundary | Correction |
| --- | --- | --- |
| Legacy S23 top-level null crash | Backend legacy test versus `ApprovalRegisterPanels` DTO/dereference and UI fixture | 007T |
| Post-action stale overwrite and invalid S21 fixtures | `SanctionWorkbench.act()` versus ordinary generation guards/tests | 007T |
| Reversed legal-document dependency and direct authority bypass | codebase-design §§6.3/36.2 versus 008B module/model imports and view-only checks | 008B2 |
| Selector drift and unconstrained loan-account UUID | codebase-design §7.2 and data-model §16.3/§34 versus 008B module/model | 008B2 |
| Metadata-only PDF and fake DOCX evidence | functional §15.1/M06-FR-013 versus renderer/tests/stored-byte assertions | 008B3 |
| Missing governed real M05 Term Sheet terms | terminal writer, A-079, positive direct fixture | A-101 and 008B3 blocker proof |

No Blocked slice was available to reopen. Existing architecture rules decide the implementable
corrections, so no ADR was needed.
