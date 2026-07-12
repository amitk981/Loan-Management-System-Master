# Prototype Fidelity Checklist

- Existing AppShell/sidebar/header route and Appraisal Workbench composition retained.
- Existing queue, header, StageStepper, EligibilityChecklist, LoanLimitCalculator, card, badge,
  alert, input, and textarea patterns reused.
- No colour, typography, spacing, layout, card, badge, or queue pattern introduced.
- Only a required `Submission remarks` textarea was exposed using the existing `areaField` helper.
- Visual fixtures display stored API facts only; action visibility consumes six-field resource
  actions and never derives eligibility, money, review, or sanction authority locally.
