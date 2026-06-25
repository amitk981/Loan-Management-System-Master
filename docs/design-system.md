# design-system.md

# SFPCL Member Credit Administration & Settlement — Detailed Design System

## 1. Document Control

| Field | Detail |
|---|---|
| Document name | `design-system.md` |
| Product / platform | SFPCL Member Credit Administration & Settlement / Loan Management System |
| Client | Sahyadri Farmers Producer Company Limited |
| Source process | `SOP_SFPCL_LOANDISBURSEMENT` and WhatsLoan visual SOP summary |
| Current design system status | Draft for product, UX, UI, engineering and QA alignment |
| Intended readers | Product, design, engineering, QA, compliance, operations, implementation and client stakeholders |
| Related analysis artifacts | Client brief, user flows, functional specification, information architecture, screen specification, content specification and component specification |
| Primary process covered | Member loan request, assessment, sanction, documentation, disbursement, monitoring, repayment, default handling, closure and compliance |

---

## 2. Purpose of This Design System

This design system defines the visual, interaction, content, component and implementation standards for the SFPCL Member Credit Administration & Settlement product. It translates the SOP-driven loan lifecycle into a consistent product experience that is usable by operational teams while preserving the strict controls required for member lending, statutory compliance, documentation, finance posting, disbursement, repayment monitoring and auditability.

The design system must ensure that every interface supports the following business outcomes:

1. **No non-member loan processing.** The UI must make member validation visible and enforceable.
2. **No uncontrolled disbursement.** Disbursement must be blocked until sanction, documentation, SAP setup, bank verification and checklist approvals are complete.
3. **No invisible exceptions.** Any deviation from limits, policy, required documentation or approval sequence must be visibly captured in an Exception Register flow.
4. **No unclear accountability.** Every action must identify the actor, role, timestamp, decision, reason and resulting state.
5. **No fragmented information.** Registers, dashboards and operational queues must be views generated from the same underlying loan record, not separate data islands.
6. **No borrower-unfriendly communication.** Borrower-facing messages must be simple, respectful, specific and suitable for farmer / FPC contexts.
7. **No compliance ambiguity.** Legal and regulatory gates must be surfaced through statuses, warnings, checklists, required reason capture and audit trails.

---

## 3. Product Context the Design System Must Support

### 3.1 Organisation Context

SFPCL is a farmer-owned Producer Company with individual farmer shareholders and Farmer Producer Companies as members. The lending product exists to provide structured, transparent and controlled credit support to members for agricultural and crop-production purposes.

### 3.2 Process Scope

The UI and design system must support six SOP lifecycle stages:

| Stage | Name | Primary operational focus |
|---:|---|---|
| 1 | Initial Loan Request | Application intake, borrower / nominee data, KYC and supporting documents |
| 2 | Credit Assessment | Completeness check, reference number, eligibility, appraisal note and loan limit calculation |
| 3 | Credit Scrutiny and Approval | Sanction Committee review, approval matrix, rejection, special-case routing and registers |
| 4 | Documentation and Stamping | PoA, Tri-party Agreement, SH-4, CDSL pledge, Term Sheet, Loan Agreement, bank verification and checklist approvals |
| 5 | Loan Disbursement | SAP customer code, final verification, RBL bank transfer initiation, CFC approval and disbursement advice |
| 6 | Monitoring and Repayment | Repayment posting, interest accrual, invoices, DPD monitoring, default handling, recovery action and closure |

### 3.3 Primary User Roles

The design system must support different role-based workspaces and permission-aware components.

| Role | Interface needs |
|---|---|
| Borrower / Member / Farmer / FPC | Simple application status, required document guidance, repayment information, NOC / closure communication and grievance access |
| Deputy Manager – Finance | Application completeness, reference number generation, appraisal drafting, document checks and handoff to Credit Manager |
| Credit Manager | Loan Request Register, eligibility review, appraisal review, loan limit confirmation, rejection note, reminders, DPD monitoring and MIS inputs |
| Compliance Team Member | Documentation preparation, checklist management, stamping status, legal document tracking and signature mismatch handling |
| Company Secretary | Legal and compliance verification, PoA, stamp duty, SH-4 custody, grievance log, record retention and compliance sign-off |
| Sanction Committee | Sanction review, approval / rejection, exception decisions, special-case checks and Credit Sanction Register actions |
| Chief Financial Officer | Approval participation, policy oversight, Section 186 / NBFC monitoring, MIS review and exception review |
| Senior Manager – Finance | SAP customer code creation coordination, final document verification, disbursement initiation and checklist completion |
| Chief Financial Controller | Final bank transfer approval and execution |
| Accounts Team / Accounts Head | SAP accounting entries, repayment posting, interest accrual, invoices, DPD and portfolio reporting |
| IT Head / System Administrator | User access, role configuration, data protection, audit logs and system health |
| Internal / Statutory Auditor | Read-only audit evidence, registers, documents, approvals, logs and exception traceability |

---

## 4. Design System Principles

### 4.1 Compliance First, Usability Always

Interfaces must never hide compliance obligations behind convenience. However, compliance must be made understandable through clear labels, checklists, progressive disclosure, guided decisions and plain-language explanations.

### 4.2 Lifecycle-First Navigation

The system should reflect the loan journey from application to closure. Every loan should have a visible stage, status, next action and blocker state.

### 4.3 One Loan, One Source of Truth

All dashboards, queues and registers must derive from the same canonical loan application / loan account record. The UI should discourage duplicate offline registers by making register views exportable and auditable.

### 4.4 Maker-Checker by Default

Any action with financial, legal, compliance or borrower impact should separate preparation from approval. The design system must include reusable maker-checker patterns for appraisal, sanction, documentation, disbursement, recovery and closure.

### 4.5 Traceability Over Speed

The product must prioritise complete records, captured reasons and visible evidence over fast but undocumented action.

### 4.6 No Invisible Business Logic

Calculations and blockers must be explainable. Loan limit, eligibility, DPD, approval authority and document completeness should display input values and calculation breakdowns.

### 4.7 Role-Aware but Consistent

Different roles need different actions, but the same object should look and behave consistently across roles. A loan application should not become visually different merely because it is viewed by Finance, Compliance or Sanction Committee.

### 4.8 Farmer-Friendly Communication

Borrower-facing content must be direct, respectful and actionable. It must avoid legalistic language unless required, and must explain what is needed, why it is needed and what happens next.

### 4.9 Configurable for Policy Changes

The SOP contains policy values that may change, including share valuation percentage, per-acre cost of cultivation, loan thresholds, interest rate, penal charges and re-KYC frequency. UI components must read these from configuration, not hard-coded copy or logic.

### 4.10 Audit-Ready by Design

Every critical component should answer: who acted, when, under what authority, based on which data, with which documents, with what result.

---

## 5. Brand and Visual Foundations

### 5.1 Brand Attributes

The product’s visual identity should communicate:

| Attribute | Design interpretation |
|---|---|
| Trust | Stable layout, clear hierarchy, low visual noise, explicit confirmations |
| Transparency | Visible calculations, audit trails, status explanations and non-hidden blockers |
| Agriculture | Organic green accents, crop / farmland imagery only where useful, natural visual warmth |
| Financial control | Structured tables, precise amounts, strong validation, approval gates |
| Compliance | Formal states, document completeness patterns, mandatory reason capture |
| Member support | Plain-language guidance, clear next steps, respectful borrower communication |

### 5.2 Logo and Brand Asset Usage

If official SFPCL / Sahyadri Farms logo files are available, use them in the following placements:

| Placement | Usage |
|---|---|
| Login / access landing | Primary logo, centred or top-left depending on layout |
| Application shell | Compact logo in sidebar or header |
| Generated documents | Full-width header logo with company name and document metadata |
| Borrower communication PDFs | Logo plus contact information and document title |
| Email templates | Logo optional, subject and body clarity more important |

Rules:

- Do not distort the logo.
- Maintain clear space equal to at least the logo mark height.
- Do not place the logo on low-contrast or busy backgrounds.
- Do not use crop imagery as a substitute for official identity.
- Do not embed unofficial watermarks in legal documents.

### 5.3 Visual Tone

The system should use a practical enterprise tone: clean, controlled, plain and action-oriented. Avoid decorative UI that distracts from compliance tasks.

Recommended visual qualities:

- White or very light neutral work surfaces.
- Clear cards for task grouping.
- Green as a primary brand / positive action colour.
- Amber for warnings and pending action.
- Red for errors, defaults and destructive actions.
- Blue for informational and finance / SAP states.
- Purple or violet for exception and policy-deviation states.
- Strong typography hierarchy for dense administrative screens.

---

## 6. Design Tokens

### 6.1 Token Naming Convention

Use a layered token model:

```text
primitive token → semantic token → component token
```

Examples:

```text
color.green.700 → color.action.primary.bg → button.primary.bg
space.4 → layout.card.padding.sm → document-card.padding
font.size.14 → text.body.sm.size → table-cell.font-size
```

Recommended naming format:

```text
category.role.property.variant.state
```

Examples:

```text
color.status.approved.bg
color.status.rejected.text
border.form.error
shadow.card.default
radius.button.md
space.stack.form-row
```

---

## 7. Colour System

### 7.1 Primitive Palette

The following palette is recommended as a product baseline. Official brand colours should override only after contrast testing.

#### Green / Primary

| Token | Hex | Usage |
|---|---|---|
| `color.green.50` | `#F0FDF4` | Light success / primary surface |
| `color.green.100` | `#DCFCE7` | Badge backgrounds, selected rows |
| `color.green.200` | `#BBF7D0` | Subtle borders |
| `color.green.300` | `#86EFAC` | Progress accents |
| `color.green.500` | `#22C55E` | Secondary visual accents |
| `color.green.600` | `#16A34A` | Primary button background |
| `color.green.700` | `#15803D` | Primary button hover / strong emphasis |
| `color.green.800` | `#166534` | Dark primary text on light green |
| `color.green.900` | `#14532D` | High-emphasis primary text |

#### Neutral

