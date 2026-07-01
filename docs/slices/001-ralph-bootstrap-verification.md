# Slice 001: Ralph Bootstrap Verification

## Status
Complete

## Goal
Verify Ralph folder structure, config, state, permissions, docs, and scripts exist and can run preflight safely.

## User Value
The user can safely start Ralph automation from one command without relying on chat history.

## Depends On
None

## Source References
- Ralph AFK Automation Requirements v2.1
- `docs/source/`

## Screens Involved
None.

## Prototype Reference
None.

## Frontend Scope
None.

## Backend/API Scope
None.

## Database/Model Impact
None.

## API Contracts
None.

## Permissions
Ralph must not modify `docs/source/**`, secrets, or `.git/**`.

## Validation Rules
- Required Ralph files exist.
- `.ralph/state.json` and `.ralph/permissions.json` are valid JSON.
- `.ralph/config.yaml` is parseable or passes section validation.
- Preflight detects the `sfpcl-lms` package and build command.

## Test Cases
- `./scripts/afk-dev.sh --mode bootstrap`
- `./scripts/afk-dev.sh --dry-run`
- `npm run build` from `sfpcl-lms/`

## Visual Acceptance Criteria
None.

## Evidence Required
- `.ralph/runs/<run-id>/preflight-results.md`
- `.ralph/runs/<run-id>/ralph-artifact-validation.md`
- `.ralph/runs/<run-id>/build-results.md`

## Risk Level
Low

## Acceptance Criteria
- All required Ralph files exist.
- Preflight runs successfully.
- No product features are implemented.
- `docs/source/` remains read-only.

## Done Checklist
- [x] Execution plan written
- [x] Validation run
- [x] Evidence saved
- [x] Risk assessment completed
- [x] Handoff updated
- [x] State updated
- [x] Commit created only after passing gates
