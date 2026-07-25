// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import {
  downloadArchiveManifest,
  fetchArchiveRecords,
  type ArchiveRecordProjection,
} from '../../services/recoveryApi';
import {
  createAuditObservation,
  fetchAuditLogs,
  fetchAuditObservation,
  fetchAuditObservations,
  type AuditLogProjection,
  type AuditObservationProjection,
} from '../../services/auditExplorerApi';
import AuditArchiveHub from './AuditArchiveHub';
import archiveSource from './AuditArchiveHub.tsx?raw';
import auditApiSource from '../../services/auditExplorerApi.ts?raw';

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

vi.mock('../../services/auditExplorerApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/auditExplorerApi')>(),
  fetchAuditLogs: vi.fn(),
  fetchAuditObservations: vi.fn(),
  fetchAuditObservation: vi.fn(),
  createAuditObservation: vi.fn(),
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

const auditLog: AuditLogProjection = {
  audit_log_id: 'audit-log-012dac',
  actor: { user_id: 'actor-012dac', full_name: 'Ivy Auditor' },
  actor_type: 'user',
  actor_role_codes: ['internal_auditor'],
  actor_team_codes: ['audit'],
  action: 'compliance.evidence_submitted',
  module: 'compliance',
  entity_type: 'compliance_evidence',
  entity_id: 'evidence-012dac',
  linked_record: {
    entity_type: 'compliance_evidence',
    entity_id: 'evidence-012dac',
  },
  old_value: { status: 'missing' },
  new_value: { status: 'accepted' },
  reason: 'M14-FR-012 quarterly sample',
  outcome: 'success',
  request_id: 'request-012dac',
  ip_address: '10.0.0.8',
  device: 'AuditBrowser/1.0',
  created_at: '2026-07-25T06:00:00Z',
};

const observation: AuditObservationProjection = {
  audit_observation_id: 'observation-012dac',
  creator: {
    user_id: 'auditor-011pe',
    full_name: 'Ivy Auditor',
    role_code: 'internal_auditor',
    team_codes: ['audit'],
  },
  audit_scope: 'audit_readonly',
  observation: 'M14-FR-012 sample is complete and traceable.',
  source_references: [{
    source_type: 'audit_log',
    source_id: 'audit-log-012dac',
    entity_type: 'compliance_evidence',
    entity_id: 'evidence-012dac',
  }],
  created_at: '2026-07-25T06:10:00Z',
};