| Token | Hex | Usage |
|---|---|---|
| `color.neutral.0` | `#FFFFFF` | Primary page / card surface |
| `color.neutral.50` | `#F8FAFC` | App background |
| `color.neutral.100` | `#F1F5F9` | Subtle panels |
| `color.neutral.200` | `#E2E8F0` | Borders |
| `color.neutral.300` | `#CBD5E1` | Disabled borders |
| `color.neutral.400` | `#94A3B8` | Placeholder text |
| `color.neutral.500` | `#64748B` | Secondary text |
| `color.neutral.600` | `#475569` | Body secondary |
| `color.neutral.700` | `#334155` | Primary body text |
| `color.neutral.800` | `#1E293B` | Headings |
| `color.neutral.900` | `#0F172A` | High-emphasis text |

#### Blue / Information and Finance

| Token | Hex | Usage |
|---|---|---|
| `color.blue.50` | `#EFF6FF` | Info surface |
| `color.blue.100` | `#DBEAFE` | SAP / finance badge bg |
| `color.blue.600` | `#2563EB` | Info actions and links |
| `color.blue.700` | `#1D4ED8` | Link hover |
| `color.blue.900` | `#1E3A8A` | Info text |

#### Amber / Warning

| Token | Hex | Usage |
|---|---|---|
| `color.amber.50` | `#FFFBEB` | Warning surface |
| `color.amber.100` | `#FEF3C7` | Pending badge bg |
| `color.amber.500` | `#F59E0B` | Warning icon |
| `color.amber.700` | `#B45309` | Warning text |
| `color.amber.900` | `#78350F` | High-emphasis warning text |

#### Red / Error, Rejection and Default

| Token | Hex | Usage |
|---|---|---|
| `color.red.50` | `#FEF2F2` | Error surface |
| `color.red.100` | `#FEE2E2` | Rejected / default badge bg |
| `color.red.500` | `#EF4444` | Error icon |
| `color.red.600` | `#DC2626` | Destructive button |
| `color.red.700` | `#B91C1C` | Destructive hover / error text |
| `color.red.900` | `#7F1D1D` | High-emphasis destructive text |

#### Violet / Exception and Policy Deviation

| Token | Hex | Usage |
|---|---|---|
| `color.violet.50` | `#F5F3FF` | Exception surface |
| `color.violet.100` | `#EDE9FE` | Exception badge bg |
| `color.violet.600` | `#7C3AED` | Exception accent |
| `color.violet.800` | `#5B21B6` | Exception text |

#### Teal / Completion and Closure

| Token | Hex | Usage |
|---|---|---|
| `color.teal.50` | `#F0FDFA` | Closure surface |
| `color.teal.100` | `#CCFBF1` | Closure badge bg |
| `color.teal.700` | `#0F766E` | Closure text |

### 7.2 Semantic Colour Tokens

| Token | Value | Usage |
|---|---|---|
| `color.surface.app` | `color.neutral.50` | Main application background |
| `color.surface.card` | `color.neutral.0` | Cards, panels, tables |
| `color.surface.muted` | `color.neutral.100` | Secondary panels |
| `color.text.primary` | `color.neutral.900` | Main text |
| `color.text.secondary` | `color.neutral.600` | Supporting text |
| `color.text.muted` | `color.neutral.500` | Metadata, timestamps |
| `color.border.default` | `color.neutral.200` | Standard borders |
| `color.border.strong` | `color.neutral.300` | Emphasised divider |
| `color.action.primary.bg` | `color.green.600` | Primary actions |
| `color.action.primary.hover` | `color.green.700` | Primary action hover |
| `color.action.secondary.bg` | `color.neutral.0` | Secondary actions |
| `color.action.destructive.bg` | `color.red.600` | Delete, reject, invoke security |
| `color.action.link` | `color.blue.600` | Links |
| `color.focus.ring` | `color.green.600` | Keyboard focus ring |

### 7.3 Status Colour Mapping

| Status family | Background | Border | Text | Icon |
|---|---|---|---|---|
| Draft / Not started | `neutral.100` | `neutral.200` | `neutral.700` | Circle |
| Submitted / Received | `blue.50` | `blue.100` | `blue.900` | Inbox |
| In review | `amber.50` | `amber.100` | `amber.900` | Clock |
| Approved | `green.50` | `green.100` | `green.900` | CheckCircle |
| Rejected | `red.50` | `red.100` | `red.900` | XCircle |
| Blocked | `red.50` | `red.100` | `red.900` | AlertTriangle |
| Exception | `violet.50` | `violet.100` | `violet.800` | AlertOctagon |
| Disbursed | `green.50` | `green.200` | `green.900` | Banknote |
| Closed | `teal.50` | `teal.100` | `teal.700` | BadgeCheck |
| Archived | `neutral.100` | `neutral.300` | `neutral.600` | Archive |

### 7.4 Stage Colour Mapping

| SOP stage | Stage colour | Primary use |
|---|---|---|
| Stage 1 — Initial Loan Request | Blue | Intake, submission, reference number |
| Stage 2 — Credit Assessment | Amber | Completeness, eligibility, appraisal |
| Stage 3 — Credit Scrutiny and Approval | Violet | Sanction, approval matrix, exceptions |
| Stage 4 — Documentation and Stamping | Indigo / Blue | Legal documents, checklist, stamping |
| Stage 5 — Loan Disbursement | Green | SAP, finance approval, bank transfer |
| Stage 6 — Monitoring and Repayment | Teal / Amber / Red based on condition | Repayments, DPD, default, closure |

### 7.5 Colour Accessibility Rules

- All text must meet WCAG AA contrast: at least 4.5:1 for normal text and 3:1 for large text.
- Colour must never be the only indicator of status. Pair with label and icon.
- Red and green must include distinct icons and text for users with colour vision deficiencies.
- Disabled controls must remain legible but clearly non-interactive.
- Critical banners must use text labels such as `Blocked`, `Exception`, `Default`, or `Approval Required`.

---

## 8. Typography System

### 8.1 Typeface

Recommended product font stack:

```css
font-family: Inter, "Noto Sans", "Noto Sans Devanagari", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
```

Rationale:

- Inter provides excellent legibility for enterprise UI.
- Noto Sans provides strong multilingual support.
- Noto Sans Devanagari supports Marathi / Hindi-ready borrower-facing interfaces if required.
- System fallbacks preserve performance.

### 8.2 Type Scale

| Token | Size | Line height | Weight | Usage |
|---|---:|---:|---:|---|
| `text.display.lg` | 40px | 48px | 700 | Rare executive / landing headings |
| `text.display.md` | 32px | 40px | 700 | Module landing pages |
| `text.heading.h1` | 28px | 36px | 700 | Page title |
| `text.heading.h2` | 24px | 32px | 700 | Section page title |
| `text.heading.h3` | 20px | 28px | 600 | Card or panel title |
| `text.heading.h4` | 18px | 26px | 600 | Form section title |
| `text.body.lg` | 16px | 24px | 400 | Prominent body copy |
| `text.body.md` | 14px | 22px | 400 | Default UI body text |
| `text.body.sm` | 13px | 20px | 400 | Table cells, metadata |
| `text.caption` | 12px | 16px | 400 | Helper text, badges, timestamps |
| `text.overline` | 11px | 14px | 600 | Section labels, uppercase metadata |

### 8.3 Typography Rules

- Use sentence case for UI labels and page titles.
- Use title case only for formal document names and generated document headings.
- Use tabular numerals for currency, dates, counts, DPD days, loan amounts and share quantities.
- Keep table content at `13px` or `14px` depending on density.
- Use `font-weight: 600` for labels that must stand out, such as status, approvals and blockers.
- Do not use all caps for long labels. Reserve uppercase for short reference labels such as `PAN`, `KYC`, `CKYC`, `SAP`, `NOC`, `SH-4`, `DPD`.

### 8.4 Numeric Formatting

| Type | Format |
|---|---|
| Currency | `₹5,00,000` |
| Large currency | Indian comma format, e.g. `₹12,50,000` |
| Percentages | `10%`, `30%`, `12.5% p.a.` |
| Dates | `07 Aug 2025` in UI; ISO in exports where required |
| Application ID | `LO00000001` |
| Tenure | `12 months`, `3 months`, `1 year` |
| DPD | `1 year – 2 years`, `2 years – 3 years`, `3+ years` |

---

## 9. Spacing, Grid and Layout System

### 9.1 Spacing Scale

Use a 4px base grid.

| Token | Value | Usage |
|---|---:|---|
| `space.0` | 0px | No spacing |
| `space.1` | 4px | Tight icon-label gap |
| `space.2` | 8px | Small gaps, table cell padding |
| `space.3` | 12px | Form row gaps |
| `space.4` | 16px | Default card padding |
| `space.5` | 20px | Section spacing |
| `space.6` | 24px | Panel padding |
| `space.8` | 32px | Page section separation |
| `space.10` | 40px | Major layout break |
| `space.12` | 48px | Landing / empty state spacing |
| `space.16` | 64px | Large page separation |

### 9.2 Layout Breakpoints

| Breakpoint | Width | Usage |
|---|---:|---|
| `xs` | <480px | Borrower mobile views, minimal operational access |
| `sm` | 480–767px | Simple forms, borrower status pages |
| `md` | 768–1023px | Tablet / field officer workflows |
| `lg` | 1024–1279px | Standard desktop operations |
| `xl` | 1280–1535px | Dense operational dashboards |
| `2xl` | 1536px+ | Audit / finance / large table views |

### 9.3 Page Layout Patterns

#### Standard Operational Page

```text
Global header
Sidebar navigation
Page header with title, status and actions
Optional stage stepper
Main content grid
Right-side context panel or audit drawer
Footer metadata / pagination where applicable
```

#### Loan 360 Page

```text
Loan identity header
Stage stepper
Critical blocker strip
Two-column layout:
  Main column: tabs, forms, documents, transactions
  Right column: status, next actions, checklist, audit trail
```

#### Approval Page

```text
Summary header
Decision panel
Loan and borrower facts
Eligibility and limit calculation
Documents and exceptions
Reason capture
Approve / reject actions
Audit trail
```

### 9.4 Layout Widths

| Area | Width |
|---|---:|
| Sidebar collapsed | 72px |
| Sidebar expanded | 248px |
| Header height | 64px |
| Page max content width | 1440px |
| Standard card min width | 320px |
| Right drawer width | 420px |
| Wide drawer width | 640px |
| Modal small | 480px |
| Modal medium | 720px |
| Modal large | 960px |

---

## 10. Shape, Radius, Border and Elevation

### 10.1 Radius Tokens

