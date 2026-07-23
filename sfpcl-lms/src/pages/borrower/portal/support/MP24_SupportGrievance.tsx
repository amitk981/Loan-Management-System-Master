import React, { useEffect, useState } from 'react';
import { BadgeCheck, CheckCircle2, FileText, MessageSquareWarning, Send } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import {
  fetchPortalGrievance,
  fetchPortalGrievances,
  submitPortalGrievance,
  type PortalGrievance,
} from '../../../../services/portalApi';

const guideSections = [
  { title: 'Who Can Apply', text: 'Active SFPCL members may apply. Final loan approval is subject to SFPCL review.' },
  { title: 'Allowed Loan Purposes', text: 'Use the facility for eligible crop production, agricultural activity, and other purposes accepted during SFPCL review.' },
  { title: 'Required Documents', text: 'PAN, Aadhaar or OVD, nominee KYC, share certificate where applicable, 7/12 extract, crop plan, six-month bank statement and cancelled cheque may be required.' },
  { title: 'Application Steps', text: 'Complete the application, upload documents, review the declarations, and submit it for completeness checks.' },
  { title: 'After Submission', text: 'SFPCL checks completeness and eligibility, prepares an appraisal, and records the approval outcome.' },
  { title: 'Documentation & Signing', text: 'After sanction, follow the portal instructions for the Term Sheet, Loan Agreement, PoA, tri-party agreement, SH-4, or CDSL pledge.' },
  { title: 'Disbursement', text: 'Funds are processed only after required documents, verification, SAP setup, and payment authorisation are complete.' },
  { title: 'Repayment', text: 'Repayment may be direct or through approved subsidiary deductions. Portal balances update after verification and posting.' },
  { title: 'Closure & NOC', text: 'After complete repayment, SFPCL records closure, security return or unpledge, and issues the NOC through an authorised process.' },
  { title: 'Support & Grievances', text: 'Use the grievance form for application, document, disbursement, repayment, interest, data-correction, or closure questions.' },
] as const;

const categories = [
  ['application_issue', 'Application help'],
  ['document_issue', 'Document issue'],
  ['approval_delay', 'Loan status query'],
  ['disbursement_delay', 'Disbursement query'],
  ['repayment_adjustment_issue', 'Repayment query'],
  ['interest_charge_dispute', 'Interest / invoice query'],
  ['noc_closure_delay', 'Closure / NOC query'],
  ['kyc_data_correction_issue', 'Data correction request'],
  ['other', 'Other complaint'],
] as const;

