# Durable Action Contract Evidence

Sanitized retained shapes verified through the public workspace API and owner rows:

- Signed copy: application, generated loan-document identity, independent uploaded file identity,
  checksum, uploader, remarks, request, opaque workspace action, predecessor, optional resolved
  review action, audit, workflow, and version identities. Public refetch exposes only id, safe file
  name/time/remarks; the generated original remains the download source.
- Review action: exact checklist item or approval role, optional loan document, actor/name/role/team,
  reason or condition, prior/current state, opaque action, request, audit, workflow, and version.
- A-125: queue/detail status `blocked`, reason `governed_attorney_unconfigured`, no action, no PoA.
  Injected configured decisions are application-scoped and decision-id-bound; stale/wrong-role
  decisions remain zero-write.

The focused test log demonstrates initial upload, exact zero-write replay, changed conflict,
successor creation, correction creation, exact replay, resolution by successor, condition/return
retention, approval denial, and final approval after resolution. Values in tests are synthetic.
