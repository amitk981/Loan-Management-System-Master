# Independent Standards Review

## Hard Findings

- `NewApplication.tsx` and `MP05_NewApplication.tsx` duplicate the time-dependent adult/minor
  eligibility rule in React and use it for UI availability. This can diverge from backend intake
  and credit checks. `codebase-design.md` §§23.3/42.3 require pages to render backend facts/actions
  and validation rather than decide business rules.
- 005I3 tests omit required invalid staff PATCH and portal create/PATCH paths. The staff invalid
  test exercises POST only; portal tests cover happy create/update/submit. This misses 005I3's
  blocked-path contract and §42.2's success-and-blocked-path rule.
- `applications.services.serialize_application_detail` labels
  `received_by_user or created_by_user` as `assigned_owner`; neither is an assignment fact. The
  backend test enshrines creator-as-owner instead of proving a persisted conflicting owner,
  defeating 005I4's no-invented-owner goal.
- Application Detail tests exercise the loader separately, then inject status/data into the
  exported view. They do not mount the production component's async success/error/action path,
  contrary to 005I4's test correction and §26.3's mocked-HTTP UI-behavior rule.
- 006C2 adds cultivated-acreage financial behavior to `applications.services` with HTTP-heavy
  tests instead of the source-named loan-limit module interface (§§6.2, 7.3, 12.2, 26.1). This is
  significant at HEAD but already explicitly owned by immediately queued 006D2B.

## Judgment / Watch Items

- 006D2A's credit module reaches into application services for completeness/object access and
  returns the concrete ORM model with its snapshot. This weakens the deep seam, though the reused
  application capabilities are outside the moved eligibility rule itself and model ownership is
  deliberately staged under ADR-0002.
- The configuration resolver is a function rather than the class shape illustrated by
  codebase-design §38.1. The selected slice explicitly chose this narrow function, so no ADR is
  required now; dependency direction and static boundary enforcement still require correction.

Disposition: Findings 1-4 are owned by new corrective slice 005I5; the loan-limit extraction,
static boundary proof, configuration dependency direction, and locking are owned by sharpened
006D2B.
