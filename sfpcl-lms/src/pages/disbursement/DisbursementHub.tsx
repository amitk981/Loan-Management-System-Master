import React, { useEffect, useMemo, useRef, useState } from 'react';
import { AlertTriangle, Banknote, Check, CheckCircle2, FileText, Lock } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import {
  fetchDisbursementWorkspace,
  submitDisbursementAction,
  type DisbursementAction,
  type DisbursementWorkspaceRow,
} from '../../services/disbursementApi';

interface DisbursementHubProps {
  onOpenApplication: (id: string) => void;
  initialSelectedId?: string;
}

type LoadState = 'loading' | 'ready' | 'unauthorized' | 'error';

const DisbursementHub: React.FC<DisbursementHubProps> = ({ onOpenApplication, initialSelectedId }) => {
  const [rows, setRows] = useState<DisbursementWorkspaceRow[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(initialSelectedId ?? null);
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [message, setMessage] = useState('');
  const [form, setForm] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const idempotencyKeys = useRef<Record<string, string>>({});

  const load = async () => {
    setLoadState('loading'); setMessage('');
    try {
      const result = await fetchDisbursementWorkspace();
      setRows(result.items);
      setSelectedId(current => result.items.some(row => row.workspace_id === current || row.loan_application_id === current)
        ? current : result.items[0]?.workspace_id ?? null);
      setLoadState('ready');
    } catch (error) {
      setRows([]);
      setLoadState(error instanceof AuthSessionError && [401, 403].includes(error.status ?? 0) ? 'unauthorized' : 'error');
      setMessage(error instanceof Error ? error.message : 'Disbursement workspace could not be loaded.');
    }
  };

  useEffect(() => { void load(); }, []);
  const selected = rows.find(row => row.workspace_id === selectedId || row.loan_application_id === selectedId) ?? rows[0] ?? null;
  const createSap = selected?.available_actions.find(action => action.action_code === 'create_sap_request');
  const sendSap = selected?.available_actions.find(action => action.action_code === 'send_sap_request');
  const initiate = selected?.available_actions.find(action => action.action_code === 'initiate_disbursement');
  const completeSap = selected?.available_actions.find(action => action.action_code === 'complete_sap_request');
  const transfer = selected?.available_actions.find(action => action.action_code === 'mark_transfer_successful');
  const advice = selected?.available_actions.find(action => action.action_code === 'send_disbursement_advice');
  const primaryAction = createSap ?? sendSap ?? completeSap ?? initiate ?? transfer ?? advice;
  const selectedWorkspaceId = selected?.workspace_id;
  const initiateFields = primaryAction?.fields;

  useEffect(() => {
    if (!selectedWorkspaceId) { setForm({}); return; }
    const defaults = Object.fromEntries((initiateFields ?? []).map(field => [field.name, field.value ?? '']));
    setForm(defaults);
  }, [selectedWorkspaceId, initiateFields]);

  const runAction = async (action: DisbursementAction) => {
    if (!selected) return;
    setSubmitting(true); setMessage('');
    const isInitiation = action.action_code === 'initiate_disbursement';
    const isIdempotent = isInitiation || ['mark_transfer_successful', 'send_disbursement_advice'].includes(action.action_code);
    const keySlot = `${selected.workspace_id}:${action.action_code}`;
    if (isIdempotent && !idempotencyKeys.current[keySlot]) idempotencyKeys.current[keySlot] = `${action.action_code}-${selected.workspace_id}-${globalThis.crypto?.randomUUID?.() ?? Date.now()}`;
    try {
      const result = await submitDisbursementAction(action, form, isIdempotent ? idempotencyKeys.current[keySlot] : undefined);
      const successMessage = result.idempotency_replayed
        ? 'The original payment initiation was returned; no duplicate was created.'
        : action.action_code === 'create_sap_request' ? 'SAP customer request created successfully.'
          : action.action_code === 'send_sap_request' ? 'SAP customer request sent successfully.'
            : action.action_code === 'complete_sap_request' ? 'SAP customer code confirmed successfully.'
          : action.action_code === 'mark_transfer_successful' ? 'Transfer recorded successfully.'
            : action.action_code === 'send_disbursement_advice' ? 'Disbursement advice queued successfully.'
              : 'Payment initiation recorded successfully.';
      await load();
      setMessage(successMessage);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Payment initiation failed.');
    } finally { setSubmitting(false); }
  };

  if (loadState === 'loading') return <div className="p-6"><div className="card text-sm text-slate-500">Loading SAP and disbursement workspace…</div></div>;
  if (loadState !== 'ready') return <div className="p-6"><AlertBanner type="error" title={loadState === 'unauthorized' ? 'Access Denied' : 'Disbursement Workspace Unavailable'} message={message} /></div>;

  return (
    <div className="p-6 space-y-4">
      <div><h1 className="text-xl font-bold text-slate-900">SAP & Disbursement Hub</h1><p className="text-sm text-slate-500 mt-0.5">Backend-owned SAP, readiness and payment initiation status</p></div>
      {rows.length === 0 ? <Empty /> : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="card p-0 overflow-hidden lg:col-span-1">
            <div className="p-4 bg-slate-50 border-b border-slate-200"><p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Finance Queue ({rows.length})</p></div>
            <div className="divide-y divide-slate-100">{rows.map(row => (
              <button key={row.workspace_id} type="button" onClick={() => setSelectedId(row.workspace_id)} className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 text-left ${selected?.workspace_id === row.workspace_id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}>
                <Banknote size={16} className="text-green-600" /><div className="flex-1 min-w-0"><p className="font-semibold text-slate-900 num text-sm">{row.application_reference_number || row.loan_account_number || 'Pending reference'}</p><p className="text-xs text-slate-500 truncate">{row.member.display_name}</p><p className="text-xs text-green-700 num font-medium">{money(row.disbursement_amount)}</p></div><StatusBadge label={row.bank_transfer_status || row.authorisation_status || row.sap.status} size="sm" />
              </button>
            ))}</div>
          </div>
          {selected && <div className="lg:col-span-2 space-y-4">
            <div className="card"><div className="flex items-start justify-between"><div><div className="flex items-center gap-2"><h2 className="text-lg font-bold text-slate-900 num">{selected.loan_account_number || selected.application_reference_number}</h2><StatusBadge label={selected.readiness.ready_for_disbursement ? 'disbursement_ready' : 'blocked'} size="sm" /></div><p className="text-sm text-slate-500">{selected.member.display_name} · {money(selected.disbursement_amount)}</p></div><button type="button" onClick={() => onOpenApplication(selected.loan_application_id)} className="btn-secondary flex items-center gap-2"><FileText size={14} /> Full Application</button></div></div>
            <div className="card"><h3 className="text-sm font-semibold text-slate-700 mb-3">SAP Customer Code and Bank Verification</h3><div className="grid grid-cols-2 sm:grid-cols-4 gap-3"><Info label="Request status" value={label(selected.sap.status)} /><Info label="Customer code" value={selected.sap.customer_code_masked || 'Pending'} /><Info label="Beneficiary" value={selected.beneficiary_bank ? `${selected.beneficiary_bank.account_number_masked} · ${selected.beneficiary_bank.ifsc_code}` : 'Pending'} /><Info label="Source bank" value={selected.source_bank ? `${selected.source_bank.bank_name} · ${selected.source_bank.account_number_masked}` : 'Pending'} /></div></div>
            <div className="card"><div className="flex items-center justify-between mb-3"><h3 className="text-sm font-semibold text-slate-700">Disbursement Readiness</h3><StatusBadge label={selected.readiness.ready_for_disbursement ? 'Ready' : 'Blocked'} size="sm" /></div><div className="space-y-2">{selected.readiness.checks.map(check => <div key={check.code} className={`rounded-lg p-3 text-sm flex items-start gap-2 ${check.status === 'pass' ? 'bg-green-50 text-green-700' : 'bg-amber-50 text-amber-800'}`}>{check.status === 'pass' ? <Check size={16} /> : <AlertTriangle size={16} />}<div><p className="font-medium">{check.label}</p>{check.reason && <p className="text-xs mt-0.5">{check.reason}</p>}</div></div>)}</div></div>
            {primaryAction && <div className="card"><h3 className="text-sm font-semibold text-slate-700 mb-3">{createSap || sendSap ? 'SAP Customer Request' : initiate ? 'Payment Initiation' : completeSap ? 'SAP Confirmation' : transfer ? 'Transfer Success' : 'Disbursement Advice'}</h3><div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{primaryAction.fields.map(field => <ActionField key={field.name} field={field} value={form[field.name] ?? ''} onChange={value => setForm(current => ({ ...current, [field.name]: value }))} />)}</div>{message && <div className="mt-4"><AlertBanner type={message.includes('success') || message.includes('original') ? 'success' : 'error'} title="Finance action" message={message} /></div>}<button type="button" className="btn-primary mt-4 w-full flex items-center justify-center gap-2" disabled={(Boolean(initiate) && !selected.readiness.ready_for_disbursement) || !primaryAction.enabled || submitting} onClick={() => void runAction(primaryAction)}>{!initiate || selected.readiness.ready_for_disbursement ? <CheckCircle2 size={15} /> : <Lock size={15} />}{submitting ? 'Submitting…' : primaryAction.label}</button>{initiate && (!selected.readiness.ready_for_disbursement || initiate.disabled_reason) && <p className="text-xs text-amber-700 mt-2">{initiate.disabled_reason || 'Payment initiation is disabled until every readiness check passes.'}</p>}</div>}
          </div>}
        </div>
      )}
    </div>
  );
};

