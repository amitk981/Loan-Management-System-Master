import React, { useCallback, useEffect, useRef, useState } from 'react';
import { AlertTriangle, Calendar, CheckCircle2, Clock, FileText, Lock, Shield } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import {
  createRecoveryDecision,
  completeRecoveryAction,
  fetchDefaultCase,
  fetchDefaultCases,
  fetchRecoveryApprovalCase,
  initiateRecoveryAction,
  uploadRecoveryEvidence,
  type DefaultCaseProjection,
  type RecoveryApprovalProjection,
  type RecoveryDecisionProjection,
} from '../../services/recoveryApi';
import { formatMoney } from '../../utils/formatMoney';

type DefaultTab = 'cases' | 'grace' | 'non_payment' | 'recovery' | 'security';
type LoadState = 'loading' | 'ready' | 'empty' | 'unauthorized' | 'error';

const tabs: Array<{ id: DefaultTab; label: string }> = [
  { id: 'cases', label: 'All Cases' },
  { id: 'grace', label: 'Grace Period / Extension' },
  { id: 'non_payment', label: 'Non-Payment Note' },
  { id: 'recovery', label: 'Recovery Approval' },
  { id: 'security', label: 'Security Invocation' },
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
  const [approvalCase, setApprovalCase] = useState<RecoveryApprovalProjection | null>(null);
  const [approvalLoading, setApprovalLoading] = useState(false);
  const [approvalError, setApprovalError] = useState('');
  const [approvalUnauthorized, setApprovalUnauthorized] = useState(false);
  const [decisionReason, setDecisionReason] = useState('');
  const [decisionFieldError, setDecisionFieldError] = useState('');
  const [decisionMessage, setDecisionMessage] = useState('');
  const [decisionBusy, setDecisionBusy] = useState(false);
  const [invocationDate, setInvocationDate] = useState('');
  const [invocationRemarks, setInvocationRemarks] = useState('');
  const [recoveryEvidence, setRecoveryEvidence] = useState<File | null>(null);
  const [recoveredAmount, setRecoveredAmount] = useState('');
  const [recoveryBusy, setRecoveryBusy] = useState(false);
  const [recoveryMessage, setRecoveryMessage] = useState('');
  const [interactionMode, setInteractionMode] = useState('borrower_contact');
  const [interactionPerson, setInteractionPerson] = useState('');
  const [interactionSummary, setInteractionSummary] = useState('');
  const [interactionNextAction, setInteractionNextAction] = useState('');
  const [interactionComplaintRaised, setInteractionComplaintRaised] = useState(false);
  const [interactionGrievanceReference, setInteractionGrievanceReference] = useState('');
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

  useEffect(() => {
    const approvalCaseId = selectedCase?.non_payment_note?.approval_case_id;
    setApprovalCase(null);
    setApprovalError('');
    setApprovalUnauthorized(false);
    setDecisionReason('');
    setDecisionFieldError('');
    setDecisionMessage('');
    if (!approvalCaseId) return;
    let current = true;
    setApprovalLoading(true);
    void fetchRecoveryApprovalCase(approvalCaseId)
      .then(projection => {
        if (current) setApprovalCase(projection);
      })
      .catch(error => {
        if (!current) return;
        setApprovalUnauthorized(
          error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0),
        );
        setApprovalError(error instanceof Error ? error.message : 'Approval evidence could not be loaded.');
      })
      .finally(() => {
        if (current) setApprovalLoading(false);
      });
    return () => {
      current = false;
    };
  }, [selectedCase?.default_case_id, selectedCase?.non_payment_note?.approval_case_id]);

  const recordRecoveryDecision = async () => {
    const control = selectedCase?.recovery_decision_control;
    if (
      !selectedCase
      || !control?.enabled
      || !control.approval_case_id
      || !control.decision
    ) return;
    const reason = decisionReason.trim();
    if (!reason) {
      setDecisionFieldError('A decision reason is required.');
      return;
    }
    setDecisionBusy(true);
    setDecisionFieldError('');
    setDecisionMessage('');
    try {
      await createRecoveryDecision(selectedCase.default_case_id, {
        approval_case_id: control.approval_case_id,
        decision: control.decision,
        decision_reason: reason,
      });
      const canonical = await fetchDefaultCase(selectedCase.default_case_id);
      setSelectedCase(canonical);
      setCases(current => current.map(row => (
        row.default_case_id === canonical.default_case_id ? canonical : row
      )));
      setDecisionMessage('Recovery decision recorded from canonical backend state.');
    } catch (error) {
      if (error instanceof AuthSessionError && error.fieldErrors?.decision_reason) {
        setDecisionFieldError(error.fieldErrors.decision_reason);
      }
      setDecisionMessage(error instanceof Error ? error.message : 'Recovery decision could not be recorded.');
    } finally {
      setDecisionBusy(false);
    }
  };

  const refreshSelectedCase = async () => {
    if (!selectedCase) return;
    const canonical = await fetchDefaultCase(selectedCase.default_case_id);
    setSelectedCase(canonical);
    setCases(current => current.map(row => (
      row.default_case_id === canonical.default_case_id ? canonical : row
    )));
  };

  const submitRecoveryAction = async () => {
    if (
      !selectedCase
      || !recoveryEvidence
      || !invocationRemarks.trim()
      || !interactionPerson.trim()
      || !interactionSummary.trim()
      || !interactionNextAction.trim()
      || !interactionGrievanceReference.trim()
    ) return;
    const decision = selectedCase.recovery_decision;
    const executeAction = decision?.available_actions.find(
      action => action.action_code === 'execute_recovery',
    );
    const existingAction = selectedCase.recovery_action;
    const canComplete = existingAction?.available_actions.some(
      action => action.action_code === 'complete_recovery',
    );
    if ((!existingAction && !executeAction) || (existingAction && !canComplete)) return;
    setRecoveryBusy(true);
    setRecoveryMessage('');
    try {
      const documentId = await uploadRecoveryEvidence(selectedCase.loan_account_id, recoveryEvidence);
      if (!existingAction) {
        const initiatedAt = invocationDate
          ? new Date(`${invocationDate}T00:00:00`).toISOString()
          : new Date().toISOString();
        await initiateRecoveryAction(decision!.recovery_decision_id, {
          action_type: executeAction!.action_type,
          initiated_at: initiatedAt,
          evidence_document_ids: [documentId],
          remarks: invocationRemarks.trim(),
          interaction_log: [{
            interaction_at: initiatedAt,
            interaction_mode: interactionMode,
            person_contacted: interactionPerson.trim(),
            summary: interactionSummary.trim(),
            next_action: interactionNextAction.trim(),
            complaint_raised: interactionComplaintRaised,
            grievance_reference: interactionGrievanceReference.trim(),
            evidence_document_ids: [documentId],
          }],
        });
        setRecoveryMessage('Approved recovery action initiated successfully.');
      } else {
        await completeRecoveryAction(existingAction.recovery_action_id, {
          completed_at: new Date().toISOString(),
          amount_recovered: recoveredAmount,
          evidence_document_ids: [documentId],
          remarks: invocationRemarks.trim(),
        });
        setRecoveryMessage('Verified recovery proceeds posted successfully.');
      }
      await refreshSelectedCase();
      setRecoveryEvidence(null);
      setInvocationRemarks('');
      setRecoveredAmount('');
      setInteractionPerson('');
      setInteractionSummary('');
      setInteractionNextAction('');
      setInteractionComplaintRaised(false);
      setInteractionGrievanceReference('');
    } catch (error) {
      setRecoveryMessage(error instanceof Error ? error.message : 'Recovery action failed.');
    } finally {
      setRecoveryBusy(false);
    }
  };

  const securityAvailable = Boolean(
    selectedCase?.recovery_action
    || (
      selectedCase?.recovery_decision?.status === 'approved'
      && selectedCase.recovery_decision.available_actions.some(
        action => action.action_code === 'execute_recovery',
      )
    ),
  );
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
            (() => {
              const disabled = tab.id === 'security' && !securityAvailable;
              return (
            <button
              key={tab.id}
              type="button"
              disabled={disabled}
              aria-describedby={disabled ? 'recovery-execution-blocker' : undefined}
              onClick={() => {
                if (!disabled) setActiveTab(tab.id);
              }}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : disabled
                    ? 'border-transparent text-slate-300 cursor-not-allowed'
                    : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {disabled && <Lock size={12} />}
              {tab.label}
              {tab.id === 'cases' && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${
                  activeTab === 'cases' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
                }`}>
                  {totalCount}
                </span>
              )}
            </button>
              );
            })()
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
            ['Recovery Workflow', selectedCase?.recovery_decision
              ? `${displayLabel(selectedCase.recovery_decision.status)} / ${securityAvailable ? 'Execution Available' : 'Execution Blocked'}`
              : 'Decision Not Recorded'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
              <p className="text-xs font-semibold text-slate-700">{label}</p>
              <p className="text-xs text-slate-500 mt-2">{value}</p>
            </div>
          ))}
        </div>
      </div>

      {!securityAvailable && (
        <AlertBanner
          type="warning"
          title="Recovery execution blocked"
          message={(
            <span id="recovery-execution-blocker">
              Security invocation remains unavailable until the canonical recovery decision projects
              an approved executable action.
            </span>
          )}
        />
      )}

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
        {activeTab === 'recovery' && (
          <RecoveryDecisionPanel
            selectedCase={selectedCase}
            detailLoading={detailLoading}
            detailUnauthorized={detailUnauthorized}
            detailError={message}
            approvalCase={approvalCase}
            approvalLoading={approvalLoading}
            approvalUnauthorized={approvalUnauthorized}
            approvalError={approvalError}
            decisionReason={decisionReason}
            decisionFieldError={decisionFieldError}
            decisionMessage={decisionMessage}
            decisionBusy={decisionBusy}
            onReasonChange={value => {
              setDecisionReason(value);
              if (value.trim()) setDecisionFieldError('');
            }}
            onRecord={() => void recordRecoveryDecision()}
          />
        )}
        {activeTab === 'security' && selectedCase && (
          <SecurityInvocationPanel
            selectedCase={selectedCase}
            invocationDate={invocationDate}
            invocationRemarks={invocationRemarks}
            recoveryEvidence={recoveryEvidence}
            recoveredAmount={recoveredAmount}
            recoveryBusy={recoveryBusy}
            recoveryMessage={recoveryMessage}
            interactionMode={interactionMode}
            interactionPerson={interactionPerson}
            interactionSummary={interactionSummary}
            interactionNextAction={interactionNextAction}
            interactionComplaintRaised={interactionComplaintRaised}
            interactionGrievanceReference={interactionGrievanceReference}
            onInvocationDateChange={setInvocationDate}
            onInvocationRemarksChange={setInvocationRemarks}
            onRecoveryEvidenceChange={setRecoveryEvidence}
            onRecoveredAmountChange={setRecoveredAmount}
            onInteractionModeChange={setInteractionMode}
            onInteractionPersonChange={setInteractionPerson}
            onInteractionSummaryChange={setInteractionSummary}
            onInteractionNextActionChange={setInteractionNextAction}
            onInteractionComplaintRaisedChange={setInteractionComplaintRaised}
            onInteractionGrievanceReferenceChange={setInteractionGrievanceReference}
            onSubmit={() => void submitRecoveryAction()}
          />
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
                  ['6', 'Recovery action approval', selectedCase.recovery_decision ? 'complete' : 'locked'],
                  ['7', 'Security invocation / legal action', selectedCase.recovery_action
                    ? selectedCase.recovery_action.action_status === 'completed' ? 'complete' : 'active'
                    : selectedCase.recovery_decision?.status === 'approved'
                      && selectedCase.recovery_decision.available_actions.some(action => action.action_code === 'execute_recovery')
                      ? 'active'
                      : 'locked'],
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

interface RecoveryDecisionPanelProps extends PanelProps {
  approvalCase: RecoveryApprovalProjection | null;
  approvalLoading: boolean;
  approvalUnauthorized: boolean;
  approvalError: string;
  decisionReason: string;
  decisionFieldError: string;
  decisionMessage: string;
  decisionBusy: boolean;
  onReasonChange: (value: string) => void;
  onRecord: () => void;
}

const RecoveryDecisionPanel: React.FC<RecoveryDecisionPanelProps> = ({
  selectedCase,
  detailLoading,
  detailUnauthorized,
  detailError,
  approvalCase,
  approvalLoading,
  approvalUnauthorized,
  approvalError,
  decisionReason,
  decisionFieldError,
  decisionMessage,
  decisionBusy,
  onReasonChange,
  onRecord,
}) => (
  <div className="max-w-3xl space-y-5">
    <DetailBoundary detailLoading={detailLoading} detailUnauthorized={detailUnauthorized} detailError={detailError} selectedCase={selectedCase}>
      {selectedCase?.recovery_decision ? (
        <>
          {decisionMessage && (
            <AlertBanner
              type={decisionMessage.startsWith('Recovery decision recorded') ? 'success' : 'error'}
              title={decisionMessage.startsWith('Recovery decision recorded') ? 'Decision Recorded' : 'Decision Update Failed'}
              message={decisionMessage}
            />
          )}
          <section className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between gap-3 mb-4">
              <h3 className="font-semibold text-slate-900">Terminal Recovery Decision</h3>
              <StatusBadge label={selectedCase.recovery_decision.status} />
            </div>
            <FieldGrid fields={[
              ['Decision', displayLabel(selectedCase.recovery_decision.decision)],
              ['Approval Case', selectedCase.recovery_decision.approval_case_id || 'Not recorded'],
              ['Decided By Role', displayLabel(selectedCase.recovery_decision.decided_by_role_code || 'not_recorded')],
              ['Decided At', selectedCase.recovery_decision.decided_at ? formatTimestamp(selectedCase.recovery_decision.decided_at) : 'Not recorded'],
            ]} />
            <div className="mt-4">
              <div className="text-xs text-slate-500">Mandatory Decision Reason</div>
              <div className="text-sm font-medium text-slate-800 mt-1">
                {selectedCase.recovery_decision.decision_reason || 'Not exposed'}
              </div>
            </div>
            <ApprovalEvidence evidence={selectedCase.recovery_decision.approval_evidence} />
          </section>
        </>
      ) : !selectedCase?.non_payment_note ? (
        <BlockedCard
          title="Recovery decision blocked"
          message="A frozen Non-Payment Note is required before recovery approval can be decided."
        />
      ) : !selectedCase.non_payment_note.approval_case_id ? (
        <BlockedCard
          title="Recovery decision blocked"
          message="The frozen Non-Payment Note is not linked to approval evidence."
        />
      ) : approvalLoading ? (
        <div className="bg-white border border-slate-200 rounded-xl p-8 text-sm text-slate-500">
          Loading recovery approval evidence…
        </div>
      ) : approvalError ? (
        <AlertBanner
          type="error"
          title={approvalUnauthorized ? 'Access Denied' : 'Recovery Approval Unavailable'}
          message={approvalError}
        />
      ) : approvalCase ? (
        <PendingRecoveryDecision
          selectedCase={selectedCase}
          approvalCase={approvalCase}
          decisionReason={decisionReason}
          decisionFieldError={decisionFieldError}
          decisionMessage={decisionMessage}
          decisionBusy={decisionBusy}
          onReasonChange={onReasonChange}
          onRecord={onRecord}
        />
      ) : (
        <BlockedCard
          title="Recovery approval evidence not available"
          message="The backend did not return the note-linked approval case."
        />
      )}
    </DetailBoundary>
  </div>
);

const PendingRecoveryDecision: React.FC<{
  selectedCase: DefaultCaseProjection;
  approvalCase: RecoveryApprovalProjection;
  decisionReason: string;
  decisionFieldError: string;
  decisionMessage: string;
  decisionBusy: boolean;
  onReasonChange: (value: string) => void;
  onRecord: () => void;
}> = ({
  selectedCase,
  approvalCase,
  decisionReason,
  decisionFieldError,
  decisionMessage,
  decisionBusy,
  onReasonChange,
  onRecord,
}) => {
  const control = selectedCase.recovery_decision_control;
  const blocker = control?.disabled_reason
    || (!control?.enabled ? 'Recovery decision is not available from canonical backend state.' : '');
  return (
    <>
      <AlertBanner
        type={blocker ? 'warning' : 'info'}
        title={blocker ? 'Recovery decision blocked' : 'Frozen approval evidence ready'}
        message={blocker || 'The action below is fixed by the terminal backend approval and cannot be changed in the browser.'}
      />
      <section className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between gap-3 mb-4">
          <h3 className="font-semibold text-slate-900">Recovery Approval Evidence</h3>
          <StatusBadge label={approvalCase.current_status} />
        </div>
        <FieldGrid fields={[
          ['Approval Case', approvalCase.approval_case_id],
          ['Source Note', approvalCase.related_entity_id],
          ['Source-Permitted Decision', displayLabel(approvalCase.reason_for_approval)],
          ['Decision Date', approvalCase.decision_date || 'Not recorded'],
          ['Required Authorities', String(approvalCase.required_approvers.length)],
          ['Recorded Approvals', String(approvalCase.approval_actions.filter(row => row.decision === 'approved').length)],
          ['Conflict Exclusions', String(approvalCase.excluded_approvers.length)],
          ['Frozen Principal', formatMoney(selectedCase.non_payment_note!.outstanding_principal_amount)],
        ]} />
        <div className="mt-5 space-y-2">
          <div className="text-xs font-semibold text-slate-700">Required approval authority</div>
          {approvalCase.required_approvers.map(approver => (
            <div key={`${approver.role_code}-${approver.user_id}`} className="flex items-center justify-between rounded-lg bg-slate-50 border border-slate-100 p-3">
              <div>
                <div className="text-sm font-medium text-slate-800">{approver.full_name || 'Named backend approver'}</div>
                <div className="text-xs text-slate-500">{displayLabel(approver.role_code)}</div>
              </div>
              <StatusBadge label={approver.decision || 'pending'} size="sm" />
            </div>
          ))}
        </div>
        {approvalCase.approval_actions.length > 0 && (
          <div className="mt-5 space-y-2">
            <div className="text-xs font-semibold text-slate-700">Recorded approval decisions</div>
            {approvalCase.approval_actions.map(action => (
              <div key={action.approval_action_id} className="rounded-lg bg-slate-50 border border-slate-100 p-3">
                <div className="flex items-center justify-between gap-3">
                  <div className="text-sm font-medium text-slate-800">{action.full_name || displayLabel(action.role_code)}</div>
                  <StatusBadge label={action.decision} size="sm" />
                </div>
                <div className="text-xs text-slate-500 mt-1">{formatTimestamp(action.acted_at)} · {action.comments}</div>
              </div>
            ))}
          </div>
        )}
        {approvalCase.excluded_approvers.length > 0 && (
          <div className="mt-5 space-y-2">
            <div className="text-xs font-semibold text-slate-700">Conflict exclusions</div>
            {approvalCase.excluded_approvers.map(exclusion => (
              <AlertBanner
                key={`${exclusion.user_id}-${exclusion.conflict_code}`}
                type="warning"
                title={displayLabel(exclusion.conflict_code)}
                message={exclusion.reason}
              />
            ))}
          </div>
        )}
      </section>
      {!blocker && (
        <section className="bg-white border border-slate-200 rounded-xl p-6">
          <h3 className="font-semibold text-slate-900 mb-4">Record Recovery Decision</h3>
          <div className="mb-4">
            <label htmlFor="recovery-decision-action" className="block text-sm font-medium text-slate-700 mb-1.5">
              Approved recovery action
            </label>
            <div id="recovery-decision-action" className="field-input bg-slate-50">
              {displayLabel(control?.decision || 'not_available')}
            </div>
          </div>
          <div>
            <label htmlFor="recovery-decision-reason" className="block text-sm font-medium text-slate-700 mb-1.5">
              Decision reason
            </label>
            <textarea
              id="recovery-decision-reason"
              className="field-input min-h-24"
              value={decisionReason}
              onChange={event => onReasonChange(event.target.value)}
              aria-invalid={Boolean(decisionFieldError)}
              disabled={decisionBusy}
            />
            {decisionFieldError && <p className="text-xs text-red-600 mt-1">{decisionFieldError}</p>}
          </div>
          {decisionMessage && !decisionMessage.startsWith('Recovery decision recorded') && (
            <div className="mt-4">
              <AlertBanner type="error" title="Decision Not Recorded" message={decisionMessage} />
            </div>
          )}
          <div className="flex justify-end mt-4">
            <button type="button" className="btn-primary" onClick={onRecord} disabled={decisionBusy}>
              {decisionBusy ? 'Recording…' : 'Record Recovery Decision'}
            </button>
          </div>
        </section>
      )}
    </>
  );
};

const SecurityInvocationPanel: React.FC<{
  selectedCase: DefaultCaseProjection;
  invocationDate: string;
  invocationRemarks: string;
  recoveryEvidence: File | null;
  recoveredAmount: string;
  recoveryBusy: boolean;
  recoveryMessage: string;
  interactionMode: string;
  interactionPerson: string;
  interactionSummary: string;
  interactionNextAction: string;
  interactionComplaintRaised: boolean;
  interactionGrievanceReference: string;
  onInvocationDateChange: (value: string) => void;
  onInvocationRemarksChange: (value: string) => void;
  onRecoveryEvidenceChange: (value: File | null) => void;
  onRecoveredAmountChange: (value: string) => void;
  onInteractionModeChange: (value: string) => void;
  onInteractionPersonChange: (value: string) => void;
  onInteractionSummaryChange: (value: string) => void;
  onInteractionNextActionChange: (value: string) => void;
  onInteractionComplaintRaisedChange: (value: boolean) => void;
  onInteractionGrievanceReferenceChange: (value: string) => void;
  onSubmit: () => void;
}> = ({
  selectedCase,
  invocationDate,
  invocationRemarks,
  recoveryEvidence,
  recoveredAmount,
  recoveryBusy,
  recoveryMessage,
  interactionMode,
  interactionPerson,
  interactionSummary,
  interactionNextAction,
  interactionComplaintRaised,
  interactionGrievanceReference,
  onInvocationDateChange,
  onInvocationRemarksChange,
  onRecoveryEvidenceChange,
  onRecoveredAmountChange,
  onInteractionModeChange,
  onInteractionPersonChange,
  onInteractionSummaryChange,
  onInteractionNextActionChange,
  onInteractionComplaintRaisedChange,
  onInteractionGrievanceReferenceChange,
  onSubmit,
}) => {
  const decision = selectedCase.recovery_decision;
  const projectedAction = decision?.available_actions.find(action => action.action_code === 'execute_recovery');
  const action = selectedCase.recovery_action;
  const canComplete = action?.available_actions.some(item => item.action_code === 'complete_recovery');
  if (!selectedCase.recovery_action && !projectedAction) {
    return (
      <BlockedCard
        title="Security invocation blocked"
        message="The canonical recovery decision does not project an executable recovery action."
      />
    );
  }
  return (
    <div className="max-w-3xl space-y-5">
      <AlertBanner
        type="success"
        title="Approved recovery execution available"
        message="This control is exposed only from the canonical decision's execute_recovery action."
      />
      <section className="bg-white border border-slate-200 rounded-xl p-6">
        <div className="flex items-center justify-between gap-3 mb-4">
          <h3 className="font-semibold text-slate-900">Security Invocation</h3>
          <StatusBadge label={selectedCase.recovery_action?.action_status || decision?.status || 'approved'} />
        </div>
        <FieldGrid fields={[
          ['Recovery Decision', decision?.recovery_decision_id || 'Not recorded'],
          ['Approved Action', displayLabel(projectedAction?.action_type || decision?.decision || 'not_recorded')],
          ['Security Type', displayLabel(action?.source_security.security_type || 'validated_on_initiation')],
          ['Execution Status', displayLabel(action?.action_status || 'ready_to_initiate')],
        ]} />
        {action?.interaction_log.map(item => (
          <div key={item.interaction_at} className="bg-slate-50 border border-slate-100 rounded-lg p-3 text-sm mt-4">
            <div className="font-medium">{displayLabel(item.interaction_mode)}</div>
            <div className="text-slate-600 mt-1">{item.summary}</div>
            <a className="text-green-700 text-xs" href={item.grievance_reference}>Grievance route</a>
          </div>
        ))}
        {(!action || canComplete) && (
          <div className="space-y-4 mt-5">
            {!action && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-invocation-date">
                  Invocation date
                </label>
                <input
                  id="recovery-invocation-date"
                  type="date"
                  value={invocationDate}
                  onChange={event => onInvocationDateChange(event.target.value)}
                  className="field-input"
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-evidence">
                Recovery evidence
              </label>
              <input
                id="recovery-evidence"
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={event => onRecoveryEvidenceChange(event.target.files?.[0] ?? null)}
                className="field-input"
              />
            </div>
            {action && (
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovered-amount">
                  Verified amount recovered
                </label>
                <input
                  id="recovered-amount"
                  value={recoveredAmount}
                  onChange={event => onRecoveredAmountChange(event.target.value)}
                  className="field-input"
                />
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-remarks">
                Recovery action remarks
              </label>
              <textarea
                id="recovery-remarks"
                value={invocationRemarks}
                onChange={event => onInvocationRemarksChange(event.target.value)}
                rows={3}
                className="field-input resize-none"
              />
            </div>
            {!action && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-interaction-mode">
                    Interaction mode
                  </label>
                  <select
                    id="recovery-interaction-mode"
                    className="field-select"
                    value={interactionMode}
                    onChange={event => onInteractionModeChange(event.target.value)}
                  >
                    <option value="borrower_contact">Borrower contact</option>
                    <option value="call">Call</option>
                    <option value="visit">Visit</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-interaction-person">
                    Person contacted
                  </label>
                  <input
                    id="recovery-interaction-person"
                    className="field-input"
                    value={interactionPerson}
                    onChange={event => onInteractionPersonChange(event.target.value)}
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-interaction-summary">
                    Interaction summary
                  </label>
                  <textarea
                    id="recovery-interaction-summary"
                    className="field-input resize-none"
                    value={interactionSummary}
                    onChange={event => onInteractionSummaryChange(event.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-next-action">
                    Next action
                  </label>
                  <input
                    id="recovery-next-action"
                    className="field-input"
                    value={interactionNextAction}
                    onChange={event => onInteractionNextActionChange(event.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1.5" htmlFor="recovery-grievance-reference">
                    Grievance reference or route
                  </label>
                  <input
                    id="recovery-grievance-reference"
                    className="field-input"
                    value={interactionGrievanceReference}
                    onChange={event => onInteractionGrievanceReferenceChange(event.target.value)}
                  />
                </div>
                <label className="flex items-center gap-2 text-sm text-slate-700 md:col-span-2">
                  <input
                    type="checkbox"
                    checked={interactionComplaintRaised}
                    onChange={event => onInteractionComplaintRaisedChange(event.target.checked)}
                  />
                  Borrower raised a complaint
                </label>
              </div>
            )}
            {recoveryMessage && (
              <AlertBanner
                type={recoveryMessage.includes('successfully') ? 'success' : 'error'}
                title={recoveryMessage.includes('successfully') ? 'Recovery Updated' : 'Recovery Action Failed'}
                message={recoveryMessage}
              />
            )}
            <button
              type="button"
              onClick={onSubmit}
              disabled={
                !recoveryEvidence
                || !invocationRemarks.trim()
                || recoveryBusy
                || (Boolean(action) && !recoveredAmount.trim())
                || (!action && (
                  !interactionPerson.trim()
                  || !interactionSummary.trim()
                  || !interactionNextAction.trim()
                  || !interactionGrievanceReference.trim()
                ))
              }
              className="btn-primary"
            >
              <Shield size={16} />
              {recoveryBusy ? 'Submitting…' : action ? 'Complete and Post Proceeds' : 'Initiate Approved Recovery'}
            </button>
          </div>
        )}
        {action?.action_status === 'completed' && (
          <AlertBanner
            type="success"
            title="Recovery action completed"
            message={`Verified amount recovered: ${formatMoney(action.amount_recovered || '0.00')}. External SAP status: ${displayLabel(action.external_sap_status)}.`}
          />
        )}
      </section>
    </div>
  );
};

const ApprovalEvidence: React.FC<{
  evidence: RecoveryDecisionProjection['approval_evidence'];
}> = ({ evidence }) => {
  if (!evidence) return null;
  return (
    <div className="mt-5">
      <div className="text-xs font-semibold text-slate-700 mb-2">Frozen approval authority</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
        {(evidence.required_approvers ?? []).map(approver => (
          <div key={`${approver.role_code}-${approver.user_id}`} className="rounded-lg bg-slate-50 border border-slate-100 p-3 text-sm">
            <div className="font-medium text-slate-800">{approver.full_name || 'Named backend approver'}</div>
            <div className="text-xs text-slate-500">{displayLabel(approver.role_code)}</div>
          </div>
        ))}
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
        {(evidence.approval_actions ?? []).map(action => (
          <div key={action.approval_action_id} className="rounded-lg bg-slate-50 border border-slate-100 p-3 text-sm">
            <div className="font-medium text-slate-800">{action.approver_display_name}</div>
            <div className="text-xs text-slate-500">
              {displayLabel(action.approver_role_code)} · {displayLabel(action.decision)} · {formatTimestamp(action.acted_at)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

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
