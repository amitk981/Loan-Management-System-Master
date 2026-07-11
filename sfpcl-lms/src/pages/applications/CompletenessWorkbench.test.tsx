import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { CompletenessWorkbenchView } from './CompletenessWorkbench';
import workbenchSource from './CompletenessWorkbench.tsx?raw';
import type {
  ApplicationCompleteness,
  ApplicationDeficiency,
  StaffApplication,
} from '../../services/applicationIntakeApi';

describe('CompletenessWorkbenchView', () => {
  it('renders backend queue, checklist, and complete deficiency history without mock authority', () => {
    const html = render('success', true);
    expect(html).toContain('API Borrower One');
    expect(html).toContain('Borrower PAN');
    expect(html).toContain('Current PAN copy is missing.');
    expect(html).toContain('Verified replacement from borrower.');
    expect(html).not.toContain('Ganesh Thorat');
    expect(workbenchSource).not.toContain("../../data/mockData");
    expect(workbenchSource).not.toContain('getNextLoanReference');
    expect(workbenchSource).not.toContain('seededDeficiencies');
  });

  it('renders backend-issued reference and hides mutation actions without canonical permission', () => {
    const completed = render('success', false, {
      ...completeness,
      application_reference_number: 'LO00000042',
      application_status: 'reference_generated',
      completeness_status: 'complete',
      blocking_document_types: [],
      can_generate_reference: false,
    });

    expect(completed).toContain('LO00000042');
    expect(completed).not.toContain('Generate reference number');
    expect(completed).not.toContain('Return for deficiency');
    expect(completed).toContain('Read-only');
  });

  it('renders loading, empty, unauthorized, validation, and stale conflict states', () => {
    expect(render('loading', false)).toContain('Loading completeness queue');
    expect(render('empty', false)).toContain('Completeness queue is clear');
    expect(render('unauthorized', false)).toContain('not authorised');
    expect(render('validation', true)).toContain('message: This field is required.');
    expect(render('stale', true)).toContain('changed on the server');
  });
});

const render = (
  status: React.ComponentProps<typeof CompletenessWorkbenchView>['status'],
  canAct: boolean,
  selectedCompleteness: ApplicationCompleteness | null = completeness,
) => renderToStaticMarkup(
  <CompletenessWorkbenchView
    status={status}
    message={stateMessage(status)}
    applications={status === 'empty' ? [] : [application]}
    selectedId="app-1"
    completeness={selectedCompleteness}
    deficiencies={deficiencies}
    canAct={canAct}
    comment="Please submit the missing document."
    reasons={{ borrower_pan: 'Current PAN copy is missing.' }}
    rejectionCategory="missing_document"
    reapplyAllowed
    busyAction={null}
    onSelect={vi.fn()}
    onCommentChange={vi.fn()}
    onReasonChange={vi.fn()}
    onRejectionCategoryChange={vi.fn()}
    onReapplyAllowedChange={vi.fn()}
    onPass={vi.fn()}
    onReturn={vi.fn()}
    onReject={vi.fn()}
    onResolve={vi.fn()}
    onRetry={vi.fn()}
    onOpenApplication={vi.fn()}
    onOpenAppraisal={vi.fn()}
  />,
);

const stateMessage = (status: React.ComponentProps<typeof CompletenessWorkbenchView>['status']) => (stateMessages[status] ?? '');

const stateMessages: Partial<Record<React.ComponentProps<typeof CompletenessWorkbenchView>['status'], string>> = {
  unauthorized: 'You are not authorised to access this completeness review.',
  validation: 'message: This field is required.',
  stale: 'This application changed on the server.',
  error: 'Completeness data could not be loaded.',
};

const application: StaffApplication = {
  loan_application_id: 'app-1',
  application_reference_number: null,
  member: {
    member_id: 'member-1',
    display_name: 'API Borrower One',
    member_type: 'individual_farmer',
    folio_number: 'FOL-100',
    kyc_status: 'verified',
  },
  application_date: '2026-07-10',
  required_loan_amount: '250000.00',
  declared_purpose: 'Crop production',
  purpose_category: 'crop_production',
  application_status: 'submitted',
  current_stage: 'initial_loan_request',
  completeness_status: 'not_started',
};

const completeness: ApplicationCompleteness = {
  loan_application_id: 'app-1',
  application_reference_number: null,
  application_status: 'submitted',
  current_stage: 'initial_loan_request',
  completeness_status: 'not_started',
  member: application.member,
  nominee: null,
  nominee_selection_status: 'valid',
  required_checklist_items: [{
    document_type: 'borrower_pan',
    submission_status: 'missing',
    verification_status: 'pending',
    complete: false,
    reason_code: 'missing_metadata',
  }],
  blocking_document_types: ['borrower_pan'],
  can_generate_reference: false,
};

const deficiencies: ApplicationDeficiency[] = [
  {
    deficiency_id: 'def-open',
    item_code: 'borrower_pan',
    description: 'Current PAN copy is missing.',
    resolution_status: 'open',
  },
  {
    deficiency_id: 'def-resolved',
    item_code: 'borrower_pan',
    description: 'Earlier PAN copy was unclear.',
    resolution_status: 'resolved',
    resolution_notes: 'Verified replacement from borrower.',
  },
];
