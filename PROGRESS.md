# SFPCL LMS — Build Progress Ledger

## Project: SFPCL Member Credit Administration System
## Stack: React + TypeScript + Vite 5 + Tailwind CSS 3 + lucide-react
## Node: 18.x (Vite 5 compatible)

---

## Build Phases

### Phase 0 — Project Setup
- [x] Vite + React + TypeScript project created
- [x] Tailwind CSS 3 configured (tailwind.config.js + postcss.config.js — CommonJS format)
- [x] Inter font loaded via Google Fonts
- [x] index.html (title: SFPCL Member Credit Administration System)
- [x] main.tsx + App.tsx + routing (state-based, no React Router)
- [x] vite-env.d.ts for CSS import type declarations
- [x] package.json scripts: dev, build, preview
- [x] .claude/launch.json for preview server

### Phase 1 — Design System & Shared UI
- [x] src/index.css (Tailwind base + CSS tokens + component classes)
- [x] src/types/index.ts (all domain types — 12 roles, 18+ states)
- [x] src/data/mockData.ts (5 members, 5 applications, 3 loan accounts, repayments, docs, securities, audit events, compliance records, dashboard stats)
- [x] src/components/ui/StatusBadge.tsx (50+ status mappings, formatStatusLabel, colour families)
- [x] src/components/ui/KPICard.tsx (highlight, trend, icon, onClick)
- [x] src/components/ui/StageStepper.tsx (6 stage states, compact mode)
- [x] src/components/ui/Tabs.tsx (controlled + uncontrolled, badge support)
- [x] src/components/ui/Modal.tsx (sm/md/lg/xl, footer slot, destructive)
- [x] src/components/ui/AlertBanner.tsx (info/warning/error/success/exception)

### Phase 2 — App Shell
- [x] src/components/layout/AppShell.tsx
- [x] src/components/layout/Sidebar.tsx (16 nav items, badge counts, collapse to icon-only)
- [x] src/components/layout/Header.tsx (search, notifications bell, user profile dropdown)

### Phase 3 — Dashboard
- [x] src/pages/Dashboard.tsx
  - Role-based greeting (Priya Kulkarni / Credit Manager)
  - Section 186 utilisation % (top-right KPI)
  - Exception alert banner (violet) with CFO+Director notice
  - TAT deadline alert (amber) for at-deadline applications
  - Application Pipeline KPI row (6 KPIs: New/Completeness/Appraisal/Sanction/Documentation/Disbursement)
  - Portfolio Health KPI row (4 KPIs: Active/Overdue/Exceptions/Re-KYC)
  - My Task Queue (clickable application list)
  - Overdue & At-Risk Loans (DPD shown)
  - Section 186 progress bar with colour thresholds

### Phase 4 — Applications Module
- [x] src/pages/applications/ApplicationList.tsx
  - Search by number/member, status filter dropdown, exceptions-only checkbox
  - Table: App No. (EX badge), Member, Type, Requested, Eligible, Status (formatted), Owner, TAT
- [x] src/pages/applications/NewApplication.tsx
  - 4-step wizard: Member Selection → Loan Details → Nominee → Review & Submit
  - Member selector with eligibility guard (inactive/default warnings)
  - Loan limit calculator inline on step 2
  - Submission confirmation screen
- [x] src/pages/applications/ApplicationDetail.tsx
  - Full 360 view: header with all metadata, stage stepper (6 stages)
  - Exception banner when applicable
  - 8 tabs: Overview, Applicant & Member, Eligibility & Limit, Sanction & Approvals, Documents (badge), Security, Disbursement, Audit Trail
  - Each tab fully populated with domain-specific components

### Phase 5 — Members Module
- [x] src/pages/members/MemberDirectory.tsx
  - Search, KYC filter, type filter
  - Table with avatar, folio, shares, KYC status, active status, exposure, default flag
- [x] src/pages/members/MemberProfile.tsx
  - 3 tabs: Profile, Loans, Exposure & Limits
  - Re-KYC and default alert banners
  - Shareholding-based limit calculator with headroom display

