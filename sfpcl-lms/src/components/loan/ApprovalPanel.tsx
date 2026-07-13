import React, { useMemo, useState } from 'react';
import { AlertCircle, CheckCircle2, Gavel, MessageSquare, Scale, User, XCircle } from 'lucide-react';
import Modal from '../ui/Modal';
import type { ApprovalApprover, ApprovalAvailableAction } from '../../services/sanctionApi';

interface ApprovalPanelProps {
  applicationNumber: string;
  amount: string;
  authoritySummary: string;
  approvers: ApprovalApprover[];
  excludedApprovers: Array<{ user_id: string; reason: string }>;
  actions: ApprovalAvailableAction[];
  permissions: string[];
  busy?: boolean;
  fieldError?: string;
  onDecision: (action: ApprovalAvailableAction['action_code'], comments: string) => Promise<boolean>;
}

type DecisionActionCode = 'approve' | 'reject' | 'return' | 'abstain';
const actionLabels: Record<DecisionActionCode, string> = {
  approve: 'Approve', reject: 'Reject', return: 'Return for Clarification', abstain: 'Abstain for Conflict',
};
const decisionStyle: Record<string, { className: string; icon: React.ReactNode; label: string }> = {
  approved: { className: 'bg-green-100 text-green-700', icon: <CheckCircle2 size={14} />, label: 'Approved' },
  rejected: { className: 'bg-red-100 text-red-700', icon: <XCircle size={14} />, label: 'Rejected' },
  returned_for_clarification: { className: 'bg-amber-100 text-amber-700', icon: <MessageSquare size={14} />, label: 'Returned' },
  abstained: { className: 'bg-slate-100 text-slate-700', icon: <Scale size={14} />, label: 'Abstained' },
  pending: { className: 'bg-slate-100 text-slate-500', icon: <User size={14} />, label: 'Pending' },
};
const formatMoney = (value: string) => `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2 })}`;

const ApprovalPanel: React.FC<ApprovalPanelProps> = ({ applicationNumber, amount, authoritySummary, approvers, excludedApprovers, actions, permissions, busy = false, fieldError, onDecision }) => {
  const usable = useMemo(() => actions.filter((action): action is ApprovalAvailableAction & { action_code: DecisionActionCode } => action.action_code !== 'record_general_meeting_approval' && action.enabled && permissions.includes(action.required_permission)), [actions, permissions]);
  const [showModal, setShowModal] = useState(false);
  const [selectedAction, setSelectedAction] = useState<DecisionActionCode>('approve');
  const [comments, setComments] = useState('');
  const availableSelection = usable.some(action => action.action_code === selectedAction) ? selectedAction : usable[0]?.action_code;
  const needsReason = availableSelection !== 'approve';
  const valid = Boolean(availableSelection) && (!needsReason || comments.trim().length > 0);
  const close = () => { setShowModal(false); setComments(''); };
  const submit = async () => {
    if (!availableSelection || !valid) return;
    if (await onDecision(availableSelection, comments.trim())) close();
  };

  return <div className="space-y-4">
    <div className="bg-slate-50 border border-slate-200 rounded-lg p-4"><div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Required Approval Authority</div><div className="flex items-center justify-between gap-2"><span className="text-sm font-semibold text-slate-900">{authoritySummary}</span><span className="text-sm text-slate-500 num">{formatMoney(amount)}</span></div></div>
    <div className="space-y-2">{approvers.map(approver => {
      const style = decisionStyle[approver.decision || 'pending'] ?? decisionStyle.pending;
      return <div key={`${approver.role_code}-${approver.user_id}`} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg"><div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0"><User size={16} className="text-slate-500" /></div><div className="flex-1 min-w-0"><div className="text-sm font-medium text-slate-900">{approver.full_name}</div><div className="text-xs text-slate-500">{approver.role_code.replace(/_/g, ' ')}</div></div><span className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${style.className}`}>{style.icon}{style.label}</span></div>;
    })}</div>
    {excludedApprovers.map(approver => <div key={approver.user_id} className="bg-amber-50 border border-amber-200 text-amber-800 text-sm px-4 py-3 rounded-lg flex gap-2"><Scale size={16} className="flex-shrink-0" /><span><strong>Excluded / abstained:</strong> {approver.reason}</span></div>)}
    {usable.length ? <div className="flex items-center gap-3"><button onClick={() => { setSelectedAction(usable[0].action_code); setShowModal(true); }} disabled={busy} className="btn-primary flex items-center gap-2"><Gavel size={16} /> Record My Decision</button><span className="text-sm font-semibold text-amber-600 flex items-center gap-1.5"><AlertCircle size={14} /> Your decision pending</span></div> : <div className="bg-slate-50 border border-slate-200 text-slate-700 text-sm px-4 py-3 rounded-lg flex gap-2"><AlertCircle size={16} className="text-slate-500 flex-shrink-0" /><span>{actions.find(action => action.disabled_reason)?.disabled_reason || 'Read-only — no case action is available to you.'}</span></div>}
    <Modal isOpen={showModal} onClose={close} title={`Sanction Decision — ${applicationNumber}`} subtitle={`Loan amount: ${formatMoney(amount)} · Authority: ${authoritySummary}`} footer={<><button onClick={close} className="btn-secondary">Cancel</button><button onClick={() => void submit()} disabled={!valid || busy} className={availableSelection === 'reject' ? 'btn-destructive' : 'btn-primary'}>Confirm Decision</button></>}>
      <div className="space-y-4"><div><label className="field-label">Decision</label><div className="grid grid-cols-2 gap-3">{usable.map(action => <label key={action.action_code} className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${availableSelection === action.action_code ? action.action_code === 'reject' ? 'border-red-400 bg-red-50' : 'border-green-400 bg-green-50' : 'border-slate-200 hover:border-slate-300'}`}><input type="radio" name="sanction-decision" value={action.action_code} checked={availableSelection === action.action_code} onChange={() => setSelectedAction(action.action_code)} className="sr-only" /><span className="text-sm font-medium">{actionLabels[action.action_code]}</span></label>)}</div></div>
      <div><label htmlFor="sanction-decision-reason" className="field-label">Decision reason{needsReason && <span className="text-red-500"> *</span>}</label><textarea id="sanction-decision-reason" value={comments} onChange={event => setComments(event.target.value)} rows={4} className="field-input resize-none" placeholder="Provide the committee decision reason or comments." />{(fieldError || (needsReason && !comments.trim())) && <p className="text-xs text-red-600 mt-1">{fieldError || 'A reason is required for this action.'}</p>}</div></div>
    </Modal>
  </div>;
};

export default ApprovalPanel;
