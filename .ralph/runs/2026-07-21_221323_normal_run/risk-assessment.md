# Risk Assessment

## Classification

- Risk level: High
- Selected slice: `010N4-global-search-sensitive-authority-closure`
- Mode: `normal_run`
- Standing approval: active; no owner veto is recorded for this slice.

## Material risks and controls

- Sensitive match existence could disclose a member to an otherwise global member reader. Security,
  SAP, bank, PAN, and Aadhaar inputs now execute only inside their public owner facades after exact
  input authority and scope checks; denied input lookups return no card, count, action, or group side
  channel.
- Cross-domain aggregation could cap before object authority and hide an authorised older record.
  Application and account facades now apply canonical object scope in their database query before
  ordering and the 100-result cap; the 100-denied-plus-one-authorised regression is GREEN.
- Independently authorised groups could accidentally borrow member-group authority. Application and
  account facades search their own borrower/reference fields under their own permission and object
  scope; the member group may remain absent while the authorised application group returns truth.
- Raw sensitive input could remain in URLs, browser storage, React state, or pagination requests.
  Search stays in a POST body; header, app, form, and active-request state clear after completion;
  subsequent pages use a random actor-bound opaque token rather than resubmitting the raw value.
- A leaked or guessed continuation could cross actor boundaries. Continuations are 128-bit random,
  cache-bound to the authenticated actor, expire after five minutes, and fail with a nondisclosing
  validation error when invalid or expired.

## Residual risk

The server intentionally retains the raw search value in its actor-bound cache for up to five minutes
to support opaque pagination. It is never returned, logged, audited, placed in a URL, or persisted by
the client. Independent High-risk validation should confirm the configured cache deployment retains
the same TTL/isolation semantics and run the authoritative complete backend suite.
