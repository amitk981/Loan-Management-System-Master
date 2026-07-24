// @vitest-environment jsdom
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import {
  downloadArchiveManifest,
  fetchArchiveRecords,
  type ArchiveRecordProjection,
} from '../../services/recoveryApi';
import AuditArchiveHub from './AuditArchiveHub';
import archiveSource from './AuditArchiveHub.tsx?raw';

const currentUser = {
  id: 'auditor-011pe',
  role: 'auditor',
  roleCodes: ['internal_auditor'],
  permissions: ['closure.archive.read'],
};

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({ currentUser }),
}));

vi.mock('../../services/recoveryApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/recoveryApi')>(),
  fetchArchiveRecords: vi.fn(),
  downloadArchiveManifest: vi.fn(),
}));

const archive: ArchiveRecordProjection = {
  archive_record_id: 'archive-1',
  loan_closure_id: 'closure-1',
  loan_account_id: 'loan-1',
  file_location_physical: 'Archive Room / Rack A / Box 12',
  file_location_digital: 'governed://loan-archive/manifest-25',
  retention_start_date: '2026-07-25',
  retention_until_date: '2034-07-25',
  archived_by_user_id: 'archivist-1',
  archived_by_role_code: 'company_secretary',
  archived_at: '2026-07-25T10:00:00Z',
  destruction_eligible: false,
  destruction_certificate_id: null,
  idempotency_replayed: false,
  available_actions: [],
};

beforeEach(() => {
  vi.mocked(fetchArchiveRecords).mockResolvedValue({
    items: [archive],
    totalCount: 1,
    totalPages: 1,
    pageSize: 100,
  });
  vi.mocked(downloadArchiveManifest).mockResolvedValue({
    fileName: 'archive-manifest-archive-1.json',
    content: new Blob([JSON.stringify(archive)], { type: 'application/json' }),
  });
  vi.stubGlobal('URL', {
    createObjectURL: vi.fn(() => 'blob:archive-manifest'),
    revokeObjectURL: vi.fn(),
  });
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => undefined);
});

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
  vi.unstubAllGlobals();
});

describe('011PE audit archive owner wiring', () => {
  it('renders canonical archive records as a read-only surface without owned fixtures', async () => {
    render(<AuditArchiveHub />);

    expect(screen.getByText('Loading archive records…')).toBeTruthy();
    expect(await screen.findByText('archive-1')).toBeTruthy();
    expect(screen.getByText('Archive Room / Rack A / Box 12')).toBeTruthy();
    expect(screen.getByText('25/07/2034')).toBeTruthy();
    expect(screen.getByText('Read-only access — archive records cannot be edited.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /archive file|record destruction|delete|edit/i })).toBeNull();
    expect(archiveSource).not.toMatch(/mockData|auditEvents|Radha Kisan Org|PF-2025-025/);
  });

  it('downloads only after the governed audited detail read and supports canonical search refetch', async () => {
    render(<AuditArchiveHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'Download manifest archive-1' }));

    expect(downloadArchiveManifest).toHaveBeenCalledWith(archive);
    expect(await screen.findByText('Archive manifest downloaded through the audited read endpoint.')).toBeTruthy();

    await userEvent.type(screen.getByLabelText('Search archive records'), 'loan-1');
    await userEvent.click(screen.getByRole('button', { name: 'Search' }));
    expect(fetchArchiveRecords).toHaveBeenLastCalledWith('loan-1');
  });

  it('renders empty, unauthorized, general error, and download failure states', async () => {
    vi.mocked(fetchArchiveRecords).mockResolvedValueOnce({
      items: [],
      totalCount: 0,
      totalPages: 1,
      pageSize: 100,
    });
    const empty = render(<AuditArchiveHub />);
    expect(await screen.findByText('No archive records are available in your scope.')).toBeTruthy();
    empty.unmount();

    vi.mocked(fetchArchiveRecords).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Archive scope denied.', 403),
    );
    const denied = render(<AuditArchiveHub />);
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.getByText('Archive scope denied.')).toBeTruthy();
    denied.unmount();

    vi.mocked(fetchArchiveRecords).mockRejectedValueOnce(new Error('Archive service unavailable.'));
    const failed = render(<AuditArchiveHub />);
    expect(await screen.findByText('Audit Archive Unavailable')).toBeTruthy();
    failed.unmount();

    vi.mocked(fetchArchiveRecords).mockResolvedValueOnce({
      items: [archive],
      totalCount: 1,
      totalPages: 1,
      pageSize: 100,
    });
    vi.mocked(downloadArchiveManifest).mockRejectedValueOnce(new Error('Manifest read failed.'));
    render(<AuditArchiveHub />);
    await userEvent.click(await screen.findByRole('button', { name: 'Download manifest archive-1' }));
    expect(await screen.findByText('Manifest read failed.')).toBeTruthy();
  });
});
