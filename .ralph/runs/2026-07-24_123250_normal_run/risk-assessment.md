# Risk Assessment

Risk level: High

- Selected slice: 012E2-tracer-and-demo-route-production-isolation
- Mode: normal_run
- Manual review required: yes; independent Ralph validation remains authoritative.

## Risks and controls

- Production could import the tracer models/views or register a newly added tracer route. The
  production settings module forces demo surfaces off, removes the tracer app, and the negative
  deployment test recursively inspects every registered production URL for tracer routes, names,
  or callback modules before also proving the known URL is 404/unreversible.
- Predictable users could survive if a local database were promoted. Production authentication now
  rejects the reserved synthetic `@sfpcl.example` domain for both staff and portal login before
  session creation, and access/refresh validation revokes such existing sessions.
- A seed command could recreate predictable data. Every inventoried demo/E2E seed entry point
  (`seed_demo_users`, `seed_e2e_users`, `seed_portal_e2e_fixture`,
  `seed_epic_009_e2e_fixture`, and `seed_approval_configuration`) consumes the centralized setting
  and refuses under production even when its command-local flags are forced true.
- Frontend permission data could expose Tracer despite backend isolation. Production navigation
  removes Tracer and the direct navigation resolver denies it regardless of a returned legacy
  permission.
- Static imports could retain tracer API/demo identity code. Tracer, role fixtures, demo login, and
  role switching are in production-eliminable lazy branches. A production build with both demo
  flags maliciously forced true contains none of the recorded tracer/demo/dev-endpoint markers.

## Residual risk

- The production build retains the longstanding Vite large-chunk warning; it does not contain the
  isolated tracer/demo markers and is unrelated to this boundary.
- Tracer tables/migrations remain in repository history and may remain physically present in a
  database, but the production app registry, URL surface, authentication path, seeds, and frontend
  expose no execution path to them.
- No browser screenshots were required by this slice (`Runtime Capabilities: none`); behavior and
  bundle evidence are retained as terminal logs.

## Outcome

No unresolved Critical/High implementation risk was found in the selected scope. No source or
protected file was modified.
