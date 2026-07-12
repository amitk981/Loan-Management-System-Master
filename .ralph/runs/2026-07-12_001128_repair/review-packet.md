# Review Packet: 2026-07-12_001128_repair

## Result
Success.

## Slice
006X3-credit-visual-and-real-browser-closure

## Repair finding

Both prior trusted runs failed because reload reset the app's in-memory route to Dashboard, while
the finance fixture's global permissions could not read the fourth canonical sanction resource.
The prior raw untracked PNGs also contributed 5,346 lines to a 6,498-line diff. This repair reopens
the route after reload, grants the synthetic finance actor global sanction authority only to prove
resource role/state suppression, and stores exact PNG bytes as one-line base64 baselines.

Trusted execution exposed four additional contract defects: the Appraisal navigation item includes
its queue badge in its accessible name; the empty state does not render a workbench heading; duplicate
fixture actions shadowed the appraisal resource's enabled actions; and the role-switch assertion could
reuse an already-completed finance response. The final contract uses the real accessible name, lets
each caller assert its own destination state, gives each fixture resource sole action ownership, and
waits for a live response recorded after the manager handoff.

## Delivered and traceability

- Source implementation-roadmap §11 and API §§22-24 require the eligibility-to-review chain; the
  real contract and `test_seeded_fixture_completes_real_two_role_http_path` drive that chain.
- API §44 requires resource actions; every browser mutation is preceded by an exact six-field
  action assertion, and the globally permissioned finance actor still cannot invoke sanction.
- Successful mutations assert exactly one write and the canonical four reads. Repeat sanction
  returns one `409`, causes no browser refresh, and retains shared server IDs.
- The visual contract owns all eighteen appraisal states and exact screenshot names without local
  eligibility/workflow decisions. The two legacy browser specs are retired.

## Verification

- Playwright collection: exactly 2 tests in the declared file.
- Frontend: lint, typecheck, 166 tests, and build pass.
- Backend: check, migration sync, and 407 tests pass with five expected PostgreSQL skips; coverage
  is 94% against the 85% floor.
- Focused TDD logs prove the guarded seed and submission-remarks seams red then green.
- Both independent trusted-browser runs pass and each emits all twenty declared screenshots; all
  eighteen visual baselines compare successfully on the second run.
- `git diff --check` passes; the final changed-line estimate remains below the 2,000-line limit.

## Recommended Next Action

Merge the independently validated repair, then run 006Y.
