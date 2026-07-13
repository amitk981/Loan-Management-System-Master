# Credit Public Action / Write Results

| Matrix row | Enabled public write | Disabled public write | Denied evidence |
|---|---|---|---|
| eligibility run | success | exact permission denial | zero new audit/workflow; assessment unchanged |
| loan-limit calculate | success | exact permission denial | zero new audit/workflow; snapshot unchanged |
| appraisal create | success | exact create denial | zero note/risk/audit/workflow |
| appraisal update | success | exact update denial | draft unchanged; zero audit/workflow |
| prerequisite revalidate | success | exact revalidate denial | provenance unchanged; zero audit/workflow |
| submit for review | success | exact submit denial | state unchanged; zero audit/workflow |
| review: reviewed | one history row | exact review denial | zero history/note/audit/workflow |
| review: returned | one history row | exact review denial | zero history/note/audit/workflow |
| review: rejected | one history + one rejection note | exact review denial | zero history/note/audit/workflow |
| submit sanction | one case | exact state denial | zero case/audit/workflow |

Focused result: 11 tests passed. PostgreSQL result: 6 races passed twice, zero skips.
