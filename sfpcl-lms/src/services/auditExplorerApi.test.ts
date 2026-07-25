// @vitest-environment jsdom
import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
  createAuditObservation,
  fetchAuditLogs,
  fetchAuditObservation,
  fetchAuditObservations,
} from './auditExplorerApi';

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem('sfpcl_staff_auth_session', JSON.stringify({
    accessToken: 'audit-token',
    refreshToken: 'audit-refresh',
  }));
  vi.restoreAllMocks();
});

describe('auditExplorerApi', () => {
  it('round-trips the S74 entity, action, actor, date, and pagination filters', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        success: true,
        data: [{
          audit_log_id: 'audit-log-012dac',
          actor: { user_id: 'actor-012dac', full_name: 'Internal Auditor' },
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
          old_value: {},
          new_value: { outcome: 'accepted' },
          reason: 'Quarterly sample',
          outcome: 'success',
          request_id: 'request-012dac',
          ip_address: '10.0.0.8',
          device: 'AuditBrowser/1.0',
          created_at: '2026-07-25T06:00:00Z',
        }],
        pagination: {
          page: 2,
          page_size: 20,
          total_count: 21,
          total_pages: 2,
          has_next: false,
          has_previous: true,
        },
      }),
    } as Response);
    vi.stubGlobal('fetch', fetchMock);

    await expect(fetchAuditLogs({
      entityType: 'compliance_evidence',
      action: 'compliance.evidence_submitted',
      actorUserId: 'actor-012dac',
      createdFrom: '2026-07-01',
      createdTo: '2026-07-25',
      page: 2,
      pageSize: 20,
    })).resolves.toMatchObject({
      items: [{ audit_log_id: 'audit-log-012dac' }],
      pagination: { page: 2, total_count: 21 },
    });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/audit-logs/?entity_type=compliance_evidence&action=compliance.evidence_submitted&actor_user_id=actor-012dac&created_from=2026-07-01&created_to=2026-07-25&page=2&page_size=20',
      expect.objectContaining({
        method: 'GET',
        headers: expect.objectContaining({
          Accept: 'application/json',
          Authorization: 'Bearer audit-token',
        }),
      }),
    );
  });

  it('creates and revisits an immutable observation against an explicitly sampled audit row', async () => {
    const observation = {
      audit_observation_id: 'observation-012dac',
      creator: {
        user_id: 'auditor-012dac',
        full_name: 'Internal Auditor',
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
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: observation }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          success: true,
          data: [observation],
          pagination: {
            page: 1,
            page_size: 20,
            total_count: 1,
            total_pages: 1,
            has_next: false,
            has_previous: false,
          },
        }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true, data: observation }),
      } as Response);
    vi.stubGlobal('fetch', fetchMock);

    await expect(createAuditObservation({
      observation: 'M14-FR-012 sample is complete and traceable.',
      sourceReferences: [{
        source_type: 'audit_log',
        source_id: 'audit-log-012dac',
      }],
    })).resolves.toEqual(observation);
    await expect(fetchAuditObservations({ page: 1, pageSize: 20 }))
      .resolves.toMatchObject({
        items: [{ audit_observation_id: 'observation-012dac' }],
      });
    await expect(fetchAuditObservation('observation-012dac')).resolves.toEqual(observation);

    expect(fetchMock).toHaveBeenNthCalledWith(
      1,
      'http://127.0.0.1:8000/api/v1/audit-observations/',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          audit_scope: 'audit_readonly',
          observation: 'M14-FR-012 sample is complete and traceable.',
          source_references: [{
            source_type: 'audit_log',
            source_id: 'audit-log-012dac',
          }],
        }),
      }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      'http://127.0.0.1:8000/api/v1/audit-observations/?audit_scope=audit_readonly&page=1&page_size=20',
      expect.objectContaining({ method: 'GET' }),
    );
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      'http://127.0.0.1:8000/api/v1/audit-observations/observation-012dac/',
      expect.objectContaining({ method: 'GET' }),
    );
  });
});
