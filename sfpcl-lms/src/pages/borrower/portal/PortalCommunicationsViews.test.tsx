// @vitest-environment jsdom
import React from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import type { PortalClosure, PortalGrievance, PortalNotice, PortalNotification } from '../../../services/portalApi';
import { MP20ClosureView } from './loans/MP20_ClosureNOC';
import { MP19NoticesView } from './notices/MP19_NoticesLetters';
import { MP23NotificationsView } from './notifications/MP23_Notifications';
import { MP24SupportView } from './support/MP24_SupportGrievance';
import mp19Source from './notices/MP19_NoticesLetters.tsx?raw';
import mp20Source from './loans/MP20_ClosureNOC.tsx?raw';
import mp23Source from './notifications/MP23_Notifications.tsx?raw';
import mp24Source from './support/MP24_SupportGrievance.tsx?raw';

afterEach(cleanup);

describe('MP19-MP24 member communication views', () => {
  it('renders MP19 loading, empty, error, real notice, and download behavior', async () => {
    const loading = render(<MP19NoticesView notices={[]} loading error={null} downloadingId={null} onDownload={vi.fn()} />);
    expect(screen.getByText('Loading notices and letters…')).toBeTruthy();
    loading.unmount();
    const empty = render(<MP19NoticesView notices={[]} loading={false} error={null} downloadingId={null} onDownload={vi.fn()} />);
    expect(screen.getByText('No borrower notices or letters are available yet.')).toBeTruthy();
    empty.unmount();
    const download = vi.fn();
    render(<MP19NoticesView notices={[notice]} loading={false} error="Notice access denied." downloadingId={null} onDownload={download} />);
    expect(screen.getByText('Notice access denied.')).toBeTruthy();
    expect(screen.getByText('NOC issued')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Download' }));
    expect(download).toHaveBeenCalledWith(notice);
  });

  it('renders MP20 own closure statuses and only enables an issued NOC', async () => {
    const download = vi.fn();
    render(<MP20ClosureView closures={[closure]} loading={false} error={null} onDownload={download} />);
    expect(screen.getByText('LN-PORTAL-CLOSED')).toBeTruthy();
    expect(screen.getByText('Full repayment is confirmed.')).toBeTruthy();
    expect(screen.getByText('CDSL unpledge')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Download NOC' }));
    expect(download).toHaveBeenCalledWith(closure);
  });

  it('renders MP23 direct alerts and invokes mark-read only for unread records', async () => {
    const markRead = vi.fn();
    render(<MP23NotificationsView notifications={[notification]} loading={false} error={null} onMarkRead={markRead} />);
    expect(screen.getByText('Your grievance has a response')).toBeTruthy();
    expect(screen.getByText('Unread')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: /mark as read/i }));
    expect(markRead).toHaveBeenCalledWith(notification);
  });

  it('renders all MP24 guide sections, validates required fields, submits, and shows resolution', async () => {
    const submit = vi.fn();
    const select = vi.fn();
    const { rerender } = render(
      <MP24SupportView grievances={[]} loading={false} error={null} success={null} submitting={false} onSubmit={submit} />
    );
    expect(screen.getByText('Who Can Apply')).toBeTruthy();
    expect(screen.getByText('Support & Grievances')).toBeTruthy();
    expect(screen.getByText('No grievances have been submitted.')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', { name: 'Submit Grievance' }));
    expect(screen.getByText('Choose a category and enter both a subject and message.')).toBeTruthy();
    expect(submit).not.toHaveBeenCalled();

    await userEvent.selectOptions(screen.getByLabelText(/Category/), 'other');
    await userEvent.type(screen.getByLabelText(/Subject/), 'Statement query');
    await userEvent.type(screen.getByLabelText(/Message/), 'Please explain this statement entry.');
    await userEvent.click(screen.getByRole('button', { name: 'Submit Grievance' }));
    expect(submit).toHaveBeenCalledWith({
      grievance_category: 'other',
      subject: 'Statement query',
      description: 'Please explain this statement entry.',
    });

    rerender(<MP24SupportView grievances={[grievance]} loading={false} error={null} success={grievance} submitting={false} onSubmit={submit} onSelect={select} />);
    expect(screen.getAllByText(/GRV-PORTAL-001/)).toHaveLength(2);
    expect(screen.getByText('The statement entry is a verified repayment.')).toBeTruthy();
    expect(screen.getByText('Resolved')).toBeTruthy();
    await userEvent.click(screen.getByText('Statement query'));
    expect(select).toHaveBeenCalledWith(grievance);
  });

  it('contains no production mock communication fixtures', () => {
    const source = [mp19Source, mp20Source, mp23Source, mp24Source].join('\n');
    expect(source).not.toContain('mockData');
    expect(source).not.toContain('LO00000042');
    expect(source).not.toContain('UTR2024');
    expect(source).not.toContain('GR-001');
    expect(source).not.toContain('1800 123 4567');
  });
});

const notice: PortalNotice = {
  notice_id: 'notice-1',
  notice_type: 'noc',
  title: 'NOC issued',
  message: 'Your authorised NOC is ready.',
  status: 'sent',
  issued_at: '2026-07-23T10:00:00Z',
  related_entity_type: 'noc',
  related_entity_id: 'noc-1',
  related_loan_account_id: 'loan-1',
  related_reference: 'LN-PORTAL-CLOSED',
  download_url: '/api/v1/portal/notices/notice-1/download/',
};

const closure: PortalClosure = {
  loan_account_id: 'loan-1',
  loan_account_number: 'LN-PORTAL-CLOSED',
  full_repayment_status: 'confirmed',
  closure_review_status: 'complete',
  closed_at: '2026-07-22T10:00:00Z',
  noc_status: 'issued',
  noc_download_url: '/api/v1/portal/notices/notice-1/download/',
  security_return_status: 'completed',
  cdsl_unpledge_status: 'not_applicable',
  security_items: [],
};

const notification: PortalNotification = {
  notification_id: 'notification-1',
  notification_type: 'grievance_response',
  category: 'support',
  severity: 'info',
  title: 'Your grievance has a response',
  message: 'Open Support & Grievance to view it.',
  action_label: null,
  action_url: null,
  read: false,
  read_at: null,
  read_state_version: 1,
  created_at: '2026-07-23T10:00:00Z',
};

const grievance: PortalGrievance = {
  grievance_id: 'grievance-1',
  grievance_reference: 'GRV-PORTAL-001',
  grievance_category: 'other',
  subject: 'Statement query',
  description: 'Please explain this statement entry.',
  loan_account_id: null,
  loan_application_id: null,
  received_date: '2026-07-22',
  resolution_due_date: '2026-07-29',
  status: 'resolved',
  is_overdue: false,
  resolution_summary: 'The statement entry is a verified repayment.',
  closed_at: '2026-07-23T10:00:00Z',
  borrower_informed: true,
  borrower_acknowledged: false,
};
