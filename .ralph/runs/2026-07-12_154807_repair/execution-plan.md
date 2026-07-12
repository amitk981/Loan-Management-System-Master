# Execution Plan

Selected slice: 006Y8-witness-maker-checker-and-browser-closure

Mode: repair

1. Preserve the completed slice implementation and reproduce the exact recorded trusted-browser
   failure from `2026-07-12_152923_repair`: session switching timed out because the test waited for
   a finance-user email that Header renders only after its profile menu is open.
2. Verify the current focused Playwright scenario contains only the demonstrated repair: open the
   profile menu through the visible seeded finance-user name, then click the real Sign out action.
3. Run the tight feedback loop: Playwright collection plus the slice-specific browser scenario when
   Chromium is available. Preserve honest sandbox launch output and rely on the orchestrator's two
   outside-sandbox executions for the authoritative browser verdict.
4. Run the configured frontend and backend gates with the mandated shared Python interpreter, then
   record terminal evidence and final Ralph artifacts. Do not alter production code unless the
   focused loop disproves the existing repair.
5. Verify the next Not Started slice is already concretely sharpened, update handoff/progress/state
   only to reflect this repair run, and leave 006Y8 Complete.
