# Independent Spec Review

Fixed point: `1e2d873112c1b14a43b81fa398f0013ba4bb02ae`

Diff command: `git diff 1e2d873...HEAD`

## Spec

- **High — 006C calculates against owned acreage, not evidenced acreage under cultivation.**
  Slice 006C and `functional-spec.md` BR-020 require land-based limit from scale of finance and
  acreage under cultivation. The service sums selected `LandHolding.area_acres` and never uses
  `CropPlan.planned_area_acres`; crop plan is checked only for member/application/alignment. The
  test masks the difference because both fixtures are five acres. Corrective slice: `006C2`.
- **Medium — 005I2 still synthesizes workflow state and overwrites backend ownership.** The slice
  requires stage/owner/document/status facts from the API or neutral absence. The page inherits
  documentation/disbursement defaults, hardcodes later-stage owner roles and stepper dates/claims,
  and tests only a submitted application. Corrective slice: `005I4`.
- **Medium — 006B invents nominee selection and can pass incomplete evidence.** The slice says not
  to invent a nominee selection rule. The service orders application-linked rows and silently
  chooses `.first()`, although the reverse link is not unique, then treats false `minor_flag` with
  no DOB/age as valid. Primary-contract inspection raised the impact to High: source §19.2 requires
  `nominee_id`, but no public staff/portal application API can store it, so the green eligible path
  requires direct ORM writes. Corrective slice: `005I3`.

No material scope creep was found.
