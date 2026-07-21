import React, { useEffect, useMemo, useState } from 'react';
import {
  Banknote, FileText, History, ReceiptIndianRupee, Search,
  ShieldCheck, UserRound,
} from 'lucide-react';
import type { Page } from '../../App';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchGlobalSearch,
  type GlobalSearchResult,
  type GlobalSearchResultType,
  type GlobalSearchResponse,
  type GlobalSearchPages,
  type GlobalSearchRequest,
} from '../../services/globalSearchApi';

interface GlobalSearchResultsProps {
  query: string;
  onNavigate: (page: Page, id?: string) => void;
  onQueryConsumed?: () => void;
}

const groupOrder = [
  'members', 'loan_applications', 'loan_accounts', 'documents',
  'repayments', 'compliance_records', 'audit_logs',
];

const groupLabels: Record<string, string> = {
  members: 'Members', loan_applications: 'Loan Applications',
  loan_accounts: 'Loan Accounts', documents: 'Documents', repayments: 'Repayments',
  compliance_records: 'Compliance Records', audit_logs: 'Audit Logs',
};

const resultIcons: Record<GlobalSearchResultType, React.ReactNode> = {
  member: <UserRound size={16} className="text-green-600" />,
  loan_application: <FileText size={16} className="text-blue-600" />,
  loan_account: <Banknote size={16} className="text-amber-600" />,
  document: <FileText size={16} className="text-blue-600" />,
  repayment: <ReceiptIndianRupee size={16} className="text-green-600" />,
  compliance_record: <ShieldCheck size={16} className="text-amber-600" />,
  audit_log: <History size={16} className="text-slate-600" />,
};

const formatMoney = (value: string) =>
  new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(Number(value));

const formatDate = (value: string) => new Intl.DateTimeFormat('en-IN', {
  day: '2-digit', month: 'short', year: 'numeric',
}).format(new Date(value));

const ResultCard: React.FC<{
  result: GlobalSearchResult;
  onNavigate: GlobalSearchResultsProps['onNavigate'];
}> = ({ result, onNavigate }) => (
  <div className="p-4">
    <div className="flex flex-col gap-3 lg:flex-row lg:items-center">
      <div className="flex items-start gap-3 flex-1 min-w-0">
        <div className="mt-0.5 h-8 w-8 rounded-lg bg-slate-50 border border-slate-100 flex items-center justify-center flex-shrink-0">
          {resultIcons[result.result_type]}
        </div>
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <p className="font-semibold text-slate-900 num">{result.title}</p>
            <StatusBadge label={result.status} size="sm" />
            {result.risk_status && <StatusBadge label={result.risk_status} size="sm" />}
          </div>
          {result.identifier && <p className="text-sm text-slate-500 mt-0.5 truncate">{result.identifier}</p>}
        </div>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 lg:w-[520px]">
        {result.amount && <ResultField label="Amount" value={formatMoney(result.amount)} />}
        {result.owner && <ResultField label="Owner" value={result.owner} />}
        <ResultField label="Last updated" value={formatDate(result.last_updated_at)} />
        {result.last_updated_by && <ResultField label="Updated by" value={result.last_updated_by} />}
      </div>
      {result.quick_actions.length > 0 && (
        <div className="flex flex-wrap gap-2 lg:w-44 lg:justify-end">
          {result.quick_actions.map(action => (
            <button
              key={`${result.id}-${action.label}`}
              type="button"
              className="btn-secondary text-xs"
              onClick={() => onNavigate(action.page as Page, action.entity_id)}
            >
              {action.label}
            </button>
          ))}
        </div>
      )}
    </div>
  </div>
);

const ResultField: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="rounded-lg bg-slate-50 px-3 py-2">
    <p className="text-[11px] text-slate-400">{label}</p>
    <p className="text-xs font-medium text-slate-700 truncate">{value}</p>
  </div>
);