| Token | Value | Usage |
|---|---:|---|
| `radius.none` | 0px | Tables requiring strict grid alignment |
| `radius.xs` | 2px | Tiny tags |
| `radius.sm` | 4px | Inputs, badges |
| `radius.md` | 8px | Buttons, table filters, cards |
| `radius.lg` | 12px | Panels, empty states |
| `radius.xl` | 16px | High-level dashboard cards |
| `radius.full` | 9999px | Pills, avatar circles |

### 10.2 Border Tokens

| Token | Value | Usage |
|---|---|---|
| `border.default` | `1px solid color.border.default` | Cards, inputs, table cells |
| `border.strong` | `1px solid color.border.strong` | Section separation |
| `border.focus` | `2px solid color.focus.ring` | Keyboard focus |
| `border.error` | `1px solid color.red.600` | Invalid fields |
| `border.warning` | `1px solid color.amber.500` | Warning panels |
| `border.exception` | `1px solid color.violet.600` | Exceptions |

### 10.3 Elevation Tokens

| Token | CSS | Usage |
|---|---|---|
| `shadow.none` | `none` | Flat tables, forms |
| `shadow.xs` | `0 1px 2px rgba(15, 23, 42, 0.06)` | Subtle cards |
| `shadow.sm` | `0 1px 3px rgba(15, 23, 42, 0.10)` | Dropdowns, small panels |
| `shadow.md` | `0 4px 12px rgba(15, 23, 42, 0.12)` | Modals, drawers |
| `shadow.lg` | `0 16px 32px rgba(15, 23, 42, 0.16)` | High-risk confirmations |

Rules:

- Avoid heavy shadows in dense operations pages.
- Use shadows primarily for overlays, drawers, dropdowns and modals.
- Use borders more than shadows for enterprise clarity.

---

## 11. Iconography System

### 11.1 Icon Style

Recommended icon family:

- Lucide, Feather, Material Symbols Rounded or an equivalent open-source line icon set.

Icon rules:

- 1.5px or 2px line weight.
- Rounded line caps preferred.
- Default size: 16px in tables, 20px in buttons, 24px in cards.
- Never use icons without labels for critical actions.
- Tooltips are required for icon-only controls.

### 11.2 Core Icon Mapping

| Concept | Icon suggestion |
|---|---|
| Member / borrower | UserRound |
| FPC / Producer Institution | Building2 |
| Loan application | FileText |
| KYC | IdCard |
| Land record | MapPinned |
| Crop plan | Sprout |
| Shareholding | PieChart / BadgeIndianRupee |
| Appraisal | ClipboardCheck |
| Sanction | Gavel / ShieldCheck |
| Documentation | FolderCheck |
| Stamp duty | Stamp |
| PoA | ScrollText |
| SH-4 | FileSignature |
| CDSL pledge | LockKeyhole |
| SAP | Database |
| Bank transfer | Banknote |
| Repayment | ReceiptIndianRupee |
| Interest invoice | FileSpreadsheet |
| DPD monitoring | TimerReset |
| Default | AlertTriangle |
| Exception | AlertOctagon |
| Grievance | MessageSquareWarning |
| NOC / Closure | BadgeCheck |
| Audit trail | History |
| Archive | Archive |

### 11.3 Icon Accessibility

- Icons must include accessible labels when they communicate meaning.
- Decorative icons must be hidden from screen readers.
- Status icons must be paired with text labels.

---

## 12. Motion and Interaction Feedback

### 12.1 Motion Principles

Motion should clarify state changes, not entertain. Use subtle transitions for:

- Drawer open / close.
- Stepper progress.
- Saving states.
- Field validation.
- Toast notifications.
- Row expansion.

Avoid motion for:

- Financial amounts changing.
- Approval confirmations.
- Legal document acceptance.
- Audit logs.

### 12.2 Duration Tokens

| Token | Duration | Usage |
|---|---:|---|
| `motion.fast` | 100ms | Hover, focus, pressed state |
| `motion.normal` | 180ms | Dropdown, row expand |
| `motion.slow` | 240ms | Drawer, modal |
| `motion.long` | 320ms | Page-level transitions, rarely used |

### 12.3 Easing

```css
ease-standard: cubic-bezier(0.2, 0, 0, 1)
ease-emphasized: cubic-bezier(0.2, 0, 0, 1)
ease-exit: cubic-bezier(0.4, 0, 1, 1)
```

### 12.4 Reduced Motion

Respect `prefers-reduced-motion`. Replace transitions with instant state changes where required.

---

## 13. Accessibility Standards

### 13.1 Required Standard

Target WCAG 2.2 AA for internal and borrower-facing interfaces.

### 13.2 Keyboard Requirements

- Every action must be reachable by keyboard.
- Focus order must follow visual order.
- Modal focus must trap within modal until closed or submitted.
- Escape must close non-critical drawers and modals.
- Escape must not close high-risk confirmation dialogs unless an explicit cancel action exists.
- Tables must support keyboard row navigation where possible.
- File upload must be accessible through keyboard and file picker, not only drag-and-drop.

### 13.3 Screen Reader Requirements

- Page title must update on route change.
- Status badges must be announced with status value.
- Validation messages must be linked to invalid fields.
- Required fields must be programmatically indicated.
- Calculation result changes must be announced when triggered by user input.
- Approval and rejection confirmations must have descriptive modal titles.

### 13.4 Forms Accessibility

- Every input must have a persistent label.
- Placeholder text must not replace labels.
- Required fields must show visible and programmatic required status.
- Error text must be explicit and actionable.
- Helper text must explain why sensitive data is required.

### 13.5 Colour and Contrast

- Minimum 4.5:1 contrast for body text.
- Minimum 3:1 contrast for icons and large text.
- Focus indicator must be clearly visible at 2px.
- Status must never rely on colour alone.

---

## 14. Data Density and Enterprise Usability

### 14.1 Density Modes

The product should support two density modes for operational users:

| Mode | Usage |
|---|---|
| Comfortable | Default for forms, borrower-facing screens and dashboards |
| Compact | Tables, registers, audit logs and finance screens |

### 14.2 Table Density Rules

| Element | Comfortable | Compact |
|---|---:|---:|
| Row height | 48px | 36px |
| Cell horizontal padding | 16px | 12px |
| Cell vertical padding | 12px | 8px |
| Font size | 14px | 13px |
| Checkbox size | 18px | 16px |

### 14.3 Dense Information Rules

- Use sticky table headers for long registers.
- Freeze key identifying columns for wide tables.
- Use column configuration for audit / finance users.
- Use progressive disclosure for secondary fields.
- Provide export for register views.
- Do not hide status, amount, applicant name, current stage, pending owner or ageing in queues.

---

## 15. Application Shell

### 15.1 Global Header

The global header should include:

- Product name or compact brand.
- Global search.
- Current environment indicator if applicable, e.g. `Production`, `UAT`.
- Notifications icon with unread count.
- Task inbox shortcut.
- User profile and role switcher if multi-role.
- Help / SOP reference shortcut.

Header height: 64px.

### 15.2 Sidebar Navigation

Primary navigation:

1. Dashboard
2. Applications
3. Members & Borrowers
4. Appraisal
5. Sanctions
6. Documentation
7. SAP & Finance
8. Disbursements
9. Repayments
10. Monitoring & Default
11. Closure
12. Compliance
13. Registers
14. Grievances
15. Reports
16. Administration

Role-specific sidebar examples:

| Role | Prioritised sections |
|---|---|
| Credit Manager | Dashboard, Applications, Appraisal, Sanctions, Monitoring, Registers, Reports |
| Compliance Team | Documentation, Compliance, Registers, Grievances, Closure |
| Senior Manager – Finance | SAP & Finance, Disbursements, Repayments, Registers |
| CFO | Dashboard, Sanctions, Exceptions, Compliance, Reports |
| Auditor | Registers, Reports, Audit Trail, Documents |

### 15.3 Breadcrumbs

Breadcrumbs should show module hierarchy:

```text
Applications / LO00000042 / Documentation / Checklist
```

Rules:

- Never include excessive breadcrumbs beyond four levels.
- Current page is not clickable.
- Loan application ID should be clickable back to Loan 360.

### 15.4 Page Header

Every page header should include:

- Page title.
- Short description where helpful.
- Primary status badge.
- Key metadata such as `Loan ID`, `Borrower`, `Current owner`.
- Primary actions.
- Secondary actions in overflow menu.

Loan page header example:

```text
LO00000042 — Loan application for Ramesh Patil
Stage 4: Documentation and Stamping · Pending Company Secretary review
Requested amount: ₹4,50,000 · Eligible amount: ₹4,80,000
```

---

## 16. Status Badge System

### 16.1 Badge Anatomy

A status badge consists of:

- Icon.
- Label.
- Optional count or timestamp.
- Tooltip with definition.

### 16.2 Badge Sizes

| Size | Height | Text | Usage |
|---|---:|---:|---|
| Small | 22px | 12px | Tables |
| Medium | 28px | 13px | Cards, headers |
| Large | 36px | 14px | Page-level stage display |

### 16.3 Application Status Labels

| Status | Visual family | Meaning |
|---|---|---|
| Draft | Neutral | Application data started but not submitted |
| Submitted | Blue | Borrower application received |
| Incomplete | Amber | Missing required fields or documents |
| Reference issued | Blue | Unique `LO...` reference generated |
| Under appraisal | Amber | Deputy Manager / Credit Manager assessment in progress |
| Rejected by Credit | Red | Credit Assessment Team rejected before sanction |
| Pending sanction | Violet | Sent to Sanction Committee |
| Approved | Green | Sanction Committee approved |
| Rejected by Sanction Committee | Red | Sanction Committee rejected |
| Documentation pending | Amber | Documents not complete |
| Documentation complete | Green | All required documents verified |
| SAP setup pending | Blue | SAP code not created / confirmed |
| Ready for disbursement | Green | All gates complete; finance may initiate |
| Disbursement initiated | Blue | Payment initiated by Senior Manager – Finance |
| Disbursed | Green | Bank transfer executed |
| Active repayment | Blue | Loan account active |
| Overdue | Amber / Red by severity | Repayment overdue |
| Default review | Red | Non-payment review triggered |
| Recovery approval pending | Violet / Red | Recovery action awaiting approval |
| Closed | Teal | Fully repaid and NOC issued |
| Archived | Neutral | Loan file retained for records |

