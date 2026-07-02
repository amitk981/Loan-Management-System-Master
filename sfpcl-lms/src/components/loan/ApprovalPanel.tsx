import React, { useState } from 'react';
import { Gavel, User, CheckCircle2, XCircle, AlertOctagon, MessageSquare, Paperclip, AlertCircle, Scale, FileText } from 'lucide-react';
import Modal from '../ui/Modal';

interface ApproverSlot {
  role: string;
  name?: string;
  decision?: 'approved' | 'approved_with_conditions' | 'rejected' | 'clarification' | 'abstained' | 'pending';
  timestamp?: string;
  reason?: string;
  comment?: string;
  evidence?: boolean;
}

interface ApprovalPanelProps {
  applicationNumber: string;
  requestedAmount: number;
  eligibleAmount?: number;
  isException?: boolean;
  isSpecialCase?: boolean;
  approvers: ApproverSlot[];
  onDecision?: (decision: 'approved' | 'rejected', reason: string, slotRole?: string) => void;
}

const decisionConfig = {
  approved:  { icon: <CheckCircle2 size={14} className="text-green-600" />, badge: 'bg-green-100 text-green-700', label: 'Approved' },
  approved_with_conditions: { icon: <CheckCircle2 size={14} className="text-green-600" />, badge: 'bg-green-100 text-green-700', label: 'Approved w/ Cond.' },
  rejected:  { icon: <XCircle size={14} className="text-red-600" />,        badge: 'bg-red-100 text-red-700', label: 'Rejected' },
  clarification: { icon: <MessageSquare size={14} className="text-amber-600" />, badge: 'bg-amber-100 text-amber-700', label: 'Clarification Req.' },
  abstained: { icon: <Scale size={14} className="text-slate-600" />,        badge: 'bg-slate-100 text-slate-700', label: 'Abstained' },
  pending:   { icon: <User size={14} className="text-slate-400" />,          badge: 'bg-slate-100 text-slate-500', label: 'Pending' },
};

