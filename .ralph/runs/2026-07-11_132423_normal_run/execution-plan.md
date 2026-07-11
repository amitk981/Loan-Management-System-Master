# Execution Plan

Selected slice: CR-001-e2e-visual-baselines-nondeterministic

1. Add a dashboard-scenario clock fixture fixed to the committed-baseline instant and explicit
   browser timezone, then add exact greeting and role/date header assertions to both affected E2E
   modules.
2. Update both README commands to derive the Ralph virtualenv from Git's absolute common directory.
3. Run focused static/unit gates, verify the documented path expression, regenerate the two
   dashboard baselines once if required, and run both affected scenarios twice without updates.
4. Run all configured frontend and backend gates, save terminal evidence, review the diff and
   protected paths, then complete Ralph state/progress/handoff/slice artifacts.