### 16.4 Documentation Status Labels

| Status | Meaning |
|---|---|
| Not started | No document process initiated |
| Pending borrower documents | Borrower / nominee / witness documents missing |
| Pending preparation | Compliance Team must generate documents |
| Pending signature | Signature required from borrower, nominee, witness or authority |
| Pending stamping | Stamp duty / stamp paper not completed |
| Pending notarisation | PoA / Loan Agreement notarisation incomplete |
| Pending CS review | Company Secretary verification required |
| Pending Credit Manager review | Credit Manager limit / document review required |
| Pending Sanction Committee final approval | Checklist approval required |
| Complete | All documentation gates satisfied |
| Blocked | Cannot proceed due to defect or mismatch |

### 16.5 Security Status Labels

| Security | Statuses |
|---|---|
| SH-4 | Not required, Required, Pending signature, Held in custody, Returned, Invoked |
| Blank-dated cheque | Pending collection, Held in custody, Returned, Presented, Cancelled |
| CDSL pledge | Not required, PRF pending, PSN generated, Pledge accepted, Pledged, Invocation requested, Invoked, Unpledged |
| PoA | Drafted, Signed, Stamped, Notarised, Active, Closed |

### 16.6 Repayment and Default Status Labels

| Status | Meaning |
|---|---|
| Current | No overdue principal or interest condition requiring action |
| Interest invoice due | Year-end interest invoice pending |
| Interest unpaid after 30 April | Interest must be capitalised if not paid |
| Principal overdue | Scheduled principal not paid |
| Grace period active | Three-month extension after missed repayment is active |
| Non-payment review | Team must classify intentional vs non-intentional |
| One-year extension active | Non-intentional non-payment extension granted |
| Non-recoverable review | Extension failed; Note for Non-Payment required |
| Recovery action pending | Sanction Committee decision required |
| Security invoked | SH-4, CDSL pledge or cheque action approved and executed |
| Fully repaid | Principal and dues fully settled |
| NOC issued | Closure confirmed |

---

## 17. Buttons and Action System

### 17.1 Button Hierarchy

| Button type | Usage | Example |
|---|---|---|
| Primary | Main page action | `Submit application`, `Approve sanction`, `Initiate disbursement` |
| Secondary | Supporting action | `Save draft`, `Download checklist` |
| Tertiary / ghost | Low emphasis action | `View details`, `Add note` |
| Destructive | Irreversible / high-risk action | `Reject application`, `Invoke SH-4`, `Delete draft` |
| Warning | Risky but not destructive | `Create exception`, `Mark incomplete` |
| Link | Navigation or lightweight action | `View audit trail` |

### 17.2 Button States

Each button must support:

- Default.
- Hover.
- Focus.
- Pressed.
- Loading.
- Disabled.
- Success where applicable.

### 17.3 Button Labels

Use verb + object.

Good:

- `Submit application`
- `Generate reference number`
- `Approve loan`
- `Reject with reason`
- `Send to Sanction Committee`
- `Confirm SAP customer code`
- `Initiate bank transfer`
- `Issue NOC`

Avoid:

- `Submit`
- `Done`
- `OK`
- `Proceed`
- `Update`
- `Process`

### 17.4 Destructive Action Rules

Destructive or high-risk actions require:

1. Confirmation dialog.
2. Summary of impact.
3. Mandatory reason.
4. Authority check.
5. Audit event.
6. Success / failure message.

High-risk actions include:

- Reject application.
- Approve exception over permissible limit.
- Use undated cheque.
- Invoke SH-4.
- Invoke CDSL pledge.
- Delete uploaded document.
- Override validation.
- Mark loan non-recoverable.
- Close loan account.

---

## 18. Form System

### 18.1 Form Layout

Use sectioned forms with clear group headings.

Recommended section pattern:

```text
Section title
Short instruction / helper text
Field grid
Validation summary if errors exist
Save / continue actions
```

### 18.2 Field Grid

| Screen size | Columns |
|---|---:|
| Mobile | 1 |
| Tablet | 2 |
| Desktop | 2–3 |
| Dense admin | 3–4 only for short fields |

### 18.3 Field Label Standards

- Use persistent top labels.
- Required fields show `Required` or `*` with accessible label.
- Use helper text for legal / financial meaning.
- Do not rely on placeholders.

Example:

```text
PAN number *
Enter the borrower’s 10-character PAN. This is required for KYC verification.
```

### 18.4 Input Types

| Field | Component |
|---|---|
| Borrower name | Text input with title-case normalisation guidance |
| PAN | Masked / uppercase text input with format validation |
| Aadhaar | Masked numeric input, display last 4 digits after save |
| Date of birth / age | Date picker or age input depending SOP form |
| Gender | Select / radio group |
| Folio number | Text input with member lookup |
| Share count | Numeric input |
| Loan amount | Currency input in Indian format |
| Per-acre cultivation cost | Config-driven numeric / currency field |
| Land area | Decimal numeric input with unit |
| Crop plan | Structured fields plus upload |
| Bank IFSC | Uppercase text input with bank validation where available |
| Bank account number | Masked after save |
| Document upload | File upload component |
| Approval reason | Required textarea for approval / rejection / exception |
| Risk rating | Select or radio group |
| Intentionality of default | Required classification radio with evidence notes |

### 18.5 Validation Message Pattern

Use this pattern:

```text
[Problem]. [How to fix it].
```

Examples:

- `PAN number is required. Enter the borrower’s 10-character PAN.`
- `Nominee cannot be a minor. Enter nominee details for a person aged 18 years or above.`
- `Requested amount exceeds the eligible loan amount. Reduce the amount or create an exception request.`
- `Loan Agreement cannot be marked complete until stamping and notarisation are recorded.`
- `Disbursement is blocked because SAP customer code is not confirmed.`

### 18.6 Autosave and Drafts

- Long forms should autosave every 30 seconds or after field blur.
- Show `Saved just now`, `Saving...`, or `Unable to save` status.
- Do not autosubmit.
- Draft data must remain clearly distinct from submitted data.
- Critical legal fields should require explicit save / confirmation.

### 18.7 Sensitive Data Display

| Data | Display rule |
|---|---|
| Aadhaar | Mask except last 4 digits after save |
| Bank account number | Mask except last 4 digits in most views |
| Blank cheque details | Restricted visibility to authorised roles |
| PAN | Display fully only to permitted internal roles; mask in borrower summaries if required |
| KYC documents | Access controlled; audit every view / download |
| Signature documents | Restricted to compliance, authorised finance and audit roles |

---

## 19. Table and Register System

### 19.1 Register Philosophy

SOP registers should be implemented as controlled views from system records. They must be exportable and auditable.

Required register-style views:

- Loan Request Register.
- Credit Sanction Register.
- Exception Register.
- Document Checklist Register.
- Security Custody Register.
- SAP Customer Code Register.
- Disbursement Register.
- Repayment Register.
- Interest Invoice Register.
- DPD / Monitoring Register.
- Default / Recovery Register.
- Grievance Register.
- NOC / Closure Register.
- Compliance Task Register.
- Audit Log.

### 19.2 Table Anatomy

Tables should include:

- Title and description.
- Search.
- Filters.
- Column configuration.
- Sort controls.
- Export button.
- Row actions.
- Pagination.
- Last updated timestamp.

### 19.3 Required Column Behaviour

- Applicant / borrower name should link to Borrower 360.
- Application number should link to Loan 360.
- Status should be shown as badge.
- Amounts should be right-aligned.
- Dates should be sortable.
- Pending owner should be visible.
- Ageing / TAT should be visible for task queues.
- Exception and blocker indicators should be visible in first visible columns.

### 19.4 Example Loan Request Register Columns

| Column | Type |
|---|---|
| Application no. | Link |
| Application date | Date |
| Borrower name | Link |
| Borrower type | Badge |
| Folio no. | Text |
| Shares held | Number |
| Requested amount | Currency |
| Eligible amount | Currency |
| Application status | Status badge |
| Current stage | Stage badge |
| Pending owner | User / role |
| TAT ageing | Duration |
| Deficiencies | Count / badge |
| Last updated | Timestamp |

### 19.5 Empty State Pattern

Empty state should include:

- Clear title.
- Explanation.
- Primary action if user has permission.
- Secondary action to learn or filter.

Example:

```text
No applications need your review
Applications submitted by borrowers will appear here once they pass the completeness check.
```

---

## 20. Card System

### 20.1 Card Types

| Card type | Usage |
|---|---|
| KPI card | Dashboard counts and amounts |
| Task card | Work items in dashboard or inbox |
| Status card | Loan summary, stage, blockers |
| Document card | Individual document status and actions |
| Compliance card | Section 186, NBFC, KYC or stamp duty tracker |
| Calculation card | Loan limit, interest or DPD calculation |
| Alert card | Critical issues requiring attention |

### 20.2 Card Anatomy

- Header with title and optional icon.
- Status or value.
- Supporting metadata.
- Actions.
- Optional footer.

### 20.3 KPI Card Rules

KPI cards should include:

- Metric title.
- Metric value.
- Time period.
- Delta or trend where relevant.
- Drill-down link.

Examples:

- `Applications pending completeness check`.
- `Loans pending sanction`.
- `Documentation blocked`.
- `Ready for disbursement`.
- `Overdue loans`.
- `Re-KYC due`.
- `Loans with exceptions`.

---

## 21. Stage Stepper Component

### 21.1 Purpose

The Stage Stepper communicates where a loan is in the SOP lifecycle and what must happen next.

### 21.2 Stages

1. Initial Loan Request.
2. Credit Assessment.
3. Credit Scrutiny & Approval.
4. Documentation & Stamping.
5. Loan Disbursement.
6. Monitoring & Repayment.

### 21.3 Step States

| State | Meaning |
|---|---|
| Not started | Stage not reached |
| In progress | Current stage active |
| Completed | Stage complete |
| Blocked | Stage has unresolved gate |
| Rejected | Application rejected in this stage |
| Exception | Stage proceeded with documented exception |

### 21.4 Behaviour

- Current stage is highlighted.
- Completed stages are clickable to view evidence.
- Future stages are visible but disabled.
- Blocked stage shows reason tooltip.
- Exception stage shows exception indicator.
- Stepper should collapse into a dropdown on mobile.

