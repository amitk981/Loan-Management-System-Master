// @vitest-environment jsdom
import { cleanup, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import Header from './Header';
import headerSource from './Header.tsx?raw';

vi.mock('../../contexts/RoleContext', () => ({
  useRole: () => ({
    currentUser: {
      id: 'user-1', name: 'Search User', email: 'search@example.com',
      role: 'cfo', roleName: 'CFO', roleCodes: ['cfo'], teamCodes: [],
      permissions: [], availableActions: [], prototypePermissions: [],
    },
    setRole: vi.fn(),
    can: vi.fn(() => true),
  }),
}));

afterEach(cleanup);

describe('010N Header search path', () => {
  it('navigates the transient query to S02 without building a local result index', async () => {
    const onSearch = vi.fn();
    render(<Header onSearch={onSearch} />);
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'Sensitive exact value{Enter}');
    expect(onSearch).toHaveBeenCalledWith('Sensitive exact value');
    expect(headerSource).not.toContain('loanAccounts');
    expect(headerSource).not.toContain('loanApplications');
    expect(headerSource).not.toContain('members.filter');
    expect(headerSource).not.toContain('Quick Results');
  });
});
