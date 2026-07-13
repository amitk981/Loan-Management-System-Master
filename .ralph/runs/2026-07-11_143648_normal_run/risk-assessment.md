# Risk Assessment

Risk level: Medium

- Selected slice: `006G4-sanction-dependency-boundary-regression`
- Change type: test-only architecture regression strengthening.
- Production blast radius: none; no runtime code, dependencies, configuration, schema, API, or
  frontend files changed.
- Primary risk: a resolver bug could falsely permit a forbidden dependency or falsely reject a
  documented public handoff.
- Mitigation: positive and negative synthetic fixtures cover direct, aliased, package-level, and
  package-exposed imports; the production scan must both find zero violations and observe the
  intended public edge.
- Rollback: revert the single backend test-file change and Ralph bookkeeping.
- Residual risk: dynamic imports are outside this static AST guard; no production dynamic business
  app imports were found or introduced by this slice.
