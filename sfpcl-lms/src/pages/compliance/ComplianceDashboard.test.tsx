// @vitest-environment jsdom
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchComplianceDashboard,
  reviewSection186Tracker,
  type ComplianceDashboardProjection,
} from '../../services/recoveryApi';
import ComplianceDashboard from './ComplianceDashboard';
import dashboardSource from './ComplianceDashboard.tsx?raw';

const currentUser = {
  id: 'reviewer-011pd',
  role: 'cfo',
  roleCodes: ['cfo'],
  permissions: [
    'compliance.control.read',
    'compliance.task.read',
    'compliance.evidence.review',
    'compliance.section186.read',
    'compliance.nbfc_test.read',
    'reports.compliance.read',
  ],
};

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({ currentUser }),
}));

vi.mock('../../services/recoveryApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/recoveryApi')>(),
  fetchComplianceDashboard: vi.fn(),
  reviewComplianceEvidence: vi.fn(),
  reviewSection186Tracker: vi.fn(),
  reviewNbfcPrincipalTest: vi.fn(),
}));

const projection: ComplianceDashboardProjection = {
  controls: [{
    compliance_control_id: 'control-1',
    control_code: 'MEMBER_ONLY_LENDING',
    control_name: 'Member-only lending control',
    control_area: 'producer_company',
    legal_basis: 'Producer Company member lending requirement.',
    control_type: 'preventive',
    frequency: 'ongoing',
    owner_role_code: 'company_secretary',
    owner_user_id: 'owner-1',
    reviewer_user_id: currentUser.id,
    first_due_date: '2026-04-01',
    evidence_required: 'Loan and membership register.',
    risk_if_missed: 'Non-member lending.',
    status: 'active',
    available_actions: [],
  }],
  tasks: [{
    compliance_task_id: 'task-1',
    compliance_control_id: 'control-1',
    control_code: 'MEMBER_ONLY_LENDING',
    task_period: 'ongoing',
    due_date: '2026-07-31',
    assigned_to_user_id: 'owner-1',
    reviewer_user_id: currentUser.id,
    task_status: 'evidence_submitted',
    remarks: 'Register reconciled.',
    closed_at: null,
    compliance_evidence_id: 'evidence-1',
    available_actions: ['review_evidence'],
  }],
  section186: [{
    section_186_tracker_id: 'section-1',
    financial_year: 'FY2026-27',
    quarter: 'Q1',
    paid_up_capital_amount: '10000000.00',
    free_reserves_amount: '5000000.00',
    securities_premium_amount: '2000000.00',
    limit_60_percent_basis_amount: '10200000.00',
    limit_100_percent_basis_amount: '7000000.00',
    applicable_limit_amount: '10200000.00',
    total_loans_exposure_amount: '8000000.00',
    headroom_amount: '2200000.00',
    within_limit_flag: true,
    special_resolution_required_flag: false,
    compliance_task_id: 'task-section',
    compliance_evidence_id: 'evidence-section',
    review_status: 'pending',
    review_comments: '',
    presented_to_board_flag: false,
    available_actions: ['review'],
  }],
  nbfcTests: [{
    nbfc_principal_test_id: 'nbfc-1',
    financial_year: 'FY2026-27',
    quarter: 'Q1',
    financial_assets_amount: '20000000.00',
    total_assets_amount: '60000000.00',
    financial_asset_ratio: '33.3333',
    financial_income_amount: '1000000.00',
    gross_income_amount: '8000000.00',
    financial_income_ratio: '12.5000',
    early_warning_threshold_ratio: '40.0000',
    registration_triggered_flag: false,
    one_ratio_above_statutory_flag: false,
    early_warning_flag: false,
    presented_to_board_flag: false,
    compliance_task_id: 'task-nbfc',
    compliance_evidence_id: 'evidence-nbfc',
    review_status: 'pending',
    review_comments: '',
    available_actions: ['review'],
  }],
  kycReviews: [{
    kyc_review_id: 'kyc-1',
    member_id: 'member-1',
    member_name: 'Seeded Re-KYC Member',
    member_type: 'individual',
    member_status: 'active',
    kyc_status: 'verified',
    risk_rating: 'medium',
    due_date: '2026-07-20',
    days_overdue: 5,
    status: 'overdue',
    assigned_to_user_id: 'owner-1',
    completeness: {
      complete: true,
      pan_status: 'verified',
      ckyc_consent_status: 'available',
    },
    available_actions: [],
  }],
  moneyLendingReviews: [{
    money_lending_law_review_id: 'money-1',
    financial_year: 'FY2026-27',
    state: 'Maharashtra',
    applicability: 'exempt',
    exemption_applicable_flag: true,
    compliance_task_id: 'task-money',
    compliance_evidence_id: 'evidence-money',
    reviewed_by_user_id: 'secretary-1',
    reviewed_at: '2026-03-15T10:00:00Z',
  }],
  stampDuty: [{
    stamp_duty_record_id: 'stamp-1',
    loan_document_id: 'document-1',
    document_type: 'loan_agreement',
    loan_application_id: 'application-1',
    application_reference_number: 'APP-STAMP-011PD',
    member_id: 'member-1',
    borrower_name: 'Seeded Stamp Member',
    stamp_paper_amount: '500.00',
    stamp_type: 'physical',
    stamp_number: 'STAMP-011PD',
    stamp_purchase_date: '2026-06-01',
    executed_date: '2026-06-02',
    status: 'adequate',
    notarisation_status: 'completed',
  }],
};

