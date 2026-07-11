# Risk Assessment

Risk level: High.

Authorization/UI risk was the primary concern: a global permission previously manufactured a
resource control. The implementation now uses only selected-resource actions, with `/auth/me`
permissions and roles narrowing usability. Django still independently enforces every action.
No schema, migration, dependency, money formula, workflow transition, or sanction identity changed.
Regression risk is controlled by focused appraisal/sanction tests and all configured gates at 94%
backend coverage. Standing approval applies and no veto exists.

