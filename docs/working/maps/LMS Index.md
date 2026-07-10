# LMS Index

This is the entry point for the SFPCL Loan Management System specification vault.

The vault is organised through native Obsidian links rather than folders. Use the document map for source authority, the capability maps for section-level navigation and the traceability matrix for coverage review.

## Start Here

- [[product-requirements|Product Requirements]] — product scope, MVP boundary, acceptance criteria and issue slicing.
- [[sfpcl_client_brief|Client Brief]] — closest available interpretation of the source SOP and its unresolved policy questions.
- [[LMS Traceability Matrix]] — capability-by-capability coverage across requirements, domain, data, UI, APIs, permissions and tests.
- [[Open Decisions Index]] — unresolved policy, legal, operational and technical decisions.
- [[LMS Architecture.canvas|LMS Architecture Canvas]] — curated visual map of the specification system.

## Source and Product Authority

- [[sfpcl_client_brief|Client Brief]]
- [[user-flows|User Flows]]
- [[functional-spec|Functional Specification]]
- [[product-requirements|Product Requirements]]
- [[implementation-roadmap|Implementation Roadmap]]

## Experience and Interface Specifications

- [[information-architecture|Information Architecture]]
- [[screen-spec|Internal Screen Specification]]
- [[screen-spec-member-portal|Member Portal Screen Specification]]
- [[component-spec|Component Specification]]
- [[content-spec|Content Specification]]
- [[design-system|Design System]]

## Domain, Data and Engineering

- [[domain-model|Domain Model]]
- [[data-model|Data Model]]
- [[technical-architecture|Technical Architecture]]
- [[api-contracts|API Contracts]]
- [[auth-permissions|Authentication and Permissions]]
- [[integrations|Integrations]]
- [[codebase-design|Codebase Design]]

## Security, Operations and Quality

- [[security-privacy|Security and Privacy]]
- [[deployment-ops|Deployment and Operations]]
- [[test-plan|Test Plan]]

## Capability Maps

- [[Membership and KYC Map]]
- [[Application and Completeness Map]]
- [[Eligibility and Loan Limit Map]]
- [[Appraisal and Sanction Map]]
- [[Documentation and Security Map]]
- [[SAP and Disbursement Map]]
- [[Repayment and Interest Map]]
- [[Monitoring Default and Recovery Map]]
- [[Closure and Compliance Map]]
- [[Platform Security and Operations Map]]

## Authority Rules

1. The original SOP remains the ultimate business source, but it is not present in this vault. [[sfpcl_client_brief|Client Brief]] is the closest available derived interpretation.
2. [[product-requirements|Product Requirements]] governs product scope and MVP boundaries.
3. [[functional-spec|Functional Specification]] governs functional behaviour; [[user-flows|User Flows]] governs operational sequence and actors.
4. [[domain-model|Domain Model]] governs business vocabulary and aggregate boundaries.
5. [[data-model|Data Model]] governs persistence, relationships, constraints and calculation snapshots.
6. [[content-spec|Content Specification]] governs UI and communication copy; [[design-system|Design System]] governs visual and interaction behaviour.
7. [[api-contracts|API Contracts]], [[auth-permissions|Authentication and Permissions]] and [[codebase-design|Codebase Design]] govern implementation interfaces and enforcement.
8. Repetition across derived documents is not independent confirmation of an unresolved policy. Track such matters in [[Open Decisions Index]].

## Navigation Rules

- Use heading links for unique numbered sections.
- Use stable block IDs for exact rules when headings repeat.
- Use capability maps for end-to-end traceability.
- Every capability map must include both [[domain-model|Domain Model]] and [[data-model|Data Model]] coverage.
- Graph View shows note-to-note relationships; it does not render headings as separate nodes.

