# Two-Axis Independent Review

Range: `git diff 7e119610...12e2dea4`

Commits: 008D2 `08356302`, 008E2 `f3abacc7`, 008F `3c6a653c`, 008G `12e2dea4`.

## Standards

1. Critical: `SecurityPackage`, `PowerOfAttorney`, and their workflow live in `legal_documents`,
   contrary to data-model §17 and codebase-design §§8.2/36.2's `security_instruments` owner.
2. High: stamp/notary, signature, and verification domain modules import and parse HTTP request
   serializers, reversing codebase-design §§6.3-6.4/36.1.
3. High: PoA duplicates actor/role/permission logic outside the legal authority seam; evidence and
   request-context helpers are copied with already-divergent identity payloads.
4. Medium: §26.6 does not return the §6.3 action response, and unresolved mismatch overwrite uses
   generic 409 rather than §7.2's specific error contract.
5. Judgement: PoA races omit activation/checker contention; purpose validation rejects unrelated
   negative language anywhere in otherwise affirmative legal text.

Worst Standards issue: future SH-4/CDSL work would deepen security policy in the wrong app.

## Spec

1. High: a second actor can materially edit pending stamp/notary/signature/PoA facts while the row
   retains the first maker id, then act as checker through another role.
2. High: Compliance can PATCH an active PoA back to draft/pending and clear the CS verifier.
3. High: mutable application status creates a package without canonical terminal sanction, and a
   verified tri-party's consumed signature can later be rewritten while verification stays true.
4. Medium: 008G's PostgreSQL-only race was skipped with no declared runtime capability, and its
   promised public-generation tracer manually labels ORM rows as renderer-current.

No unrelated scope creep was found. Worst Spec issue: stale current-maker identity permits a user
to check the facts they actually prepared.

Corrective ownership: 008G2 closes legal evidence/action/race gaps; 008F2 closes the security
boundary and PoA sanction/lifecycle gaps. Reports were produced in isolated contexts and reconciled
against current code, tests, evidence, and source citations by the root reviewer.

