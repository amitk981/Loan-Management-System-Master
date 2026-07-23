// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import { fetchAuditorEpic011 } from '../../services/auditorApi';
import AuditorEpic011View from './AuditorEpic011View';

vi.mock('../../services/auditorApi', () => ({
  fetchAuditorEpic011: vi.fn(),
}));

const empty = {
  summary: {
    default_cases: 0,
    closures: 0,
    compliance_items: 0,
    grievances: 0,
  },
  default_cases: [],
  closures: [],
  compliance_items: [],
  grievances: [],
};

const populated = {
  summary: {
    default_cases: 1,
    closures: 1,
    compliance_items: 1,
    grievances: 1,
  },
  default_cases: [
    {
      default_case_id: 'default-1',
      loan_account_number: 'LN-AUD-001',
      borrower_name: 'Masked Member',
      default_case_status: 'recovery_in_progress',
      total_outstanding: '125000.00',
      audit_references: ['audit-default-1'],
      workflow_references: ['workflow-default-1'],
    },
  ],
  closures: [
    {
      loan_closure_id: 'closure-1',
      loan_account_number: 'LN-AUD-002',
      borrower_name: 'Closed Member',
      closure_stage: 'financially_closed',
      closed_at: '2026-07-22T10:00:00Z',
      requirements: [{ requirement_type: 'noc', requirement_status: 'completed' }],
      audit_references: ['audit-closure-1'],
      workflow_references: ['workflow-closure-1'],
    },
  ],
  compliance_items: [
    {
      record_type: 'task',
      record_id: 'task-1',
      details: {
        control_code: 'RECOVERY_CONDUCT',
        task_period: '2026-Q2',
        task_status: 'evidence_submitted',
        compliance_evidence_id: 'evidence-1',
      },
      audit_references: ['audit-task-1'],
      workflow_references: [],
    },
  ],
  grievances: [
    {
      grievance_id: 'grievance-1',
      grievance_reference: 'GRV-2026-AUD-001',
      grievance_category: 'recovery_conduct_issue',
      status: 'open',
      description: 'Recovery interaction requires review.',
      audit_references: ['audit-grievance-1'],
      workflow_references: [],
    },
  ],
};

describe('011O auditor read-only view', () => {
  beforeEach(() => {
    vi.mocked(fetchAuditorEpic011).mockResolvedValue(populated);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  it('filters and opens populated Epic 011 records without mutation controls', async () => {
    render(<AuditorEpic011View />);

    expect(await screen.findByText('Epic 011 Audit View')).toBeTruthy();
    expect(screen.getByText('LN-AUD-001')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /approve|review evidence|update|close|issue|return|archive/i })).toBeNull();

    await userEvent.selectOptions(screen.getByLabelText('Record family'), 'compliance');
    expect(screen.getByText('RECOVERY_CONDUCT')).toBeTruthy();
    expect(screen.queryByText('LN-AUD-001')).toBeNull();

    await userEvent.click(screen.getByRole('button', { name: 'View task-1' }));
    expect(screen.getByText('Immutable references')).toBeTruthy();
    expect(screen.getByText('audit-task-1')).toBeTruthy();
    expect(screen.getByRole('link', { name: 'Evidence metadata evidence-1' })).toBeTruthy();
  });

  it('shows the declared empty state', async () => {
    vi.mocked(fetchAuditorEpic011).mockResolvedValue(empty);
    render(<AuditorEpic011View />);
    expect(await screen.findByText('No Epic 011 records match this view.')).toBeTruthy();
  });

  it('shows the declared unauthorised state for a denied read', async () => {
    vi.mocked(fetchAuditorEpic011).mockRejectedValue({ status: 403 });
    render(<AuditorEpic011View />);
    expect(await screen.findByText('Auditor access is not authorised.')).toBeTruthy();
  });

  it('shows a retryable error state', async () => {
    vi.mocked(fetchAuditorEpic011)
      .mockRejectedValueOnce({ status: 500 })
      .mockResolvedValueOnce(empty);
    render(<AuditorEpic011View />);
    expect(await screen.findByText('Epic 011 audit records could not be loaded.')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Retry' }));
    await waitFor(() => expect(fetchAuditorEpic011).toHaveBeenCalledTimes(2));
    expect(await screen.findByText('No Epic 011 records match this view.')).toBeTruthy();
  });
});
