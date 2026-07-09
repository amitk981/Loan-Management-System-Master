# Risk Assessment

Risk level: Medium

- Selected slice: `004C-individual-farmer-and-fpc-profile-details`
- Schema: one non-destructive migration adds seven columns to the existing individual profile
  table. Existing rows receive empty first/last-name values during migration; all future model saves
  run full validation and require those source-mandated fields.
- Access: the existing `members.member.read` gate is unchanged. No create/update API, permission
  grant, sensitive reveal permission, or object-scope expansion was added.
- Sensitive data: member PAN/Aadhaar remain last-four masked. Producer signatory PAN/Aadhaar are
  neither persisted nor serialized; API tests assert those keys do not leak.
- Integrity: model-boundary tests prove an individual profile cannot belong to an FPC/producer
  member and a producer profile cannot belong to an individual farmer.
- Audit/workflow: the capability is read-only; tests confirm no profile-read audit or workflow event
  beyond the normal login audit.
- Frontend: changes reuse existing cards, tiles, empty panels, spacing, colors, and typography.
  No new package, route, screen, or mock data was introduced.
- Rollback: reverse migration removes only the newly added individual-profile columns. Application
  rollback restores 004B serialization/UI behavior.
- Residual risk: live browser PNG capture was unavailable. Self-contained rendered HTML and frontend
  rendering tests cover both profile types and missing-profile state.

Standing approval applies; no `[revoked]` entry exists for this slice.
