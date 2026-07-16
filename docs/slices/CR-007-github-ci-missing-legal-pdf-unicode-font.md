# Slice CR-007: GitHub backend CI does not provision the legal PDF Unicode font

## Status
Complete

## Origin
Change request (maintenance stage), accepted 2026-07-15 from docs/change-requests/accepted/CR-007-github-ci-missing-legal-pdf-unicode-font.md.

## Risk Level
High

## Depends On
- None

## Change Request (verbatim)

# GitHub backend CI does not provision the legal PDF Unicode font

## Type
bug-backend

## Severity
High

## What Is Happening
The full backend suite passes locally, including under `TZ=UTC`, but GitHub Actions backend CI fails two legal-document PDF tests. The PDF renderer fails closed with `Configured Unicode fonts do not cover the retained legal text.` because the Ubuntu runner has DejaVu Sans but does not provision the Noto Devanagari font that the renderer checks. Both affected API calls therefore return HTTP 400 instead of generating retained PDFs.

## Expected Behaviour
Every supported CI and deployment runtime must provision the Unicode font set required by the retained legal-document renderer. GitHub backend CI must generate PDFs containing Latin text, Devanagari text, and the Indian rupee symbol without depending on fonts that happen to exist on a developer workstation.

## Steps To Reproduce
1. Run GitHub Actions CI for staging commit `2de35942` on the Ubuntu runner.
2. Observe backend job 87342851243 execute the full `sfpcl_credit.tests` suite.
3. Observe `test_pdf_wraps_long_legal_text_across_bounded_pages` and `test_sanctioned_application_generates_retained_pdf_from_exact_template` fail because the generation endpoint returns HTTP 400.
4. Inspect the response field error: `Configured Unicode fonts do not cover the retained legal text.`
5. Run all 887 backend tests locally under `TZ=UTC` on macOS, where the configured host fallbacks exist, and observe all tests pass. This isolates missing Ubuntu font provisioning rather than application timezone behaviour.

## Where It Appears
GitHub Actions workflow `.github/workflows/ci.yml`, backend job; legal PDF renderer `sfpcl_credit/legal_documents/modules/document_renderer.py`; tests `sfpcl_credit/tests/test_loan_document_generation_api.py`; GitHub Actions run 29412562242, backend job 87342851243.

## Source Document Reference
`docs/working/ASSUMPTIONS.md` A-103 requires deployment to provide host fonts whose combined coverage includes every retained legal-text token and permits `LEGAL_DOCUMENT_PDF_FONT_PATH`. Ubuntu Noble's official `fonts-noto-core` package provides `/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf`, which is already an explicit renderer fallback. `docs/source/implementation-roadmap.md` section 13.3 and `docs/source/codebase-design.md` legal-document renderer sections require genuine readable Unicode PDF output and fail-closed rendering.

## Acceptance Criteria
GitHub backend CI explicitly installs the Ubuntu Unicode font package that supplies the renderer's existing Noto Devanagari path and verifies that path exists before running backend tests; the two legal PDF regression tests pass on the Ubuntu runner; all 887 backend tests and the 85% coverage gate pass; frontend CI remains green; the complete GitHub Actions run for the resulting staging commit is green; no legal-text glyph validation or quality gate is weakened.

## Mandatory First Step: Impact Analysis
Before changing ANY code, write impact-analysis.md in the run folder covering:
- Affected backend models/endpoints/services, with grep evidence.
- Affected frontend screens/components/routes.
- Blast radius: every OTHER module that consumes the affected pieces.
- Existing tests covering the affected pieces, and the regression tests to add in EACH affected module.
- FRONTEND_DESIGN_RULES compliance note for any UI change.
Validation fails this run if impact-analysis.md is missing.

## Acceptance Criteria
- The change request's own acceptance criteria are met.
- Regression tests added for every module named in the impact analysis.
- All quality gates pass.

## Resolution

Owner-authorized protected-path repair `615c1876` provisions Ubuntu's `fonts-noto-core` package in
the GitHub backend job and verifies
`/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf` before Python dependencies and
tests run. GitHub Actions run `29414744868` completed successfully: frontend CI passed, the font
provisioning step passed, and backend CI passed all 887 tests plus the 85% coverage gate. The
renderer and its fail-closed glyph validation were not changed.