### Phase 6 — Appraisal & Sanction
- [x] src/components/loan/LoanLimitCalculator.tsx
  - SOP policy warning (30% vs 10% contradiction)
  - Shareholding limit + Land limit + Final eligible (lower of)
  - Excess detection → exception flag
  - Collapsible formula disclosure
- [x] src/components/loan/EligibilityChecklist.tsx
  - 12 checks, pass/fail/needs_review/pending, progress bar
- [x] src/components/loan/ApprovalPanel.tsx
  - Authority matrix (≤₹5L: CFO+1Dir, >₹5L: CFO+2Dir)
  - Approver slots with decision badges
  - Decision modal: approve/reject/clarification/abstain
  - Exception register notice + special-case GM approval notice
- [x] src/pages/appraisal/AppraisalWorkbench.tsx
  - Queue panel + detail panel (split view)
  - Loan limit + eligibility inline
  - Appraisal note textarea → Save & Forward to Sanction
- [x] src/pages/sanction/SanctionWorkbench.tsx
  - Queue panel + detail panel with exception banner
  - ApprovalPanel with full decision recording

### Phase 7 — Documentation
- [x] src/components/loan/DocumentChecklist.tsx
  - 4 groups: KYC & Identity, Agriculture Evidence, Legal, Bank & Security
  - Stamp + notarisation sub-status for PoA/Loan Agreement
  - Disbursement blocker warning
  - 4-step sign-off sequence (CS → Credit Mgr → Sanction → SM Finance)
- [x] src/pages/documentation/DocumentationHub.tsx
  - Queue + detail panel with DocumentChecklist
  - Security instruments tracker (stamp/notarisation/custodian/PSN)

### Phase 8 — Disbursement
- [x] src/pages/disbursement/DisbursementHub.tsx
  - SAP Customer Code + bank details input
  - 6-stage progress indicator (SAP pending → bank verify → ready → initiated → CFC → completed)
  - Payment confirmation modal with amber warning
  - Recently-disbursed list when queue empty

### Phase 9 — Loan Account 360
- [x] src/components/loan/RepaymentLedger.tsx
  - Summary KPIs: Disbursed / Total Paid / Outstanding / Interest Collected
  - Table: Date, Amount, Principal, Interest, Channel (RTGS/NEFT/subsidiary), UTR, SAP status
  - Totals footer row
- [x] src/components/loan/AuditTimeline.tsx
  - Chronological event log with role labels, colour-coded icons, reason display
- [x] src/pages/loan-accounts/LoanAccount360.tsx
  - Two modes: account list (table) + account detail (tabs)
  - 5 KPI chips (sanctioned / outstanding / accrued interest / rate / DPD)
  - Overdue and grace period alert banners
  - 4 tabs: Summary, Repayment Ledger, Repayment Schedule (12-row EMI table), Audit Trail
  - DPD bucket label on each account

### Phase 10 — Repayments Hub
- [x] src/pages/repayments/RepaymentsHub.tsx
  - Account selector panel + repayment ledger
  - "Post Repayment" modal: account, amount, channel (RTGS/NEFT/subsidiary/other), UTR
  - SAP pending count banner

### Phase 11 — Monitoring & Compliance
- [x] src/pages/monitoring/MonitoringDashboard.tsx
  - 5-bucket DPD analysis (0 / 1-30 / 31-90 / 91-365 / 1yr+) with amounts
  - At-risk loan table with Remind + Recovery action buttons
  - Overdue alert banner (naming specific accounts)
  - MIS summary: total accounts, portfolio OS, accrued interest, DPD>0 count
- [x] src/pages/compliance/ComplianceDashboard.tsx
  - Section 186 limit bar (portfolio / estimated cap / utilisation %)
  - NBFC Principal Business Test (2 criteria display)
  - KYC tracker (verified / re-KYC due / expired / pending counts)
  - Compliance register (8 records: frequency, owner, evidence count, due date)
- [x] src/pages/registers/RegistersHub.tsx
  - 6 tabs: Loan Register, Credit Sanction Register, Security Register, Exception Register, Member Register, Audit Log
  - Export Register button
  - All registers fully populated from mock data

