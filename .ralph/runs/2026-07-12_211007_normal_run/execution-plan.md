# Execution Plan

Selected slice: 006Y10-witness-correction-matrix-and-module-boundary-closure

1. Add failing backend tests for the contact/identity permission, object-scope, maker-checker,
   stale-version, malformed/non-object, unknown/immutable-field, success, and zero-evidence matrix;
   add a static dependency test proving the correction module does not import generic services.
2. Move witness correction projection and write authority behind one acyclic public module seam;
   leave generic serializers as translation-only callers and preserve standard API error categories.
3. Add failing mounted WitnessPanel tests for 400/403/409 responses for both correction kinds,
   proving one PATCH, no error refetch/retry/local merge, retained server facts, and one success refetch.
4. Instrument the trusted Playwright scenario to assert zero verifier PATCHes and exact versioned
   PATCH plus canonical GET counts/bodies for contact and checker successes without interception.
5. Run focused red/green suites, browser collection, then configured frontend/backend gates; save
   self-contained logs and packets, update slice/state/progress/handoff, and sharpen the next slices.

Permissions checked: all intended product, test, slice, working-doc, and run-artifact paths are
allowed by `.ralph/permissions.json`; no protected or forbidden path will be edited.
