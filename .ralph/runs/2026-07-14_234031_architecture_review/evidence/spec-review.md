# Specification Review

Fixed point: `e046a9d3`  
Reviewed head: `bacc285d`  
Slices: 008G2, 008F2, 008H, 008I

## Findings

1. **High — mandatory ₹500 PoA stamp is not enforced.**
   Functional M06-FR-008 and V10 p.14 §4.3 require ₹500 plus notarisation. Activation checks only
   the generic `adequate` outcome; a focused public-path regression changed the adequate amount to
   ₹1 and still received HTTP 200. Corrective: 008I2.
2. **High — nullable pending CDSL evidence crashes.**
   Data-model §17.4 makes evidence nullable and 008I makes it mandatory only for acceptance, but
   pending POST dereferences the absent legal document and raises `AttributeError`. Corrective:
   008I4.
3. **High — implementation contradicts explicit owner/seam contracts.**
   008F2 promises real security ownership but leaves a dynamic legal wrapper; 008I promises the
   established masking/reveal owner but adds local crypto and reveal policy. Corrective: I2/I3/I4.
4. **Medium — complete changed-payload winner/loser proof is partial.**
   Tri-party omits promised workflow identity and CDSL acceptance does not prove exactly one
   material returned winner. Corrective: 008I3.

## Functional coverage

No epic completed. M06-FR-009/016/017 have substantive current-maker, tri-party, mismatch, and
consumed-evidence behavior. M06-FR-007/008 remain partial through I2. M06-FR-010/011/012 remain
partial across I3/I4. M06-FR-015 and the A-101/A-107 governed-term/signed-copy limits remain partial.

Totals: 3 High, 1 Medium. Worst issues: missing exact ₹500 enforcement and a source-valid request
causing an internal error.
