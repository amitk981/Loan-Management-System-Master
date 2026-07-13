# Quality Gate Evidence

## Frontend

- `npm run build`: PASS (Vite production build).
- `npm run typecheck`: PASS.
- `npm run lint`: PASS.
- `npm test`: PASS, 29 files / 208 tests.
- Full output: `terminal-logs/13-frontend-full-gates.txt`.

## Backend

- Django system check: PASS.
- Migration synchronization: PASS, no changes detected.
- Full coverage suite: PASS, 628 tests, 19 expected PostgreSQL-only skips.
- Coverage: 93%, above the 85% floor.
- Final full output: `terminal-logs/18-backend-full-coverage-final.txt`.

The first full coverage attempt exposed migration-test graph isolation and is retained honestly in
`terminal-logs/12-backend-full-coverage-failure-summary.txt`. The true migration dependency was narrowed and the
exact full coverage gate then passed.
