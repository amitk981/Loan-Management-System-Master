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
      <div className="flex items-center gap-2">
        <div className={`text-2xl font-bold num ${assessment.overall_result === 'eligible' ? 'text-green-700' : assessment.overall_result === 'ineligible' ? 'text-red-700' : 'text-amber-700'}`}>
          {[assessment.member_active_check, assessment.default_check, assessment.document_check, assessment.terms_acceptance_check, assessment.purpose_check, assessment.nominee_check].filter(value => passing.has(value)).length}/6
        </div>
        <div className="text-sm text-slate-600">checks passed</div>
      </div>
      <div className="flex-1 bg-slate-200 rounded-full h-2 overflow-hidden">
        <div className={`h-2 rounded-full ${assessment.overall_result === 'eligible' ? 'bg-green-500' : assessment.overall_result === 'ineligible' ? 'bg-red-500' : 'bg-amber-500'}`} style={{ width: `${([assessment.member_active_check, assessment.default_check, assessment.document_check, assessment.terms_acceptance_check, assessment.purpose_check, assessment.nominee_check].filter(value => passing.has(value)).length / 6) * 100}%` }} />
      </div>
      <span className={`text-xs font-semibold px-2 py-1 rounded-full capitalize ${assessment.overall_result === 'eligible' ? 'text-green-700 bg-green-100' : assessment.overall_result === 'ineligible' ? 'text-red-700 bg-red-100' : 'text-amber-700 bg-amber-100'}`}>
        {title(assessment.overall_result)}
      </span>
    </div>
    <div className="space-y-2">
      {labels.map(([field, label]) => {
        const result = String(assessment[field]);
        const pass = passing.has(result); const fail = blocking.has(result);
        return (
          <div key={field} className={`flex items-start gap-3 p-3 rounded-lg border border-transparent ${pass ? 'bg-green-50' : fail ? 'bg-red-50' : 'bg-amber-50'}`}>
            {pass ? <CheckCircle2 size={16} className="text-green-600 mt-0.5" /> : fail ? <XCircle size={16} className="text-red-600 mt-0.5" /> : <AlertCircle size={16} className="text-amber-600 mt-0.5" />}
            <div className="flex-1 flex items-start justify-between gap-2">
              <span className="text-sm font-medium text-slate-800">{label}</span>
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full capitalize ${pass ? 'bg-green-100 text-green-700' : fail ? 'bg-red-100 text-red-700' : 'bg-amber-100 text-amber-700'}`}>{title(result)}</span>
            </div>
          </div>
        );
      })}
    </div>
    <p className="text-xs text-slate-500">{assessment.assessment_notes} · Assessed {new Date(assessment.assessed_at).toLocaleDateString('en-IN')}</p>
  </div>
);

export default EligibilityChecklist;
