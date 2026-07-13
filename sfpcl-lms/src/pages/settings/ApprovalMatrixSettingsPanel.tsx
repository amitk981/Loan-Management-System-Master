import React, { useEffect, useState } from 'react';
import { Edit, Shield } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import Modal from '../../components/ui/Modal';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import {
  fetchApprovalMatrixRules,
  supersedeApprovalMatrixRule,
  type ApprovalConfigurationProposal,
  type ApprovalMatrixRule,
  type ApprovalMatrixRuleReplacement,
} from '../../services/approvalRegistersApi';

interface EditForm {
  versionNumber: string;
  effectiveFrom: string;
  effectiveTo: string;
  amountMin: string;
  amountMax: string;
  conditionCode: string;
  requiredRoles: string;
  directorCount: string;
  jointApproval: boolean;
  registerRequired: string;
  reason: string;
}

export const ApprovalMatrixSettingsPanel: React.FC = () => {
  const { currentUser } = useRole();
  const canRead = currentUser.permissions.includes('approvals.matrix.read');
  const canManage = currentUser.permissions.includes('approvals.matrix.manage');
  const [rules, setRules] = useState<ApprovalMatrixRule[]>([]);
  const [state, setState] = useState<'loading' | 'success' | 'error'>(canRead ? 'loading' : 'error');
  const [message, setMessage] = useState(canRead ? '' : 'You do not have approval matrix permission.');
  const [editing, setEditing] = useState<ApprovalMatrixRule | null>(null);
  const [form, setForm] = useState<EditForm | null>(null);
  const [busy, setBusy] = useState(false);
  const [proposal, setProposal] = useState<ApprovalConfigurationProposal | null>(null);

  useEffect(() => {
    if (!canRead) {
      setRules([]);
      setEditing(null);
      setForm(null);
      setProposal(null);
      setState('error');
      setMessage('You do not have approval matrix permission.');
      return;
    }
    let cancelled = false;
    setState('loading');
    fetchApprovalMatrixRules({ page: 1, pageSize: 100 }).then(result => {
      if (cancelled) return;
      setRules(result.items);
      setState('success');
      setMessage('');
    }).catch(error => {
      if (cancelled) return;
      setRules([]);
      setState('error');
      setMessage(error instanceof Error ? error.message : 'Unable to load the approval matrix.');
    });
    return () => { cancelled = true; };
  }, [canRead]);

  const beginEdit = (rule: ApprovalMatrixRule) => {
    setEditing(rule);
    setForm({
      versionNumber: '',
      effectiveFrom: '',
      effectiveTo: '',
      amountMin: rule.amount_min ?? '',
      amountMax: rule.amount_max ?? '',
      conditionCode: rule.condition_code ?? '',
      requiredRoles: rule.required_approver_roles.join(', '),
      directorCount: String(rule.required_director_count),
      jointApproval: rule.joint_approval_required_flag,
      registerRequired: rule.register_required ?? '',
      reason: '',
    });
    setMessage('');
  };

  const submit = async () => {
    if (!editing || !form) return;
    if (!form.versionNumber.trim() || !form.effectiveFrom || !form.reason.trim()) {
      setMessage('Successor version, effective date, and change reason are required.');
      return;
    }
    const payload: ApprovalMatrixRuleReplacement = {
      decision_type: editing.decision_type,
      amount_min: form.amountMin.trim() || null,
      amount_max: form.amountMax.trim() || null,
      condition_code: form.conditionCode.trim() || null,
      required_approver_roles: form.requiredRoles.split(',').map(value => value.trim()).filter(Boolean),
      required_director_count: Number(form.directorCount),
      joint_approval_required_flag: form.jointApproval,
      register_required: form.registerRequired.trim() || null,
      effective_from: form.effectiveFrom,
      effective_to: form.effectiveTo || null,
      version_number: form.versionNumber.trim(),
      reason: form.reason.trim(),
    };
    setBusy(true);
    setMessage('');
    try {
      const created = await supersedeApprovalMatrixRule(editing.approval_matrix_rule_id, payload);
      setProposal(created);
      setEditing(null);
      setForm(null);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to submit the configuration proposal.');
    } finally {
      setBusy(false);
    }
  };

  if (state === 'error') {
    return <AlertBanner type="error" title="Approval matrix unavailable" message={message} />;
  }

  return (
    <div className="max-w-4xl space-y-5">
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex justify-between items-start">
        <div>
          <h3 className="font-semibold text-slate-900 mb-1 flex items-center gap-2"><Shield size={16} className="text-green-600" /> Approval Authority Matrix</h3>
          <p className="text-sm text-slate-500">Approval rules apply after activation. Existing approval cases retain the matrix version used when routed.</p>
        </div>
        <span className="bg-slate-100 text-slate-700 text-xs font-semibold px-2 py-0.5 rounded-full border border-slate-200">Versioned</span>
      </div>

      {proposal && (
        <AlertBanner
          type="success"
          title="Configuration proposal pending approval"
          message={<>Proposal <span className="num font-medium">{proposal.approval_configuration_proposal_id}</span> preserves the active rule until a distinct CFO or Company Secretary approves it.</>}
          onDismiss={() => setProposal(null)}
        />
      )}
      {message && <AlertBanner type="error" title="Matrix change not submitted" message={message} onDismiss={() => setMessage('')} />}

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm min-w-max">
            <thead className="bg-slate-50">
              <tr>
                {['Version', 'Decision type', 'Amount / condition', 'Required authority', 'Minimum approvals', 'Register', 'Effective dates', 'Status'].map(label => (
                  <th key={label} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">{label}</th>
                ))}
                {canManage && <th className="text-right px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Action</th>}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {state === 'loading' ? (
                <tr><td colSpan={canManage ? 9 : 8} className="px-4 py-12 text-center text-slate-400">Loading approval matrix…</td></tr>
              ) : rules.length === 0 ? (
                <tr><td colSpan={canManage ? 9 : 8} className="px-4 py-12 text-center text-slate-400">No approval matrix rules are configured.</td></tr>
              ) : rules.map(rule => (
                <tr key={rule.approval_matrix_rule_id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-800 num">{rule.version_number}</td>
                  <td className="px-4 py-3 text-slate-700 capitalize">{words(rule.decision_type)}</td>
                  <td className="px-4 py-3 text-slate-600 text-xs">{amountCondition(rule)}</td>
                  <td className="px-4 py-3 text-slate-700">{authority(rule)}</td>
                  <td className="px-4 py-3 text-slate-700 text-center">{minimumApprovals(rule)}</td>
                  <td className="px-4 py-3 text-slate-600 text-xs capitalize">{rule.register_required ? words(rule.register_required) : 'None'}</td>
                  <td className="px-4 py-3 text-slate-600 text-xs">{rule.effective_from} — {rule.effective_to ?? 'Current'}</td>
                  <td className="px-4 py-3"><StatusBadge label={rule.status} size="sm" /></td>
                  {canManage && <td className="px-4 py-3 text-right">
                    {rule.status === 'active' && <button aria-label={`Edit ${rule.version_number}`} onClick={() => beginEdit(rule)} className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors"><Edit size={14} /></button>}
                  </td>}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <Modal
        isOpen={Boolean(editing && form)}
        onClose={() => { if (!busy) { setEditing(null); setForm(null); setMessage(''); } }}
        title="Propose Approval Matrix Successor"
        subtitle={editing?.version_number}
        size="lg"
        footer={<>
          <button className="btn-secondary" disabled={busy} onClick={() => { setEditing(null); setForm(null); setMessage(''); }}>Cancel</button>
          <button className="btn-primary" disabled={busy} onClick={() => void submit()}>Submit for Approval</button>
        </>}
      >
        {form && <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Field label="Successor version" value={form.versionNumber} onChange={value => setForm({ ...form, versionNumber: value })} />
          <Field label="Effective from" type="date" value={form.effectiveFrom} onChange={value => setForm({ ...form, effectiveFrom: value })} />
          <Field label="Effective to" type="date" value={form.effectiveTo} onChange={value => setForm({ ...form, effectiveTo: value })} />
          <Field label="Minimum amount" value={form.amountMin} onChange={value => setForm({ ...form, amountMin: value })} />
          <Field label="Maximum amount" value={form.amountMax} onChange={value => setForm({ ...form, amountMax: value })} />
          <Field label="Condition code" value={form.conditionCode} onChange={value => setForm({ ...form, conditionCode: value })} />
          <Field label="Required roles" value={form.requiredRoles} onChange={value => setForm({ ...form, requiredRoles: value })} />
          <Field label="Required Director count" type="number" value={form.directorCount} onChange={value => setForm({ ...form, directorCount: value })} />
          <Field label="Register required" value={form.registerRequired} onChange={value => setForm({ ...form, registerRequired: value })} />
          <label className="flex items-center gap-2 text-sm text-slate-700 mt-6">
            <input type="checkbox" checked={form.jointApproval} onChange={event => setForm({ ...form, jointApproval: event.target.checked })} /> Joint approval required
          </label>
          <label className="md:col-span-2 text-sm font-medium text-slate-700">Change reason
            <textarea aria-label="Change reason" className="field-input mt-1 min-h-24" value={form.reason} onChange={event => setForm({ ...form, reason: event.target.value })} />
          </label>
        </div>}
      </Modal>
    </div>
  );
};

const Field: React.FC<{ label: string; value: string; type?: string; onChange: (value: string) => void }> = ({ label, value, type = 'text', onChange }) => (
  <label className="text-sm font-medium text-slate-700">{label}
    <input aria-label={label} type={type} className="field-input mt-1" value={value} onChange={event => onChange(event.target.value)} />
  </label>
);

const words = (value: string) => value.replace(/_/g, ' ');
const money = (value: string) => `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const amountCondition = (rule: ApprovalMatrixRule) => {
  if (rule.condition_code) return words(rule.condition_code);
  if (rule.amount_min !== null && rule.amount_max !== null) return `${money(rule.amount_min)} to ${money(rule.amount_max)}`;
  if (rule.amount_min !== null) return `From ${money(rule.amount_min)}`;
  if (rule.amount_max !== null) return `Up to ${money(rule.amount_max)}`;
  return 'All amounts';
};

const authority = (rule: ApprovalMatrixRule) => rule.required_approver_roles.map(role => {
  if (role === 'cfo') return 'CFO';
  if (role === 'director') return `${rule.required_director_count} Director${rule.required_director_count === 1 ? '' : 's'}`;
  return words(role).replace(/\b\w/g, (letter: string) => letter.toUpperCase());
}).join(' + ');

const minimumApprovals = (rule: ApprovalMatrixRule) => rule.required_approver_roles.reduce(
  (total, role) => total + (role === 'director' ? rule.required_director_count : 1),
  0,
);