const GlobalSearchResults: React.FC<GlobalSearchResultsProps> = ({ query, onNavigate, onQueryConsumed }) => {
  const [localQuery, setLocalQuery] = useState(query);
  const [request, setRequest] = useState<GlobalSearchRequest | null>(null);
  const [continuation, setContinuation] = useState('');
  const [response, setResponse] = useState<GlobalSearchResponse | null>(null);
  const [pages, setPages] = useState<GlobalSearchPages>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!query.trim()) {
      setLocalQuery('');
      return;
    }
    setLocalQuery(query);
    setPages({});
    setContinuation('');
    setRequest(query.trim() ? { search: query.trim(), pages: {} } : null);
  }, [query]);

  useEffect(() => {
    if (!request) {
      return;
    }
    if (!('search' in request) && !request.continuation) {
      setResponse(null);
      setError(null);
      setLoading(false);
      return;
    }
    let cancelled = false;
    const consumedRawSearch = 'search' in request;
    setLoading(true);
    setError(null);
    fetchGlobalSearch(request)
      .then(data => {
        if (!cancelled) {
          setResponse(data);
          setContinuation(data.continuation);
          setLocalQuery('');
          setRequest(null);
          if (consumedRawSearch) onQueryConsumed?.();
        }
      })
      .catch(reason => {
        if (!cancelled) {
          setResponse(null);
          setError(reason as Error);
          setLocalQuery('');
          setRequest(null);
          if (consumedRawSearch) onQueryConsumed?.();
        }
      })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [request, onQueryConsumed]);

  const visibleGroups = useMemo(() => groupOrder
    .map(name => [name, response?.groups[name]] as const)
    .filter((entry): entry is readonly [string, NonNullable<typeof entry[1]>] => Boolean(entry[1])),
  [response]);
  const resultCount = visibleGroups.reduce((sum, [, group]) => sum + group.pagination.total_count, 0);
  const unauthorised = error instanceof AuthSessionError && error.status === 403;

  return (
    <div className="p-6 space-y-5">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Global Search Results</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            Search across authorised records. Sensitive identifiers are matched and masked by the server.
          </p>
        </div>
        <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm">
          <p className="text-xs text-slate-500">Results</p>
          <p className="text-2xl font-bold text-slate-900 num">{resultCount}</p>
        </div>
      </div>

      <div className="card">
        <form
          className="flex flex-col gap-3 sm:flex-row"
          onSubmit={event => {
            event.preventDefault();
            const search = localQuery.trim();
            if (!search) return;
            setPages({});
            setContinuation('');
            setResponse(null);
            setRequest({ search, pages: {} });
          }}
        >
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              value={localQuery}
              onChange={event => setLocalQuery(event.target.value)}
              className="field-input pl-10"
              placeholder="Borrower, folio, app no., loan no., SAP code, PAN, Aadhaar last 4..."
              autoComplete="off"
            />
          </div>
          <button className="btn-primary" type="submit">Search</button>
        </form>
      </div>

      {!request && !response && !error && (
        <div className="card py-12 text-center">
          <Search size={28} className="mx-auto text-slate-300 mb-3" />
          <p className="text-sm font-semibold text-slate-700">Enter a search term to find authorised records.</p>
        </div>
      )}
      {loading && (
        <div className="card py-12 text-center text-sm text-slate-500">Searching authorised records…</div>
      )}
      {error && (
        <AlertBanner
          type="error"
          title={unauthorised ? 'Access Denied' : 'Search Unavailable'}
          message={error.message || 'Global search could not be completed.'}
        />
      )}
      {!loading && !error && response && resultCount === 0 && (
        <div className="card py-12 text-center">
          <Search size={28} className="mx-auto text-slate-300 mb-3" />
          <p className="text-sm font-semibold text-slate-700">No matching records found</p>
          <p className="text-xs text-slate-400 mt-1">Results are limited to records available to your current role.</p>
        </div>
      )}
      {!loading && !error && visibleGroups.map(([name, group]) => (
        <section key={name} className="card p-0 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900">{groupLabels[name]}</h2>
              <p className="text-xs text-slate-500 mt-0.5">{group.pagination.total_count} authorised matches</p>
            </div>
            <ShieldCheck size={14} className="text-green-600" />
          </div>
          {group.items.length === 0 ? (
            <p className="px-5 py-6 text-sm text-slate-500">No matches in this authorised group.</p>
          ) : (
            <div className="divide-y divide-slate-100">
              {group.items.map(result => <ResultCard key={result.id} result={result} onNavigate={onNavigate} />)}
            </div>
          )}
          {(group.pagination.has_previous || group.pagination.has_next) && (
            <div className="px-5 py-3 border-t border-slate-100 flex items-center justify-between">
              <button
                type="button"
                className="btn-secondary text-xs"
                aria-label={`Previous ${groupLabels[name]} page`}
                disabled={!group.pagination.has_previous}
                onClick={() => {
                  const nextPages = { ...pages, [name]: Math.max(1, group.pagination.page - 1) };
                  setPages(nextPages);
                  setRequest({ continuation, pages: nextPages });
                }}
              >
                Previous
              </button>
              <p className="text-xs text-slate-500 num">
                Page {group.pagination.page} of {group.pagination.total_pages}
              </p>
              <button
                type="button"
                className="btn-secondary text-xs"
                aria-label={`Next ${groupLabels[name]} page`}
                disabled={!group.pagination.has_next}
                onClick={() => {
                  const nextPages = { ...pages, [name]: group.pagination.page + 1 };
                  setPages(nextPages);
                  setRequest({ continuation, pages: nextPages });
                }}
              >
                Next
              </button>
            </div>
          )}
        </section>
      ))}
    </div>
  );
};

export default GlobalSearchResults;
