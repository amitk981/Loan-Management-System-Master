import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, Calendar, CheckCircle2, Clock, FileText, Lock } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchDefaultCase,
  fetchDefaultCases,
  type DefaultCaseProjection,
} from '../../services/recoveryApi';
import { formatMoney } from '../../utils/formatMoney';

type DefaultTab = 'cases' | 'grace' | 'non_payment';
type LoadState = 'loading' | 'ready' | 'empty' | 'unauthorized' | 'error';

const tabs: Array<{ id: DefaultTab | 'recovery' | 'security'; label: string; disabled?: boolean }> = [
  { id: 'cases', label: 'All Cases' },
  { id: 'grace', label: 'Grace Period / Extension' },
  { id: 'non_payment', label: 'Non-Payment Note' },
  { id: 'recovery', label: 'Recovery Approval', disabled: true },
  { id: 'security', label: 'Security Invocation', disabled: true },
];

const DefaultRecoveryHub: React.FC = () => {
  const [activeTab, setActiveTab] = useState<DefaultTab>('cases');
  const [cases, setCases] = useState<DefaultCaseProjection[]>([]);
  const [selectedCase, setSelectedCase] = useState<DefaultCaseProjection | null>(null);
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailUnauthorized, setDetailUnauthorized] = useState(false);
  const [message, setMessage] = useState('');
  const [totalCount, setTotalCount] = useState(0);
  const detailRequestId = useRef(0);

  const loadDetail = useCallback(async (defaultCaseId: string) => {
    const requestId = detailRequestId.current + 1;
    detailRequestId.current = requestId;
    setSelectedCaseId(defaultCaseId);
    setDetailLoading(true);
    setDetailUnauthorized(false);
    setMessage('');
    try {
      const projection = await fetchDefaultCase(defaultCaseId);
      if (detailRequestId.current === requestId) {
        setSelectedCase(projection);
      }
    } catch (error) {
      if (detailRequestId.current === requestId) {
        setSelectedCase(null);
        setDetailUnauthorized(
          error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0),
        );
        setMessage(error instanceof Error ? error.message : 'The selected default case could not be loaded.');
      }
    } finally {
      if (detailRequestId.current === requestId) {
        setDetailLoading(false);
      }
    }
  }, []);

  const loadCases = useCallback(async () => {
    setLoadState('loading');
    setMessage('');
    try {
      const result = await fetchDefaultCases();
      setCases(result.items);
      setTotalCount(result.pagination.total_count);
      if (result.items.length === 0) {
        setSelectedCase(null);
        setSelectedCaseId(null);
        setLoadState('empty');
        return;
      }
      setLoadState('ready');
      await loadDetail(result.items[0].default_case_id);
    } catch (error) {
      setCases([]);
      setSelectedCase(null);
      setSelectedCaseId(null);
      setMessage(error instanceof Error ? error.message : 'Default cases could not be loaded.');
      setLoadState(
        error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0)
          ? 'unauthorized'
          : 'error',
      );
    }
  }, [loadDetail]);

  useEffect(() => {
    void loadCases();
  }, [loadCases]);

  if (loadState === 'loading') {
    return (
      <div className="p-6">
        <div className="card text-sm text-slate-500">Loading default cases…</div>
      </div>
    );
  }

  if (loadState === 'unauthorized' || loadState === 'error') {
    return (
      <div className="p-6">
        <AlertBanner
          type="error"
          title={loadState === 'unauthorized' ? 'Access Denied' : 'Default Cases Unavailable'}
          message={message}
          actions={(
            <button type="button" onClick={() => void loadCases()} className="btn-secondary">
              Retry
            </button>
          )}
        />
      </div>
    );
  }

  if (loadState === 'empty') {
    return (
      <div className="p-6">
        <Header />
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
          <FileText size={32} className="mx-auto text-slate-300 mb-3" />
          <div className="font-semibold text-slate-700">No default cases are available in your scope.</div>
          <div className="text-sm text-slate-500 mt-1">
            Missed scheduled principal repayments will appear here when the backend opens a case.
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <Header />

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          {
            label: 'Default Cases',
            value: String(totalCount),
            detail: 'Backend scoped total',
            color: 'text-orange-600',
            bg: 'bg-orange-50',
            border: 'border-orange-100',
          },
          {
            label: 'Selected Case',
            value: selectedCase ? '1' : '—',
            detail: selectedCase ? displayLabel(selectedCase.default_case_status) : 'Detail unavailable',
            color: 'text-red-600',
            bg: 'bg-red-50',
            border: 'border-red-100',
          },
          {
            label: 'Frozen Note',
            value: selectedCase?.non_payment_note ? '1' : '0',
            detail: selectedCase?.non_payment_note ? 'Backend evidence available' : 'Not exposed',
            color: 'text-violet-700',
            bg: 'bg-violet-50',
            border: 'border-violet-100',
          },
        ].map(kpi => (
          <div key={kpi.label} className={`${kpi.bg} ${kpi.border} border rounded-xl p-4`}>
            <div className={`text-2xl font-bold ${kpi.color}`}>{kpi.value}</div>
            <div className="text-xs text-slate-600 mt-0.5">{kpi.label}</div>
            <div className="text-sm font-semibold text-slate-700 mt-1">{kpi.detail}</div>
          </div>
        ))}
      </div>

      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              type="button"
              disabled={tab.disabled}
              aria-describedby={tab.disabled ? 'recovery-wiring-blocker' : undefined}
              onClick={() => {
                if (!tab.disabled) setActiveTab(tab.id as DefaultTab);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : tab.disabled
                    ? 'border-transparent text-slate-300 cursor-not-allowed'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.disabled && <Lock size={12} />}
              {tab.label}
              {tab.id === 'cases' && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${
                  activeTab === 'cases' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                }`}>
                  {totalCount}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 mb-6">
        <div className="flex items-center justify-between gap-3 mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-900">Workflow Status</h3>
            <p className="text-xs text-slate-500 mt-0.5">
              Current server projections for the selected default case.
            </p>
          </div>
          {selectedCase && <StatusBadge label={selectedCase.default_case_status} size="sm" />}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          {[
            ['Grace State', selectedCase ? displayLabel(selectedCase.grace_state) : 'Unavailable'],
            ['Reason Assessment', selectedCase?.current_assessment ? 'Recorded' : 'Not Recorded'],
            ['Extension Note', selectedCase?.extension_note ? 'Recorded' : 'Not Recorded'],
            ['Non-Payment Note', selectedCase?.non_payment_note ? 'Frozen' : 'Not Exposed'],
            ['Recovery Actions', 'Locked Until 011PB'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
              <p className="text-xs font-semibold text-slate-700">{label}</p>
              <p className="text-xs text-slate-500 mt-2">{value}</p>
            </div>
          ))}
        </div>
      </div>

      <AlertBanner
        type="info"
        title="S53-S55 read-only evidence"
        message={(
          <span id="recovery-wiring-blocker">
            Recovery approval and security invocation remain unavailable until the server-owned S56/S57
            action contract is wired in 011PB.
          </span>
        )}
      />

      <div className="mt-6">
        {activeTab === 'cases' && (
          <CasesPanel
            cases={cases}
            selectedCase={selectedCase}
            selectedCaseId={selectedCaseId}
            detailLoading={detailLoading}
            detailUnauthorized={detailUnauthorized}
            detailError={message}
            onSelect={defaultCaseId => void loadDetail(defaultCaseId)}
          />
        )}
        {activeTab === 'grace' && (
          <GracePanel selectedCase={selectedCase} detailLoading={detailLoading} detailUnauthorized={detailUnauthorized} detailError={message} />
        )}
        {activeTab === 'non_payment' && (
          <NonPaymentPanel selectedCase={selectedCase} detailLoading={detailLoading} detailUnauthorized={detailUnauthorized} detailError={message} />
        )}
      </div>
    </div>
  );
};

const Header: React.FC = () => (
  <div className="mb-6">
    <h1 className="text-xl font-bold text-slate-900">Default & Recovery Management</h1>
    <p className="text-sm text-slate-500 mt-1">
      Review backend-owned default cases, grace periods, extension evidence, and frozen non-payment notes.
    </p>
  </div>
);

const CasesPanel: React.FC<{
  cases: DefaultCaseProjection[];
  selectedCase: DefaultCaseProjection | null;
  selectedCaseId: string | null;
  detailLoading: boolean;
  detailUnauthorized: boolean;
  detailError: string;
  onSelect: (defaultCaseId: string) => void;
}> = ({ cases, selectedCase, selectedCaseId, detailLoading, detailUnauthorized, detailError, onSelect }) => (
  <div className="flex flex-col lg:flex-row gap-6">
    <div className="w-full lg:w-80 flex-shrink-0 space-y-2">
      {cases.map(row => (
        <button
          key={row.default_case_id}
          type="button"
          onClick={() => onSelect(row.default_case_id)}
          className={`w-full text-left border rounded-xl p-4 transition-all ${
            selectedCaseId === row.default_case_id
              ? 'border-green-300 bg-green-50'
              : 'border-slate-200 bg-white hover:border-slate-300'
          }`}
        >
          <div className="flex items-start justify-between mb-2">
            <span className="text-xs font-mono font-medium text-slate-600">{row.loan_account_number}</span>
            <StatusBadge label={row.default_case_status} size="sm" />
          </div>
          <div className="font-medium text-slate-900 text-sm">{row.borrower_name}</div>
          <div className="text-xs text-slate-500 mt-1">{formatMoney(row.total_outstanding)} outstanding</div>
        </button>
      ))}
    </div>

    <div className="flex-1">
      <DetailBoundary detailLoading={detailLoading} detailUnauthorized={detailUnauthorized} detailError={detailError} selectedCase={selectedCase}>
        {selectedCase && (
          <div className="space-y-4">
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2">
                    <h2 className="text-lg font-bold text-slate-900">{selectedCase.loan_account_number}</h2>
                    <StatusBadge label={selectedCase.default_case_status} />
                  </div>
                  <div className="text-slate-600 mt-0.5">{selectedCase.borrower_name}</div>
                  <div className="text-xs text-slate-500 mt-2">Case {selectedCase.default_case_id}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-slate-500">Total Outstanding</div>
                  <div className="text-2xl font-bold text-red-600">
                    {formatMoney(selectedCase.total_outstanding)}
                  </div>
                </div>
              </div>
              <FieldGrid fields={[
                ['Scheduled Due Date', selectedCase.scheduled_due_date],
                ['Grace Start Date', selectedCase.grace_period_start_date],
                ['Grace End Date', selectedCase.grace_period_end_date],
                ['Grace State', displayLabel(selectedCase.grace_state)],
                ['Principal Outstanding', formatMoney(selectedCase.principal_outstanding)],
                ['Interest Outstanding', formatMoney(selectedCase.interest_outstanding)],
                ['Trigger', displayLabel(selectedCase.trigger_event)],
                ['Current Stage', displayLabel(selectedCase.default_case_status)],
                ['Case Reason', selectedCase.reason || 'No case reason recorded.'],
              ]} />
            </div>
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-800 mb-4">Default Resolution Workflow</h3>
              <div className="space-y-3">
                {[
                  ['1', `Default case — ${displayLabel(selectedCase.default_case_status)}`, 'complete'],
                  ['2', `Grace period — ${displayLabel(selectedCase.grace_state)}`, selectedCase.grace_state === 'active' ? 'active' : 'complete'],
                  ['3', 'Reason assessment', selectedCase.current_assessment ? 'complete' : 'locked'],
                  ['4', 'Extension note', selectedCase.extension_note ? 'complete' : 'locked'],
                  ['5', 'Non-payment note to Sanction Committee', selectedCase.non_payment_note ? 'active' : 'locked'],
                  ['6', 'Recovery action approval', 'locked'],
                  ['7', 'Security invocation / legal action', 'locked'],
                ].map(([step, label, state]) => (
                  <div key={step} className="flex items-center gap-3">
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 text-xs font-bold ${
                      state === 'complete'
                        ? 'bg-green-600 text-white'
                        : state === 'active'
                          ? 'bg-blue-600 text-white'
                          : 'bg-slate-100 text-slate-500'
                    }`}>
                      {state === 'complete' ? <CheckCircle2 size={14} /> : state === 'locked' ? <Lock size={12} /> : step}
                    </div>
                    <span className={`text-sm ${
                      state === 'complete'
                        ? 'text-slate-900 font-medium'
                        : state === 'active'
                          ? 'text-blue-900 font-semibold'
                          : 'text-slate-400'
                    }`}>{label}</span>
                    {state === 'active' && (
                      <span className="text-[10px] uppercase font-bold tracking-wider text-blue-600 ml-2 bg-blue-50 px-2 py-0.5 rounded">
                        Active
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </DetailBoundary>
    </div>
  </div>
);

const GracePanel: React.FC<PanelProps> = ({ selectedCase, detailLoading, detailUnauthorized, detailError }) => (
  <div className="max-w-2xl space-y-5">
    <DetailBoundary detailLoading={detailLoading} detailUnauthorized={detailUnauthorized} detailError={detailError} selectedCase={selectedCase}>
      {selectedCase && (
        <>
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-1">Grace Period Rules</h3>
            <p className="text-xs text-slate-500 mb-4">
              Three-month grace and any one-year extension are displayed from the backend workflow.
            </p>
            <div className="space-y-3 text-sm">
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <Clock size={16} className="text-blue-600 mt-0.5 flex-shrink-0" />
                <div><strong>Grace Period:</strong> starts on the scheduled due date and ends on the backend-projected date.</div>
              </div>
              <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg">
                <Calendar size={16} className="text-amber-600 mt-0.5 flex-shrink-0" />
                <div><strong>Extension:</strong> the Extension Note and dates below are immutable server evidence.</div>
              </div>
            </div>
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Clock size={16} className="text-blue-600" />
              Grace Period Tracking
            </h3>
            <FieldGrid fields={[
              ['Loan Account', selectedCase.loan_account_number],
              ['Grace Start Date', selectedCase.grace_period_start_date],
              ['Grace End Date', selectedCase.grace_period_end_date],
              ['Grace Status', displayLabel(selectedCase.grace_state)],
              ['Principal Outstanding', formatMoney(selectedCase.principal_outstanding)],
              ['Case Stage', displayLabel(selectedCase.default_case_status)],
            ]} />
          </div>

          {selectedCase.current_assessment ? (
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4">Reason Assessment</h3>
              <FieldGrid fields={[
                ['Classification', displayLabel(selectedCase.current_assessment.payment_failure_classification)],
                ['Assessed At', formatTimestamp(selectedCase.current_assessment.assessed_at)],
                ['Recommended Action', displayLabel(selectedCase.current_assessment.recommended_action)],
                ['Evidence Records', String(selectedCase.current_assessment.evidence_document_ids.length)],
              ]} />
              <p className="text-sm text-slate-700 mt-4">{selectedCase.current_assessment.reason_summary}</p>
              <p className="text-xs text-slate-500 mt-2">
                Borrower interaction: {selectedCase.current_assessment.borrower_interaction_summary}
              </p>
            </div>
          ) : (
            <BlockedCard title="Reason assessment not recorded" message="The backend has not attached a post-grace assessment to this case." />
          )}

          {selectedCase.extension_note ? (
            <div className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
                <Calendar size={16} className="text-amber-600" />
                Extension Note
              </h3>
              <FieldGrid fields={[
                ['Extension Start', selectedCase.extension_note.extension_start_date],
                ['Extension End', selectedCase.extension_note.extension_end_date],
                ['Extension Status', displayLabel(selectedCase.extension_note.status)],
                ['Document ID', selectedCase.extension_note.document_id],
              ]} />
              <p className="text-sm text-slate-700 mt-4">{selectedCase.extension_note.extension_reason}</p>
            </div>
          ) : (
            <BlockedCard title="Extension note not recorded" message="No server-owned Extension Note is available for this case." />
          )}
        </>
      )}
    </DetailBoundary>
  </div>
);

const NonPaymentPanel: React.FC<PanelProps> = ({ selectedCase, detailLoading, detailUnauthorized, detailError }) => (
  <div className="max-w-2xl space-y-5">
    <DetailBoundary detailLoading={detailLoading} detailUnauthorized={detailUnauthorized} detailError={detailError} selectedCase={selectedCase}>
      {selectedCase?.non_payment_note ? (
        <>
          <AlertBanner
            type="warning"
            title="Frozen backend evidence"
            message="This browser view is read-only and cannot manufacture or amend the Non-Payment Note."
          />
          <section
            aria-labelledby="non-payment-note-heading"
            className="bg-white border border-slate-200 rounded-xl p-6"
          >
            <div className="flex items-center justify-between gap-3 mb-4">
              <h3 id="non-payment-note-heading" className="font-semibold text-slate-900">
                Note for Non-Payment
              </h3>
              <StatusBadge label={selectedCase.non_payment_note.status} />
            </div>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="block text-sm font-medium text-slate-700 mb-1.5">Loan Account</div>
                  <div className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50">
                    {selectedCase.loan_account_number}
                  </div>
                </div>
                <div>
                  <div className="block text-sm font-medium text-slate-700 mb-1.5">Borrower</div>
                  <div className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50">
                    {selectedCase.borrower_name}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm bg-slate-50 rounded-lg p-4">
                <div><div className="text-slate-500">Original Due Date</div><div className="font-medium text-slate-900">{frozenFact(selectedCase, 'original_due_date')}</div></div>
                <div><div className="text-slate-500">Grace Period Outcome</div><div className="font-medium text-slate-900">{frozenFact(selectedCase, 'grace_outcome_summary')}</div></div>
                <div><div className="text-slate-500">Extension Outcome</div><div className="font-medium text-slate-900">{frozenFact(selectedCase, 'extension_outcome_summary')}</div></div>
                <div><div className="text-slate-500">Amount Still Unpaid</div><div className="font-medium text-red-600">{formatMoney(selectedCase.non_payment_note.outstanding_principal_amount)}</div></div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="block text-sm font-medium text-slate-700 mb-1.5">Intentional / Non-Intentional Assessment</div>
                  <div className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50">
                    {displayLabel(selectedCase.non_payment_note.intentionality_assessment)}
                  </div>
                </div>
                <div>
                  <div className="block text-sm font-medium text-slate-700 mb-1.5">Evidence Reviewed</div>
                  <div className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50">
                    {selectedCase.non_payment_note.evidence_document_ids.length} evidence record(s)
                  </div>
                </div>
              </div>

              <div>
                <div className="block text-sm font-medium text-slate-700 mb-1.5">Reason for non-payment</div>
                <div className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50 min-h-24">
                  {selectedCase.non_payment_note.reason_for_non_payment}
                </div>
              </div>

              <div>
                <div className="block text-sm font-medium text-slate-700 mb-1.5">Credit Assessment Team Recommendation</div>
                <div className="p-3 rounded-lg border border-slate-100 bg-slate-50 text-sm">
                  {displayLabel(selectedCase.non_payment_note.recommended_recovery_action)}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="block text-sm font-medium text-slate-700 mb-1.5">Prepared By</div>
                  <div className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50">
                    {frozenFact(selectedCase, 'prepared_by_name')}
                  </div>
                </div>
                <div>
                  <div className="block text-sm font-medium text-slate-700 mb-1.5">Submitted At</div>
                  <div className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm bg-slate-50">
                    {selectedCase.non_payment_note.submitted_to_sanction_committee_at
                      ? formatTimestamp(selectedCase.non_payment_note.submitted_to_sanction_committee_at)
                      : 'Not submitted'}
                  </div>
                </div>
              </div>
            </div>
          </section>
        </>
      ) : (
        <BlockedCard
          title="Frozen non-payment note not available"
          message="The backend has not exposed an authorised frozen note for this default case."
        />
      )}
    </DetailBoundary>
  </div>
);

interface PanelProps {
  selectedCase: DefaultCaseProjection | null;
  detailLoading: boolean;
  detailUnauthorized: boolean;
  detailError: string;
}

const DetailBoundary: React.FC<PanelProps & { children: React.ReactNode }> = ({
  selectedCase,
  detailLoading,
  detailUnauthorized,
  detailError,
  children,
}) => {
  if (detailLoading) {
    return <div className="bg-white border border-slate-200 rounded-xl p-8 text-sm text-slate-500">Loading selected default case…</div>;
  }
  if (detailError) {
    return (
      <AlertBanner
        type="error"
        title={detailUnauthorized ? 'Access Denied' : 'Default Case Detail Unavailable'}
        message={detailError}
      />
    );
  }
  if (!selectedCase) {
    return <BlockedCard title="No default case selected" message="Select a case to view its server-owned evidence." />;
  }
  return <>{children}</>;
};

const BlockedCard: React.FC<{ title: string; message: string }> = ({ title, message }) => (
  <div className="bg-white border border-slate-200 rounded-xl p-8 text-center">
    <Lock size={28} className="mx-auto text-slate-300 mb-3" />
    <div className="font-semibold text-slate-700">{title}</div>
    <div className="text-sm text-slate-500 mt-1">{message}</div>
  </div>
);

const FieldGrid: React.FC<{ fields: Array<[string, string]> }> = ({ fields }) => (
  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
    {fields.map(([label, value]) => (
      <div key={label}>
        <div className="text-xs text-slate-500">{label}</div>
        <div className="font-medium text-slate-800 mt-0.5 break-words">{value || '—'}</div>
      </div>
    ))}
  </div>
);

const displayLabel = (value: string) =>
  value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase());

const formatTimestamp = (value: string) =>
  new Intl.DateTimeFormat('en-IN', {
    dateStyle: 'medium',
    timeStyle: 'short',
    timeZone: 'Asia/Kolkata',
  }).format(new Date(value));

const frozenFact = (selectedCase: DefaultCaseProjection, key: string) =>
  selectedCase.non_payment_note?.frozen_case_facts[key] || 'Not recorded';

export default DefaultRecoveryHub;
