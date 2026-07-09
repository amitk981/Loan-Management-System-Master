import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { describe, expect, it, vi } from 'vitest';
import { ApplicationListView } from './ApplicationList';
import type { LoanRequestRegisterRow, Pagination, StaffApplication } from '../../services/applicationIntakeApi';

describe('ApplicationListView', () => {
  it('renders API-backed application and register rows without mock-only rows', () => {
    const html = renderToStaticMarkup(
      <ApplicationListView
        status="success"
        message=""
        applications={[application]}
        registerRows={[registerRow]}
        pagination={pagination}
        search=""
        statusFilter="all"
        canCreate
        onSearchChange={vi.fn()}
        onStatusFilterChange={vi.fn()}
        onNew={vi.fn()}
        onSelect={vi.fn()}
      />,
    );

    expect(html).toContain('Ramesh Patil');
    expect(html).toContain('Incomplete - Returned to Applicant');
    expect(html).toContain('LO00000001');
    expect(html).toContain('Loan Request Register');
    expect(html).not.toContain('Ganesh Thorat');
    expect(html).not.toContain('EX-2026-015');
  });

  it('renders loading, empty, and error states with existing table structure', () => {
    const loading = renderState('loading');
    const empty = renderState('success');
    const error = renderState('error', 'You do not have access to this loan application.');

    expect(loading).toContain('Loading applications');
    expect(empty).toContain('No applications match your filters.');
    expect(error).toContain('You do not have access to this loan application.');
  });
});

const pagination: Pagination = {
  page: 1,
  page_size: 20,
  total_count: 1,
  total_pages: 1,
  has_next: false,
  has_previous: false,
};

const application: StaffApplication = {
  loan_application_id: 'app-1',
  application_reference_number: null,
  member: {
    member_id: 'member-1',
    display_name: 'Ramesh Patil',
    member_type: 'individual_farmer',
    folio_number: 'FOL-005A',
  },
  application_date: '2026-07-10',
  required_loan_amount: '250000.00',
  purpose_category: 'crop_production',
  application_status: 'incomplete_returned',
  current_stage: 'initial_loan_request',
  completeness_status: 'incomplete',
  assigned_owner: { user_id: 'user-1', full_name: 'Deputy Manager Finance' },
  tat: { due_at: null, status: 'blocked' },
};

const registerRow: LoanRequestRegisterRow = {
  loan_request_register_entry_id: 'register-1',
  loan_application_id: 'app-2',
  application_reference_number: 'LO00000001',
  borrower_name: 'Ramesh Patil',
  folio_number: 'FOL-005A',
  member_type: 'individual_farmer',
  requested_amount: '250000.00',
  register_status: 'reference_generated',
  current_stage: 'credit_assessment',
  current_owner_role: 'credit_manager',
};

const renderState = (
  status: React.ComponentProps<typeof ApplicationListView>['status'],
  message = '',
) => renderToStaticMarkup(
  <ApplicationListView
    status={status}
    message={message}
    applications={[]}
    registerRows={[]}
    pagination={{ ...pagination, total_count: 0 }}
    search=""
    statusFilter="all"
    canCreate
    onSearchChange={vi.fn()}
    onStatusFilterChange={vi.fn()}
    onNew={vi.fn()}
    onSelect={vi.fn()}
  />,
);
