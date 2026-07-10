import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as applicationIntakeApi from '../../services/applicationIntakeApi';
import ApplicationDetail, { ApplicationDetailView } from './ApplicationDetail';
import { loadApplicationDetail, type ApplicationDetailData } from './applicationDetailLoader';
import type { ApplicationDeficiency, ApplicationDocumentChecklistItem, StaffApplication } from '../../services/applicationIntakeApi';

describe('ApplicationDetail API-backed rendering', () => {
  afterEach(() => vi.restoreAllMocks());

  it('loads detail, checklist, and deficiencies through the production HTTP service seam', async () => {
    vi.spyOn(applicationIntakeApi, 'fetchApplicationDetail').mockResolvedValueOnce(application);
    vi.spyOn(applicationIntakeApi, 'fetchApplicationDocumentChecklist').mockResolvedValueOnce({
      loan_application_id: application.loan_application_id,
      items: [],
    });
    vi.spyOn(applicationIntakeApi, 'fetchApplicationDeficiencies').mockResolvedValueOnce({
      loan_application_id: application.loan_application_id,
      items: [],
    });

    await expect(loadApplicationDetail(application.loan_application_id)).resolves.toEqual({
      application,
      checklistItems: [],
      deficiencies: [],
      eligibility: null,
      loanLimit: null,
      appraisal: null,
    });
  });

  it('renders production loading and HTTP-service error states without synthetic application facts', async () => {
    const loading = renderToStaticMarkup(
      <ApplicationDetail applicationId="app-1" onBack={vi.fn()} onNavigateMember={vi.fn()} />,
    );
    vi.spyOn(applicationIntakeApi, 'fetchApplicationDetail').mockRejectedValueOnce(new Error('Application service unavailable.'));
    vi.spyOn(applicationIntakeApi, 'fetchApplicationDocumentChecklist').mockResolvedValueOnce({
      loan_application_id: application.loan_application_id,
      items: [],
    });
    vi.spyOn(applicationIntakeApi, 'fetchApplicationDeficiencies').mockResolvedValueOnce({
      loan_application_id: application.loan_application_id,
      items: [],
    });
    let errorMessage = '';
    try {
      await loadApplicationDetail(application.loan_application_id);
    } catch (error) {
      errorMessage = error instanceof Error ? error.message : '';
    }
    const error = renderView({ status: 'error', data: null, message: errorMessage });

    expect(loading).toContain('Loading application');
    expect(loading).not.toContain('Loading member');
    expect(loading).not.toContain('15 Apr 2026');
    expect(error).toContain('Application unavailable');
    expect(error).toContain('Application service unavailable.');
    expect(error).not.toContain('Pending Disbursement');
  });

  it('renders the submitted backend owner without fixed lifecycle or readiness facts', async () => {
    const submitted = {
      ...application,
      application_reference_number: 'LO00000035',
      assigned_owner: { user_id: 'owner-submitted', full_name: 'Maya Backend Queue Owner' },
    };
    mockApplicationDetailServices(submitted, [], []);

    const data = await loadApplicationDetail(submitted.loan_application_id);
    const html = renderView({ status: 'success', data, message: '' });

    expect(html).toContain('LO00000035');
    expect(html).toContain('Maya Backend Queue Owner');
    expect(html).not.toContain('Deputy Manager Finance');
    expect(html).not.toContain('Compliance Team');
    expect(html).not.toContain('Company Secretary');
    expect(html).not.toContain('15 Apr 2026');
    expect(html).not.toContain('20 Apr 2026');
    expect(html).not.toContain('Credit reviewed');
    expect(html).not.toContain('CS verified');
    expect(html).not.toContain('Ready for payment');
    expect(html).not.toContain('Mark Ready for Payment');
  });

  it('renders only object-shaped actions supplied by the backend', async () => {
    const draft = {
      ...application,
      application_status: 'draft',
      available_actions: [{
        action_code: 'submit',
        label: 'Submit Application',
        enabled: false,
        disabled_reason: 'Complete required application facts before submit.',
        required_permission: 'applications.loan_application.submit',
      }],
    };
    mockApplicationDetailServices(draft, [], []);

    const data = await loadApplicationDetail(draft.loan_application_id);
    const html = renderView({ status: 'success', data, message: '' });

    expect(html).toContain('Submit Application');
    expect(html).toContain('Complete required application facts before submit.');
    expect(html).not.toContain('Mark Ready for Payment');
    expect(html).not.toContain('Initiate Disbursement');
  });

  it('renders a conflicting later-stage backend owner and neutral disbursement state', async () => {
    const laterStage = {
      ...application,
      application_reference_number: 'LO00000087',
      application_status: 'documentation_in_progress',
      current_stage: 'documentation',
      assigned_owner: { user_id: 'owner-later', full_name: 'Arjun Backend Custodian' },
      available_actions: [],
    };
    mockApplicationDetailServices(laterStage, [
      {
        document_type: 'loan_application_form',
        required_flag: 'mandatory',
        submission_status: 'submitted',
        verification_status: 'verified',
        complete: true,
        reason_code: null,
        latest_application_document_id: 'document-1',
      },
    ], []);

    const data = await loadApplicationDetail(laterStage.loan_application_id);
    const html = renderView({ status: 'success', data, message: '', activeTab: 9 });

    expect(html).toContain('Arjun Backend Custodian');
    expect(html).toContain('Stage history unavailable');
    expect(html).toContain('Current backend stage:');
    expect(html).toContain('No backend disbursement facts are available');
    expect(html).not.toContain('Compliance Team');
    expect(html).not.toContain('Company Secretary');
    expect(html).not.toContain('Senior Manager');
    expect(html).not.toContain('Chief Financial Controller');
    expect(html).not.toContain('Accounts');
    expect(html).not.toContain('Ready for payment');
    expect(html).not.toContain('Mark Ready for Payment');
    expect(html).not.toContain('SAP code confirmed');
  });

  it('preserves selected nominee metadata through the HTTP rendering seam without sensitive controls', async () => {
    const withNominee = {
      ...application,
      nominee: {
        nominee_id: 'nominee-1',
        nominee_name: 'API Nominee',
        age_at_application: 42,
        minor_flag: false,
        kyc_status: 'verified',
        relationship_to_borrower: 'Spouse',
        signature_required_flag: true,
      },
    };
    mockApplicationDetailServices(withNominee, [], []);

    const data = await loadApplicationDetail(withNominee.loan_application_id);
    const html = renderView({ status: 'success', data, message: '', activeTab: 3 });

    expect(html).toContain('nominee-1');
    expect(html).toContain('API Nominee');
    expect(html).toContain('42');
    expect(html).toContain('Adult');
    expect(html).toContain('Verified');
    expect(html).toContain('Spouse');
    expect(html).toContain('Required');
    expect(html).not.toContain('Nominee PAN');
    expect(html).not.toContain('Nominee Aadhaar');
    expect(html).not.toContain('token');
    expect(html).not.toContain('hash');
    expect(html).not.toContain('Reveal');
  });

  it('preserves rejection-note metadata through the HTTP rendering seam', async () => {
    const withRejectionNote = {
      ...application,
      rejection_note: {
        rejection_note_id: 'note-1',
        note_status: 'draft',
        rejection_stage: 'credit_assessment',
        rejection_reason_category: 'eligibility',
        reapply_allowed_flag: true,
        prepared_by_user_id: 'user-1',
        approved_by_user_id: null,
        communication_mode: 'email',
        communication_id: null,
        sent_by_user_id: null,
        sent_at: null,
        created_at: '2026-07-10T01:57:23Z',
        updated_at: '2026-07-10T01:57:23Z',
        updated_by_user_id: 'user-1',
      },
    };
    mockApplicationDetailServices(withRejectionNote, [], []);

    const data = await loadApplicationDetail(withRejectionNote.loan_application_id);
    const html = renderView({ status: 'success', data, message: '' });

    expect(html).toContain('Rejection Note');
    expect(html).toContain('Draft');
    expect(html).toContain('credit assessment');
    expect(html).toContain('eligibility');
    expect(html).toContain('email');
    expect(html).not.toContain('Borrower does not meet active member criteria.');
  });

  it('renders neutral empty nominee and witness states through the HTTP rendering seam', async () => {
    mockApplicationDetailServices(application, [], []);
    const data = await loadApplicationDetail(application.loan_application_id);
    const nomineeHtml = renderView({ status: 'success', data, message: '', activeTab: 3 });
    const witnessHtml = renderView({ status: 'success', data, message: '', activeTab: 4 });

    expect(nomineeHtml).toContain('No API-backed nominee details are available');
    expect(witnessHtml).toContain('No API-backed witness details are available');
    expect(`${nomineeHtml}${witnessHtml}`).not.toContain('Sudha Patil');
    expect(`${nomineeHtml}${witnessHtml}`).not.toContain('Rajan Marathe');
    expect(`${nomineeHtml}${witnessHtml}`).not.toContain('Sunanda Patil');
  });

  it('renders the stored credit summary and workbench link', () => {
    const eligibility: ApplicationDetailData['eligibility'] = { eligibility_assessment_id: 'eligibility-1', loan_application_id: 'app-1', member_active_check: 'pass', default_check: 'no_default', document_check: 'complete', terms_acceptance_check: 'accepted', purpose_check: 'agriculture_aligned', nominee_check: 'valid', overall_result: 'eligible', assessment_notes: 'Stored detail explanation.', assessed_by_user_id: 'user-1', assessed_at: '2026-07-10T10:00:00Z' };
    const loanLimit: ApplicationDetailData['loanLimit'] = { loan_limit_assessment_id: 'limit-1', loan_application_id: 'app-1', member_id: 'member-1', shareholding_id: 'share-1', number_of_shares: 100, valuation_per_share: '2500.00', share_limit_percentage: '10.0000', per_share_cap_amount: '250.00', shareholding_based_limit_amount: '250000.00', land_area_acres: '12.50', scale_of_finance_per_acre_amount: '30000.00', land_based_limit_amount: '375000.00', final_eligible_loan_amount: '250000.00', requested_amount: '250000.00', amount_within_limit_flag: true, exception_required_flag: false, calculation_rule_version: 'board-policy-2026', configuration_source: { type: 'loan_policy_config', loan_policy_config_id: 'policy-1', policy_name: 'Board policy', board_approval_reference: 'BR-01' }, warnings: [], calculated_by_user_id: 'user-1', calculated_at: '2026-07-10T10:05:00Z' };
    const html = renderView({ status: 'success', message: '', activeTab: 5, data: { application, checklistItems: [], deficiencies: [], eligibility, loanLimit, appraisal: null }, onNavigateAppraisal: vi.fn() });
    expect(html).toContain('Stored detail explanation.'); expect(html).toContain('board-policy-2026'); expect(html).toContain('Open Appraisal Workbench');
  });
});