beforeEach(() => {
  currentUser.role = 'auditor';
  currentUser.roleCodes = ['internal_auditor'];
  currentUser.permissions = [
    'audit.audit_log.read',
    'audit.observation.read',
    'audit.observation.create',
    'closure.archive.read',
  ];
  vi.mocked(fetchAuditLogs).mockResolvedValue({
    items: [auditLog],
    pagination: {
      page: 1,
      page_size: 20,
      total_count: 21,
      total_pages: 2,
      has_next: true,
      has_previous: false,
    },
  });
  vi.mocked(fetchAuditObservations).mockResolvedValue({
    items: [],
    pagination: {
      page: 1,
      page_size: 20,
      total_count: 0,
      total_pages: 1,
      has_next: false,
      has_previous: false,
    },
  });
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

describe('012DAC audit explorer, observation, and retained archive wiring', () => {
  it('filters and paginates the S74 explorer through backend query parameters', async () => {
    render(<AuditArchiveHub />);

    expect(screen.getByText('Loading audit events…')).toBeTruthy();
    expect(await screen.findByText('compliance.evidence_submitted')).toBeTruthy();

    await userEvent.type(screen.getByLabelText('Entity type'), 'compliance_evidence');
    await userEvent.type(screen.getByLabelText('Action'), 'compliance.evidence_submitted');
    await userEvent.type(screen.getByLabelText('Actor user ID'), 'actor-012dac');
    await userEvent.type(screen.getByLabelText('From date'), '2026-07-01');
    await userEvent.type(screen.getByLabelText('To date'), '2026-07-25');
    await userEvent.click(screen.getByRole('button', { name: 'Apply audit filters' }));

    await waitFor(() => expect(fetchAuditLogs).toHaveBeenLastCalledWith({
      entityType: 'compliance_evidence',
      action: 'compliance.evidence_submitted',
      actorUserId: 'actor-012dac',
      createdFrom: '2026-07-01',
      createdTo: '2026-07-25',
      page: 1,
      pageSize: 20,
    }));

    await userEvent.click(screen.getByRole('button', { name: 'Next audit page' }));
    await waitFor(() => expect(fetchAuditLogs).toHaveBeenLastCalledWith(
      expect.objectContaining({ page: 2, pageSize: 20 }),
    ));
  });

  it('renders only a read-only audit whitelist and never exposes restricted change fields', async () => {
    vi.mocked(fetchAuditLogs).mockResolvedValueOnce({
      items: [{
        ...auditLog,
        old_value: {
          status: 'missing',
          pan_number: 'ABCDE1234F',
        },
        new_value: {
          status: 'accepted',
          bank_account_number: '123456789012',
          storage_key: 'private/audit/evidence.pdf',
        },
      }],
      pagination: {
        page: 1,
        page_size: 20,
        total_count: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    });
    render(<AuditArchiveHub />);

    await userEvent.click(await screen.findByRole('button', {
      name: 'View audit event audit-log-012dac',
    }));
    expect(screen.getByText('10.0.0.8')).toBeTruthy();
    expect(screen.getByText('AuditBrowser/1.0')).toBeTruthy();
    expect(screen.getByText('missing')).toBeTruthy();
    expect(screen.getByText('accepted')).toBeTruthy();

    expect(screen.getByRole('heading', { name: 'Audit Event Detail' })).toBeTruthy();
    expect(screen.getByText('M14-FR-012 quarterly sample')).toBeTruthy();
    expect(screen.getByText('This audit event is immutable and read-only.')).toBeTruthy();
    expect(screen.queryByText(/ABCDE1234F|123456789012|private\/audit/i)).toBeNull();
    expect(screen.queryByText(/pan_number|bank_account_number|storage_key/i)).toBeNull();
    expect(screen.queryByRole('button', { name: /edit|save|delete|update/i })).toBeNull();
  });

  it('records and revisits a separate immutable M14-FR-012 auditor observation', async () => {
    vi.mocked(fetchAuditObservations)
      .mockResolvedValueOnce({
        items: [],
        pagination: {
          page: 1,
          page_size: 20,
          total_count: 0,
          total_pages: 1,
          has_next: false,
          has_previous: false,
        },
      })
      .mockResolvedValue({
        items: [observation],
        pagination: {
          page: 1,
          page_size: 20,
          total_count: 1,
          total_pages: 1,
          has_next: false,
          has_previous: false,
        },
      });
    vi.mocked(createAuditObservation).mockResolvedValue(observation);
    vi.mocked(fetchAuditObservation).mockResolvedValue(observation);
    render(<AuditArchiveHub />);

    await userEvent.click(await screen.findByRole('button', {
      name: 'View audit event audit-log-012dac',
    }));
    await userEvent.click(screen.getByRole('button', { name: 'Sample this event' }));
    await userEvent.type(
      screen.getByLabelText('Auditor observation'),
      'M14-FR-012 sample is complete and traceable.',
    );
    await userEvent.click(screen.getByRole('button', { name: 'Record observation' }));

    await waitFor(() => expect(createAuditObservation).toHaveBeenCalledWith({
      observation: 'M14-FR-012 sample is complete and traceable.',
      sourceReferences: [{
        source_type: 'audit_log',
        source_id: 'audit-log-012dac',
      }],
    }));
    expect(await screen.findByText('Observation recorded as immutable.')).toBeTruthy();

    await userEvent.click(screen.getByRole('button', { name: 'Close audit event detail' }));
    await userEvent.click(screen.getByRole('button', { name: 'Auditor Observations' }));
    expect(await screen.findByText('M14-FR-012 sample is complete and traceable.')).toBeTruthy();
    await userEvent.click(screen.getByRole('button', {
      name: 'View observation observation-012dac',
    }));

    await waitFor(() => expect(fetchAuditObservation).toHaveBeenCalledWith('observation-012dac'));
    expect(await screen.findByRole('heading', { name: 'Observation Detail' })).toBeTruthy();
    expect(screen.getByText('Creator, scope, source references, text and time cannot be edited.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /edit|save|delete|update/i })).toBeNull();
  });

  it('surfaces backend observation validation without exposing details or lifecycle controls', async () => {
    vi.mocked(createAuditObservation).mockRejectedValueOnce(new AuthSessionError(
      'VALIDATION_ERROR',
      'Audit observation request failed validation.',
      400,
      { observation: 'The observation contains unsafe or sensitive content.' },
      { storage_key: 'private/audit/foreign-evidence.pdf' },
    ));
    render(<AuditArchiveHub />);

    await userEvent.click(await screen.findByRole('button', {
      name: 'View audit event audit-log-012dac',
    }));
    await userEvent.click(screen.getByRole('button', { name: 'Sample this event' }));
    await userEvent.type(screen.getByLabelText('Auditor observation'), 'Unsafe sample note');
    await userEvent.click(screen.getByRole('button', { name: 'Record observation' }));

    expect(await screen.findByText('The observation contains unsafe or sensitive content.')).toBeTruthy();
    expect(screen.queryByText(/private\/audit|storage_key/i)).toBeNull();
    expect(screen.queryByLabelText(/status|severity|assigned/i)).toBeNull();
    expect(auditApiSource).not.toMatch(/export const (?:update|patch|delete)Audit/i);
  });

  it('surfaces a foreign or stale sample denial without leaking backend details', async () => {
    vi.mocked(createAuditObservation).mockRejectedValueOnce(new AuthSessionError(
      'NOT_FOUND',
      'Audit observation source was not found.',
      404,
      undefined,
      { storage_key: 'private/audit/foreign-evidence.pdf' },
    ));
    render(<AuditArchiveHub />);

    await userEvent.click(await screen.findByRole('button', {
      name: 'View audit event audit-log-012dac',
    }));
    await userEvent.click(screen.getByRole('button', { name: 'Sample this event' }));
    await userEvent.type(screen.getByLabelText('Auditor observation'), 'Governed sample note');
    await userEvent.click(screen.getByRole('button', { name: 'Record observation' }));

    expect(await screen.findByText('Audit observation source was not found.')).toBeTruthy();
    expect(screen.queryByText(/private\/audit|storage_key/i)).toBeNull();
  });

  it('keeps a valid observation list visible when one revisit is denied', async () => {
    vi.mocked(fetchAuditObservations).mockResolvedValueOnce({
      items: [observation],
      pagination: {
        page: 1,
        page_size: 20,
        total_count: 1,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    });
    vi.mocked(fetchAuditObservation).mockRejectedValueOnce(
      new AuthSessionError('NOT_FOUND', 'Observation detail was not found.', 404),
    );
    render(<AuditArchiveHub />);

    await userEvent.click(screen.getByRole('button', { name: 'Auditor Observations' }));
    await userEvent.click(await screen.findByRole('button', {
      name: 'View observation observation-012dac',
    }));

    expect(await screen.findByText('Observation detail was not found.')).toBeTruthy();
    expect(screen.getByText('M14-FR-012 sample is complete and traceable.')).toBeTruthy();
    expect(screen.queryByText('Auditor observations could not be loaded.')).toBeNull();
  });

  it('keeps observation controls unavailable to a non-auditor even with forged permission codes', async () => {
    currentUser.role = 'credit_manager';
    currentUser.roleCodes = ['credit_manager'];
    currentUser.permissions = [
      'audit.audit_log.read',
      'audit.observation.read',
      'audit.observation.create',
    ];
    render(<AuditArchiveHub />);

    await userEvent.click(await screen.findByRole('button', {
      name: 'View audit event audit-log-012dac',
    }));
    expect(screen.getByText('Observation creation is not authorised for this role or scope.')).toBeTruthy();
    expect(screen.queryByLabelText('Auditor observation')).toBeNull();
    await userEvent.click(screen.getByRole('button', { name: 'Close audit event detail' }));
    await userEvent.click(screen.getByRole('button', { name: 'Auditor Observations' }));
    expect(screen.getByText('Observation access is not authorised.')).toBeTruthy();
    expect(fetchAuditObservations).not.toHaveBeenCalled();
  });

  it('renders truthful audit empty, unauthorized, and retryable error states', async () => {
    vi.mocked(fetchAuditLogs).mockResolvedValueOnce({
      items: [],
      pagination: {
        page: 1,
        page_size: 20,
        total_count: 0,
        total_pages: 1,
        has_next: false,
        has_previous: false,
      },
    });
    const empty = render(<AuditArchiveHub />);
    expect(await screen.findByText(
      'No audit events are available for these filters and your scope.',
    )).toBeTruthy();
    empty.unmount();

    vi.mocked(fetchAuditLogs).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Audit scope denied.', 403),
    );
    const denied = render(<AuditArchiveHub />);
    expect(await screen.findByText('Audit access is not authorised.')).toBeTruthy();
    expect(screen.getByText('Audit scope denied.')).toBeTruthy();
    denied.unmount();

    vi.mocked(fetchAuditLogs).mockRejectedValueOnce(new Error('Audit service unavailable.'));
    render(<AuditArchiveHub />);
    expect(await screen.findByText('Audit events could not be loaded.')).toBeTruthy();
    expect(screen.getByRole('button', { name: 'Retry' })).toBeTruthy();
  });

  it('renders canonical archive records as a read-only surface without owned fixtures', async () => {
    render(<AuditArchiveHub />);

    await userEvent.click(screen.getByRole('button', { name: 'Archive Register' }));
    expect(await screen.findByText('archive-1')).toBeTruthy();
    expect(screen.getByText('Archive Room / Rack A / Box 12')).toBeTruthy();
    expect(screen.getByText('25/07/2034')).toBeTruthy();
    expect(screen.getByText('Read-only access — archive records cannot be edited.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: /archive file|record destruction|delete|edit/i })).toBeNull();
    expect(archiveSource).not.toMatch(/mockData|auditEvents|Radha Kisan Org|PF-2025-025/);
  });

  it('downloads only after the governed audited detail read and supports canonical search refetch', async () => {
    render(<AuditArchiveHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Archive Register' }));
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
    await userEvent.click(screen.getByRole('button', { name: 'Archive Register' }));
    expect(await screen.findByText('No archive records are available in your scope.')).toBeTruthy();
    empty.unmount();

    vi.mocked(fetchArchiveRecords).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Archive scope denied.', 403),
    );
    const denied = render(<AuditArchiveHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Archive Register' }));
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.getByText('Archive scope denied.')).toBeTruthy();
    denied.unmount();

    vi.mocked(fetchArchiveRecords).mockRejectedValueOnce(new Error('Archive service unavailable.'));
    const failed = render(<AuditArchiveHub />);
    await userEvent.click(screen.getByRole('button', { name: 'Archive Register' }));
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
    await userEvent.click(screen.getByRole('button', { name: 'Archive Register' }));
    await userEvent.click(await screen.findByRole('button', { name: 'Download manifest archive-1' }));
    expect(await screen.findByText('Manifest read failed.')).toBeTruthy();
  });
});
