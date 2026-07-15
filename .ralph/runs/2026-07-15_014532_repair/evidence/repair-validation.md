# Repair Validation

## Demonstrated failures

- Three new CDSL tests generated non-canonical legal document types and dereferenced a 400 error as
  a success envelope.
- Reveal-denial audit rows were written inside the pledge-lock atomic block and rolled back when the
  central policy exception propagated to the HTTP adapter.
- After the newly pinned native dependency was installed, the dependency-direction test bypassed
  Ralph's arm64 virtualenv wrapper for its subprocess and selected the incompatible x86_64 slice.

## Repair

- Test setup now generates canonical `cdsl_pledge_evidence` and asserts HTTP 200 before reading data.
- The coordinator exits the lock transaction normally after central denial evidence is written,
  then raises the same validation/access/rate/ciphertext exception for unchanged API handling.
- The dependency probe launches the virtualenv `bin/python` entrypoint and preserves fresh-process
  guarded-import behavior.

## Results

- Focused recorded failures: 4 passed.
- Dependency-direction probe: passed.
- Backend: 841 passed, 36 expected SQLite skips, 92% coverage; check and migration sync passed.
- PostgreSQL: 10 PoA/tri-party/SH-4/CDSL races passed twice with separate test databases.
- Frontend: lint and typecheck passed; 293 tests passed; production build passed.
