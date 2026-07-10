import { AlertTriangle, Info } from 'lucide-react';
import type { LoanLimitAssessment } from '../../services/creditAssessmentApi';

const money = (value: string | null) => value == null ? '—' : `₹${Number(value).toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

const LoanLimitCalculator: React.FC<{ assessment: LoanLimitAssessment }> = ({ assessment }) => (
  <div className="space-y-4">
    {assessment.warnings.map(warning => (
      <div key={warning.code} className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 flex gap-2">
        <AlertTriangle size={16} className="text-amber-600 mt-0.5" />
        <div><p className="text-sm font-semibold text-amber-900">{warning.code}</p><p className="text-sm text-amber-800">{warning.message}</p></div>
      </div>
    ))}
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
      {[
        ['Shareholding-based limit', assessment.shareholding_based_limit_amount],
        ['Land-based limit', assessment.land_based_limit_amount],
        ['Final eligible amount', assessment.final_eligible_loan_amount],
      ].map(([label, value]) => (
        <div key={label} className="bg-slate-50 border border-slate-200 rounded-lg p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">{label}</div>
          <div className="text-xl font-bold text-slate-900 num">{money(value)}</div>
        </div>
      ))}
    </div>
    <div className={`rounded-lg border px-4 py-3 ${assessment.amount_within_limit_flag ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
      <div className="flex items-center justify-between gap-3">
        <span className={`text-sm font-semibold ${assessment.amount_within_limit_flag ? 'text-green-900' : 'text-red-900'}`}>
          Requested amount {assessment.amount_within_limit_flag ? 'is within eligible limit' : 'exceeds eligible limit'}
        </span>
        <span className="font-bold num">{money(assessment.requested_amount)}</span>
      </div>
    </div>
    <div className="bg-slate-50 rounded-lg border border-slate-200 p-4 text-xs text-slate-600 space-y-1">
      <p className="flex items-center gap-1 font-semibold text-slate-700"><Info size={12} /> Stored calculation provenance</p>
      <p>Rule version: {assessment.calculation_rule_version}</p>
      <p>Policy: {assessment.configuration_source.policy_name ?? 'Not supplied'} · Board reference: {assessment.configuration_source.board_approval_reference ?? 'Not supplied'}</p>
      <p>Cultivated acreage: {assessment.land_area_acres} · Share valuation: {money(assessment.valuation_per_share)} · Scale of finance: {money(assessment.scale_of_finance_per_acre_amount)}</p>
    </div>
  </div>
);

export default LoanLimitCalculator;
