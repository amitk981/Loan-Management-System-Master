# Risk Assessment

Risk level: Medium

- Selected slice: architecture-review
- Mode: architecture_review
- Rewrite target: oversized slice 012DA only
- Failed candidate: 3,475 changed lines against a 2,000-line limit

## Assessed Risks

1. **Contract loss during splitting — Medium.** The original combines two page owners, a
   report screen, register exports, the audit explorer, a separate observation workflow, five
   screenshots, and cross-surface evidence. The requirement-preservation matrix maps every
   prerequisite, requirement, test, evidence duty, mock removal, acceptance criterion, checklist,
   runtime capability, and risk to 012DAA-012DAC. Terminal 012DAC repeats the complete original
   five-screenshot, two-run browser contract.
2. **A successor still exceeds the diff limit — Medium.** Three natural capability seams replace
   the 3,475-line candidate. Predicted sizes are 1,050, 1,250, and 1,350 lines, leaving 650-950
   lines below the configured limit. The shared report page and browser spec extend serially.
3. **Premature mock-removal or shared-file collision — Medium.** 012DAA removes mock-backed report
   reads, while 012DAB explicitly owns final mock removal from `ReportsMIS.tsx` and
   `RegistersHub.tsx`. The dependency chain serializes both shared seams before 012DAC performs
   terminal acceptance.
4. **Security boundary loss — Medium.** Export permission/masking/audited-download requirements
   remain together in 012DAB. Read-only audit projection, restricted fields, and separately
   immutable observations remain together in 012DAC, preventing either boundary from being
   weakened to make an earlier slice green.
5. **Dependency bypass — Low after validation.** 012DAA inherits 012D2, each later successor
   depends on its immediate predecessor, and the only existing downstream dependency in 012G now
   points to terminal 012DAC. Dedicated split validation and full queue lint pass.
6. **Unauthorized scope expansion — Low.** No product code, source documents, protected files,
   mechanical Ralph state/progress, handoff, or unrelated slice content changed. The Epic digest
   changed only where its 012DA queue guidance became stale.

## Validation Evidence

- Dedicated oversized-slice split validation for 012DA: pass
- Full slice queue lint: pass
- Runtime-capability validation: pass for 012DAA, 012DAB, and 012DAC
- Whitespace validation: pass
- Queue rewrite: 6 queue/digest paths and 342 changed lines, below configured limits
- Product, source, protected, and mechanical-state changes: none
- Required review-packet Result text: pass
- Requirement preservation: complete; see `evidence/requirement-preservation-matrix.md`

## Residual Risk

Predicted successor sizes remain estimates because the rejected product diff is not present in this
worktree. The current run prompt retains its authoritative 3,475-line measurement and 2,000-line
limit; the three-way capability split deliberately caps the largest prediction at 1,350 lines.
Independent validation must continue to enforce the normal limit for every successor.