---

## 22. Loan Limit Calculator Component

### 22.1 Purpose

Calculates and explains the borrower’s eligible loan amount using SOP formulas.

### 22.2 Inputs

| Input | Source |
|---|---|
| Number of shares held | Member / shareholding record |
| Share valuation per share | Policy configuration based on latest audited financials |
| Applicable share valuation percentage | Policy configuration |
| Land area under cultivation | Land documents / 7/12 extract |
| Per-acre cost of cultivation | Policy configuration, current cap ₹20,000 per acre unless updated |
| Requested amount | Loan application |

### 22.3 Outputs

- Shareholding-based limit.
- Agricultural land-based limit.
- Final eligible loan amount = lower of the two.
- Requested amount vs eligible amount.
- Exception requirement if requested amount exceeds eligible amount.
- Formula explanation.
- Policy version used.

### 22.4 Special SOP Clarification Banner

Because the current analysis identified a contradiction between `30% of valuation per share`, `10% of share value` and `₹200 per share`, the calculator must support a configuration warning until client policy is confirmed.

Banner copy:

```text
Loan limit policy requires confirmation
The SOP references both 30% and 10% of share valuation, and also mentions ₹200 per share. Confirm the approved policy before using this value for automated sanctions.
```

### 22.5 Interaction Rules

- System-calculated fields are read-only unless user has policy admin permission.
- Any manual override requires exception reason and approval.
- Calculation must be printable / exportable in the Loan Appraisal Note.
- Values must be locked at sanction to preserve historical accuracy.

---

## 23. Eligibility Checklist Component

### 23.1 Purpose

Shows whether the applicant satisfies the SOP’s loan eligibility conditions.

### 23.2 Checklist Items

| Check | Result types |
|---|---|
| Applicant is a member | Pass / fail / needs review |
| Applicant is active | Pass / fail / needs review |
| Individual / FPC active member conditions verified | Pass / fail / not applicable |
| No default with SFPCL | Pass / fail |
| No default with subsidiary / associate company | Pass / fail / needs external confirmation |
| Land documents submitted | Pass / fail |
| KYC submitted | Pass / fail |
| Six-month bank statement submitted | Pass / fail |
| Crop plan submitted | Pass / fail |
| Loan purpose is crop production / agricultural activity | Pass / fail |
| Borrower agrees to Term Sheet / Loan Agreement | Pending / complete |
| Nominee is not minor | Pass / fail |

### 23.3 Behaviour

- Failed hard checks block further movement.
- Needs-review checks allow internal note but not final sanction without resolution.
- Every fail should map to a deficiency or rejection reason.
- Each checklist item should link to source evidence.

---

## 24. Document Checklist Component

### 24.1 Purpose

Controls the documentation and stamping process before disbursement.

### 24.2 Required Documents

| Document | Required when | Key statuses |
|---|---|---|
| Loan Application Form | All applications | Uploaded, signed, complete |
| Borrower PAN | All borrowers | Uploaded, verified |
| Borrower Aadhaar | All borrowers | Uploaded, verified |
| Nominee PAN | All individual borrower cases | Uploaded, verified |
| Nominee Aadhaar | All individual borrower cases | Uploaded, verified |
| Share certificates | Physical shares / shareholding evidence | Uploaded, verified |
| Land documents / 7/12 extract | Agricultural land-based limit | Uploaded, verified |
| Crop plan | All loans | Uploaded, verified |
| Six-month bank statement | All borrowers | Uploaded, verified |
| Witness PAN and Aadhaar | Documentation stage | Uploaded, verified |
| Cancelled cheque | Disbursement | Uploaded, verified |
| Blank-dated cheque | Security | Collected, held, returned / invoked |
| Power of Attorney | All applicable cases | Drafted, signed, stamped, notarised |
| Tri-party Agreement / Declaration | Subsidiary repayment route | Drafted, signed, active |
| SH-4 | Physical shares | Signed, held, returned / invoked |
| CDSL pledge evidence | Demat shares | PRF / PSN / pledge confirmation |
| Term Sheet | All sanctioned loans | Signed by required authority |
| Loan Agreement | All loans | Signed, stamped, notarised |
| Bank Verification Letter | Signature mismatch | Uploaded, verified |
| Signature declaration | Signature mismatch alternative | Uploaded, verified |
| Final checklist | Before disbursement | CS, Credit Manager, Sanction Committee, Senior Manager – Finance sign-off |

### 24.3 Checklist Approval Sequence

1. Compliance Team prepares documents.
2. Company Secretary verifies documents and signs checklist.
3. Credit Manager confirms loan limits and signs checklist.
4. Sanction Committee gives final approval and signs checklist.
5. Senior Manager – Finance signs after actual disbursement.

### 24.4 Behaviour

- Display documents grouped by category: KYC, Loan, Security, Bank, Approvals, Closure.
- Show required / conditional / optional status.
- Show blockers at top.
- Support upload, preview, replace, mark verified, reject document and add note.
- Any replaced document must preserve version history.
- A document marked verified must capture verifier, timestamp and method.
- Disbursement cannot proceed until mandatory documents are complete.

---

## 25. Approval Panel Component

### 25.1 Purpose

Provides a standard decision interface for Credit Manager, Sanction Committee, CFO, Directors, Company Secretary and finance approvers.

### 25.2 Approval Panel Anatomy

- Decision title.
- Role required.
- Authority rule.
- Loan summary.
- Required evidence checklist.
- Decision options.
- Reason field.
- Comments / internal notes.
- Attach supporting note.
- Confirm decision.

### 25.3 Decision Types

| Decision | Required reason? | Notes |
|---|---|---|
| Approve | Optional unless exception | Reason recommended for audit |
| Reject | Required | Must feed Rejection Note |
| Request clarification | Required | Creates task for previous owner |
| Approve with exception | Required | Creates Exception Register record |
| Abstain | Required for conflict / special case | Required for director / relative situations |
| Return for correction | Required | Used for documentation defects |

### 25.4 Approval Matrix Display

The panel must show the applicable matrix:

| Amount / condition | Required authority |
|---|---|
| Up to ₹5,00,000 per member | CFO + one Director |
| Above ₹5,00,000 per member | CFO + two Directors |
| Exceeding maximum permissible limit | CFO + two Directors + Exception Register reason |
| Director / Sanction Committee member / relative as borrower | Remaining committee members and members’ approval in general meeting as required |

### 25.5 Behaviour

- Hide or disable actions not permitted for the logged-in user.
- Show who else must approve.
- Prevent self-approval when maker-checker separation applies.
- Require abstention where conflict is declared.
- Record all decisions in Credit Sanction Register or relevant register.

---

## 26. Exception Component

### 26.1 Purpose

Captures deviations from SOP controls or policy configuration.

### 26.2 Exception Types

- Requested amount exceeds eligible limit.
- Loan amount above ₹5 lakh requiring higher approval.
- Missing / delayed document allowed temporarily.
- Signature mismatch resolved through declaration.
- Policy formula ambiguity.
- Director / relative borrower special case.
- Disbursement outside normal TAT.
- Repayment extension.
- Recovery action approval.
- Any CFO-approved stage bypass.

### 26.3 Required Fields

| Field | Requirement |
|---|---|
| Exception type | Required |
| Linked loan application | Required |
| SOP rule affected | Required |
| Reason | Required |
| Risk impact | Required |
| Mitigation | Required |
| Requested by | Auto |
| Approval authority | Auto / configurable |
| Approval decision | Required |
| Expiry / review date | Required where temporary |
| Evidence attachment | Required where applicable |

### 26.4 Visual Treatment

Exceptions should use violet styling and appear:

- In Loan 360 header.
- In stage stepper.
- In approval panel.
- In registers.
- In audit trail.
- In reports.

---

## 27. Notification and Alert System

### 27.1 Notification Channels

| Channel | Usage |
|---|---|
| In-app notification | Internal tasks, approvals, blockers |
| Email | Formal communications, borrower rejection / approval, internal handoffs |
| SMS | Borrower interest rate changes, repayment reminders, status updates if enabled |
| Hard copy | Required borrower intimation such as unpaid interest capitalisation where SOP requires |

### 27.2 Notification Types

| Type | Example |
|---|---|
| Task assigned | `LO00000042 requires your appraisal review.` |
| Approval required | `Sanction approval required for ₹6,00,000 loan.` |
| Document missing | `Loan Agreement is pending notarisation.` |
| Blocker | `Disbursement blocked: SAP customer code is not confirmed.` |
| TAT warning | `Appraisal TAT will breach in 4 hours.` |
| Rejection | `Application rejected due to incomplete KYC.` |
| Repayment reminder | `Scheduled repayment is due.` |
| Default review | `Grace period ended. Non-payment review required.` |
| Closure | `Full repayment confirmed. Issue NOC.` |
| Compliance | `Re-KYC due for borrower.` |

### 27.3 Notification Design

- Include clear object reference: application no. / borrower / amount.
- Include required action.
- Include due date or TAT where relevant.
- Include link to exact screen.
- Avoid vague messages.

---

## 28. Audit Timeline Component

### 28.1 Purpose

Provides chronological evidence of actions and decisions for every loan, member, document, approval and compliance task.

### 28.2 Events to Capture

- Application draft created.
- Application submitted.
- Document uploaded / replaced / verified / rejected.
- Reference number generated.
- Appraisal note drafted / reviewed.
- Eligibility check completed.
- Loan limit calculated.
- Rejection note generated.
- Sanction Committee decision recorded.
- Exception created / approved / rejected.
- Document checklist updated.
- PoA / Term Sheet / Loan Agreement signed / stamped / notarised.
- SH-4 collected / returned / invoked.
- CDSL pledge created / invoked / unpledged.
- SAP customer code request sent / confirmed.
- Disbursement initiated / approved / executed.
- Repayment received / posted.
- Interest invoice generated.
- Interest capitalised.
- DPD bucket changed.
- Reminder sent.
- Extension granted.
- Note for Non-Payment created.
- Recovery action approved.
- NOC issued.
- Loan archived.

### 28.3 Event Fields

| Field | Requirement |
|---|---|
| Event type | Required |
| Timestamp | Required |
| Actor name | Required |
| Actor role | Required |
| Object affected | Required |
| Old value | Required where state changed |
| New value | Required where state changed |
| Reason | Required for decision / override / rejection |
| Evidence | Link to document / note where available |
| IP / device metadata | Recommended for security logs |

