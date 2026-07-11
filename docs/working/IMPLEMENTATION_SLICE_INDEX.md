# Implementation Slice Index

This index is the ordered Ralph implementation queue. Broad module concepts live in `docs/epics/`; these slice files are the actual AFK work units.

Selection rule: Ralph picks the lowest filename-sorted `Not Started` slice. Slices marked "None (independent)" may be run out of order (via `--slice`) if the queue head is blocked. All slices, including High risk, run under the owner's standing approval unless marked `[revoked]` in `docs/working/HIGH_RISK_APPROVALS.md`.

| Order | Slice | Parent Epic | Depends On | Risk | Frontend | Backend/API | Database | Tests |
|---|---|---|---|---|---|---|---|---|
| 1 | `001` Ralph Bootstrap Verification | Epic 001 | None, | Low | No | No | No | Yes |
| 2 | `002A` Backend Scaffold and Health Endpoint | Epic 002 | 001, | Medium | No | Yes | Yes | Yes |
| 3 | `002B` User Model and JWT Login Refresh Logout | Epic 002 | 002A, | High | No | Yes | Yes | Yes |
| 3a | `002B2` Auth Hardening — PyJWT and Packaging | Epic 002 | 002B, | High | No | Yes | No | Yes |
| 4 | `002C` Role and Permission Catalogue Seed | Epic 002 | 002B, | High | No | Yes | Yes | Yes |
| 5 | `002D` Current User API with Permissions and Teams | Epic 002 | 002C, | High | No | Yes | Yes | Yes |
| 5a | `002D2` Backend Dev Infrastructure (Env, DB, CORS) | Epic 002 | 002D, | Medium | No | Yes | Yes | Yes |
| 6 | `002E` Protected Frontend Route Shell | Epic 002 | 002D2, | Medium | Yes | Yes | No | Yes |
| 6a | `002EX` Early End-to-End Tracer Bullet | Epic 002 | 002E, | High | Yes | Yes | Yes | Yes |
| 6b | `002EY` E2E and Visual Regression Harness | Epic 002 | 002EX, | Medium | Yes | No | No | Yes |
| 7 | `002F` Role-Aware Sidebar Header Navigation | Epic 002 | 002E, | Medium | Yes | Yes | No | Yes |
| 7a | `002FL` Frontend Lint Baseline (ESLint) | Epic 002 | 002F, | Medium | Yes | No | No | Yes |
| 8 | `002G` Admin User and Role Management Shell | Epic 002 | 002F, | Medium | Yes | Yes | Yes | Yes |
| 9 | `002H` State Machine and Transition Guard Foundation | Epic 002 | 002G, | Medium | No | Yes | Yes | Yes |
| 10 | `002I` Object-Level Permission Test Harness | Epic 002 | 002H, | High | No | Yes | No | Yes |
| 11 | `002J` API Contract Test Harness | Epic 002 | 002I, | Medium | No | Yes | No | Yes |
| 12 | `002K` Seed Data and Demo Users | Epic 002 | 002J, | Medium | No | Yes | Yes | Yes |
| 13 | `003A` Audit Log Foundation | Epic 003 | 002K, | Medium | No | Yes | Yes | Yes |
| 14 | `003B` Workflow Event Foundation | Epic 003 | 003A, | Medium | No | Yes | Yes | Yes |
| 15 | `003C` Document Metadata and Storage Adapter | Epic 003 | 003B, | Medium | No | Yes | Yes | Yes |
| 16 | `003D` Secure Document Download with Audit | Epic 003 | 003C, | Medium | No | Yes | Yes | Yes |
| 17 | `003E` Versioned Configuration Shell | Epic 003 | 003D, | Medium | Yes | Yes | Yes | Yes |
| 18 | `003F` Communication Template Shell | Epic 003 | 003E, | Medium | Yes | Yes | Yes | Yes |
| 19 | `003G` Dashboard Task Summary API | Epic 003 | 003F, | Medium | Yes | Yes | Yes | Yes |
| 20 | `003H` Dashboard Task UI Wiring | Epic 003 | 003G, | Medium | Yes | Yes | No | Yes |
| 21 | `003I` Notification Adapter Shell | Epic 003 | 003H, | Medium | No | Yes | Yes | Yes |
| 21a | `003IA` Notifications Center UI Wiring | Epic 003 | 003I, | Medium | Yes | Yes | No | Yes |
| 22 | `003J` Background Job Scheduling Foundation | Epic 003 | 003I, | Medium | No | Yes | Yes | Yes |
| 23 | `003K` Prototype Visual Gap Report Update | Epic 003 | None (independent), | Low | No | No | No | Yes |
| 24 | `003L` Data Import and Migration Planning | Epic 003 | None (independent), | Medium | No | No | No | Yes |
| 25 | `004A` Member Directory API and UI | Epic 004 | 003L, | Medium | Yes | Yes | Yes | Yes |
| 26 | `004B` Member Profile API and UI | Epic 004 | 004A, | Medium | Yes | Yes | Yes | Yes |
| 27 | `004C` Individual Farmer and FPC Profile Details | Epic 004 | 004B, | Medium | No | Yes | Yes | Yes |
| 28 | `004D` Nominee Validation and UI | Epic 004 | 004C, | Medium | Yes | Yes | No | Yes |
| 29 | `004E` Witness Shareholder Validation | Epic 004 | 004D, | Medium | No | Yes | Yes | Yes |
| 30 | `004F` Shareholding and Share Certificate Records | Epic 004 | 004E, | Medium | No | Yes | Yes | Yes |
| 31 | `004G` Landholding and Crop Plan Records | Epic 004 | 004F, | Medium | No | Yes | Yes | Yes |
| 32 | `004H` KYC Upload and Verification | Epic 004 | 004G, | High | No | Yes | Yes | Yes |
| 33 | `004I` Sensitive Masking and Reveal Audit | Epic 004 | 004H, | High | No | Yes | Yes | Yes |
| 34 | `004J` Bank Account and Cancelled Cheque Profile Foundation | Epic 004 | 004I, | High | No | Yes | Yes | Yes |
| 34a | `004K` Borrower 360, KYC Panel, and Masking UI Wiring | Epic 004 | 004J, | Medium | Yes | Yes | No | Yes |
| 35 | `005A` Loan Application Draft Create Update | Epic 005 | 004J, | Medium | No | Yes | Yes | Yes |
| 36 | `005B` Application Submit and Status Transition | Epic 005 | 005A, | Medium | No | Yes | Yes | Yes |
| 37 | `005C` Reference Number Generation and Loan Request Register | Epic 005 | 005B, | Medium | No | Yes | Yes | Yes |
| 37a | `005C2` Application Object Access Hardening | Epic 005 | 005C, | Medium | No | Yes | No | Yes |
| 38 | `005D` Application Document Checklist | Epic 005 | 005C2, | Medium | No | Yes | Yes | Yes |
| 39 | `005E` Completeness Workbench | Epic 005 | 005D, | Medium | Yes | Yes | Yes | Yes |
| 39a | `005E2` Completeness Workbench Real-Data Corrective | Epic 005 | 005I, | Medium | Yes | Yes | No | Yes |
| 40 | `005F` Deficiency Creation and Resolution | Epic 005 | 005E, | Medium | No | Yes | Yes | Yes |
| 40a | `005FA` Member Portal Authentication | Epic 005 | 005F, | High | Yes | Yes | Yes | Yes |
| 40a2 | `005FA2` Portal Demo-Login Gating and Session Authority | Epic 005 | 005FA, | High | Yes | No | No | Yes |
| 40a3 | `005FA3` Portal Auth Interaction and Demo-Flag Proof | Epic 005 | 005FA2, | High | Yes | No | No | Yes |
| 40b | `005FB` Member Portal Dashboard, Profile, and Supply View | Epic 005 | 005FA, | Medium | Yes | Yes | No | Yes |
| 41 | `005G` Member Portal Application Start Status | Epic 005 | 005FB, | Medium | Yes | Yes | Yes | Yes |
| 42 | `005H` Rejection Note Shell | Epic 005 | 005G, | Medium | Yes | Yes | Yes | Yes |
| 42a | `005I` Application Intake Frontend Wiring | Epic 005 | 005H, | Medium | Yes | Yes | No | Yes |
| 43 | `006A` Active Member Eligibility Service | Epic 006 | 005H, | Medium | No | Yes | Yes | Yes |
| 44 | `006B` Default Document Purpose and Terms Eligibility Checks | Epic 006 | 006A, | Medium | No | Yes | Yes | Yes |
| 45 | `006C` Loan Limit Configuration and Calculator | Epic 006 | 006B, | High | No | Yes | Yes | Yes |
| 46 | `006D` Loan Limit Snapshot Storage | Epic 006 | 006C, | High | No | Yes | Yes | Yes |
| 47 | `006E` Appraisal Note Create Edit Submit | Epic 006 | 006D, | Medium | No | Yes | Yes | Yes |
| 48 | `006F` Credit Manager Review | Epic 006 | 006E, | Medium | Yes | Yes | Yes | Yes |
| 49 | `006G` Submit to Sanction | Epic 006 | 006F, | Medium | No | Yes | Yes | Yes |
| 49a | `006G4` Sanction Dependency Boundary Regression | Epic 006 | 006G3, | Medium | No | Yes | No | Yes |
| 50 | `006H` Eligibility Appraisal Frontend Integration | Epic 006 | 006G, | Medium | Yes | Yes | No | Yes |
| 50a | `006H5` App Shell Application State Authority | Epic 006 | 006H4, | Medium | Yes | No | No | Yes |
| 50b | `006H6` Workbench Action Projection and Interaction Proof | Epic 006 | 006H4 and 006G4, | High | Yes | Yes | No | Yes |
| 50c | `006H3` Appraisal Workbench Prototype Fidelity Restoration | Epic 006 | 006H6, | Medium | Yes | No | No | Yes |
| 51 | `006X` MVP End-to-End Happy Path Tracer Bullet | Epic 006 | 006H, | High | No | Yes | Yes | Yes |
| 51a | `006Y` Member Create/Update and Identity Governance | Epic 004 | 006X, | High | No | Yes | Yes | Yes |
| 51b | `006Y2` Member Form and Witness Capture UI Wiring | Epic 004 | 006Y, | Medium | Yes | Yes | No | Yes |
| 51c | `006Z` Produce Supply History Persistence | Epic 006 | 006Y2, | High | Yes | Yes | Yes | Yes |
| 51d | `006Z2` Portal Application Limit Display Authority | Epic 006 | 006Z, | Medium | Yes | Yes | No | Yes |
| 52 | `007A` Approval Matrix Configuration | Epic 007 | 006X, | Medium | No | Yes | Yes | Yes |
| 53 | `007B` Approval Case Creation from Appraisal | Epic 007 | 007A, | Medium | No | Yes | Yes | Yes |
| 54 | `007C` CFO and Director Threshold Routing | Epic 007 | 007B, | Medium | No | Yes | Yes | Yes |
| 55 | `007D` Approval Action API Approve Reject Return | Epic 007 | 007C, | Medium | No | Yes | Yes | Yes |
| 56 | `007E` Conflict of Interest Blocking | Epic 007 | 007D, | High | No | Yes | Yes | Yes |
| 57 | `007F` Exception Approval Workflow | Epic 007 | 007E, | Medium | No | Yes | Yes | Yes |
| 58 | `007G` General Meeting Evidence for Special Cases | Epic 007 | 007F, | Medium | No | Yes | Yes | Yes |
| 59 | `007H` Credit Sanction Register | Epic 007 | 007G, | Medium | No | Yes | Yes | Yes |
| 60 | `007I` Sanction Workbench UI | Epic 007 | 007H, | Medium | Yes | Yes | No | Yes |
| 60a | `007J` Registers and Approval Matrix Settings UI Wiring | Epic 007 | 007I, | Medium | Yes | Yes | No | Yes |
| 60b | `007J2` SettingsHub Remaining Panels Wiring or Lockdown | Epic 007 | 007J, | Medium | Yes | Yes | No | Yes |
| 61 | `008A` Document Template Model and Versioning | Epic 008 | 007I, | Medium | No | Yes | Yes | Yes |
| 62 | `008B` Document Generation Shell | Epic 008 | 008A, | Medium | Yes | Yes | Yes | Yes |
| 63 | `008C` Documentation Checklist Applicability | Epic 008 | 008B, | Medium | No | Yes | Yes | Yes |
| 64 | `008D` Stamp Duty and Notarisation Tracking | Epic 008 | 008C, | Medium | No | Yes | Yes | Yes |
| 65 | `008E` Signature Mismatch Workflow | Epic 008 | 008D, | Medium | No | Yes | Yes | Yes |
| 66 | `008F` Power of Attorney Workflow | Epic 008 | 008E, | Medium | No | Yes | Yes | Yes |
| 67 | `008G` Tri-Party Agreement Workflow | Epic 008 | 008F, | Medium | No | Yes | Yes | Yes |
| 68 | `008H` SH-4 Physical Share Security Workflow | Epic 008 | 008G, | High | No | Yes | Yes | Yes |
| 69 | `008I` CDSL Pledge Workflow | Epic 008 | 008H, | Medium | No | Yes | Yes | Yes |
| 70 | `008J` Blank-Dated Cheque and Cancelled Cheque Custody | Epic 008 | 008I, | Medium | No | Yes | Yes | Yes |
| 71 | `008K` Final Documentation Approval Sequence | Epic 008 | 008J, | Medium | No | Yes | Yes | Yes |
| 72 | `008L` Member Portal Documentation Actions | Epic 008 | 008K, | Medium | Yes | Yes | Yes | Yes |
| 72b | `008L2` Member Portal Deficiency Response and Resubmission | Epic 005 | 008L, | High | Yes | Yes | Yes | Yes |
| 72a | `008M` Documentation Hub Frontend Wiring | Epic 008 | 008L, | Medium | Yes | Yes | No | Yes |
| 73 | `009A` SAP Customer Code Request | Epic 009 | 008L, | High | No | Yes | Yes | Yes |
| 74 | `009B` SAP Customer Code Confirmation and Reuse | Epic 009 | 009A, | High | No | Yes | Yes | Yes |
| 75 | `009C` Loan Account Creation from Sanctioned Application | Epic 009 | 009B, | Medium | No | Yes | Yes | Yes |
| 76 | `009D` Disbursement Readiness Service | Epic 009 | 009C, | High | No | Yes | Yes | Yes |
| 77 | `009E` Payment Initiation by Senior Manager Finance | Epic 009 | 009D, | High | No | Yes | Yes | Yes |
| 78 | `009F` CFC Authorization Rejection | Epic 009 | 009E, | High | No | Yes | Yes | Yes |
| 79 | `009G` UTR Capture and Transfer Success | Epic 009 | 009F, | High | No | Yes | Yes | Yes |
| 80 | `009H` Disbursement Advice and Communication | Epic 009 | 009G, | High | No | Yes | Yes | Yes |
| 81 | `009I` Member Portal Disbursement Status | Epic 009 | 009H, | High | Yes | Yes | No | Yes |
| 82 | `009J` Loan Account 360 Initial View | Epic 009 | 009I, | Medium | Yes | Yes | No | Yes |
| 82a | `009K` Disbursement and CFC Authorization Frontend Wiring | Epic 009 | 009J, | High | Yes | Yes | No | Yes |
| 83 | `010A` Loan Account Schedule and Ledger | Epic 010 | 009J, | Medium | No | Yes | Yes | Yes |
| 84 | `010B` Direct Repayment Posting | Epic 010 | 010A, | High | No | Yes | Yes | Yes |
| 85 | `010C` Principal-First Allocation | Epic 010 | 010B, | High | No | Yes | Yes | Yes |
| 86 | `010D` Bank Statement Matching Unmatched Receipts | Epic 010 | 010C, | High | No | Yes | Yes | Yes |
| 87 | `010E` Subsidiary Deduction Reconciliation | Epic 010 | 010D, | Medium | No | Yes | Yes | Yes |
| 88 | `010F` Interest Invoice Generation | Epic 010 | 010E, | High | No | Yes | Yes | Yes |
| 89 | `010G` Monthly Interest Accrual | Epic 010 | 010F, | High | No | Yes | Yes | Yes |
| 90 | `010H` Interest Capitalisation after 30 April | Epic 010 | 010G, | High | No | Yes | Yes | Yes |
| 91 | `010I` DPD Calculation and Monitoring Buckets | Epic 010 | 010H, | Medium | No | Yes | Yes | Yes |
| 92 | `010J` Reminder Queue | Epic 010 | 010I, | Medium | No | Yes | Yes | Yes |
| 93 | `010K` CFO Quarterly MIS | Epic 010 | 010J, | Medium | No | Yes | Yes | Yes |
| 94 | `010L` Member Portal Repayment View | Epic 010 | 010K, | High | Yes | Yes | No | Yes |
| 94a | `010M` Servicing and Monitoring Frontend Wiring | Epic 010 | 010L, | High | Yes | Yes | No | Yes |
| 94b | `010N` Global Search API and UI | Epic 010 | 010M, | Medium | Yes | Yes | Yes | Yes |
| 94c | `010O` Header Notification Summary Wiring | Epic 003 | 010N, | Low | Yes | Yes | No | Yes |
| 95 | `011A` Default Case Opening | Epic 011 | 010L, | Medium | No | Yes | Yes | Yes |
| 96 | `011B` Grace Period Tracking | Epic 011 | 011A, | Medium | No | Yes | Yes | Yes |
| 97 | `011C` Extension Note Workflow | Epic 011 | 011B, | Medium | No | Yes | Yes | Yes |
| 98 | `011D` Non-Payment Note Workflow | Epic 011 | 011C, | High | No | Yes | Yes | Yes |
| 99 | `011E` Recovery Decision Approval | Epic 011 | 011D, | High | No | Yes | Yes | Yes |
| 100 | `011F` Recovery Action Execution Shell | Epic 011 | 011E, | High | Yes | Yes | Yes | Yes |
| 101 | `011G` Closure Readiness | Epic 011 | 011F, | Medium | No | Yes | Yes | Yes |
| 102 | `011H` NOC Issuance | Epic 011 | 011G, | Medium | No | Yes | Yes | Yes |
| 103 | `011I` Security Return and CDSL Unpledge Tracking | Epic 011 | 011H, | High | No | Yes | Yes | Yes |
| 104 | `011J` Archive Record and Retention | Epic 011 | 011I, | Medium | No | Yes | Yes | Yes |
| 105 | `011K` Compliance Control Tracker Foundation | Epic 011 | 011J, | Medium | No | Yes | Yes | Yes |
| 106 | `011L` Section 186 and NBFC Test Trackers | Epic 011 | 011K, | Medium | No | Yes | Yes | Yes |
| 107 | `011M` KYC Re-KYC Compliance Tracker | Epic 011 | 011L, | High | No | Yes | Yes | Yes |
| 107a | `011M2` Member Portal KYC Correction Request | Epic 011 | 011M, | High | Yes | Yes | Yes | Yes |
| 108 | `011N` Grievance Workflow | Epic 011 | 011M, | Medium | No | Yes | Yes | Yes |
| 108a | `011NA` Member Portal Notices, Grievances, and Notifications | Epic 011 | 011N, | Medium | Yes | Yes | No | Yes |
| 109 | `011O` Auditor Read-Only Views | Epic 011 | 011N, | Medium | Yes | Yes | No | Yes |
| 109a | `011P` Default, Closure, Compliance, and Grievance Staff Frontend Wiring | Epic 011 | 011O, | Medium | Yes | Yes | No | Yes |
| 110 | `012A` Report API Foundation | Epic 012 | 011O, | Medium | No | Yes | Yes | Yes |
| 111 | `012B` Register Exports | Epic 012 | 012A, | Medium | No | Yes | Yes | Yes |
| 112 | `012C` Export Masking and Permission Checks | Epic 012 | 012B, | High | No | Yes | Yes | Yes |
| 113 | `012D` Audit Explorer | Epic 012 | 012C, | Medium | No | Yes | Yes | Yes |
| 113a | `012DA` Reports, Exports, and Audit Explorer Frontend Wiring | Epic 012 | 012D, | Medium | Yes | Yes | No | Yes |
| 114 | `012E` Operational Dashboard Hardening | Epic 012 | 012D, | Medium | Yes | Yes | Yes | Yes |
| 114a0 | `012E2` Tracer and Demo Route Production Isolation | Epic 012 | 012E, | High | Yes | Yes | No | Yes |
| 114a1 | `012E3` Field-Encryption Key Separation and Rotation | Epic 012 | 012E2, | High | No | Yes | Yes | Yes |
| 114a | `012EA` Workflow Task Engine and Task Inbox APIs | Epic 012 | 012E, | Medium | No | Yes | Yes | Yes |
| 114b | `012EB` Task Inbox Frontend Wiring | Epic 012 | 012EA, | Medium | Yes | Yes | No | Yes |
| 115 | `012F` Security Privacy Regression Checks | Epic 012 | 012E, | High | No | Yes | No | Yes |
| 116 | `012G` Critical E2E UAT Smoke Scenarios | Epic 012 | 012F, | Medium | No | Yes | No | Yes |
| 117 | `012H` Deployment Readiness and Smoke Checks | Epic 012 | 012G, | Medium | No | Yes | No | Yes |
| 118 | `012I` Final UAT Review Packet | Epic 012 | 012H, | Medium | Yes | No | No | Yes |