const renderView = ({
  status,
  data,
  message,
  activeTab = 0,
  onNavigateAppraisal,
}: {
  status: 'loading' | 'success' | 'error';
  data: ApplicationDetailData | null;
  message: string;
  activeTab?: number;
  onNavigateAppraisal?: (applicationId: string) => void;
}) => renderToStaticMarkup(
  <ApplicationDetailView
    applicationId="app-1"
    onBack={vi.fn()}
    onNavigateMember={vi.fn()}
    onNavigateAppraisal={onNavigateAppraisal}
    status={status}
    message={message}
    data={data}
    activeTab={activeTab}
    onTabChange={vi.fn()}
    onAction={vi.fn()}
  />,
);

const mockApplicationDetailServices = (
  detail: StaffApplication,
  checklistItems: ApplicationDocumentChecklistItem[],
  deficiencies: ApplicationDeficiency[],
) => {
  vi.spyOn(applicationIntakeApi, 'fetchApplicationDetail').mockResolvedValueOnce(detail);
  vi.spyOn(applicationIntakeApi, 'fetchApplicationDocumentChecklist').mockResolvedValueOnce({
    loan_application_id: detail.loan_application_id,
    items: checklistItems,
  });
  vi.spyOn(applicationIntakeApi, 'fetchApplicationDeficiencies').mockResolvedValueOnce({
    loan_application_id: detail.loan_application_id,
    items: deficiencies,
  });
};

const application: StaffApplication = {
  loan_application_id: 'app-1',
  application_reference_number: null,
  member: {
    member_id: 'member-1',
    display_name: 'Ramesh Patil',
    member_type: 'individual_farmer',
    folio_number: 'FOL-005A',
    membership_status: 'active',
    kyc_status: 'verified',
  },
  application_date: '2026-07-10',
  required_loan_amount: '250000.00',
  requested_tenure_months: 12,
  declared_purpose: 'Crop production',
  purpose_category: 'crop_production',
  application_status: 'submitted',
  current_stage: 'initial_loan_request',
  completeness_status: 'not_started',
  assigned_owner: { user_id: 'owner-1', full_name: 'Deputy Manager Finance' },
  submitted_at: '2026-07-10T01:57:23Z',
  rejection_note: null,
};
