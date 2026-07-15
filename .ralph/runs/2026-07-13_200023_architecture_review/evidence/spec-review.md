# Specification Review

Review window: `git diff b32559c...78d912f`

1. Critical: 007F/M05-FR-006 requires recommended amount above frozen eligible amount or an
   explicit forced route. Production trusts the boolean alone; a test blesses ₹4,00,000 recommended
   against ₹5,00,000 eligible after manually flipping the flag. Corrective owner: 007F2.
2. High: 007G requires rejected General Meeting evidence to block sanction and appear on case
   detail. The pending case detail reads only a terminal/return-frozen FK, so pending/rejected
   current evidence remains null. Corrective owner: 007G2.
3. Medium: 007G requires each evidence document to be one the actor may access. Global permission
   plus unrestricted metadata existence does not satisfy that per-file rule. Corrective owner: 007G2.

No material scope creep was found. M05-FR-011 is substantive. M05-FR-003/006, M05-FR-012, and the
read-confidentiality portion of M05-FR-009 remain partial until 007F2/007G2/007H2 respectively.

Spec total: 3 findings (1 Critical, 1 High, 1 Medium). Worst: the shipped exception predicate accepts
contradictory frozen facts and the real path is also hidden by the coherence mismatch.

