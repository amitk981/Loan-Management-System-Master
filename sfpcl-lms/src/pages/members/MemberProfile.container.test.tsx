// @vitest-environment jsdom
import React, { StrictMode } from 'react';
import { cleanup, render } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import * as memberApi from '../../services/memberProfileApi';
import MemberProfile from './MemberProfile';

afterEach(() => {
  cleanup();
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
});