### Phase 12 — Role System & Login Screen
- [x] src/contexts/RoleContext.tsx (RoleProvider, useRole, ROLE_LABELS, ROLE_USERS, Permission type, ROLE_PERMISSIONS)
  - 13 roles: 12 internal + borrower
  - `can(permission)` function for conditional rendering
  - ROLE_USERS maps each role to a demo user
- [x] src/pages/auth/LoginScreen.tsx (S00)
  - Split-panel layout with SFPCL branding + stats on left, login form on right
  - Demo role selector + 13 quick-login buttons
  - Post-login routes: internal → dashboard, borrower → BorrowerPortal
- [x] Updated Header.tsx — uses RoleContext, shows user name/role dynamically
  - "Switch Role" dropdown with all 13 roles (key feature for demo/QA)
  - Sign out button in profile dropdown
- [x] Updated Sidebar.tsx — filters nav items by `can(permission)`
  - CFO: sees Settings, not SAP/Interest/Appraisal
  - Borrower: sees only "My Loan"
  - CFC: sees only Payment Authorisation + Loan Accounts
  - Auditor: read-only pages only
- [x] Updated AppShell.tsx — passes `onLogout` through to Header
- [x] Updated App.tsx — wraps in RoleProvider, login gate, 24+ pages routed

### Phase 13 — Borrower Portal (Farmer/FPC Self-Service)
- [x] src/pages/borrower/BorrowerPortal.tsx
  - Own header (no internal sidebar/nav)
  - Welcome banner with outstanding amount + overdue alert
  - 4 quick-stat KPI chips
  - 5 tabs: Overview, Application Status, Repayments, My Documents, Raise Grievance
  - Overview: loan details, security document status, contact officer buttons
  - Application Status: visual timeline with 7 stages
  - Repayments: full repayment schedule with paid/overdue/upcoming status
  - My Documents: download links for issued documents, upload modal
  - Grievance: raise new grievance form with submission confirmation

### Phase 14 — Default & Recovery Hub (S53–S57)
- [x] src/pages/defaults/DefaultRecoveryHub.tsx
  - 4 DPD KPI cards (overdue / grace / default review / recovery approved)
  - 5 tabs: Default Cases, Grace Period/Extension, Non-Payment Note, Recovery Approval, Security Invocation
  - Default Cases: split list+detail view with workflow progress stepper
  - Grace Period: extension note form with mandatory reason field
  - Non-Payment Note: form with recommended action radio buttons → submit to Sanction Committee
  - Recovery Approval: CFO-gated approval with decision options (role-guarded)
  - Security Invocation: SH-4 / blank cheque invocation form (CS-gated)

### Phase 15 — Loan Closure Hub (S58–S61)
- [x] src/pages/closure/LoanClosureHub.tsx
  - Loan selector (3 loans in various closure states)
  - 4 tabs: Closure Checklist, NOC Generation, Security Return/Unpledge, Archive
  - Closure Checklist: 10-item checklist with progress bar, blocks if balance > 0
  - NOC Generation: generates NOC with date/reference/language, download button
  - Security Return: SH-4, blank cheque, CDSL pledge, PoA return tracking
  - Archive: document category summary, 8-year retention policy, archive package download

### Phase 16 — Interest Management Hub (S47–S49)
- [x] src/pages/interest/InterestManagement.tsx
  - 4 KPI chips: Q2 accrued, overdue interest, invoices pending, pending capitalisation
  - 3 tabs: Interest Accrual, Yearly Invoices, Interest Capitalisation
  - Accrual: quarterly table with principal/rate/days/accrued, period selector, Post to SAP
  - Invoices: FY invoice list with download, bulk generate button
  - Capitalisation: overdue interest capitalisation workflow with SOP rule display, irreversible warning

### Phase 17 — Settings Hub (S70–S73)
- [x] src/pages/settings/SettingsHub.tsx
  - Access-restricted: only Admin, CFO, CS can view (enforced via `can('view_settings')`)
  - 4 tabs: Policy Config, Approval Matrix, Template Management, User & Role Management
  - Policy: loan parameters, eligibility rules, compliance thresholds (all editable by admin)
  - Approval Matrix: sanction authority table + TAT escalation rules
  - Templates: document template list with version, owner, active status, edit/delete (admin only)
  - Users: role→user mapping with permissions overview table

