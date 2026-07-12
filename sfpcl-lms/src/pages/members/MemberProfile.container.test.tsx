// @vitest-environment jsdom
import React, { StrictMode } from 'react';
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { clearStoredAuthSession, storedAuthSession } from '../../services/authSession';
import * as memberApi from '../../services/memberProfileApi';
import MemberProfile from './MemberProfile';

beforeEach(() => storedAuthSession({ accessToken: 'mounted-access', refreshToken: 'mounted-refresh' }));

afterEach(() => {
  cleanup();
  clearStoredAuthSession();
  window.localStorage.clear();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
});

describe('MemberProfile container', () => {
  it('loads canonical member detail once when Strict Mode replays the mount effect', () => {
    const pending = new Promise<memberApi.MemberProfileDetail>(() => undefined);
    const fetchProfile = vi.spyOn(memberApi, 'fetchMemberProfile').mockReturnValue(pending);

    render(
      <StrictMode>
        <MemberProfile memberId="member-1" onBack={vi.fn()} />
      </StrictMode>,
    );

    expect(fetchProfile).toHaveBeenCalledTimes(1);
    expect(fetchProfile).toHaveBeenCalledWith('member-1');
  });

  it.each([[400, 'VALIDATION_ERROR'], [403, 'MAKER_CHECKER_DENIED'], [409, 'STALE_WRITE']] as const)(
    'preserves approval %s %s after one POST and no canonical refetch', async (status, code) => {
      const reason = `approval ${code} server reason`;
      const fetchMock = vi.fn()
        .mockResolvedValueOnce(response(200, { success: true, data: approvableProfile }))
        .mockResolvedValueOnce(response(status, { success: false, error: { code, message: reason } }));
      vi.stubGlobal('fetch', fetchMock);
      render(<MemberProfile memberId="member-1" onBack={vi.fn()} />);

      await screen.findAllByRole('button', { name: 'Approve identity change' });
      await userEvent.click(document.querySelector('button.btn-primary') as HTMLButtonElement);

      expect(await screen.findByText(reason)).toBeTruthy();
      expect(fetchMock).toHaveBeenCalledTimes(2);
      expect(fetchMock.mock.calls[1][0]).toBe('http://127.0.0.1:8000/api/v1/member-identity-change-requests/request-1/approve/');
      expect((fetchMock.mock.calls[1][1] as RequestInit).method).toBe('POST');
    },
  );
});

function response(status: number, body: unknown): Response {
  return { ok: status >= 200 && status < 300, status, json: async () => body } as Response;
}

const approvableProfile: memberApi.MemberProfileDetail = {
  version: 7, member_id: 'member-1', member_number: 'MEM-1', member_type: 'individual_farmer', legal_name: 'Synthetic Member', display_name: 'Synthetic Member', folio_number: 'FOL-1', membership_start_date: '2026-01-01', membership_status: 'active', kyc_status: 'verified', rekyc_due_date: null, default_status: 'no_default', mobile_number: null, email: null,
  pan: { masked: '******234F', can_view_full: false }, aadhaar: { masked: '********1234', can_view_full: false }, registered_address: { line1: null, line2: null, village_city: null, district: null, state: null, pincode: null }, share_summary: { number_of_shares: 1, holding_mode: 'physical', available_share_count: 1 }, active_member_status: { status: 'active', verified_at: null }, individual_profile: null, producer_institution_profile: null,
  pending_identity_change: { identity_change_request_id: 'request-1', status: 'pending' },
  available_actions: [{ action_code: 'members.member.identity_change.approve', label: 'Approve identity change', enabled: true, disabled_reason: null, required_permission: 'members.member.update', required_role: null }],
};