import { useRole } from '../../contexts/RoleContext';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const ApprovalPanel: React.FC<ApprovalPanelProps> = ({
  applicationNumber, requestedAmount, eligibleAmount, isException, isSpecialCase,
  approvers, onDecision,
}) => {
  const { can, currentUser } = useRole();
  const [showModal, setShowModal] = useState(false);
  const [decision, setDecision] = useState<'approved' | 'approved_with_conditions' | 'rejected' | 'clarification' | 'abstained'>('approved');
  const [reason, setReason] = useState('');
  const [conditions, setConditions] = useState('');
  const [partialAmount, setPartialAmount] = useState<string>('');
  const [isPartial, setIsPartial] = useState(false);

  const authorityMatrix = requestedAmount <= 500000
    ? 'CFO + 1 Director'
    : 'CFO + 2 Directors';

  const mySlot = approvers.find(a => 
    (currentUser.role === 'cfo' && a.role === 'CFO') ||
    (currentUser.role === 'director' && a.role.startsWith('Director'))
  );

  const canRecordDecision = can('approve_sanction') && mySlot && (mySlot.decision === 'pending' || !mySlot.decision);

  const isValid = () => {
    if (decision === 'approved') {
      if (isPartial && !partialAmount.trim()) return false;
      return true;
    }
    if (decision === 'approved_with_conditions') return conditions.trim().length > 0;
    if (decision === 'rejected' || decision === 'clarification' || decision === 'abstained') return reason.trim().length > 0;
    return false;
  };

  const handleSubmit = () => {
    if (onDecision && isValid()) {
      onDecision(decision === 'approved' || decision === 'approved_with_conditions' ? 'approved' : 'rejected', reason || conditions, mySlot?.role);
    }
    setShowModal(false);
    setReason('');
  };

  return (
    <div className="space-y-4">
      {/* Authority matrix */}
      <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
        <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-3">Required Approval Authority</div>
        <div className="flex items-center justify-between">
          <div>
            <span className="text-sm font-semibold text-slate-900">{authorityMatrix}</span>
            <span className="text-sm text-slate-500 ml-2">— {fmt(requestedAmount)}</span>
          </div>
          <div className="flex gap-2">
            {isException && (
              <span className="text-xs bg-violet-100 text-violet-700 px-2 py-1 rounded-full font-semibold">Exception Register Required</span>
            )}
            {isSpecialCase && (
              <span className="text-xs bg-amber-100 text-amber-700 px-2 py-1 rounded-full font-semibold">General Meeting Approval Required</span>
            )}
          </div>
        </div>
      </div>

      {/* Approver slots */}
      <div className="space-y-2">
        {approvers.map((approver, idx) => {
          const dc = decisionConfig[approver.decision || 'pending'];
          return (
            <div key={idx} className="flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-lg">
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0">
                <User size={16} className="text-slate-500" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium text-slate-900">{approver.name || 'Pending assignment'}</div>
                <div className="text-xs text-slate-500">{approver.role}</div>
                {approver.reason && <div className="text-xs text-slate-400 mt-0.5 italic">"{approver.reason}"</div>}
              </div>
              <div className="flex items-center gap-2">
                {approver.evidence && <span className="text-xs text-blue-600 flex items-center gap-1"><FileText size={12} /> Note attached</span>}
                {approver.timestamp && <span className="text-xs text-slate-400">{approver.timestamp}</span>}
                <span className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${dc.badge}`}>
                  {dc.icon} {dc.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action button */}
      {onDecision && (
        can('approve_sanction') ? (
          canRecordDecision ? (
            <div className="flex items-center gap-3">
              <button
                onClick={() => setShowModal(true)}
                className="btn-primary flex items-center gap-2 w-full justify-center sm:w-auto"
              >
                <Gavel size={16} />
                {currentUser.role === 'cfo' ? 'Record CFO Decision' : 'Record My Decision'}
              </button>
              <span className="text-sm font-semibold text-amber-600 flex items-center gap-1.5">
                <AlertCircle size={14} /> Your decision pending
              </span>
            </div>
          ) : mySlot ? (
            <div className="bg-slate-50 border border-slate-200 text-slate-700 text-sm px-4 py-3 rounded-lg flex items-start sm:items-center flex-col sm:flex-row gap-2">
              <CheckCircle2 size={16} className="text-green-600 flex-shrink-0 mt-0.5 sm:mt-0" />
              <div>
                <span className="font-semibold text-slate-900">Your decision is recorded.</span>
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 border border-slate-200 text-slate-700 text-sm px-4 py-3 rounded-lg flex items-start sm:items-center flex-col sm:flex-row gap-2">
              <AlertCircle size={16} className="text-slate-500 flex-shrink-0 mt-0.5 sm:mt-0" />
              <div>
                <span className="font-semibold text-slate-900">Not assigned.</span>{' '}
                <span className="text-slate-600">You are not assigned to an approval slot for this application.</span>
              </div>
            </div>
          )
        ) : (
          <div className="bg-slate-50 border border-slate-200 text-slate-700 text-sm px-4 py-3 rounded-lg flex items-start sm:items-center flex-col sm:flex-row gap-2">
            <AlertCircle size={16} className="text-slate-500 flex-shrink-0 mt-0.5 sm:mt-0" />
            <div>
              <span className="font-semibold text-slate-900">Locked — Sanction Committee action required.</span>{' '}
              <span className="text-slate-600">You do not have permission to approve or reject this sanction. CFO / Director action required.</span>
            </div>
          </div>
        )
      )}

      {/* Decision modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={`Sanction Decision — ${applicationNumber}`}
        subtitle={`Loan amount: ${fmt(requestedAmount)} · Authority: ${authorityMatrix}`}
        footer={
          <>
            <button onClick={() => setShowModal(false)} className="btn-secondary">Cancel</button>
            <button
              onClick={handleSubmit}
              disabled={!isValid()}
              className={decision === 'rejected' ? 'btn-destructive' : 'btn-primary'}
            >
              Confirm Decision
            </button>
          </>
        }
      >
        <div className="space-y-4">
          <div>
            <label className="field-label">Decision</label>
            <div className="grid grid-cols-2 gap-3">
              {(['approved', 'approved_with_conditions', 'rejected', 'clarification', 'abstained'] as const).map(d => (
                <label
                  key={d}
                  className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${
                    decision === d
                      ? d === 'rejected' ? 'border-red-400 bg-red-50' : 'border-green-400 bg-green-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <input type="radio" name="decision" value={d} checked={decision === d} onChange={() => setDecision(d)} className="sr-only" />
                  <div className={`w-3 h-3 rounded-full border-2 flex items-center justify-center ${decision === d ? (d === 'rejected' ? 'border-red-600 bg-red-600' : 'border-green-600 bg-green-600') : 'border-slate-300'}`}>
                    {decision === d && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </div>
                  <span className="text-sm font-medium capitalize">{d.replace(/_/g, ' ')}</span>
                </label>
              ))}
            </div>
          </div>

          {(decision === 'approved' || decision === 'approved_with_conditions') && (
            <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 space-y-3">
              <label className="flex items-center gap-2 text-sm text-slate-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={isPartial}
                  onChange={e => {
                    setIsPartial(e.target.checked);
                    if (!e.target.checked) setPartialAmount('');
                  }}
                  className="w-4 h-4 accent-green-600 rounded border-slate-300"
                />
                Approve at reduced amount (partial sanction)
              </label>
              
              {isPartial && (
                <div className="pl-6">
                  <label className="block text-xs font-medium text-slate-700 mb-1">Sanctioned Amount <span className="text-red-500">*</span></label>
                  <input
                    type="number"
                    value={partialAmount}
                    onChange={e => setPartialAmount(e.target.value)}
                    placeholder={String(eligibleAmount || requestedAmount)}
                    className="field-input w-full"
                  />
                  {Number(partialAmount) > (eligibleAmount || requestedAmount) && (
                    <p className="text-xs text-red-600 mt-1">Sanction amount cannot exceed eligible/requested limits without exception.</p>
                  )}
                </div>
              )}
            </div>
          )}

          {decision === 'approved_with_conditions' && (
            <div>
              <label className="field-label">
                Conditions <span className="text-red-500">*</span>
              </label>
              <textarea
                value={conditions}
                onChange={e => setConditions(e.target.value)}
                rows={3}
                placeholder="e.g. Subject to CDSL pledge completion within 7 days."
                className="field-input resize-none"
              />
            </div>
          )}

          {decision !== 'approved_with_conditions' && (
            <div>
              <label className="field-label">
                {decision === 'abstained' ? 'Conflict / Abstention Reason' : decision === 'clarification' ? 'Clarification Note' : decision === 'rejected' ? 'Rejection Reason' : 'Reason / Comments'}
                {decision !== 'approved' && <span className="text-red-500"> *</span>}
              </label>
              <textarea
                value={reason}
                onChange={e => setReason(e.target.value)}
                rows={4}
                placeholder={decision === 'abstained' ? 'State nature of conflict of interest...' : 'Provide detail for your decision...'}
                className="field-input resize-none"
              />
              <p className="text-xs text-slate-400 mt-1">Will be recorded in Credit Sanction Register.</p>
            </div>
          )}

          <div>
            <label className="field-label flex items-center gap-1"><Paperclip size={12} /> Attach sanction note / evidence</label>
            <div className="border-2 border-dashed border-slate-200 rounded-lg p-4 text-center text-sm text-slate-400 hover:border-slate-300 transition-colors cursor-pointer bg-slate-50/50">
              Click to upload note or supporting evidence
            </div>
          </div>

          {isException && (
            <div className="bg-violet-50 border border-violet-200 rounded-lg px-4 py-3 flex gap-2">
              <AlertOctagon size={16} className="text-violet-600 flex-shrink-0 mt-0.5" />
              <div className="text-sm text-violet-800">
                This application exceeds the maximum permissible limit. Approval will create an <strong>Exception Register entry</strong>.
              </div>
            </div>
          )}

          {isSpecialCase && (
            <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3">
              <div className="text-sm text-amber-800 font-semibold mb-1 flex items-center gap-1"><MessageSquare size={14} /> Special Case Notice</div>
              <p className="text-sm text-amber-700">Borrower is a Director or Sanction Committee member's relative. General meeting approval evidence must be uploaded before this approval can be finalised.</p>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
};

export default ApprovalPanel;
