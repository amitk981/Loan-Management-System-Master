import React, { useEffect, useState } from 'react';
import { Plus, Settings } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import Modal from '../../components/ui/Modal';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import {
  createLoanPolicyVersion,
  fetchLoanPolicyVersions,
  type CreateLoanPolicyVersion,
  type LoanPolicyVersion,
} from '../../services/loanPolicyApi';

type FormState = Record<keyof CreateLoanPolicyVersion, string>;

const integerFields = new Set<keyof CreateLoanPolicyVersion>([
  'short_term_duration_months', 'min_secured_loan_months', 'max_secured_loan_years',
  'rekyc_frequency_months', 'record_retention_years', 'grace_period_months',
  'non_intentional_extension_months',
]);

const nullableFields = new Set<keyof CreateLoanPolicyVersion>([
  'effective_to', 'min_secured_loan_months', 'max_secured_loan_years', 'share_limit_percentage',
  'per_share_cap_amount', 'interest_benchmark', 'penal_interest_rate', 'board_approval_reference',
]);

const fields: Array<{ key: keyof CreateLoanPolicyVersion; label: string; type?: string }> = [
  { key: 'policy_name', label: 'Policy name' },
  { key: 'policy_version', label: 'New version' },
  { key: 'effective_from', label: 'Effective from', type: 'date' },
  { key: 'effective_to', label: 'Effective to', type: 'date' },
  { key: 'short_term_duration_months', label: 'Short-term duration (months)', type: 'number' },
  { key: 'min_secured_loan_months', label: 'Minimum secured-loan term (months)', type: 'number' },
  { key: 'max_secured_loan_years', label: 'Maximum secured-loan term (years)', type: 'number' },
  { key: 'approval_threshold_amount', label: 'Approval threshold amount', type: 'number' },
  { key: 'default_scale_of_finance_per_acre_amount', label: 'Scale of finance per acre', type: 'number' },
  { key: 'share_limit_percentage', label: 'Share limit percentage', type: 'number' },
  { key: 'per_share_cap_amount', label: 'Per-share cap amount', type: 'number' },
  { key: 'interest_rate_type', label: 'Interest-rate type' },
  { key: 'interest_benchmark', label: 'Interest benchmark / source' },
  { key: 'penal_interest_rate', label: 'Penal interest rate', type: 'number' },
  { key: 'rekyc_frequency_months', label: 'Re-KYC frequency (months)', type: 'number' },
  { key: 'record_retention_years', label: 'Record retention (years)', type: 'number' },
  { key: 'grace_period_months', label: 'Grace period (months)', type: 'number' },
  { key: 'non_intentional_extension_months', label: 'Non-intentional extension (months)', type: 'number' },
  { key: 'board_approval_reference', label: 'Board approval reference' },
];

