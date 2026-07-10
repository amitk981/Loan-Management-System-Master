# Capability Maps (owner-curated)

Section-level cross-references over `docs/source/`, one note per capability, imported from the
owner's Obsidian vault on 2026-07-10. Use them to find the exact spec sections a slice needs
instead of opening whole source documents — they exist to make context loading precise and cheap.

## How to resolve the links

These notes use Obsidian wikilink syntax:

- `[[api-contracts#22. Eligibility Assessment APIs|label]]` → `docs/source/api-contracts.md`,
  heading “22. Eligibility Assessment APIs”.
- `[[Eligibility and Loan Limit Map]]` → the file of that name in this folder.
- `[[LMS Architecture.canvas|…]]` → an Obsidian-only visual; it is not in this repo. Ignore it.

Every `[[name#…]]` target whose name matches a `docs/source/*.md` file refers to that file; the
section numbers match the repo copies exactly.

## Contents

- `LMS Index.md` — entry point over the whole specification set.
- `LMS Traceability Matrix.md` — capability-by-capability coverage across requirements, domain,
  data, UI, APIs, permissions, and tests.
- `Open Decisions Index.md` — unresolved policy/legal/operational/technical decisions. Directly
  supports `docs/working/DECISION_POLICY.md`: if a rule appears here as open, do NOT invent it.
- Ten capability maps (Membership/KYC, Application/Completeness, Eligibility/Loan Limit,
  Appraisal/Sanction, Documentation/Security, SAP/Disbursement, Repayment/Interest,
  Monitoring/Default/Recovery, Closure/Compliance, Platform Security/Operations) — each links the
  relevant sections of every source document plus its key decisions and open issues.

## Precedence

These maps were authored from the same spec snapshot as `docs/source/` and are navigation aids,
not authority. Where a map's "open issue" or decision note conflicts with
`docs/working/ASSUMPTIONS.md`, an ADR in `docs/adr/`, `docs/working/REVIEW_FINDINGS.md`, or an
epic digest in `docs/working/digests/`, the repo's working documents win — a decision may have
been settled after the maps were written. `docs/source/` remains the sole business-rule authority.

## When building a new epic digest

Start from the matching capability map: it already enumerates the source sections the digest
needs (the maps cover the not-yet-implemented capabilities — SAP/disbursement, repayment,
monitoring/recovery, closure/compliance, platform operations — as well as the completed ones).