### Phase 18 — Reports & MIS Center (S69)
- [x] src/pages/reports/ReportsMIS.tsx
  - Access-restricted: CFO, Credit Manager, Accounts, Auditor
  - Period selector + Export button in header
  - 5 tabs: Portfolio Summary, DPD & Aging Analysis, Compliance MIS, Member Exposure, Custom Reports
  - Portfolio: 8 KPI cards with trend indicators, member-type breakdown bar, monthly disbursement trend
  - DPD: 6-bucket aging table with visual bars, CFO quarterly MIS summary
  - Compliance: Section 186 bar + KYC status grid
  - Member Exposure: per-member headroom table with risk coloring
  - Custom Reports: report type + date range + format selector

### Phase 19 — Task Inbox (S03)
- [x] src/pages/tasks/TaskInbox.tsx
  - All 8 task types with color-coded chips
  - Priority filter (All/Critical/High/Normal) + type dropdown filter
  - Per-row: priority indicator, task type, loan no., borrower, amount, status badge, TAT, priority badge, Open button
  - Critical/overdue rows highlighted in red
  - Role-aware: shows tasks assigned to current user's role

### Phase 20 — Register Expansions
- [x] RegistersHub.tsx — added 2 new tabs (now 8 total):
  - Tab 6: Grievance Register — ref, borrower, subject, status, resolution date
  - Tab 7: Recovery Log — loan no., borrower, outstanding, DPD, stage, action taken

### Phase 21 — Screen Audit Gap Fixes
- [x] Audited current screens against `docs/screen-spec.md`, `docs/functional-spec.md`, `docs/user-flows.md`, and `docs/information-architecture.md`
- [x] BorrowerPortal.tsx — corrected borrower lifecycle order to Application → Completeness → Appraisal → Sanction → Documentation → SAP Setup → Disbursement → Active Loan / Monitoring → Closure
- [x] BorrowerPortal.tsx — added Application Data tab with borrower identity, membership/shareholding, eligibility, loan request, nominee, signature, validation, deficiency-response, bank/SAP evidence, and audit snapshot sections
- [x] BorrowerPortal.tsx — expanded borrower document sections to cover KYC, nominee, shareholding, land, crop plan, bank statement deficiency, term sheet, agreement, disbursement advice, repayment schedule, interest invoice, and NOC
- [x] BorrowerPortal.tsx — added borrower-visible role boundaries: upload/re-upload, deficiency response, download/view own documents; no approval/disbursement actions exposed to borrower
- [x] index.css — added default card padding so headings and content no longer touch card margins, while explicit `p-0` table cards continue to override padding
- [x] Build verification completed with `npm run build`

### Phase 22 — Borrower New Application Workflow
- [x] BorrowerPortal.tsx — added borrower-facing New Application tab based on S10 New Loan Application, S08 Nominee Detail Panel, S12 Completeness Check, and User Flow 2/3
- [x] Added guided application steps: Applicant → Shares → Loan → Nominee → Documents → Declarations → Review
- [x] Captures applicant type, channel, borrower KYC identity, member ID, folio, contact, email, address, PAN, Aadhaar last four
- [x] Captures shareholding mode, shares held, valuation, conditional demat BO ID, shareholding limit, land-based limit, and maximum permissible limit
- [x] Captures requested amount, agriculture/crop purpose, crop, season, repayment date, loan type, and subsidiary repayment linkage
- [x] Captures nominee name, DOB, age, gender, relationship, mobile, address, PAN, Aadhaar, borrower signature, and nominee signature
- [x] Adds mandatory document checklist for borrower PAN/Aadhaar, nominee PAN/Aadhaar, share certificate, 7/12 extract, crop plan, and six-month bank statement, with uploaded + self-attested gates
- [x] Adds declaration gates for agriculture purpose, document truth, no-default confirmation, KYC consent, and sanction-term acknowledgement
- [x] Adds final review checklist and blocks submission until all mandatory fields, documents, declarations, and signatures are complete
- [x] Build verification completed with `npm run build`