beforeEach(() => {
  currentUser.role = 'cfo';
  currentUser.roleCodes = ['cfo'];
  vi.mocked(fetchComplianceDashboard).mockResolvedValue(projection);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe('011PD compliance dashboard owner wiring', () => {
  it('renders every S62-S67 tracker from the canonical backend projection', async () => {
    render(<ComplianceDashboard />);

    expect(screen.getByText('Loading compliance trackers…')).toBeTruthy();
    expect(await screen.findByText('₹1,02,00,000.00')).toBeTruthy();
    expect(screen.getByText(/60% basis ₹1,02,00,000.00/)).toBeTruthy();
    expect(screen.getByText('₹1,00,00,000.00')).toBeTruthy();
    expect(screen.getByText(/Reserves ₹50,00,000.00/)).toBeTruthy();
    expect(screen.getByText(/Premium ₹20,00,000.00/)).toBeTruthy();
    expect(screen.getByText('33.3333%')).toBeTruthy();
    expect(screen.getByText('12.5000%')).toBeTruthy();
    expect(screen.getByText('Seeded Re-KYC Member')).toBeTruthy();
    expect(screen.getAllByText('verified').length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText('available')).toBeTruthy();
    expect(screen.getByText('FY2026-27 · Maharashtra')).toBeTruthy();
    expect(screen.getByText('APP-STAMP-011PD')).toBeTruthy();
    expect(screen.getByText('STAMP-011PD')).toBeTruthy();
    expect(screen.getByText('Member-only lending control')).toBeTruthy();
    expect(fetchComplianceDashboard).toHaveBeenCalledTimes(1);
  });

  it('is the final mock-removal owner and retains no inline compliance fixtures', () => {
    expect(dashboardSource).not.toMatch(/mockData|complianceRecords|dashboardStats|loanAccounts|members/);
    expect(dashboardSource).not.toMatch(/Adv\. R\. Kulkarni|2541667|11875000/);
  });

  it('renders empty, unauthorized, and general error states', async () => {
    vi.mocked(fetchComplianceDashboard).mockResolvedValueOnce({
      controls: [],
      tasks: [],
      section186: [],
      nbfcTests: [],
      kycReviews: [],
      moneyLendingReviews: [],
      stampDuty: [],
    });
    const empty = render(<ComplianceDashboard />);
    expect(await screen.findByText('No compliance controls are available in your scope.')).toBeTruthy();
    expect(screen.getByText('No Section 186 tracker is available.')).toBeTruthy();
    expect(screen.getByText('No stamp-duty records are available.')).toBeTruthy();
    empty.unmount();

    vi.mocked(fetchComplianceDashboard).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Compliance scope denied.', 403),
    );
    const denied = render(<ComplianceDashboard />);
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.getByText('Compliance scope denied.')).toBeTruthy();
    denied.unmount();

    vi.mocked(fetchComplianceDashboard).mockRejectedValueOnce(
      new Error('Compliance service unavailable.'),
    );
    render(<ComplianceDashboard />);
    expect(await screen.findByText('Compliance Dashboard Unavailable')).toBeTruthy();
    expect(screen.getByText('Compliance service unavailable.')).toBeTruthy();
  });
  it('validates projected reviews, refetches canonical state, and keeps auditors read-only', async () => {
    const reviewedProjection: ComplianceDashboardProjection = {
      ...projection,
      section186: [{
        ...projection.section186[0],
        review_status: 'accepted',
        review_comments: 'Quarterly source evidence reconciled.',
        available_actions: [],
      }],
    };
    vi.mocked(fetchComplianceDashboard)
      .mockResolvedValueOnce(projection)
      .mockResolvedValueOnce(reviewedProjection);
    vi.mocked(reviewSection186Tracker).mockResolvedValue(reviewedProjection.section186[0]);

    const staff = render(<ComplianceDashboard />);
    expect(await screen.findByRole('button', { name: 'Review Section 186' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Review NBFC Test' })).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Review Evidence' })).toBeTruthy();

    await userEvent.click(screen.getByRole('button', { name: 'Review Section 186' }));
    await userEvent.click(screen.getByRole('button', { name: 'Submit Review' }));
    expect(screen.getByText('Review comments are required.')).toBeTruthy();
    await userEvent.type(
      screen.getByLabelText('Review comments'),
      'Quarterly source evidence reconciled.',
    );
    await userEvent.click(screen.getByRole('button', { name: 'Submit Review' }));

    expect(reviewSection186Tracker).toHaveBeenCalledWith('section-1', {
      decision: 'accepted',
      comments: 'Quarterly source evidence reconciled.',
      presented_to_board_flag: false,
      board_document_id: null,
    });
    expect(await screen.findByText('Compliance review saved from canonical backend state.')).toBeTruthy();
    expect(fetchComplianceDashboard).toHaveBeenCalledTimes(2);
    staff.unmount();

    currentUser.role = 'auditor';
    currentUser.roleCodes = ['internal_auditor'];
    vi.mocked(fetchComplianceDashboard).mockResolvedValueOnce({
      ...projection,
      tasks: projection.tasks.map(task => ({ ...task, available_actions: [] })),
      section186: projection.section186.map(row => ({ ...row, available_actions: [] })),
      nbfcTests: projection.nbfcTests.map(row => ({ ...row, available_actions: [] })),
    });
    render(<ComplianceDashboard />);
    expect(await screen.findByText('Member-only lending control')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /review/i })).toBeNull();
  });

  it('blocks accepted statutory reviews until required Board evidence is named', async () => {
    vi.mocked(fetchComplianceDashboard).mockResolvedValueOnce({
      ...projection,
      section186: [{
        ...projection.section186[0],
        within_limit_flag: false,
        special_resolution_required_flag: true,
      }],
    });
    vi.mocked(reviewSection186Tracker).mockRejectedValueOnce(
      new AuthSessionError(
        'VALIDATION_ERROR',
        'Correct the highlighted fields.',
        400,
        { presented_to_board_flag: 'Exceeded exposure requires Board presentation.' },
      ),
    );
    render(<ComplianceDashboard />);
    await userEvent.click(await screen.findByRole('button', { name: 'Review Section 186' }));
    await userEvent.type(screen.getByLabelText('Review comments'), 'Exposure exception reviewed.');
    await userEvent.click(screen.getByRole('button', { name: 'Submit Review' }));
    expect(
      await screen.findByText('Exceeded exposure requires Board presentation.'),
    ).toBeTruthy();
    expect(reviewSection186Tracker).toHaveBeenCalledWith('section-1', {
      decision: 'accepted',
      comments: 'Exposure exception reviewed.',
      presented_to_board_flag: false,
      board_document_id: null,
    });
  });
});