export const MP24SupportView: React.FC<{
  grievances: PortalGrievance[];
  loading: boolean;
  error: string | null;
  success: PortalGrievance | null;
  submitting: boolean;
  onSubmit: (payload: { grievance_category: string; subject: string; description: string }) => void;
  onSelect?: (grievance: PortalGrievance) => void;
}> = ({ grievances, loading, error, success, submitting, onSubmit, onSelect }) => {
  const [category, setCategory] = useState('');
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [validation, setValidation] = useState<string | null>(null);

  const submit = () => {
    if (!category || !subject.trim() || !description.trim()) {
      setValidation('Choose a category and enter both a subject and message.');
      return;
    }
    setValidation(null);
    onSubmit({ grievance_category: category, subject: subject.trim(), description: description.trim() });
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Support & Grievance</h2>
        <p className="text-sm text-slate-500 mt-1">Raise and track your own service requests, questions, and complaints.</p>
      </div>
      {error && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2"><FileText size={18} className="text-green-600" />Help & Required Documents Guide</h3>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 p-6">
              {guideSections.map(section => (
                <div key={section.title} className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                  <h4 className="text-sm font-semibold text-slate-900 flex items-center gap-2"><BadgeCheck size={15} className="text-green-600" />{section.title}</h4>
                  <p className="text-xs text-slate-600 mt-2 leading-relaxed">{section.text}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2"><MessageSquareWarning size={18} className="text-amber-600" />Raise a New Grievance</h3>
            </div>
            <div className="p-6 space-y-4">
              {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-start gap-3">
                  <CheckCircle2 size={20} className="text-green-600 mt-0.5" />
                  <div><h4 className="font-semibold text-green-900">Grievance submitted</h4><p className="text-sm text-green-700 mt-1">Reference {success.grievance_reference}. Track its status below.</p></div>
                </div>
              )}
              {validation && <p className="text-sm text-red-600">{validation}</p>}
              <div>
                <label htmlFor="grievance-category" className="block text-sm font-medium text-slate-700 mb-1.5">Category <span className="text-red-600">Required</span></label>
                <select id="grievance-category" value={category} onChange={event => setCategory(event.target.value)} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 bg-white">
                  <option value="">Choose a category</option>
                  {categories.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                </select>
              </div>
              <div>
                <label htmlFor="grievance-subject" className="block text-sm font-medium text-slate-700 mb-1.5">Subject <span className="text-red-600">Required</span></label>
                <input id="grievance-subject" value={subject} onChange={event => setSubject(event.target.value)} className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" placeholder="Brief description of the issue" />
              </div>
              <div>
                <label htmlFor="grievance-message" className="block text-sm font-medium text-slate-700 mb-1.5">Message <span className="text-red-600">Required</span></label>
                <textarea id="grievance-message" value={description} onChange={event => setDescription(event.target.value)} rows={4} className="w-full px-4 py-3 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none" placeholder="Please provide details about your issue…" />
              </div>
              <div className="flex justify-end pt-2">
                <button onClick={submit} disabled={submitting} className="flex items-center gap-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-300 disabled:cursor-not-allowed text-white px-6 py-2.5 rounded-lg text-sm font-medium transition-colors">
                  <Send size={16} />{submitting ? 'Submitting…' : 'Submit Grievance'}
                </button>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50"><h3 className="font-semibold text-slate-900">Past Grievances</h3></div>
            {loading ? <div className="p-8 text-center text-sm text-slate-500">Loading grievances…</div>
              : grievances.length === 0 ? <div className="p-8 text-center text-sm text-slate-500">No grievances have been submitted.</div>
              : <div className="divide-y divide-slate-50">
                {grievances.map(grievance => (
                  <button key={grievance.grievance_id} onClick={() => onSelect?.(grievance)} className="w-full text-left p-6 hover:bg-slate-50 transition-colors">
                    <div className="flex items-start justify-between gap-4 mb-2">
                      <div><h4 className="font-semibold text-slate-900">{grievance.subject}</h4><p className="text-xs text-slate-500 mt-1"><span className="font-mono bg-slate-100 px-1.5 py-0.5 rounded text-slate-600">{grievance.grievance_reference}</span> · Logged {new Date(grievance.received_date).toLocaleDateString()}</p></div>
                      <StatusBadge label={grievance.status} size="sm" />
                    </div>
                    <p className="text-sm text-slate-600 mt-2">{grievance.description}</p>
                    {grievance.resolution_summary && <div className="mt-4 bg-slate-50 border border-slate-200 rounded-lg p-4"><p className="text-xs font-semibold text-slate-700 mb-1">SFPCL Response</p><p className="text-sm text-slate-600">{grievance.resolution_summary}</p></div>}
                  </button>
                ))}
              </div>}
          </div>
        </div>
      </div>
    </div>
  );
};

const MP24_SupportGrievance: React.FC = () => {
  const [grievances, setGrievances] = useState<PortalGrievance[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<PortalGrievance | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const select = async (row: PortalGrievance) => {
    try {
      const detail = await fetchPortalGrievance(row.grievance_id);
      setGrievances(rows => rows.map(item => item.grievance_id === detail.grievance_id ? detail : item));
    } catch { setError('Grievance details could not be loaded. Please try again.'); }
  };
  useEffect(() => {
    let active = true;
    fetchPortalGrievances()
      .then(rows => { if (active) setGrievances(rows); })
      .catch(reason => {
        if (active) setError(reason instanceof AuthSessionError && reason.status === 403
          ? 'You are not authorised to view grievances.'
          : 'Grievances could not be loaded. Please try again.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  const submit = async (payload: Parameters<typeof submitPortalGrievance>[0]) => {
    setSubmitting(true); setError(null); setSuccess(null);
    try {
      const grievance = await submitPortalGrievance(payload);
      setSuccess(grievance);
      setGrievances(rows => [grievance, ...rows.filter(row => row.grievance_id !== grievance.grievance_id)]);
    } catch (reason) {
      setError(reason instanceof AuthSessionError && reason.code === 'CONFIGURATION_REQUIRED'
        ? 'Grievance submission is temporarily unavailable because an owner or response deadline is not configured.'
        : 'The grievance could not be submitted. Check the required fields and try again.');
    } finally { setSubmitting(false); }
  };
  return <MP24SupportView grievances={grievances} loading={loading} error={error} success={success} submitting={submitting} onSubmit={submit} onSelect={select} />;
};

export default MP24_SupportGrievance;
