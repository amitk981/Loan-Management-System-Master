# Diff and Readability Review

- The existing tracked workspace remains the one public process composition root; a redundant
  facade/aggregate pair was removed to keep the slice within the 2,000-line Ralph limit.
- Action families are grouped by owner: legal/checklist/template/upload/correction, application
  bank verification, and security instruments. Small gateway dataclasses make the permitted
  process-to-module dependency explicit and prevent reverse imports.
- The queue selector is a separate 26-line page boundary and receives its projector/error factory,
  avoiding a process import cycle.
- New owner modules use canonical Python AST formatting: one statement per line, stable literals,
  and no semantic minification or chained statements. Long declarative action schemas remain local
  to the owner that validates and executes them.
- Frontend changes remove transport duplication and one invented layout block; no new component,
  CSS class, colour, typography, spacing, or package was introduced.
- `git diff --check HEAD` is clean. Independent Standards and Spec reviews both report no blocking
  gaps after the final public-seam queue regression fix.