### Phase 23 — Agentation Setup
- [x] Installed `agentation` as a dev dependency
- [x] Mounted `<Agentation endpoint="http://localhost:4747" />` at the React root behind `import.meta.env.DEV`
- [x] Added project MCP config for Claude Code at `sfpcl-lms/.mcp.json`
- [x] Added project MCP config for Codex at `sfpcl-lms/.codex/config.toml`
- [x] Started Vite dev server on `http://localhost:5173`
- [x] Started Agentation MCP/HTTP server on `http://localhost:4747`
- [x] Verified production build with `npm run build`
- [x] Verified Agentation server health with `npx agentation-mcp doctor`
- [~] Claude Code doctor does not detect the project `.mcp.json`; use `claude mcp add agentation -- npx agentation-mcp server` if Claude needs global MCP registration

### Phase 24 — Agentation Feedback Fixes
- [x] ApplicationList New Application button now opens a full internal assisted-entry workflow matching the borrower portal intake pattern
- [x] NewApplication.tsx expanded from 4 steps to Member → Applicant → Shares → Loan → Nominee → Documents → Declarations → Review
- [x] Added member eligibility validation for active status and no-default status before intake can continue
- [x] Added applicant/KYC fields, shareholding/security fields, loan purpose/crop/season/repayment fields, nominee fields, mandatory document gates, declarations, and signature gates
- [x] Added final completeness checklist and blocked submission until all mandatory application items pass
- [x] AppraisalWorkbench.tsx step bar made fully visible and stateful for Verify → Appraise → Forward
- [x] Appraisal Step 2 now includes required S19 fields: recommended amount, tenure, recommendation, proposed security, bank observations, risk rationale, conditions, draft save, and appraisal PDF action
- [x] Appraisal Step 3 now includes S20 Credit Manager review package, comment capture, return-for-correction, reject, and forward-to-sanction actions
- [x] AppraisalWorkbench.tsx left solid accent borders removed from queue selection and verification cards; replaced with product-consistent full-border/background states
- [x] BorrowerPortal.tsx layout changed to use dashboard-consistent sidebar + top header shell while preserving all borrower information, fields, and tab content
- [x] BorrowerPortal.tsx horizontal in-content tabs moved into the left menu bar; header now shows the active borrower section context and main pane uses full dashboard content width
- [x] Shared Header.tsx UX improved with stronger search affordance, cleaner control grouping, polished dropdowns, and clearer notification/profile controls without changing header information
- [x] Dashboard.tsx visual hierarchy improved across all role dashboards with a structured header panel, full-width shell usage, steadier cards, and better focus/hover states without changing role-specific information
- [x] KPICard.tsx and AppShell.tsx polished for consistent dashboard card sizing, subtle motion, and calmer page surface
- [x] Build verification completed with `npm run build`

---

## Runtime Status
- TypeScript: ✅ 0 errors (`tsc --noEmit` clean)
- Dev server: ✅ Running on http://localhost:5173 (Vite 5.4.x)
- App renders: ✅ All 24+ pages navigable, login gate working
- Login screen: ✅ Role dropdown, quick-login buttons, all 13 roles
- Role switcher: ✅ "Switch Role" in header — sidebar filters on change
- Borrower portal: ✅ Farmer self-service portal (separate chrome)
- Role-gated nav: ✅ Sidebar filtered per role (CFO≠CFC≠Auditor≠Borrower)
- New workflow hubs: ✅ Default/Recovery, Closure, Interest, Settings, Reports, Tasks
- StatusBadge: ✅ All 50+ statuses show human-readable labels

## Gap Coverage vs Spec (74 screens)
| Implemented | ~52 of 74 screens covered |
| Still missing | S02 Global Search Results, S07 Borrower 360 (distinct), S08 Nominee Panel, S09 Witness Panel, S28–S34 individual legal document screens |

## Status Key
- [x] Complete
- [~] In progress
- [ ] Not started

Last updated: 2026-06-25
Phases 0–24 complete. Agentation is installed, mounted dev-only, and the New Application feedback has been applied; consolidated screen coverage still needs the missing standalone screens listed above.
