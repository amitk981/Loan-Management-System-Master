import React, { useState } from 'react';
import { Gavel, User, CheckCircle2, XCircle, AlertOctagon, MessageSquare, Paperclip } from 'lucide-react';
import Modal from '../ui/Modal';

interface ApproverSlot {
  role: string;
  name?: string;
  decision?: 'approved' | 'rejected' | 'abstained' | 'pending';
  timestamp?: string;
  reason?: string;
}

interface ApprovalPanelProps {
  applicationNumber: string;
  requestedAmount: number;
  isException?: boolean;
  isSpecialCase?: boolean;
  approvers: ApproverSlot[];
  onDecision?: (decision: 'approved' | 'rejected', reason: string) => void;
}

const decisionConfig = {
  approved:  { icon: <CheckCircle2 size={14} className="text-green-600" />, badge: 'bg-green-100 text-green-700' },
  rejected:  { icon: <XCircle size={14} className="text-red-600" />,        badge: 'bg-red-100 text-red-700' },
  abstained: { icon: <AlertOctagon size={14} className="text-violet-600" />,badge: 'bg-violet-100 text-violet-700' },
  pending:   { icon: <User size={14} className="text-slate-400" />,          badge: 'bg-slate-100 text-slate-500' },
};

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const ApprovalPanel: React.FC<ApprovalPanelProps> = ({
  applicationNumber, requestedAmount, isException, isSpecialCase,
  approvers, onDecision,
}) => {
  const [showModal, setShowModal] = useState(false);
  const [decision, setDecision] = useState<'approved' | 'rejected' | 'clarification' | 'abstain'>('approved');
  const [reason, setReason] = useState('');

  const authorityMatrix = requestedAmount <= 500000
    ? 'CFO + 1 Director'
    : 'CFO + 2 Directors';

  const handleSubmit = () => {
    if (onDecision && reason.trim()) {
      onDecision(decision === 'approved' ? 'approved' : 'rejected', reason);
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
                {approver.timestamp && <span className="text-xs text-slate-400">{approver.timestamp}</span>}
                <span className={`flex items-center gap-1 text-xs font-semibold px-2 py-1 rounded-full ${dc.badge}`}>
                  {dc.icon} {approver.decision ? approver.decision.charAt(0).toUpperCase() + approver.decision.slice(1) : 'Pending'}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Action button */}
      {onDecision && (
        <button
          onClick={() => setShowModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Gavel size={16} />
          Record Sanction Decision
        </button>
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
              disabled={!reason.trim()}
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
              {(['approved', 'rejected', 'clarification', 'abstain'] as const).map(d => (
                <label
                  key={d}
                  className={`flex items-center gap-2 p-3 rounded-lg border cursor-pointer transition-colors ${
                    decision === d
                      ? d === 'rejected' ? 'border-red-400 bg-red-50' : 'border-green-400 bg-green-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <input type="radio" name="decision" value={d} checked={decision === d} onChange={() => setDecision(d)} className="sr-only" />
                  <div className={`w-3 h-3 rounded-full border-2 flex items-center justify-center ${decision === d ? 'border-green-600 bg-green-600' : 'border-slate-300'}`}>
                    {decision === d && <div className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </div>
                  <span className="text-sm font-medium capitalize">{d.replace('_', ' ')}</span>
                </label>
              ))}
            </div>
          </div>

          <div>
            <label className="field-label">
              Reason / Comments <span className="text-red-500">*</span>
            </label>
            <textarea
              value={reason}
              onChange={e => setReason(e.target.value)}
              rows={4}
              placeholder="Provide reason for decision. This will be recorded in the Credit Sanction Register."
              className="field-input resize-none"
            />
            <p className="text-xs text-slate-400 mt-1">Required for all decisions. Will be recorded in Credit Sanction Register.</p>
          </div>

          <div>
            <label className="field-label flex items-center gap-1"><Paperclip size={12} /> Attach supporting note (optional)</label>
            <div className="border-2 border-dashed border-slate-200 rounded-lg p-4 text-center text-sm text-slate-400 hover:border-slate-300 transition-colors cursor-pointer">
              Click to attach note / evidence
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