---

## 29. Modal, Drawer and Confirmation Patterns

### 29.1 When to Use Modal

Use modals for:

- High-risk confirmation.
- Short focused forms.
- Decision confirmation.
- Document upload.
- Reason capture.

Do not use modals for:

- Long application forms.
- Full appraisal notes.
- Large document review.
- Multi-step sanction review.

### 29.2 When to Use Drawer

Use drawers for:

- Audit trail.
- Comments.
- Quick member preview.
- Document preview metadata.
- Task details.

### 29.3 High-Risk Confirmation Pattern

High-risk confirmation must include:

- Clear title.
- Object summary.
- Consequence explanation.
- Required reason field.
- Optional evidence upload.
- Checkbox acknowledgement if legally sensitive.
- Destructive action button.
- Cancel button.

Example title:

```text
Confirm SH-4 invocation request
```

Example body:

```text
This action will start the approval workflow to invoke the SH-4 security held against this loan. It must be supported by Sanction Committee approval and recorded in the Recovery Register.
```

---

## 30. Document Viewer and File System Patterns

### 30.1 File Upload Rules

Supported file types should include:

- PDF.
- JPG / JPEG.
- PNG.
- DOCX only for internal drafts if required.
- XLSX for SAP upload templates and registers if required.

Recommended restrictions:

- Maximum file size configurable, default 10 MB per file.
- Virus scan required.
- File naming standard applied automatically.
- Version history retained.

### 30.2 File Naming Standard

Recommended generated file name format:

```text
[ApplicationNo]_[DocumentType]_[BorrowerName]_[YYYYMMDD]_v[Version].pdf
```

Example:

```text
LO00000042_LoanAgreement_RameshPatil_20250807_v01.pdf
```

### 30.3 Document Viewer Controls

- Preview.
- Download, permission-controlled.
- Rotate.
- Zoom.
- Page navigation.
- Metadata panel.
- Verification panel.
- Comments / rejection notes.
- Version history.
- Audit history.

### 30.4 Document Verification States

| State | Meaning |
|---|---|
| Uploaded | File exists, not verified |
| Under review | Assigned reviewer checking document |
| Verified | Accepted for process |
| Rejected | Defect identified; reason required |
| Replaced | New version uploaded |
| Archived | Retained after closure |

---

## 31. Dashboard Design System

### 31.1 Dashboard Types

| Dashboard | Primary users |
|---|---|
| Operational Dashboard | Deputy Manager – Finance, Credit Manager, Compliance, Finance |
| Executive Dashboard | CFO, Directors, Sanction Committee |
| Compliance Dashboard | Company Secretary, Compliance Team, Auditors |
| Repayment and Monitoring Dashboard | Credit Manager, Accounts, CFO |
| Disbursement Dashboard | Senior Manager – Finance, CFC |

### 31.2 Operational Dashboard Cards

- New applications received.
- Incomplete applications.
- Appraisals due within TAT.
- Pending Credit Manager review.
- Pending Sanction Committee review.
- Documentation pending.
- Documents blocked.
- Ready for disbursement.
- SAP setup pending.
- Disbursement initiated.

### 31.3 Executive Dashboard Cards

- Total active loan exposure.
- Loans pending sanction.
- Loans above ₹5 lakh.
- Loans with exceptions.
- Loans exceeding permissible limit.
- DPD portfolio by bucket.
- Non-recoverable review cases.
- Section 186 utilisation.
- NBFC principal business test ratios.
- Quarterly MIS status.

### 31.4 Compliance Dashboard Cards

- KYC pending.
- Re-KYC due.
- Stamp duty pending.
- PoA pending notarisation.
- SH-4 custody count.
- Blank-dated cheques held.
- CDSL pledge pending.
- NOC pending after full repayment.
- Record retention due for audit.
- Grievances open.

### 31.5 Dashboard Chart Rules

- Use simple bar charts for counts by stage.
- Use stacked bars for documentation status by stage.
- Use line charts only for trends over time.
- Use donut charts sparingly; avoid for critical compliance information.
- Always show source date and filter context.
- Charts must have table fallback or export.

---

## 32. Data Visualisation Standards

### 32.1 Chart Colour Semantics

- Green = approved, complete, disbursed, closed.
- Amber = pending, due soon, warning.
- Red = rejected, blocked, overdue, default.
- Blue = submitted, finance / SAP, informational.
- Violet = exception, policy deviation.
- Neutral = draft, archived, no data.

### 32.2 Required Visualisations

| Visualisation | Use |
|---|---|
| Stage funnel | Count of applications by SOP stage |
| TAT ageing bar | Applications pending beyond target |
| Documentation completeness grid | Required documents by status |
| DPD bucket chart | Loans in 1–2 yrs, 2–3 yrs, 3+ yrs buckets |
| Exposure by status | Principal outstanding by status |
| Compliance tracker | Section 186, NBFC, re-KYC, stamp duty tasks |
| Repayment trend | Month-wise repayment receipts |
| Disbursement trend | Month-wise disbursed amount |

### 32.3 Chart Accessibility

- Provide labels and values on hover and in data table.
- Do not rely only on colour.
- Provide chart title, date range and filter context.
- Ensure keyboard accessible chart data table.

---

## 33. Workflow-Specific UI Patterns

## 33.1 Initial Loan Request Pattern

Required interface elements:

- Borrower type selector: Individual farmer / FPC / Producer Institution.
- Member lookup by folio number, name, PAN or member ID.
- Shareholding summary.
- Nominee details.
- Required document checklist.
- Application channel indicator: offline / digital.
- Save draft and submit application.

Controls:

- Nominee age must not be minor.
- Application cannot submit without required borrower and nominee fields.
- Loan purpose must be agriculture / crop production.

## 33.2 Completeness Check Pattern

Required interface elements:

- Application summary.
- Required field and document completeness checklist.
- Deficiency list.
- Generate reference number action.
- Mark incomplete action.
- Rejection Note / deficiency communication.

Controls:

- Reference number generated only after completeness check passes.
- Reference number sequence starts at `LO00000001` and increments sequentially.

## 33.3 Appraisal Pattern

Required interface elements:

- Eligibility checklist.
- Active member evidence.
- Default history.
- Land and crop evidence.
- Loan limit calculator.
- Requested vs eligible amount.
- Risk rating.
- Appraisal recommendation.
- Credit Manager review.

Controls:

- Two-day TAT shown.
- Appraisal cannot proceed without required eligibility result.
- Rejection at appraisal must require reason and communication.

## 33.4 Sanction Pattern

Required interface elements:

- Sanction Committee decision panel.
- Approval authority display.
- Committee member checklist.
- Conflict-of-interest declaration.
- Approval / rejection / clarification actions.
- Credit Sanction Register preview.

Controls:

- Up to ₹5 lakh: CFO + one Director.
- Above ₹5 lakh: CFO + two Directors.
- Exceeding limit: CFO + two Directors and Exception Register.
- Director / relative borrower: remaining committee and general meeting approval route.

## 33.5 Documentation Pattern

Required interface elements:

- Document checklist.
- Generated document templates.
- Stamping and notarisation tracker.
- Witness validation.
- Signature mismatch workflow.
- Security instrument tracker.
- Checklist sign-off sequence.

Controls:

- Disbursement cannot proceed if required documents are incomplete.
- Loan Agreement and PoA must show ₹500 stamp and notarisation status.
- SH-4 required for physical shares.
- CDSL pledge required for demat shares.

## 33.6 SAP and Disbursement Pattern

Required interface elements:

- SAP customer code request card.
- Excel template download / upload if needed.
- Customer code confirmation.
- Bank account verification.
- Disbursement readiness checklist.
- RBL bank transfer initiation record.
- CFC final approval.
- Disbursement advice generation.

Controls:

- Payment initiation blocked until SAP code confirmed.
- Payment initiation blocked until Senior Manager – Finance final verification.
- Execution requires Chief Financial Controller approval.

## 33.7 Repayment and Monitoring Pattern

Required interface elements:

- Loan account ledger.
- Repayment schedule.
- Direct repayment posting.
- Subsidiary repayment posting.
- Bank statement matching fields.
- Principal-first allocation display.
- Interest accrual and invoice tracker.
- DPD status.
- Quarterly MIS preview.

Controls:

- Partial repayment applies to principal first.
- Unpaid interest after 30 April can be added to principal.
- Borrower intimation required for capitalised interest.
- DPD buckets reported quarterly to CFO.

## 33.8 Default and Recovery Pattern

Required interface elements:

- Missed payment alert.
- Three-month grace period tracker.
- Non-payment review form.
- Intentional / non-intentional classification.
- One-year extension note.
- Non-recoverable review.
- Note for Non-Payment.
- Sanction Committee recovery decision.
- SH-4 / cheque / CDSL action tracker.

Controls:

- Recovery action cannot be executed without approval.
- Intentionality classification requires evidence and reason.
- Use of SH-4 or undated cheque must be recorded and approved.

## 33.9 Closure Pattern

Required interface elements:

- Full repayment confirmation.
- Closure checklist.
- NOC generation.
- SH-4 return tracker.
- Blank-dated cheque return tracker.
- CDSL unpledge tracker if applicable.
- Archive confirmation.

Controls:

- NOC issued only after full repayment.
- Security documents returned on closure.
- Records archived for at least eight years.

---

## 34. Content and Microcopy Integration

### 34.1 Voice

Use a direct, calm and helpful voice.

### 34.2 Tone by Context

| Context | Tone |
|---|---|
| Borrower instruction | Simple, respectful, specific |
| Internal task | Operational, concise |
| Compliance warning | Firm, clear, non-negotiable |
| Rejection | Respectful, reasoned, actionable |
| Approval | Formal and auditable |
| Default / recovery | Serious, factual, non-coercive |
| Closure | Positive and confirmatory |

### 34.3 Standard Message Patterns

#### Success

```text
Application LO00000042 has been submitted successfully.
```

#### Warning

```text
This loan requires exception approval because the requested amount exceeds the eligible amount.
```

#### Blocker

```text
Disbursement is blocked until the Loan Agreement is stamped and notarised.
```

#### Rejection

```text
This application has been rejected because required KYC documents are incomplete. The borrower may reapply after submitting the missing documents.
```

