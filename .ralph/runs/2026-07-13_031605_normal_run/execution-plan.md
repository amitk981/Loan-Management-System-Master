# Execution Plan

Selected slice: 006Z9-active-member-authority-and-decision-contract-closure

## Scope and constraints

- Change only the member authority projection, active-member verification contract, and their public module/HTTP regression coverage.
- Preserve authority-first `OBJECT_ACCESS_DENIED` nondisclosure for unresolved or out-of-scope members.
- Do not infer member-global scope from `Role.is_system_role`, role codes, caller flags, or unowned rows.
- Do not invent a write-global role: use only explicit persisted assignment/ownership or a documented permission-based global category; otherwise deny and record the open decision.
- Keep verification atomic and ensure every rejected call leaves member status/pointer, effective history, audit, and workflow evidence unchanged.

## TDD tracer bullets

1. Add a public authority/module test proving system and custom roles with identical permissions receive identical member scope; run it red, implement the explicit projection, then run green.
2. Add public verification tests for relaxation-result/active-decision and pass-result/relaxation-decision mismatches with complete before/after evidence; run each red then green.
3. Add maker-checker tests proving creators/updaters of qualifying supply, service, or relaxation evidence cannot verify the derived result; run each red then green.
4. Complete paired module and HTTP matrix rows for success, validation, object/permission/maker-checker, stale/repeat/unsupported, and chronology outcomes, adding one observable row at a time.

## Implementation and documentation

- Centralize a reviewable member scope result in `members.modules.member_authority` and make Registry plus active verification consume its common categories.
- Enforce qualification-route-to-decision fidelity and evidence-owner separation inside the transactional verification module.
- Update `docs/working/API_CONTRACTS.md` if public envelopes or stable error cases are newly documented.
- Record any source-silent member-global write authority as an assumption rather than granting it.

## Validation and handoff

- Save red and green commands under `evidence/terminal-logs/`.
- Run focused backend tests after each tracer bullet, then backend check, migration sync, full coverage suite, and all configured frontend gates.
- Save dependency scan, changed-files, risk assessment, review packet, and final summary.
- Mark only 006Z9 complete; update Ralph state, progress, and handoff.
- Sharpen the next one or two Not Started slices only from source material already opened; 006Z10 is already concrete, so change it only if inspection identifies a genuine missing executable requirement.
