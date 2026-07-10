import { AlertCircle, CheckCircle2, XCircle } from 'lucide-react';
import type { EligibilityAssessment } from '../../services/creditAssessmentApi';

const labels: [keyof EligibilityAssessment, string][] = [
  ['member_active_check', 'Active member status'], ['default_check', 'Default history'],
  ['document_check', 'Required document evidence'], ['terms_acceptance_check', 'Terms acceptance'],
  ['purpose_check', 'Agriculture-aligned purpose'], ['nominee_check', 'Nominee eligibility'],
];
const passing = new Set(['pass', 'relaxation', 'no_default', 'complete', 'accepted', 'agriculture_aligned', 'valid']);
const blocking = new Set(['fail', 'default_found', 'incomplete', 'non_agriculture', 'minor']);
const title = (value: string) => value.replace(/_/g, ' ');

const EligibilityChecklist: React.FC<{ assessment: EligibilityAssessment }> = ({ assessment }) => (
  <div className="space-y-4">
    <div className="flex items-center gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
      <div className="flex-1">
        <p className="text-xs text-slate-500 uppercase tracking-wide">Stored eligibility result</p>
        <p className="text-lg font-bold text-slate-900 capitalize">{title(assessment.overall_result)}</p>
        <p className="text-xs text-slate-500 mt-1">{assessment.assessment_notes}</p>
      </div>
      <span className="text-xs font-semibold bg-slate-100 text-slate-700 px-2 py-1 rounded-full">
        {new Date(assessment.assessed_at).toLocaleDateString('en-IN')}
      </span>
    </div>
    <div className="space-y-2">
      {labels.map(([field, label]) => {
        const result = String(assessment[field]);
        const pass = passing.has(result); const fail = blocking.has(result);
        return (
          <div key={field} className={`flex items-start gap-3 p-3 rounded-lg ${pass ? 'bg-green-50' : fail ? 'bg-red-50' : 'bg-amber-50'}`}>
            {pass ? <CheckCircle2 size={16} className="text-green-600 mt-0.5" /> : fail ? <XCircle size={16} className="text-red-600 mt-0.5" /> : <AlertCircle size={16} className="text-amber-600 mt-0.5" />}
            <div className="flex-1 flex items-start justify-between gap-2">
              <span className="text-sm font-medium text-slate-800">{label}</span>
              <span className="text-xs font-semibold text-slate-600 capitalize">{title(result)}</span>
            </div>
          </div>
        );
      })}
    </div>
  </div>
);

export default EligibilityChecklist;