#### Approval

```text
Loan approved as per the applicable authority matrix. The decision has been recorded in the Credit Sanction Register.
```

### 34.4 Mandatory Reason Capture

Reason capture is mandatory for:

- Rejection.
- Exception approval.
- Stage bypass.
- Return for correction.
- Recovery action.
- Default classification.
- Security invocation.
- Disbursement hold release.
- Document rejection.
- Policy override.

---

## 35. Generated Document Design Standards

### 35.1 Generated Document Header

Each generated document should contain:

- SFPCL logo / name.
- Document title.
- Application number.
- Borrower name.
- Date generated.
- Version number.
- Confidentiality marker where applicable.

### 35.2 Required Generated Documents

- Loan Application Form.
- Loan Appraisal Note.
- Rejection Note.
- Power of Attorney.
- Tri-party Agreement / Declaration.
- Term Sheet.
- Loan Agreement.
- Bank Verification Letter.
- Checklist.
- SAP customer code template.
- Credit Sanction Register extract.
- Exception Note.
- Extension Note.
- Note for Non-Payment.
- Disbursement Advice.
- Interest Invoice.
- NOC.
- Grievance Acknowledgement.

### 35.3 Document Typography

Generated PDFs should use:

- 11pt body text.
- 14–16pt section headings.
- Clear table borders.
- Adequate signature space.
- Page numbers.
- Footer with document ID and version.

### 35.4 Signature Blocks

Signature blocks should include:

- Name.
- Role.
- Signature.
- Date.
- Place.
- Witness where required.

### 35.5 Legal Document Caution

Legal templates must be configuration-controlled and reviewed by authorised legal / compliance owners before use. UI should not allow unauthorised editing of approved legal template text.

---

## 36. Role-Based Design Variations

### 36.1 Borrower / Member View

Simplify to:

- Application status.
- Documents required.
- Loan terms summary.
- Repayment due / paid.
- Messages from SFPCL.
- NOC / closure confirmation.
- Grievance submission.

Avoid exposing:

- Internal risk rating.
- Internal committee comments.
- Exception discussions.
- Other borrowers’ data.
- Internal compliance notes.

### 36.2 Credit Assessment View

Emphasise:

- Application queue.
- Completeness.
- Eligibility.
- Loan limit calculator.
- Appraisal note.
- Rejection note.
- Monitoring reminders.

### 36.3 Compliance View

Emphasise:

- Legal document completeness.
- Stamp duty.
- Notarisation.
- PoA.
- SH-4.
- CDSL pledge.
- Security custody.
- Re-KYC.
- Record retention.

### 36.4 Sanction Committee / CFO View

Emphasise:

- Loan summary.
- Amount and eligibility.
- Approval matrix.
- Exceptions.
- Borrower history.
- Risk and mitigation.
- Required decision.
- Register recording.

### 36.5 Finance / Treasury View

Emphasise:

- SAP code creation.
- Bank verification.
- Disbursement readiness.
- RBL transfer initiation.
- CFC approval.
- Repayment posting.
- Interest accrual and invoices.

### 36.6 Auditor View

Emphasise:

- Read-only registers.
- Document evidence.
- Audit trail.
- Export.
- Compliance trackers.
- Exceptions.
- Maker-checker evidence.

---

## 37. Responsive and Mobile Standards

### 37.1 Mobile Use Cases

Mobile should support:

- Borrower status checks.
- Document upload by field staff.
- Application draft capture.
- Task approvals only if policy allows.
- Notifications.
- Quick borrower lookup.

Mobile should avoid:

- Complex sanction review.
- Large register management.
- Full document comparison.
- Detailed financial reconciliation.

### 37.2 Mobile Layout Rules

- Collapse sidebar into bottom navigation or hamburger menu.
- Stack form fields vertically.
- Use accordions for long sections.
- Keep primary action sticky at bottom when safe.
- Avoid horizontal tables; use list cards.
- Preserve status and blockers at top.

### 37.3 Tablet Field Operations

Tablet layout should support:

- Two-column forms.
- Camera-based document upload.
- Offline draft capture if future scope allows.
- Signature capture only if legally approved.

---

## 38. Internationalisation and Local Language Readiness

### 38.1 Language Strategy

Primary internal UI may be English. Borrower-facing communication should be ready for local language support, especially where interest rates, charges and repayment obligations are disclosed.

### 38.2 Content Architecture

- All labels and messages must be string-token based.
- Avoid hard-coded text in components.
- Use variables for borrower name, amount, dates and reference numbers.
- Maintain separate templates for borrower-facing and internal communications.

### 38.3 Translation Rules

- Do not translate legal terms inconsistently.
- Maintain defined acronyms with explanation on first use.
- Use plain, non-technical borrower communication.
- Test text expansion in Marathi / Hindi / local language if enabled.

---

## 39. Security and Privacy Design Standards

### 39.1 Access Control UX

When users lack permission:

- Hide actions they can never perform.
- Disable actions temporarily unavailable due to state, with reason.
- Show `You do not have permission` only where helpful.
- Never expose sensitive data through disabled controls or tooltips.

### 39.2 Sensitive Document UX

- View / download access must be logged.
- Download can require reason for sensitive legal / KYC documents.
- Watermark sensitive previews with user name and timestamp if required.
- Do not show Aadhaar or bank details in broad registers.

### 39.3 Session and Environment

- Show production / UAT environment indicator.
- Warn users before timeout where possible.
- Require re-authentication for high-risk actions if policy requires.

---

## 40. Component Implementation Standards

### 40.1 Component API Principles

Components should be:

- Role-aware.
- State-driven.
- Accessible by default.
- Configurable through tokens.
- Auditable for critical actions.
- Reusable across modules.

### 40.2 Example Component Props: Status Badge

```ts
interface StatusBadgeProps {
  status: string;
  family: 'neutral' | 'info' | 'pending' | 'approved' | 'rejected' | 'blocked' | 'exception' | 'closed';
  size?: 'sm' | 'md' | 'lg';
  icon?: boolean;
  tooltip?: string;
  ariaLabel?: string;
}
```

### 40.3 Example Component Props: Approval Panel

```ts
interface ApprovalPanelProps {
  applicationId: string;
  decisionType: 'sanction' | 'documentation' | 'disbursement' | 'exception' | 'recovery' | 'closure';
  requiredAuthority: string[];
  currentUserRole: string;
  availableActions: Array<'approve' | 'reject' | 'clarify' | 'abstain'>;
  requiresReason: boolean;
  requiresAttachment?: boolean;
  onDecision: (decision: ApprovalDecision) => Promise<void>;
}
```

### 40.4 Example Component Props: Document Checklist

```ts
interface DocumentChecklistProps {
  applicationId: string;
  borrowerType: 'individual' | 'fpc' | 'producer_institution';
  shareMode: 'physical' | 'demat' | 'unknown';
  documents: DocumentChecklistItem[];
  currentUserRole: string;
  disbursementGate: boolean;
  onVerify: (documentId: string) => void;
  onReject: (documentId: string, reason: string) => void;
}
```

### 40.5 State Management Rules

- UI state must not independently decide business-critical outcomes.
- Critical transitions must be server-validated.
- Frontend blockers improve usability but backend gates enforce controls.
- Audit event creation must be server-side.

---

## 41. Design Tokens for Engineering

### 41.1 CSS Variable Example

```css
:root {
  --color-surface-app: #F8FAFC;
  --color-surface-card: #FFFFFF;
  --color-text-primary: #0F172A;
  --color-text-secondary: #475569;
  --color-border-default: #E2E8F0;
  --color-action-primary-bg: #16A34A;
  --color-action-primary-hover: #15803D;
  --color-status-approved-bg: #F0FDF4;
  --color-status-approved-text: #14532D;
  --color-status-warning-bg: #FFFBEB;
  --color-status-warning-text: #78350F;
  --color-status-error-bg: #FEF2F2;
  --color-status-error-text: #7F1D1D;
  --color-status-exception-bg: #F5F3FF;
  --color-status-exception-text: #5B21B6;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
}
```

### 41.2 Tailwind-Style Mapping Example

| Design token | Tailwind-style usage |
|---|---|
| `color.action.primary.bg` | `bg-green-600` |
| `color.action.primary.hover` | `hover:bg-green-700` |
| `color.text.primary` | `text-slate-900` |
| `color.text.secondary` | `text-slate-600` |
| `color.border.default` | `border-slate-200` |
| `radius.md` | `rounded-md` |
| `space.4` | `p-4`, `gap-4` |

---

## 42. Quality Assurance Checklist

### 42.1 Visual QA

- Colours match tokens.
- Status colours are semantically correct.
- Typography hierarchy is consistent.
- Spacing uses token scale.
- Components align to grid.
- Tables remain readable in compact mode.
- Mobile layout does not cut off key actions.

### 42.2 Accessibility QA

- Keyboard navigation works across all components.
- Focus indicators are visible.
- Screen reader labels exist for icons and status.
- Required fields are announced.
- Error messages link to invalid fields.
- Colour contrast passes WCAG AA.
- Reduced motion preference is respected.

### 42.3 Functional UX QA

- Disbursement action is blocked until all required gates complete.
- Approval panel shows correct authority matrix.
- Loan limit calculator explains formula and values.
- Exception approvals create Exception Register entry.
- Rejection requires reason.
- Document verification creates audit record.
- SAP setup status affects disbursement readiness.
- Closure requires full repayment and NOC process.

### 42.4 Content QA

- UI uses controlled vocabulary.
- Borrower-facing copy is simple and respectful.
- Legal / compliance terms are consistent.
- Amounts follow Indian currency formatting.
- Dates follow standard format.
- Error messages tell user how to fix the issue.

### 42.5 Security QA

- Sensitive data masked where required.
- Unauthorised roles cannot access restricted documents.
- Download and preview are audited.
- High-risk actions require confirmation and reason.
- Role permissions are enforced server-side.

---

## 43. Design System Governance

### 43.1 Ownership

Recommended ownership:

| Area | Owner |
|---|---|
| Design tokens | Product design lead / UI lead |
| Component behaviour | Product + Engineering |
| Compliance behaviour | Company Secretary / Compliance owner |
| Approval matrix behaviour | CFO / Sanction policy owner |
| Content and templates | Product + Compliance + Legal |
| Accessibility | Product design + QA |
| Implementation consistency | Frontend engineering lead |

