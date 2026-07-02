# High-Risk Slice Approvals

Ralph refuses to start a slice whose `## Risk Level` is `High` unless that slice is listed here with an `[approved]` tag. This file is the human control point for unattended (AFK) runs: the owner reviews what a high-risk slice will touch, then grants approval for that one slice only.

How to approve a slice, one line per slice:

```
- [approved] <full-slice-id> | <date> | <one-line reason>
```

To withdraw an approval, change `[approved]` to `[revoked]`.

Blanket approvals ("approve everything") are not allowed. Approving a slice here means: "I understand this slice touches security, money, or compliance logic, and I accept that it runs and auto-merges without me watching."

## Approvals

- [approved] 002B2-auth-hardening-jwt-library-and-packaging | 2026-07-02 | Remediation slice: replaces hand-rolled JWT signing with the standard PyJWT library while keeping existing auth tests green. Seeded during the 2026-07-02 workflow repair; owner may revoke.
- [approved] 002C-role-and-permission-catalogue-seed | 2026-07-02 | Seeds the role/permission catalogue from docs/source/auth-permissions.md; data seeding with tests, no external exposure. Seeded during the 2026-07-02 workflow repair; owner may revoke.
- [approved] 002D-current-user-api-with-permissions-and-teams | 2026-07-02 | Read-only current-user API on top of the tested auth layer. Seeded during the 2026-07-02 workflow repair; owner may revoke.

## Pending (not approved yet — Ralph will stop at these)

- 002I-object-level-permission-test-harness
- 002EX-early-end-to-end-tracer-bullet (review the plan when the queue reaches it)
- All High-risk slices in epics 004, 006, 007, 008, 009, 010, 011, 012 (see docs/working/IMPLEMENTATION_SLICE_INDEX.md for the Risk column)
