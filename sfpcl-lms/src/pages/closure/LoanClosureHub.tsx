import React, { useCallback, useEffect, useRef, useState } from 'react';
import {
  Archive,
  BadgeCheck,
  CheckCircle2,
  FileText,
  Lock,
  RefreshCw,
  Shield,
} from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchAllLoanAccounts,
  type LoanAccountProjection,
} from '../../services/loanAccountsApi';
import {
  archiveLoanFile,
  closeLoan,
  fetchArchiveRecord,
  fetchClosureReadiness,
  fetchNoc,
  issueNoc,
  recordSecurityReturn,
  type ArchiveRecordProjection,
  type ClosureReadinessProjection,
  type LoanClosureProjection,
  type NocProjection,
  type SecurityReturnProjection,
} from '../../services/recoveryApi';
import { formatMoney } from '../../utils/formatMoney';

type ClosureTab = 'closure' | 'noc' | 'security_return' | 'archive';
type LoadState = 'loading' | 'ready' | 'empty' | 'unauthorized' | 'error';

const tabs: Array<{ id: ClosureTab; label: string }> = [
  { id: 'closure', label: 'Closure Checklist' },
  { id: 'noc', label: 'NOC Generation' },
  { id: 'security_return', label: 'Security Return / Unpledge' },
  { id: 'archive', label: 'Archive' },
];

const actionIdentity = (prefix: string) =>
  `${prefix}:${globalThis.crypto?.randomUUID?.() ?? `${Date.now()}`}`;

const displayLabel = (value: string) => value
  .replace(/_/g, ' ')
  .replace(/\b\w/g, letter => letter.toUpperCase());

const isUnauthorized = (error: unknown) =>
  error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0);

const isNotFound = (error: unknown) =>
  error instanceof AuthSessionError && error.status === 404;

