import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { RoleProvider } from '../../contexts/RoleContext';
import ApplicationDetail from './ApplicationDetail';
import type { ApplicationDeficiency, ApplicationDocumentChecklistItem, StaffApplication } from '../../services/applicationIntakeApi';

describe('ApplicationDetail API-backed rendering', () => {
  it('does not apply the old LO00000035 mock overrides to API-backed detail data', () => {
    const html = renderApplicationDetail({
      application: {
        ...application,
        application_reference_number: 'LO00000035',
        application_status: 'submitted',
        current_stage: 'initial_loan_request',
        completeness_status: 'not_started',
        assigned_owner: { user_id: 'owner-1', full_name: 'Deputy Manager Finance' },
      },
      checklistItems: [],
    });

    expect(html).toContain('LO00000035');
    expect(html).toContain('Submitted');
    expect(html).toContain('Owner:');
    expect(html).toContain('Deputy Manager Finance');
    expect(html).not.toContain('Sanctioned · Documentation Pending');
    expect(html).not.toContain('11 items pending');
    expect(html).not.toContain('Compliance Team / Company Secretary');
    expect(html).not.toContain('Rajan Marathe');
    expect(html).not.toContain('Sunanda Patil');
  });

  it('shows unavailable states instead of hardcoded nominee and witness facts', () => {
    const nomineeHtml = renderApplicationDetail({
      application,
      checklistItems: [],
      initialActiveTab: 3,
    });
    const witnessHtml = renderApplicationDetail({
      application,
      checklistItems: [],
      initialActiveTab: 4,
    });

    expect(nomineeHtml).toContain('Nominee Details');
    expect(nomineeHtml).toContain('Not available');
    expect(nomineeHtml).not.toContain('Sudha Patil');
    expect(nomineeHtml).not.toContain('FGHIJ5678K');
    expect(nomineeHtml).not.toContain('778944447789');
    expect(witnessHtml).toContain('Witness Details');
    expect(witnessHtml).toContain('No API-backed witness details are available');
    expect(witnessHtml).not.toContain('Rajan Marathe');
    expect(witnessHtml).not.toContain('Sunanda Patil');
  });

  it('renders the API nominee metadata without sensitive identity values', () => {
    const html = renderApplicationDetail({
      application: {
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
      },
      checklistItems: [],
      initialActiveTab: 3,
    });

    expect(html).toContain('API Nominee');
    expect(html).toContain('Spouse');
    expect(html).toContain('Adult');
    expect(html).toContain('Verified');
    expect(html).not.toContain('Nominee PAN');
    expect(html).not.toContain('Nominee Aadhaar');
  });

  it('renders staff rejection-note metadata returned by the detail API', () => {
    const html = renderApplicationDetail({
      application: {
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
      },
      checklistItems: [],
    });

    expect(html).toContain('Rejection Note');
    expect(html).toContain('Draft');
    expect(html).toContain('credit assessment');
    expect(html).toContain('eligibility');
    expect(html).toContain('email');
    expect(html).not.toContain('Borrower does not meet active member criteria.');
  });
});

const renderApplicationDetail = ({
  application,
  checklistItems,
  deficiencies = [],
  initialActiveTab = 0,
}: {
  application: StaffApplication;
  checklistItems: ApplicationDocumentChecklistItem[];
  deficiencies?: ApplicationDeficiency[];
  initialActiveTab?: number;
}) => renderToStaticMarkup(
  <RoleProvider>
    <ApplicationDetail
      applicationId={application.loan_application_id}
      onBack={vi.fn()}
      onNavigateMember={vi.fn()}
      initialActiveTab={initialActiveTab}
      initialData={{ application, checklistItems, deficiencies }}
    />
  </RoleProvider>,
);

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
