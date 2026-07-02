# Slice 002FL: Frontend Lint Baseline (ESLint)

## Status
Not Started

## Parent Epic
Epic 002: Platform Auth and Role Shell (quality infrastructure)

## Goal
Introduce ESLint so frontend code quality is machine-enforced from here on, completing the gate set (typecheck and tests already exist).

## User Value
Every future frontend slice is automatically checked for bug-prone patterns (unused variables, missing hook dependencies, unsafe patterns) — quality the owner does not have to verify by reading code.

## Depends On
- 002F

## Concrete Requirements
1. Add dev dependencies (pinned, per `docs/working/DEPENDENCY_POLICY.md`): `eslint`, `typescript-eslint`, `eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`.
2. Create a flat config (`sfpcl-lms/eslint.config.js`) using the recommended TypeScript and react-hooks rule sets. Do not invent custom rules.
3. Add script `"lint": "eslint src"` to `sfpcl-lms/package.json`.
4. Fix all reported violations across `sfpcl-lms/src/`. Rule-by-rule downgrades are allowed only with a one-line justification in the run summary; never disable a rule inline without a comment explaining why.
5. Behaviour must not change: `npm run typecheck`, `npm test`, and `npm run build` all stay green; no visual changes.
6. Ask the owner-side operator (outside the run) to flip `quality_gates.lint` to `true` in `.ralph/config.yaml` — that file is protected, so record the request in HANDOFF.md instead of editing it.

## Test Cases
- `npm run lint` exits 0.
- Existing vitest suite passes unchanged.

## Risk Level
Medium

## Acceptance Criteria
- ESLint runs clean on the whole `sfpcl-lms/src/` tree.
- HANDOFF.md notes that the lint gate is ready to be enabled in config.

## Done Checklist
- [ ] Execution plan written
- [ ] Config + script added
- [ ] Violations fixed
- [ ] Tests/typecheck/build passed
- [ ] Risk assessment completed
- [ ] Handoff updated (lint gate flip requested)
- [ ] State updated
- [ ] Commit created only after passing gates