const Empty = () => <div className="card text-center py-8"><Check size={32} className="text-green-500 mx-auto mb-3" /><p className="text-slate-600 font-semibold">No applications pending disbursement</p></div>;
const Info = ({ label: key, value }: { label: string; value: string }) => <div className="rounded-lg bg-slate-50 p-3"><p className="text-xs text-slate-500">{key}</p><p className="text-sm font-medium text-slate-900">{value}</p></div>;
const ActionField = ({ field, value, onChange }: { field: DisbursementAction['fields'][number]; value: string; onChange: (value: string) => void }) => <div className={field.type === 'textarea' ? 'sm:col-span-2' : ''}><label className="field-label" htmlFor={`finance-${field.name}`}>{field.label}</label>{field.type === 'textarea' ? <textarea id={`finance-${field.name}`} className="field-input min-h-[90px]" required={field.required} value={value} onChange={event => onChange(event.target.value)} /> : field.type === 'select' ? <select id={`finance-${field.name}`} className="field-input" required={field.required} value={value} onChange={event => onChange(event.target.value)}><option value="">Select</option>{field.options?.map(option => <option key={option.value} value={option.value}>{option.label}</option>)}</select> : <input id={`finance-${field.name}`} className="field-input" type={field.type === 'money' ? 'text' : field.type} required={field.required} value={value} onChange={event => onChange(event.target.value)} />}</div>;
const money = (value: string) => `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
const label = (value: string) => value.replace(/_/g, ' ').replace(/\b\w/g, character => character.toUpperCase());

export default DisbursementHub;