export const LoanPolicySettingsPanel: React.FC = () => {
  const { currentUser } = useRole();
  const canRead = currentUser.permissions.includes('config.loan_policy.read');
  const canManage = currentUser.permissions.includes('config.loan_policy.manage');
  const [policies, setPolicies] = useState<LoanPolicyVersion[]>([]);
  const [state, setState] = useState<'loading' | 'success' | 'error'>(canRead ? 'loading' : 'error');
  const [message, setMessage] = useState(canRead ? '' : 'You do not have loan-policy configuration permission.');
  const [form, setForm] = useState<FormState | null>(null);
  const [busy, setBusy] = useState(false);
  const [created, setCreated] = useState<LoanPolicyVersion | null>(null);

  const load = () => {
    if (!canRead) {
      setPolicies([]);
      setState('error');
      setMessage('You do not have loan-policy configuration permission.');
      return Promise.resolve();
    }
    setState('loading');
    return fetchLoanPolicyVersions({ page: 1, pageSize: 100 }).then(rows => {
      setPolicies(rows);
      setState('success');
      setMessage('');
    }).catch(error => {
      setPolicies([]);
      setState('error');
      setMessage(error instanceof Error ? error.message : 'Unable to load loan-policy configuration.');
    });
  };

  useEffect(() => {
    let cancelled = false;
    if (!canRead) {
      setPolicies([]);
      setState('error');
      setMessage('You do not have loan-policy configuration permission.');
      return;
    }
    setState('loading');
    fetchLoanPolicyVersions({ page: 1, pageSize: 100 }).then(rows => {
      if (cancelled) return;
      setPolicies(rows);
      setState('success');
      setMessage('');
    }).catch(error => {
      if (cancelled) return;
      setPolicies([]);
      setState('error');
      setMessage(error instanceof Error ? error.message : 'Unable to load loan-policy configuration.');
    });
    return () => { cancelled = true; };
  }, [canRead]);

  const beginCreate = (source: LoanPolicyVersion) => {
    setForm(Object.fromEntries(fields.map(({ key }) => [key, String(source[key] ?? '')])) as FormState);
    setMessage('');
  };

  const submit = async () => {
    if (!form) return;
    const missing = fields.filter(({ key }) => !nullableFields.has(key) && !form[key].trim());
    if (missing.length) {
      setMessage(`${missing.map(field => field.label).join(', ')} required.`);
      return;
    }
    const payload = Object.fromEntries(fields.map(({ key }) => {
      const value = form[key].trim();
      if (!value && nullableFields.has(key)) return [key, null];
      if (integerFields.has(key)) return [key, Number(value)];
      return [key, value];
    })) as CreateLoanPolicyVersion;
    setBusy(true);
    setMessage('');
    try {
      const successor = await createLoanPolicyVersion(payload);
      setCreated(successor);
      setForm(null);
      await load();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : 'Unable to create the loan-policy version.');
    } finally {
      setBusy(false);
    }
  };

  if (state === 'error' && policies.length === 0) {
    return <AlertBanner type="error" title="Loan policy unavailable" message={message} />;
  }

  const current = policies.find(policy => policy.status === 'active') ?? policies[0];

  return (
    <div className="max-w-4xl space-y-5">
      <div className="bg-white border border-slate-200 rounded-xl p-6 flex items-start justify-between gap-4">
        <div>
          <h3 className="font-semibold text-slate-900 mb-1 flex items-center gap-2"><Settings size={16} className="text-green-600" /> Loan Policy Versions</h3>
          <p className="text-sm text-slate-500">Values come from the versioned loan-policy configuration service. Historical calculations retain their original version.</p>
        </div>
        {canManage && current ? (
          <button onClick={() => beginCreate(current)} className="flex items-center gap-2 text-sm text-green-700 font-medium border border-green-200 bg-green-50 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-colors">
            <Plus size={14} /> Create new policy version
          </button>
        ) : <span className="bg-slate-100 text-slate-700 text-xs font-semibold px-2 py-0.5 rounded-full border border-slate-200">Read-only access</span>}
      </div>

      {created && <AlertBanner type="success" title="Draft policy version created" message={`${created.policy_version} is stored as a new draft. Activation remains a separate governed action.`} onDismiss={() => setCreated(null)} />}
      {message && !form && <AlertBanner type="error" title="Policy version not created" message={message} onDismiss={() => setMessage('')} />}

      <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm min-w-max">
            <thead className="bg-slate-50"><tr>
              {['Policy', 'Version', 'Effective dates', 'Approval threshold', 'Share rule', 'Scale of finance', 'Interest', 'Compliance', 'Board reference', 'Status'].map(label => <th key={label} className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">{label}</th>)}
            </tr></thead>
            <tbody className="divide-y divide-slate-100">
              {state === 'loading' ? <tr><td colSpan={10} className="px-4 py-12 text-center text-slate-400">Loading loan-policy versions…</td></tr>
                : policies.length === 0 ? <tr><td colSpan={10} className="px-4 py-12 text-center text-slate-400">No loan-policy versions are configured.</td></tr>
                  : policies.map(policy => <tr key={policy.loan_policy_config_id} className="hover:bg-slate-50">
                    <td className="px-4 py-3 font-medium text-slate-800">{policy.policy_name}</td>
                    <td className="px-4 py-3 text-slate-700 num">{policy.policy_version}</td>
                    <td className="px-4 py-3 text-slate-600 text-xs">{policy.effective_from} — {policy.effective_to ?? (policy.status === 'active' ? 'Current' : 'Not set')}</td>
                    <td className="px-4 py-3 text-slate-700 num">₹{policy.approval_threshold_amount}</td>
                    <td className="px-4 py-3 text-slate-600 text-xs">{policy.share_limit_percentage ? `${policy.share_limit_percentage}%` : 'No percentage'} · {policy.per_share_cap_amount ? `₹${policy.per_share_cap_amount} cap` : 'No cap'}</td>
                    <td className="px-4 py-3 text-slate-700 num">₹{policy.default_scale_of_finance_per_acre_amount}/acre</td>
                    <td className="px-4 py-3 text-slate-600 text-xs capitalize">{policy.interest_rate_type}{policy.interest_benchmark ? ` · ${policy.interest_benchmark}` : ''}</td>
                    <td className="px-4 py-3 text-slate-600 text-xs">Re-KYC {policy.rekyc_frequency_months}m · retain {policy.record_retention_years}y · grace {policy.grace_period_months}m</td>
                    <td className="px-4 py-3 text-slate-600 text-xs">{policy.board_approval_reference ?? 'Not supplied'}</td>
                    <td className="px-4 py-3"><StatusBadge label={policy.status} size="sm" /></td>
                  </tr>)}
            </tbody>
          </table>
        </div>
      </div>

      <Modal isOpen={Boolean(form)} onClose={() => !busy && setForm(null)} title="Create new policy version" size="lg" footer={<>
        <button onClick={() => setForm(null)} disabled={busy} className="px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 rounded-lg">Cancel</button>
        <button onClick={submit} disabled={busy} className="px-4 py-2 text-sm font-medium text-white bg-green-600 hover:bg-green-700 rounded-lg disabled:opacity-50">{busy ? 'Creating…' : 'Create draft version'}</button>
      </>}>
        {form && <div className="space-y-4">
          {message && <AlertBanner type="error" title="Policy version not created" message={message} onDismiss={() => setMessage('')} />}
          <div className="grid grid-cols-2 gap-4">{fields.map(field => <label key={field.key} className="text-sm text-slate-700">{field.label}
            <input aria-label={field.label} type={field.type ?? 'text'} value={form[field.key]} onChange={event => setForm({ ...form, [field.key]: event.target.value })} className="field-input mt-1" />
          </label>)}</div>
        </div>}
      </Modal>
    </div>
  );
};
