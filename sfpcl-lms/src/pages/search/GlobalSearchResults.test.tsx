// @vitest-environment jsdom
import { cleanup, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { AuthSessionError } from '../../services/authSession';
import { fetchGlobalSearch, type GlobalSearchResponse } from '../../services/globalSearchApi';
import GlobalSearchResults from './GlobalSearchResults';
import pageSource from './GlobalSearchResults.tsx?raw';

vi.mock('../../services/globalSearchApi', async importOriginal => ({
  ...await importOriginal<typeof import('../../services/globalSearchApi')>(),
  fetchGlobalSearch: vi.fn(),
}));

const pagination = {
  page: 1, page_size: 10, total_count: 1, total_pages: 1,
  has_next: false, has_previous: false,
};

const response: GlobalSearchResponse = {
  continuation: 'opaque-search-token',
  groups: {
    members: {
      items: [{
        id: 'member-1', result_type: 'member', title: 'API Farmer',
        identifier: 'FOL-API-001', status: 'active', risk_status: 'no_default',
        amount: null, owner: 'Field Officer', last_updated_at: '2026-07-21T10:00:00Z',
        last_updated_by: 'Field Officer',
        quick_actions: [{ label: 'Open', page: 'members/profile', entity_id: 'member-1' }],
      }],
      pagination,
    },
    loan_accounts: {
      items: [{
        id: 'loan-1', result_type: 'loan_account', title: 'LN-API-001',
        identifier: 'SAP-API-001', status: 'active', risk_status: 'Current',
        amount: '400000.00', owner: 'Loan Servicing', last_updated_at: '2026-07-21T11:00:00Z',
        last_updated_by: 'Accounts User',
        quick_actions: [{ label: 'View loan account', page: 'loan-accounts/detail', entity_id: 'loan-1' }],
      }],
      pagination: { ...pagination, total_count: 11, total_pages: 2, has_next: true },
    },
    compliance_records: {
      items: [{
        id: 'compliance-1', result_type: 'compliance_record',
        title: 'Section 186 quarterly limit', identifier: 'Section 186 · FY2026-27 Q2',
        status: 'accepted', risk_status: 'within_limit', amount: '105000.00',
        owner: 'Compliance Reviewer', last_updated_at: '2026-07-21T12:00:00Z',
        last_updated_by: 'Compliance Reviewer',
        quick_actions: [{ label: 'Open', page: 'compliance', entity_id: 'compliance-1' }],
      }],
      pagination,
    },
  },
};

describe('010N Global Search Results', () => {
  beforeEach(() => vi.mocked(fetchGlobalSearch).mockResolvedValue(response));
  afterEach(() => { cleanup(); vi.clearAllMocks(); });

  it('loads server groups, card fields, and permission-valid quick actions', async () => {
    const onNavigate = vi.fn();
    render(<GlobalSearchResults query="API Farmer" onNavigate={onNavigate} />);

    expect(screen.getByText('Searching authorised records…')).toBeTruthy();
    expect(await screen.findByText('API Farmer')).toBeTruthy();
    expect(screen.getByText('FOL-API-001')).toBeTruthy();
    expect(screen.getAllByText('Field Officer')).toHaveLength(2);
    expect(screen.getByText('₹4,00,000.00')).toBeTruthy();
    expect(screen.getByText('Accounts User')).toBeTruthy();
    expect(screen.getByRole('heading', { name: 'Compliance Records' })).toBeTruthy();
    expect(screen.getByText('Section 186 · FY2026-27 Q2')).toBeTruthy();
    expect(screen.getByText('Within Limit')).toBeTruthy();
    expect(fetchGlobalSearch).toHaveBeenCalledWith({ search: 'API Farmer', pages: {} });

    await userEvent.click(screen.getByRole('button', { name: 'View loan account' }));
    expect(onNavigate).toHaveBeenCalledWith('loan-accounts/detail', 'loan-1');
    const openActions = screen.getAllByRole('button', { name: 'Open' });
    await userEvent.click(openActions[openActions.length - 1]);
    expect(onNavigate).toHaveBeenCalledWith('compliance', 'compliance-1');
  });

  it('requests each result group page independently', async () => {
    render(<GlobalSearchResults query="API Farmer" onNavigate={vi.fn()} />);
    await screen.findByText('LN-API-001');
    await userEvent.click(screen.getByRole('button', { name: 'Next Loan Accounts page' }));
    await waitFor(() => expect(fetchGlobalSearch).toHaveBeenLastCalledWith({
      continuation: 'opaque-search-token', pages: { loan_accounts: 2 },
    }));
  });

  it('supports empty query, no results, partial groups, safe errors, and unauthorised state', async () => {
    vi.mocked(fetchGlobalSearch).mockClear();
    const emptyQuery = render(<GlobalSearchResults query="" onNavigate={vi.fn()} />);
    expect(screen.getByText('Enter a search term to find authorised records.')).toBeTruthy();
    expect(fetchGlobalSearch).not.toHaveBeenCalled();
    emptyQuery.unmount();

    vi.mocked(fetchGlobalSearch).mockResolvedValue({
      groups: {}, continuation: 'opaque-empty-token',
    });
    const noResults = render(<GlobalSearchResults query="missing" onNavigate={vi.fn()} />);
    expect(await screen.findByText('No matching records found')).toBeTruthy();
    noResults.unmount();

    vi.mocked(fetchGlobalSearch).mockRejectedValueOnce(new Error('Search is temporarily unavailable.'));
    const failed = render(<GlobalSearchResults query="failure" onNavigate={vi.fn()} />);
    expect(await screen.findByText('Search Unavailable')).toBeTruthy();
    expect(screen.getByText('Search is temporarily unavailable.')).toBeTruthy();
    failed.unmount();

    vi.mocked(fetchGlobalSearch).mockRejectedValueOnce(
      new AuthSessionError('FORBIDDEN', 'Search access denied.', 403),
    );
    render(<GlobalSearchResults query="denied" onNavigate={vi.fn()} />);
    expect(await screen.findByText('Access Denied')).toBeTruthy();
    expect(screen.queryByText('API Farmer')).toBeNull();
  });

  it('submits a replacement query without URL or local-storage caching', async () => {
    render(<GlobalSearchResults query="initial" onNavigate={vi.fn()} />);
    await screen.findByText('API Farmer');
    const input = screen.getByRole('textbox');
    await userEvent.clear(input);
    await userEvent.type(input, 'FOL-API-001');
    await userEvent.click(screen.getByRole('button', { name: 'Search' }));
    await waitFor(() => expect(fetchGlobalSearch).toHaveBeenLastCalledWith({
      search: 'FOL-API-001', pages: {},
    }));
    expect(pageSource).not.toContain('localStorage');
    expect(pageSource).not.toContain('URLSearchParams');
    expect(pageSource).not.toContain("from '../../data/mockData'");
  });

  it('clears raw sensitive input after the request and paginates with only an opaque continuation', async () => {
    const onQueryConsumed = vi.fn();
    render(
      <GlobalSearchResults
        query="CHEQUE-SENSITIVE-001"
        onNavigate={vi.fn()}
        onQueryConsumed={onQueryConsumed}
      />,
    );

    await screen.findByText('LN-API-001');
    expect((screen.getByRole('textbox') as HTMLInputElement).value).toBe('');
    expect(onQueryConsumed).toHaveBeenCalledOnce();

    vi.mocked(fetchGlobalSearch).mockClear();
    await userEvent.click(screen.getByRole('button', { name: 'Next Loan Accounts page' }));
    await waitFor(() => expect(fetchGlobalSearch).toHaveBeenCalledWith({
      continuation: 'opaque-search-token',
      pages: { loan_accounts: 2 },
    }));
  });
});
