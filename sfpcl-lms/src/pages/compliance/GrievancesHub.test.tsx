// @vitest-environment jsdom
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchGrievances,
  resolveGrievance,
  type GrievanceProjection,
} from '../../services/recoveryApi';
import GrievancesHub from './GrievancesHub';
import grievancesSource from './GrievancesHub.tsx?raw';

const currentUser = {
  id: 'company-secretary-011pe',
  role: 'company_secretary',
  roleCodes: ['company_secretary'],
  permissions: ['compliance.grievance.read', 'compliance.grievance.resolve'],
};

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({ currentUser }),
}));

vi.mock('../../services/recoveryApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/recoveryApi')>(),
  fetchGrievances: vi.fn(),
  resolveGrievance: vi.fn(),
}));

const openGrievance: GrievanceProjection = {
  grievance_id: 'grievance-1',
  grievance_reference: 'GRV-2026-001',
  member_id: 'member-1',
  loan_account_id: 'loan-1',
  loan_application_id: null,
  default_case_id: null,
  recovery_action_id: null,
  grievance_category: 'recovery_conduct_issue',
  subject: 'Recovery conduct complaint',
  description: 'Borrower disputes the conduct of a recovery visit.',
  received_date: '2026-07-20',
  received_channel: 'phone',
  assigned_to_user_id: currentUser.id,
  resolution_due_date: '2026-07-24',
  status: 'open',
  tat_days: 4,
  days_overdue: 1,
  is_overdue: true,
  resolution_summary: '',
  closed_at: null,
  borrower_informed: false,
  borrower_acknowledged: false,
  supporting_document_ids: [],
  resolution_document_id: null,
  internal_notes: '',
  borrower_acknowledgement: '',
  escalation_count: 0,
  notice_communication_id: null,
  notice_delivery_status: null,
  history: [],
  available_actions: ['resolve'],
};

const closedGrievance: GrievanceProjection = {
  ...openGrievance,
  grievance_id: 'grievance-closed',
  grievance_reference: 'GRV-2026-CLOSED',
  subject: 'Closed complaint',
  status: 'closed',
  is_overdue: false,
  days_overdue: 0,
  resolution_summary: 'Complaint closed after acknowledgement.',
  closed_at: '2026-07-24T11:00:00Z',
  borrower_informed: true,
  borrower_acknowledged: true,
  available_actions: [],
};

beforeEach(() => {
  vi.mocked(fetchGrievances).mockResolvedValue({
    items: [openGrievance, closedGrievance],
    totalCount: 2,
    totalPages: 1,
    pageSize: 100,
  });
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});

describe('011PE grievance register owner wiring', () => {
  it('renders canonical grievance facts and removes the owned mock surface', async () => {
    render(<GrievancesHub />);

    expect(screen.getByText('Loading grievances…')).toBeTruthy();
    expect(await screen.findByText('GRV-2026-001')).toBeTruthy();
    expect(screen.getByText('Recovery conduct complaint')).toBeTruthy();
    expect(screen.getByText('Recovery-related complaints require CS review.')).toBeTruthy();
    expect(screen.queryByText('GRV-2026-CLOSED')).toBeNull();
    await userEvent.click(screen.getByRole('button', { name: 'Closed' }));
    expect(screen.getByText('GRV-2026-CLOSED')).toBeTruthy();
    expect(fetchGrievances).toHaveBeenCalledTimes(1);
    expect(grievancesSource).not.toMatch(/mockData|const grievances\s*=/);
  });

  it('requires a projected status and reason, resolves, then refetches canonical state', async () => {
    const resolved = {
      ...openGrievance,
      status: 'resolved',
      is_overdue: false,
      days_overdue: 0,
      resolution_summary: 'Recovery conduct reviewed with the borrower.',
      closed_at: '2026-07-25T11:00:00Z',
      borrower_informed: true,
      available_actions: [],
    } satisfies GrievanceProjection;
    vi.mocked(fetchGrievances)
      .mockResolvedValueOnce({
        items: [openGrievance],
        totalCount: 1,
        totalPages: 1,
        pageSize: 100,
      })
      .mockResolvedValueOnce({
        items: [resolved],
        totalCount: 1,
        totalPages: 1,
        pageSize: 100,
      });
    vi.mocked(resolveGrievance).mockResolvedValue(resolved);

    render(<GrievancesHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'Resolve GRV-2026-001' }));
    await userEvent.click(screen.getByRole('button', { name: 'Submit Resolution' }));
    expect(screen.getByText('Resolution status is required.')).toBeTruthy();
    expect(screen.getByText('Resolution reason is required.')).toBeTruthy();

    await userEvent.selectOptions(screen.getByLabelText('Resolution status'), 'resolved');
    await userEvent.type(
      screen.getByLabelText('Resolution reason'),
      'Recovery conduct reviewed with the borrower.',
    );
    await userEvent.click(screen.getByRole('button', { name: 'Submit Resolution' }));

    expect(resolveGrievance).toHaveBeenCalledWith('grievance-1', {
      status: 'resolved',
      reason: 'Recovery conduct reviewed with the borrower.',
      idempotency_key: expect.stringMatching(/^grievance-resolution-grievance-1-/),
    });
    expect(fetchGrievances).toHaveBeenCalledTimes(2);
    expect(await screen.findByText('Grievance resolved from canonical backend state.')).toBeTruthy();
    expect(screen.getByText('Recovery conduct reviewed with the borrower.')).toBeTruthy();
  });

  it('renders empty, unauthorized, general error, and blocked action states', async () => {
    vi.mocked(fetchGrievances).mockResolvedValueOnce({
      items: [],
      totalCount: 0,
      totalPages: 1,
      pageSize: 100,
    });
    const empty = render(<GrievancesHub />);
    expect(await screen.findByText('No grievances found in this view.')).toBeTruthy();
    empty.unmount();

    vi.mocked(fetchGrievances).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Grievance scope denied.', 403),
    );
    const denied = render(<GrievancesHub />);
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.getByText('Grievance scope denied.')).toBeTruthy();
    denied.unmount();

    vi.mocked(fetchGrievances).mockRejectedValueOnce(new Error('Grievance service unavailable.'));
    const failed = render(<GrievancesHub />);
    expect(await screen.findByText('Grievance Register Unavailable')).toBeTruthy();
    failed.unmount();

    vi.mocked(fetchGrievances).mockResolvedValueOnce({
      items: [{ ...openGrievance, available_actions: [] }],
      totalCount: 1,
      totalPages: 1,
      pageSize: 100,
    });
    render(<GrievancesHub />);
    expect(await screen.findByText('GRV-2026-001')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Resolve GRV-2026-001' })).toBeNull();
    expect(screen.getByText('No resolution action is available for your role or this status.')).toBeTruthy();
  });
});