### 43.2 Change Control

Changes to design system should be categorised:

| Change type | Approval needed |
|---|---|
| Visual token change | Design lead + frontend lead |
| Component behaviour change | Product + engineering |
| Business rule display change | Product + relevant process owner |
| Compliance gate change | Compliance owner + CFO where relevant |
| Legal document template change | Company Secretary / legal approval |
| Approval matrix change | Board / authorised governance process as applicable |

### 43.3 Versioning

Design system releases should use semantic versioning:

```text
MAJOR.MINOR.PATCH
```

Examples:

- `1.0.0` — Initial design system release.
- `1.1.0` — New component added.
- `1.1.1` — Copy correction or token bug fix.
- `2.0.0` — Major visual or behavioural redesign.

---

## 44. Open Design Decisions and Client Confirmations Required

The design system must remain configurable because current analysis identified unresolved policy and process questions.

| Open item | Design impact |
|---|---|
| Loan limit percentage contradiction: 30% vs 10% vs ₹200 per share | Calculator, validation, approval thresholds and exception copy must be configurable |
| Annexure K naming conflict | Document navigation, template labels and generated register naming must be corrected |
| Interest rate benchmark and reset rule undefined | Interest UI, borrower disclosures and invoice templates need policy configuration |
| Penal charges / fees undefined | Term Sheet, calculator and validation cannot hard-code values |
| NACH / ECS mandate unclear | Repayment setup UI should treat as configurable / conditional |
| Guarantor rules undefined | Security and borrower compliance sections should support optional guarantor module |
| Credit bureau inquiry unclear | KYC / declaration and appraisal screens should support optional bureau consent |
| Director / relative borrower operational route needs detail | Special-case approval UI must allow general meeting evidence upload and abstention tracking |
| Money-lending law exemption requires annual confirmation | Compliance dashboard should include annual legal opinion task |
| NBFC threshold monitoring owner / format requires configuration | Compliance dashboard and Board pack export must remain configurable |
| Intentional default criteria undefined | Default review component must support configurable evidence checklist |
| Non-recoverable classification approval unclear | Default workflow should require committee decision until policy is final |

---

## 45. Design System Rollout Plan

### Phase 1 — Foundations

- Tokens.
- Typography.
- Colour semantics.
- App shell.
- Navigation.
- Buttons.
- Forms.
- Tables.
- Status badges.
- Stage stepper.
- Audit timeline.

### Phase 2 — Loan Origination Components

- Member lookup.
- Application form.
- KYC uploader.
- Completeness checklist.
- Reference number component.
- Eligibility checklist.
- Loan limit calculator.
- Appraisal note editor.

### Phase 3 — Approval and Documentation Components

- Approval panel.
- Sanction decision panel.
- Exception component.
- Document checklist.
- Document viewer.
- Template generator.
- Signature mismatch workflow.
- Security instrument tracker.

### Phase 4 — Finance, Repayment and Monitoring Components

- SAP request card.
- Disbursement readiness panel.
- Bank transfer tracker.
- Repayment ledger.
- Interest invoice tracker.
- DPD bucket component.
- Default workflow.
- Recovery approval component.
- Closure checklist.

### Phase 5 — Compliance, Reporting and Audit

- Compliance dashboard.
- Register views.
- Export templates.
- Audit evidence packs.
- Record retention tracker.
- Grievance log.
- Accessibility audit.

---

## 46. Success Criteria for the Design System

The design system is successful when:

1. Users can identify the current stage and blocker of any loan within five seconds.
2. All screens use consistent status, colour, typography and action patterns.
3. Approval authority is visible before a user makes a decision.
4. Disbursement blockers are unmissable and cannot be bypassed through UI.
5. Loan limit calculations are transparent and auditable.
6. Documentation completeness is visible before money movement.
7. Exceptions are clearly marked across dashboards, loan pages and registers.
8. Borrower-facing communication is simple and actionable.
9. Internal users can perform high-volume register work without losing clarity.
10. Auditors can trace each major decision through documents, approvals and audit logs.
11. Designers and engineers can build new screens using reusable patterns instead of inventing new UI.
12. Policy changes can be reflected through configuration without redesigning screens.

---

## 47. Appendix A — Core Controlled Vocabulary for UI

| Preferred term | Avoid |
|---|---|
| Loan application | Case, file, ticket |
| Borrower | Customer, client, farmer unless context-specific |
| Member | Non-member, user, party unless context-specific |
| Nominee | Co-applicant unless legally accurate |
| Witness | Reference person |
| Credit Assessment Team | Credit team if formal role is required |
| Sanction Committee | Approval team |
| Company Secretary | CS only in formal internal shorthand |
| Loan Appraisal Note | Appraisal memo, credit memo unless configured |
| Credit Sanction Register | Approval register |
| Exception Register | Deviation list |
| Disbursement | Payment release |
| Repayment | Recovery, unless in default context |
| NOC | Closure letter, unless explaining to borrower |
| SH-4 | Share transfer form on first mention |
| DPD | Days Past Due on first mention |

---

## 48. Appendix B — Critical UX Rules by SOP Gate

| SOP gate | UX rule |
|---|---|
| Member-only lending | Member lookup and active status must appear before application submission |
| KYC required | Application cannot move to appraisal without mandatory KYC status |
| Loan purpose restricted to agriculture | Purpose selector must restrict or flag non-agricultural purpose |
| Loan limit calculation | Requested amount must be compared with calculated eligible amount |
| Approval matrix | UI must display required authority before submission for sanction |
| Documentation | Disbursement readiness must depend on checklist completion |
| Stamping and notarisation | Legal docs cannot be marked complete without stamp / notarisation fields |
| SAP setup | Payment cannot be initiated before SAP customer code confirmation |
| Bank verification | Payment cannot be initiated if bank mismatch unresolved |
| CFC approval | Bank transfer execution must show authorised approver |
| Interest handling | Unpaid interest after 30 April must trigger capitalisation workflow |
| DPD monitoring | Quarterly CFO MIS must be generated from repayment status |
| Default handling | Grace period, extension and recovery must be stateful and auditable |
| Closure | NOC and security return must be checklist-driven |

---

## 49. Appendix C — Recommended Minimum Component Library

### Foundation Components

- AppShell.
- SidebarNavigation.
- GlobalHeader.
- Breadcrumbs.
- PageHeader.
- StatusBadge.
- StageStepper.
- ActionBar.
- Button.
- IconButton.
- Tooltip.
- Popover.
- Modal.
- Drawer.
- Tabs.
- Accordion.
- Toast.
- AlertBanner.

### Form Components

- TextInput.
- NumericInput.
- CurrencyInput.
- PercentageInput.
- DatePicker.
- Select.
- MultiSelect.
- RadioGroup.
- Checkbox.
- Textarea.
- FileUpload.
- SignatureStatusField.
- AddressBlock.
- BankAccountBlock.
- NomineeBlock.
- WitnessBlock.
- LandRecordBlock.
- CropPlanBlock.

### Data Components

- DataTable.
- RegisterTable.
- FilterBar.
- ColumnManager.
- Pagination.
- ExportMenu.
- KPIcard.
- ChartCard.
- Timeline.
- AuditLog.

### Loan-Specific Components

- MemberLookup.
- BorrowerSummaryCard.
- LoanApplicationForm.
- KYCChecklist.
- EligibilityChecklist.
- ActiveMemberEvidencePanel.
- LoanLimitCalculator.
- AppraisalNoteEditor.
- ApprovalPanel.
- SanctionMatrixPanel.
- ExceptionPanel.
- DocumentChecklist.
- DocumentViewer.
- SecurityInstrumentTracker.
- SAPCustomerCodeCard.
- DisbursementReadinessPanel.
- BankTransferTracker.
- RepaymentLedger.
- InterestInvoiceTracker.
- DPDBucketBadge.
- DefaultWorkflowPanel.
- RecoveryActionPanel.
- ClosureChecklist.
- NOCGenerator.
- GrievanceForm.

---

## 50. Appendix D — Example Screen Composition Using Design System

### Loan 360 Composition

```text
AppShell
  GlobalHeader
  SidebarNavigation
  PageHeader
    StatusBadge
    ActionBar
  StageStepper
  AlertBanner: blockers / exceptions
  Grid
    Main column
      Tabs
        Overview
          BorrowerSummaryCard
          LoanLimitCalculator
          EligibilityChecklist
        Appraisal
          AppraisalNoteEditor
        Sanction
          ApprovalPanel
          SanctionMatrixPanel
        Documentation
          DocumentChecklist
          SecurityInstrumentTracker
        Finance
          SAPCustomerCodeCard
          DisbursementReadinessPanel
          BankTransferTracker
        Repayment
          RepaymentLedger
          InterestInvoiceTracker
          DPDBucketBadge
        Closure
          ClosureChecklist
          NOCGenerator
    Right column
      TaskCard
      StatusCard
      Comments
      AuditTimeline
```

### Sanction Review Composition

```text
AppShell
  PageHeader: Sanction review for LO00000042
  AlertBanner: exception / special case if applicable
  SummaryCards
    BorrowerSummaryCard
    LoanAmountCard
    EligibilityCard
    RiskCard
  LoanLimitCalculator: read-only
  DocumentEvidencePanel
  SanctionMatrixPanel
  ApprovalPanel
  AuditTimelineDrawer
```

### Documentation Review Composition

```text
AppShell
  PageHeader: Documentation and Stamping
  StageStepper
  ChecklistProgress
  DocumentChecklist
  SecurityInstrumentTracker
  SignatureMismatchPanel if applicable
  FinalChecklistSignoff
  AuditTimeline
```

---

## 51. Final Design System Summary

The SFPCL design system must behave like a compliance-aware operating system for member credit. Its purpose is not only to create attractive screens, but to make the SOP operationally reliable, legally traceable and easy for each role to execute.

The system should be visually calm, structurally strict and operationally clear. It should use consistent tokens, statuses, components and workflow patterns to ensure that loan applications move through the correct sequence: member validation, application, appraisal, sanction, documentation, SAP setup, disbursement, repayment monitoring, default handling and closure.

The strongest design requirement is controlled clarity: users must always know what loan they are looking at, which stage it is in, who owns the next action, what is blocked, what evidence exists, what approval authority applies and what will happen if they proceed.