const LoanClosureHub: React.FC = () => {
  const { currentUser } = useRole();
  const [activeTab, setActiveTab] = useState<ClosureTab>('closure');
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [accounts, setAccounts] = useState<LoanAccountProjection[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [readiness, setReadiness] = useState<ClosureReadinessProjection | null>(null);
  const [closure, setClosure] = useState<LoanClosureProjection | null>(null);
  const [noc, setNoc] = useState<NocProjection | null>(null);
  const [securityReturn, setSecurityReturn] = useState<SecurityReturnProjection | null>(null);
  const [archiveRecord, setArchiveRecord] = useState<ArchiveRecordProjection | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailUnauthorized, setDetailUnauthorized] = useState(false);
  const [message, setMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [closureNotes, setClosureNotes] = useState('');
  const [closureFieldError, setClosureFieldError] = useState('');
  const [nocDocumentId, setNocDocumentId] = useState('');
  const [borrowerEmail, setBorrowerEmail] = useState('');
  const [nocFieldError, setNocFieldError] = useState('');
  const [securityFields, setSecurityFields] = useState<Record<string, string>>({
    item_type: 'poa', outcome: 'released', unpledge_type: 'full',
    pledgee_dp_outcome: 'accepted', auto_unpledge_flag: 'false',
  });
  const [securityFieldError, setSecurityFieldError] = useState('');
  const [physicalLocation, setPhysicalLocation] = useState('');
  const [digitalLocation, setDigitalLocation] = useState('');
  const [archiveFieldError, setArchiveFieldError] = useState('');
  const detailRequest = useRef(0);

  const selectedAccount = accounts.find(row => row.loan_account_id === selectedId) ?? null;
  const canClose = currentUser.permissions.includes('closure.loan.close');
  const canIssueNoc = currentUser.permissions.includes('closure.noc.issue');
  const canRecordSecurity = currentUser.permissions.includes('closure.security_return.record');
  const canArchive = currentUser.permissions.includes('closure.archive.create');
  const canReadArchive = currentUser.permissions.includes('closure.archive.read');

  const resetWorkflow = useCallback(() => {
    setClosure(null);
    setNoc(null);
    setSecurityReturn(null);
    setArchiveRecord(null);
    setClosureNotes('');
    setClosureFieldError('');
    setNocDocumentId('');
    setBorrowerEmail('');
    setNocFieldError('');
    setSecurityFields({
      item_type: 'poa', outcome: 'released', unpledge_type: 'full',
      pledgee_dp_outcome: 'accepted', auto_unpledge_flag: 'false',
    });
    setSecurityFieldError('');
    setPhysicalLocation('');
    setDigitalLocation('');
    setArchiveFieldError('');
    setSuccessMessage('');
  }, []);

  const loadReadiness = useCallback(async (loanAccountId: string) => {
    const requestId = detailRequest.current + 1;
    detailRequest.current = requestId;
    setSelectedId(loanAccountId);
    setDetailLoading(true);
    setDetailUnauthorized(false);
    setMessage('');
    try {
      const projection = await fetchClosureReadiness(loanAccountId);
      if (detailRequest.current === requestId) setReadiness(projection);
      return projection;
    } catch (error) {
      if (detailRequest.current === requestId) {
        setReadiness(null);
        setDetailUnauthorized(isUnauthorized(error));
        setMessage(error instanceof Error ? error.message : 'Closure readiness could not be loaded.');
      }
      throw error;
    } finally {
      if (detailRequest.current === requestId) setDetailLoading(false);
    }
  }, []);

  const selectAccount = useCallback(async (loanAccountId: string) => {
    resetWorkflow();
    setReadiness(null);
    try {
      await loadReadiness(loanAccountId);
    } catch {
      // The detail boundary presents the retained error without replacing the list.
    }
  }, [loadReadiness, resetWorkflow]);

  const loadAccounts = useCallback(async () => {
    setLoadState('loading');
    setMessage('');
    try {
      const result = await fetchAllLoanAccounts();
      setAccounts(result.items);
      if (result.items.length === 0) {
        setSelectedId(null);
        setReadiness(null);
        setLoadState('empty');
        return;
      }
      setLoadState('ready');
      await selectAccount(result.items[0].loan_account_id);
    } catch (error) {
      setAccounts([]);
      setSelectedId(null);
      setReadiness(null);
      setMessage(error instanceof Error ? error.message : 'Closure candidates could not be loaded.');
      setLoadState(isUnauthorized(error) ? 'unauthorized' : 'error');
    }
  }, [selectAccount]);

  useEffect(() => {
    void loadAccounts();
  }, [loadAccounts]);

  const loadDownstream = useCallback(async (loanClosureId: string) => {
    if (
      currentUser.permissions.includes('closure.readiness.read')
      || currentUser.permissions.includes('closure.noc.issue')
    ) {
      try {
        setNoc(await fetchNoc(loanClosureId));
      } catch (error) {
        if (isNotFound(error)) setNoc(null);
        else throw error;
      }
    }
    if (canReadArchive) {
      try {
        setArchiveRecord(await fetchArchiveRecord(loanClosureId));
      } catch (error) {
        if (isNotFound(error)) setArchiveRecord(null);
        else throw error;
      }
    }
  }, [canReadArchive, currentUser.permissions]);

  const refreshCanonical = useCallback(async () => {
    if (!selectedId) return;
    await loadReadiness(selectedId);
    if (closure) await loadDownstream(closure.loan_closure_id);
  }, [closure, loadDownstream, loadReadiness, selectedId]);

  const submitClosure = async () => {
    if (!selectedAccount || !readiness?.ready_for_closure || !canClose) return;
    const notes = closureNotes.trim();
    if (!notes) {
      setClosureFieldError('Closure notes are required.');
      return;
    }
    setBusy(true);
    setMessage('');
    setSuccessMessage('');
    setClosureFieldError('');
    try {
      const canonical = await closeLoan(selectedAccount.loan_account_id, {
        closure_notes: notes,
        idempotency_key: actionIdentity('closure'),
      });
      setClosure(canonical);
      await loadReadiness(selectedAccount.loan_account_id);
      await loadDownstream(canonical.loan_closure_id);
      setSuccessMessage('Financial closure recorded from canonical backend state.');
    } catch (error) {
      if (error instanceof AuthSessionError && error.fieldErrors?.closure_notes) {
        setClosureFieldError(error.fieldErrors.closure_notes);
      }
      setMessage(error instanceof Error ? error.message : 'Financial closure could not be recorded.');
    } finally {
      setBusy(false);
    }
  };

  const submitNoc = async () => {
    if (!closure || !canIssueNoc || !closure.available_actions.includes('closure.noc.issue')) return;
    if (!nocDocumentId.trim()) {
      setNocFieldError('Document ID is required.');
      return;
    }
    if (!borrowerEmail.trim()) {
      setNocFieldError('Borrower email is required.');
      return;
    }
    setBusy(true);
    setMessage('');
    setSuccessMessage('');
    setNocFieldError('');
    try {
      await issueNoc(closure.loan_closure_id, {
        document_id: nocDocumentId.trim(),
        delivery_mode: 'email',
        recipient_email: borrowerEmail.trim(),
        signatory_user_id: currentUser.id,
        idempotency_key: actionIdentity('noc'),
      });
      setNoc(await fetchNoc(closure.loan_closure_id));
      setSuccessMessage('NOC issued from canonical backend state.');
    } catch (error) {
      const fieldError = error instanceof AuthSessionError
        ? Object.values(error.fieldErrors ?? {})[0]
        : undefined;
      if (fieldError) setNocFieldError(fieldError);
      setMessage(error instanceof Error ? error.message : 'NOC could not be issued.');
    } finally {
      setBusy(false);
    }
  };

  const submitSecurityReturn = async () => {
    if (
      !closure
      || !canRecordSecurity
      || !closure.available_actions.includes('closure.security_return.record')
    ) return;
    const packageId = securityFields.security_package_id?.trim();
    const payload: Record<string, unknown> = {};
    if (packageId) {
      if (!securityFields.expected_version || !securityFields.source_item_id?.trim()) {
        setSecurityFieldError('Package version and source item ID are required.');
        return;
      }
      const item: Record<string, unknown> = {
        item_type: securityFields.item_type,
        source_item_id: securityFields.source_item_id.trim(),
        outcome: securityFields.outcome,
      };
      if (securityFields.outcome === 'pending') item.pending_reason = securityFields.pending_reason?.trim();
      if (['returned', 'released'].includes(securityFields.outcome)) {
        item.returned_released_to = securityFields.returned_released_to?.trim();
        item.returned_released_at = securityFields.returned_released_at;
      }
      if (securityFields.item_type === 'cdsl') {
        Object.assign(item, {
          psn: securityFields.psn?.trim(), urf_document_id: securityFields.urf_document_id?.trim(),
          urf_date: securityFields.urf_date, unpledge_type: securityFields.unpledge_type,
          pledgor_dp_submitted_at: securityFields.pledgor_dp_submitted_at,
          pledgee_dp_acted_at: securityFields.pledgee_dp_acted_at,
          pledgee_dp_outcome: securityFields.pledgee_dp_outcome,
          auto_unpledge_flag: securityFields.auto_unpledge_flag === 'true',
          completed_at: securityFields.completed_at,
          completion_evidence_document_id: securityFields.completion_evidence_document_id?.trim(),
        });
      }
      Object.assign(payload, {
        security_package_id: packageId,
        expected_version: Number(securityFields.expected_version),
        acknowledgement_document_id: securityFields.acknowledgement_document_id?.trim() || undefined,
        items: [item],
      });
    }
    setBusy(true);
    setMessage('');
    setSuccessMessage('');
    setSecurityFieldError('');
    try {
      const canonical = await recordSecurityReturn(closure.loan_closure_id, {
        payload,
        idempotency_key: actionIdentity('security-return'),
      });
      setSecurityReturn(canonical);
      await loadDownstream(closure.loan_closure_id);
      setSuccessMessage('Security return recorded from the canonical action response.');
    } catch (error) {
      const fieldError = error instanceof AuthSessionError
        ? Object.values(error.fieldErrors ?? {})[0]
        : undefined;
      if (fieldError) setSecurityFieldError(fieldError);
      setMessage(error instanceof Error ? error.message : 'Security return could not be recorded.');
    } finally {
      setBusy(false);
    }
  };

  const submitArchive = async () => {
    if (!closure || !canArchive || !closure.available_actions.includes('closure.archive.create')) return;
    if (!physicalLocation.trim() && !digitalLocation.trim()) {
      setArchiveFieldError('A physical or digital archive location is required.');
      return;
    }
    setBusy(true);
    setMessage('');
    setSuccessMessage('');
    setArchiveFieldError('');
    try {
      await archiveLoanFile(closure.loan_closure_id, {
        file_location_physical: physicalLocation.trim(),
        file_location_digital: digitalLocation.trim(),
        idempotency_key: actionIdentity('archive'),
      });
      setArchiveRecord(await fetchArchiveRecord(closure.loan_closure_id));
      setSuccessMessage('Archive recorded from canonical backend state.');
    } catch (error) {
      const fieldError = error instanceof AuthSessionError
        ? Object.values(error.fieldErrors ?? {})[0]
        : undefined;
      if (fieldError) setArchiveFieldError(fieldError);
      setMessage(error instanceof Error ? error.message : 'Archive could not be recorded.');
    } finally {
      setBusy(false);
    }
  };

  if (loadState === 'loading') {
    return <StateCard message="Loading closure candidates…" />;
  }

  if (loadState === 'unauthorized' || loadState === 'error') {
    return (
      <div className="p-6">
        <AlertBanner
          type="error"
          title={loadState === 'unauthorized' ? 'Access Denied' : 'Closure Hub Unavailable'}
          message={message}
          actions={<button type="button" onClick={() => void loadAccounts()} className="btn-secondary">Retry</button>}
        />
      </div>
    );
  }

  if (loadState === 'empty') {
    return (
      <div className="p-6">
        <PageHeader />
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
          <FileText size={32} className="mx-auto text-slate-300 mb-3" />
          <div className="font-semibold text-slate-700">No loan accounts are available in your closure scope.</div>
          <div className="text-sm text-slate-500 mt-1">
            Backend-scoped loan accounts will appear here when closure work is available.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <PageHeader />

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        {accounts.map(account => (
          <button
            key={account.loan_account_id}
            type="button"
            onClick={() => void selectAccount(account.loan_account_id)}
            className={`text-left border rounded-xl p-4 transition-all ${
              selectedId === account.loan_account_id
                ? 'border-green-300 bg-green-50'
                : 'border-slate-200 bg-white hover:border-slate-300'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-medium text-slate-600">
                {account.loan_account_number}
              </span>
              <StatusBadge label={account.loan_account_status} size="sm" />
            </div>
            <div className="font-medium text-slate-900 text-sm">{account.member.display_name}</div>
            <div className="text-xs text-slate-500 mt-1">
              {formatMoney(account.total_outstanding)} account outstanding
            </div>
          </button>
        ))}
      </div>

      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              type="button"
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {successMessage && (
        <AlertBanner type="success" title="Closure workflow updated" message={successMessage} />
      )}
      {message && loadState === 'ready' && readiness && (
        <AlertBanner type="error" title="Closure action failed" message={message} />
      )}

      <WorkflowSummary
        readiness={readiness}
        closure={closure}
        noc={noc}
        securityReturn={securityReturn}
        archiveRecord={archiveRecord}
      />

      {detailLoading ? (
        <StateCard message="Loading canonical closure readiness…" nested />
      ) : !readiness || !selectedAccount ? (
        <AlertBanner
          type={detailUnauthorized ? 'error' : 'warning'}
          title={detailUnauthorized ? 'Access Denied' : 'Closure readiness unavailable'}
          message={message || 'The selected loan readiness projection is unavailable.'}
          actions={selectedId ? (
            <button type="button" onClick={() => void loadReadiness(selectedId)} className="btn-secondary">
              Retry
            </button>
          ) : undefined}
        />
      ) : (
        <>
          {activeTab === 'closure' && (
            <ClosurePanel
              account={selectedAccount}
              readiness={readiness}
              closure={closure}
              notes={closureNotes}
              fieldError={closureFieldError}
              busy={busy}
              canClose={canClose}
              onNotes={value => {
                setClosureNotes(value);
                if (value.trim()) setClosureFieldError('');
              }}
              onClose={() => void submitClosure()}
              onRefresh={() => void refreshCanonical()}
            />
          )}
          {activeTab === 'noc' && (
            <NocPanel
              closure={closure}
              noc={noc}
              canIssue={canIssueNoc}
              documentId={nocDocumentId}
              borrowerEmail={borrowerEmail}
              fieldError={nocFieldError}
              busy={busy}
              onDocumentId={value => {
                setNocDocumentId(value);
                if (value.trim()) setNocFieldError('');
              }}
              onBorrowerEmail={value => {
                setBorrowerEmail(value);
                if (value.trim()) setNocFieldError('');
              }}
              onIssue={() => void submitNoc()}
            />
          )}
          {activeTab === 'security_return' && (
            <SecurityReturnPanel
              closure={closure}
              projection={securityReturn}
              canRecord={canRecordSecurity}
              fields={securityFields}
              fieldError={securityFieldError}
              busy={busy}
              onField={(field, value) => {
                setSecurityFields(previous => ({ ...previous, [field]: value }));
                setSecurityFieldError('');
              }}
              onRecord={() => void submitSecurityReturn()}
            />
          )}
          {activeTab === 'archive' && (
            <ArchivePanel
              closure={closure}
              projection={archiveRecord}
              canArchive={canArchive}
              physicalLocation={physicalLocation}
              digitalLocation={digitalLocation}
              fieldError={archiveFieldError}
              busy={busy}
              onPhysicalLocation={value => {
                setPhysicalLocation(value);
                if (value.trim()) setArchiveFieldError('');
              }}
              onDigitalLocation={value => {
                setDigitalLocation(value);
                if (value.trim()) setArchiveFieldError('');
              }}
              onArchive={() => void submitArchive()}
            />
          )}
        </>
      )}
    </div>
  );
};

const PageHeader = () => (
  <div className="mb-6">
    <h1 className="text-xl font-bold text-slate-900">Loan Closure & Archive</h1>
    <p className="text-sm text-slate-500 mt-1">
      Review server-owned readiness, issue NOC, return security, and retain the archive manifest.
    </p>
  </div>
);

const StateCard: React.FC<{ message: string; nested?: boolean }> = ({ message, nested = false }) => (
  <div className={nested ? 'mt-6' : 'p-6'}>
    <div className="card text-sm text-slate-500">{message}</div>
  </div>
);

interface WorkflowSummaryProps {
  readiness: ClosureReadinessProjection | null; closure: LoanClosureProjection | null;
  noc: NocProjection | null; securityReturn: SecurityReturnProjection | null;
  archiveRecord: ArchiveRecordProjection | null;
}
const WorkflowSummary: React.FC<WorkflowSummaryProps> = ({ readiness, closure, noc, securityReturn, archiveRecord }) => (
  <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6">
    <div className="flex items-center justify-between gap-3 mb-3">
      <div>
        <h3 className="text-sm font-semibold text-slate-900">Closure status</h3>
        <p className="text-xs text-slate-500 mt-0.5">Current canonical projections for the selected loan.</p>
      </div>
      <StatusBadge
        label={archiveRecord ? 'fully closed and archived' : closure?.closure_stage ?? (readiness?.ready_for_closure ? 'ready for closure' : 'blocked')}
        size="sm"
      />
    </div>
    <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
      {[
        ['Readiness', readiness?.ready_for_closure ? 'ready' : 'blocked'],
        ['Financial close', closure?.closure_stage ?? 'not recorded'],
        ['NOC', noc?.delivery_status ?? closure?.requirements.noc ?? 'blocked'],
        ['Security return', securityReturn?.status ?? closure?.requirements.security_return ?? 'blocked'],
        ['Archive', archiveRecord ? 'archived' : closure?.requirements.archive ?? 'blocked'],
      ].map(([label, value]) => (
        <div key={label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
          <p className="text-xs font-semibold text-slate-700">{label}</p>
          <p className="text-xs text-slate-500 mt-2">{displayLabel(value)}</p>
        </div>
      ))}
    </div>
  </div>
);

interface ClosurePanelProps {
  account: LoanAccountProjection; readiness: ClosureReadinessProjection; closure: LoanClosureProjection | null;
  notes: string; fieldError: string; busy: boolean; canClose: boolean;
  onNotes: (value: string) => void; onClose: () => void; onRefresh: () => void;
}
const ClosurePanel: React.FC<ClosurePanelProps> = ({ account, readiness, closure, notes, fieldError, busy, canClose, onNotes, onClose, onRefresh }) => (
  <div className="max-w-3xl space-y-5">
    <div className="bg-white border border-slate-200 rounded-xl p-6">
      <div className="flex items-start justify-between gap-4 mb-5">
        <div>
          <h3 className="font-semibold text-slate-900">Closure Checklist — {account.loan_account_number}</h3>
          <p className="text-xs text-slate-500 mt-0.5">{account.member.display_name}</p>
        </div>
        <StatusBadge label={readiness.ready_for_closure ? 'Ready for closure' : 'Blocked'} />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-5 text-sm">
        {[
          ['Principal', formatMoney(readiness.principal_outstanding)],
          ['Interest', formatMoney(readiness.interest_outstanding)],
          ['Charges', formatMoney(readiness.charges_outstanding)],
          ['Total', formatMoney(readiness.total_outstanding)],
        ].map(([label, value]) => (
          <div key={label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
            <div className="text-xs text-slate-500">{label} outstanding</div>
            <div className="font-semibold text-slate-900 mt-1">{value}</div>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        {readiness.checks.map(check => (
          <div
            key={check.code}
            className={`flex items-center justify-between gap-3 p-3 rounded-lg ${
              check.status === 'pass' ? 'bg-green-50' : 'bg-amber-50'
            }`}
          >
            <div className="flex items-center gap-3">
              {check.status === 'pass'
                ? <CheckCircle2 size={16} className="text-green-600" />
                : <Lock size={16} className="text-amber-600" />}
              <span className="text-sm text-slate-700">{displayLabel(check.code)}</span>
            </div>
            <StatusBadge label={check.status === 'pass' ? 'Passed' : 'Failed'} size="sm" />
          </div>
        ))}
      </div>

      <div className="mt-5">
        <label htmlFor="closure-notes" className="field-label">Closure notes</label>
        <textarea
          id="closure-notes"
          rows={3}
          value={notes}
          disabled={Boolean(closure)}
          onChange={event => onNotes(event.target.value)}
          className="field-input resize-none"
          placeholder="Record the evidence reviewed before financial closure."
        />
        {fieldError && <p className="text-xs text-red-600 mt-1">{fieldError}</p>}
      </div>

      <div className="flex flex-wrap gap-3 mt-4">
        {canClose && (
          <button
            type="button"
            disabled={busy || Boolean(closure) || !readiness.ready_for_closure}
            onClick={onClose}
            className="bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold disabled:opacity-50"
          >
            <BadgeCheck size={16} className="inline mr-2" />
            Close Loan Financially
          </button>
        )}
        <button type="button" disabled={busy} onClick={onRefresh} className="btn-secondary">
          <RefreshCw size={15} className="inline mr-2" />
          Refresh readiness
        </button>
      </div>
    </div>
  </div>
);

interface NocPanelProps {
  closure: LoanClosureProjection | null; noc: NocProjection | null; canIssue: boolean;
  documentId: string; borrowerEmail: string; fieldError: string; busy: boolean;
  onDocumentId: (value: string) => void; onBorrowerEmail: (value: string) => void; onIssue: () => void;
}
const NocPanel: React.FC<NocPanelProps> = ({ closure, noc, canIssue, documentId, borrowerEmail, fieldError, busy, onDocumentId, onBorrowerEmail, onIssue }) => {
  if (!closure) {
    return <LockedPanel message="NOC remains blocked until the backend creates a financially-closed loan identity." />;
  }
  if (noc) {
    return (
      <ProjectionCard
        icon={<BadgeCheck size={16} className="text-green-600" />}
        title="No Objection Certificate"
        fields={[
          ['NOC ID', noc.noc_id],
          ['Loan account', noc.loan_account_number],
          ['Borrower', noc.borrower_name],
          ['Issued at', noc.issued_at],
          ['Delivery mode', displayLabel(noc.delivery_mode)],
          ['Delivery status', displayLabel(noc.delivery_status)],
          ['Document ID', noc.document_id],
          ['Signatory role', displayLabel(noc.signatory_role_code)],
        ]}
      />
    );
  }
  const actionAvailable = closure.available_actions.includes('closure.noc.issue');
  return (
    <div className="max-w-2xl bg-white border border-slate-200 rounded-xl p-6">
      <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
        <BadgeCheck size={16} className="text-green-600" />
        No Objection Certificate (NOC)
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label htmlFor="noc-document-id" className="field-label">NOC document ID</label>
          <input id="noc-document-id" value={documentId} onChange={event => onDocumentId(event.target.value)} className="field-input" />
        </div>
        <div>
          <label htmlFor="borrower-email" className="field-label">Borrower email</label>
          <input id="borrower-email" type="email" value={borrowerEmail} onChange={event => onBorrowerEmail(event.target.value)} className="field-input" />
        </div>
      </div>
      <p className="text-xs text-slate-500 mt-3">
        The backend validates the document, canonical borrower address, signatory identity, and full-repayment closure.
      </p>
      {fieldError && <p className="text-xs text-red-600 mt-2">{fieldError}</p>}
      {canIssue && actionAvailable ? (
        <button type="button" disabled={busy} onClick={onIssue} className="mt-4 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold disabled:opacity-50">
          Issue NOC
        </button>
      ) : (
        <p className="text-sm text-amber-700 mt-4">The canonical closure does not expose NOC issuance to this session.</p>
      )}
    </div>
  );
};

interface SecurityReturnPanelProps {
  closure: LoanClosureProjection | null; projection: SecurityReturnProjection | null;
  canRecord: boolean; fields: Record<string, string>; fieldError: string; busy: boolean;
  onField: (field: string, value: string) => void; onRecord: () => void;
}
const SecurityReturnPanel: React.FC<SecurityReturnPanelProps> = ({ closure, projection, canRecord, fields, fieldError, busy, onField, onRecord }) => {
  if (!closure) {
    return <LockedPanel message="Security return remains blocked until the backend creates a financially-closed loan identity." />;
  }
  if (projection) {
    return (
      <div className="max-w-3xl bg-white border border-slate-200 rounded-xl p-6">
        <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
          <Shield size={16} className="text-green-600" />
          Security Return & CDSL Unpledge
        </h3>
        <div className="grid grid-cols-2 gap-3 text-sm mb-4">
          <div><span className="text-slate-500">Return ID</span><div className="font-medium break-all">{projection.security_return_id}</div></div>
          <div><span className="text-slate-500">Status</span><div className="font-medium">{displayLabel(projection.status)}</div></div>
        </div>
        <div className="space-y-2">
          {projection.items.map(item => (
            <div key={item.item_type} className="flex items-start justify-between gap-4 border border-slate-100 rounded-lg p-3">
              <div>
                <div className="text-sm font-medium text-slate-800">{displayLabel(item.item_type)}</div>
                <div className="text-xs text-slate-500 mt-1">{item.custody_location || 'No custody location projected'}</div>
                {item.returned_released_to && <div className="text-xs text-slate-500">Returned/released to {item.returned_released_to}</div>}
              </div>
              <StatusBadge label={item.status} size="sm" />
            </div>
          ))}
        </div>
      </div>
    );
  }
  const actionAvailable = closure.available_actions.includes('closure.security_return.record');
  return (
    <div className="max-w-2xl bg-white border border-slate-200 rounded-xl p-6">
      <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
        <Shield size={16} className="text-green-600" />
        Security Return & CDSL Unpledge
      </h3>
      <p className="text-xs text-slate-500 mb-4">Leave the package ID empty only when no security package applies. Otherwise record one server-owned item transition at a time.</p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[
          ['security_package_id', 'Security package ID', 'text'],
          ['expected_version', 'Expected package version', 'number'],
          ['acknowledgement_document_id', 'Acknowledgement document ID', 'text'],
          ['source_item_id', 'Source item ID', 'text'],
        ].map(([name, label, type]) => (
          <div key={name}>
            <label htmlFor={`security-${name}`} className="field-label">{label}</label>
            <input id={`security-${name}`} type={type} value={fields[name] ?? ''} onChange={event => onField(name, event.target.value)} className="field-input" />
          </div>
        ))}
        <div>
          <label htmlFor="security-item-type" className="field-label">Security item</label>
          <select id="security-item-type" value={fields.item_type} onChange={event => onField('item_type', event.target.value)} className="field-input">
            <option value="sh4">SH-4 Transfer Form</option><option value="blank_cheque">Blank Cheque</option>
            <option value="poa">Power of Attorney</option><option value="cdsl">CDSL Pledge Release</option>
          </select>
        </div>
        <div>
          <label htmlFor="security-outcome" className="field-label">Outcome</label>
          <select id="security-outcome" value={fields.outcome} onChange={event => onField('outcome', event.target.value)} className="field-input">
            <option value="pending">Pending</option>
            {fields.item_type === 'cdsl'
              ? <><option value="completed">Completed</option><option value="rejected">Rejected</option></>
              : <><option value="returned">Returned</option><option value="released">Released</option></>}
          </select>
        </div>
      </div>
      {fields.outcome === 'pending' && (
        <div className="mt-4">
          <label htmlFor="security-pending-reason" className="field-label">Pending reason</label>
          <input id="security-pending-reason" value={fields.pending_reason ?? ''} onChange={event => onField('pending_reason', event.target.value)} className="field-input" />
        </div>
      )}
      {['returned', 'released'].includes(fields.outcome) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          <div><label htmlFor="security-recipient" className="field-label">Returned or released to</label><input id="security-recipient" value={fields.returned_released_to ?? ''} onChange={event => onField('returned_released_to', event.target.value)} className="field-input" /></div>
          <div><label htmlFor="security-returned-at" className="field-label">Returned or released at</label><input id="security-returned-at" type="datetime-local" value={fields.returned_released_at ?? ''} onChange={event => onField('returned_released_at', event.target.value)} className="field-input" /></div>
        </div>
      )}
      {fields.item_type === 'cdsl' && fields.outcome !== 'pending' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
          {[
            ['psn', 'Pledge sequence number', 'text'], ['urf_document_id', 'URF document ID', 'text'],
            ['urf_date', 'URF date', 'date'], ['pledgor_dp_submitted_at', 'Pledgor DP submitted at', 'datetime-local'],
            ['pledgee_dp_acted_at', 'Pledgee DP acted at', 'datetime-local'], ['completed_at', 'Completed at', 'datetime-local'],
            ['completion_evidence_document_id', 'Completion evidence document ID', 'text'],
          ].map(([name, label, type]) => (
            <div key={name}><label htmlFor={`security-${name}`} className="field-label">{label}</label><input id={`security-${name}`} type={type} value={fields[name] ?? ''} onChange={event => onField(name, event.target.value)} className="field-input" /></div>
          ))}
          <div><label htmlFor="security-unpledge-type" className="field-label">Unpledge type</label><select id="security-unpledge-type" value={fields.unpledge_type} onChange={event => onField('unpledge_type', event.target.value)} className="field-input"><option value="full">Full</option><option value="partial">Partial</option></select></div>
          <div><label htmlFor="security-dp-outcome" className="field-label">Pledgee DP outcome</label><select id="security-dp-outcome" value={fields.pledgee_dp_outcome} onChange={event => onField('pledgee_dp_outcome', event.target.value)} className="field-input"><option value="accepted">Accepted</option><option value="rejected">Rejected</option></select></div>
          <div><label htmlFor="security-auto-unpledge" className="field-label">Automatic unpledge</label><select id="security-auto-unpledge" value={fields.auto_unpledge_flag} onChange={event => onField('auto_unpledge_flag', event.target.value)} className="field-input"><option value="false">No</option><option value="true">Yes</option></select></div>
        </div>
      )}
      {fieldError && <p className="text-xs text-red-600 mt-1">{fieldError}</p>}
      {canRecord && actionAvailable ? (
        <button type="button" disabled={busy} onClick={onRecord} className="mt-4 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold disabled:opacity-50">
          Record Security Return
        </button>
      ) : (
        <p className="text-sm text-amber-700 mt-4">The canonical closure does not expose security return to this session.</p>
      )}
    </div>
  );
};

interface ArchivePanelProps {
  closure: LoanClosureProjection | null; projection: ArchiveRecordProjection | null; canArchive: boolean;
  physicalLocation: string; digitalLocation: string; fieldError: string; busy: boolean;
  onPhysicalLocation: (value: string) => void; onDigitalLocation: (value: string) => void; onArchive: () => void;
}
const ArchivePanel: React.FC<ArchivePanelProps> = ({
  closure, projection, canArchive, physicalLocation,
  digitalLocation, fieldError, busy, onPhysicalLocation, onDigitalLocation, onArchive,
}) => {
  if (!closure) return <LockedPanel message="Archive remains blocked until financial closure is recorded." />;
  if (projection) {
    return (
      <ProjectionCard
        icon={<Archive size={16} className="text-slate-600" />}
        title="Loan Archive Manifest"
        fields={[
          ['Archive ID', projection.archive_record_id],
          ['Physical location', projection.file_location_physical ?? 'Not recorded'],
          ['Digital location', projection.file_location_digital ?? 'Not recorded'],
          ['Retention start', projection.retention_start_date],
          ['Retention until', projection.retention_until_date],
          ['Archived at', projection.archived_at],
          ['Archived by role', displayLabel(projection.archived_by_role_code)],
          ['Destruction eligible', projection.destruction_eligible ? 'Yes' : 'No'],
        ]}
      />
    );
  }
  const actionAvailable = closure.available_actions.includes('closure.archive.create');
  if (!actionAvailable) {
    return <LockedPanel message="Archive remains blocked by the canonical closure requirements." />;
  }
  return (
    <div className="max-w-2xl bg-white border border-slate-200 rounded-xl p-6">
      <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
        <Archive size={16} className="text-slate-600" />
        Loan Record Archival
      </h3>
      <p className="text-xs text-slate-500 mb-4">
        The server calculates retention dates from the retained financial closure date.
      </p>
      <div className="space-y-4">
        <div>
          <label htmlFor="physical-archive-location" className="field-label">Physical archive location</label>
          <input id="physical-archive-location" value={physicalLocation} onChange={event => onPhysicalLocation(event.target.value)} className="field-input" />
        </div>
        <div>
          <label htmlFor="digital-archive-location" className="field-label">Digital archive location</label>
          <input id="digital-archive-location" value={digitalLocation} onChange={event => onDigitalLocation(event.target.value)} className="field-input" />
        </div>
      </div>
      {fieldError && <p className="text-xs text-red-600 mt-2">{fieldError}</p>}
      {canArchive && actionAvailable ? (
        <button type="button" disabled={busy} onClick={onArchive} className="mt-4 bg-slate-700 hover:bg-slate-800 text-white px-5 py-2.5 rounded-lg text-sm font-semibold disabled:opacity-50">
          Archive Loan File
        </button>
      ) : (
        <p className="text-sm text-amber-700 mt-4">The canonical closure does not expose archive creation to this session.</p>
      )}
    </div>
  );
};

const LockedPanel: React.FC<{ message: string }> = ({ message }) => (
  <div className="max-w-2xl bg-white border border-slate-200 rounded-xl p-8 text-center">
    <Lock size={32} className="mx-auto text-slate-300 mb-3" />
    <div className="font-semibold text-slate-700">Action Locked</div>
    <div className="text-sm text-slate-500 mt-1">{message}</div>
  </div>
);

const ProjectionCard: React.FC<{ icon: React.ReactNode; title: string; fields: Array<[string, string]> }> = ({ icon, title, fields }) => (
  <div className="max-w-3xl bg-white border border-slate-200 rounded-xl p-6">
    <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">{icon}{title}</h3>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
      {fields.map(([label, value]) => (
        <div key={label}>
          <div className="text-xs text-slate-500">{label}</div>
          <div className="font-medium text-slate-900 mt-1 break-all">{value}</div>
        </div>
      ))}
    </div>
  </div>
);

export default LoanClosureHub;
