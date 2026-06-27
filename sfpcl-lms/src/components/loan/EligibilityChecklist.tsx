import React, { useEffect } from 'react';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';

type CheckResult = 'pass' | 'fail' | 'needs_review' | 'pending' | 'not_required';

interface EligibilityItem {
  id: string;
  label: string;
  result: CheckResult;
  note?: string;
}

interface EligibilityChecklistProps {
  memberId?: string;
  applicationId?: string;
  onComplete?: (allPassed: boolean) => void;
}

const checks: EligibilityItem[] = [
  { id: 'e1', label: 'Applicant is a registered SFPCL member', result: 'pass', note: 'Folio FO-0042 — Active member' },
  { id: 'e2', label: 'Active member status verified', result: 'pass', note: '5 years of continuous produce supply' },
  { id: 'e3', label: 'Individual / FPC active member conditions satisfied', result: 'pass', note: 'Supply to Sahyadri Farms PH Care Ltd. confirmed' },
  { id: 'e4', label: 'No existing default with SFPCL', result: 'pass', note: 'No outstanding default on record' },
  { id: 'e5', label: 'No default with subsidiary / associate companies', result: 'pass', note: 'Confirmed — no subsidiary default' },
  { id: 'e6', label: 'Land documents (7/12 extract) submitted', result: 'pass', note: 'Land area: 3.2 acres, Dindori, Nashik' },
  { id: 'e7', label: 'KYC (PAN + Aadhaar) submitted and verified', result: 'pass', note: 'PAN: ABCDE1234F · Aadhaar: ****4521' },
  { id: 'e8', label: '6-month bank statement submitted', result: 'pass', note: 'RBL Bank account confirmed' },
  { id: 'e9', label: 'Crop plan submitted', result: 'pass', note: 'Grape cultivation, Kharif 2026-27' },
  { id: 'e10', label: 'Loan purpose is crop production / agricultural activity', result: 'pass', note: 'Purpose: Crop production' },
  { id: 'e11', label: 'Borrower accepts Term Sheet and Loan Agreement terms', result: 'not_required', note: 'Not required at appraisal — pending documentation stage' },
  { id: 'e12', label: 'Nominee is not a minor', result: 'pass', note: 'Nominee age: 34 years' },
];

const resultConfig = {
  pass:         { icon: <CheckCircle2 size={16} className="text-green-600" />, bg: 'bg-green-50', text: 'text-green-800', label: 'Pass' },
  fail:         { icon: <XCircle size={16} className="text-red-600" />,        bg: 'bg-red-50',   text: 'text-red-800',   label: 'Fail' },
  needs_review: { icon: <AlertCircle size={16} className="text-amber-600" />,  bg: 'bg-amber-50', text: 'text-amber-800', label: 'Needs Review' },
  pending:      { icon: <AlertCircle size={16} className="text-slate-400" />,  bg: 'bg-slate-50', text: 'text-slate-600', label: 'Pending' },
  not_required: { icon: <CheckCircle2 size={16} className="text-slate-400" />, bg: 'bg-slate-50', text: 'text-slate-500', label: 'Not required at appraisal' },
};

const EligibilityChecklist: React.FC<EligibilityChecklistProps> = ({ onComplete }) => {
  const activeChecks = checks.filter(c => c.result !== 'not_required');
  const pass = activeChecks.filter(c => c.result === 'pass').length;
  const total = activeChecks.length;
  const hasBlocking = activeChecks.some(c => c.result === 'fail');

  useEffect(() => {
    onComplete?.(!hasBlocking && pass === total);
  }, []);

  return (
    <div className="space-y-4">
      {/* Summary bar */}
      <div className="flex items-center gap-4 p-4 bg-slate-50 rounded-lg border border-slate-200">
        <div className="flex items-center gap-2">
          <div className="text-2xl font-bold text-green-700 num">{pass}/{total}</div>
          <div className="text-sm text-slate-600">checks passed</div>
        </div>
        <div className="flex-1 bg-slate-200 rounded-full h-2 overflow-hidden">
          <div className="bg-green-500 h-2 rounded-full transition-all" style={{ width: `${(pass/total)*100}%` }} />
        </div>
        {hasBlocking ? (
          <span className="text-xs font-semibold text-red-700 bg-red-100 px-2 py-1 rounded-full">Blocking issues</span>
        ) : (
          <span className="text-xs font-semibold text-amber-700 bg-amber-100 px-2 py-1 rounded-full">Appraisal can proceed · documentation pending</span>
        )}
      </div>

      {/* Checklist */}
      <div className="space-y-2">
        {checks.map(check => {
          const config = resultConfig[check.result];
          return (
            <div key={check.id} className={`flex items-start gap-3 p-3 rounded-lg border border-transparent ${config.bg}`}>
              <div className="mt-0.5 flex-shrink-0">{config.icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2">
                  <span className={`text-sm font-medium ${config.text}`}>{check.label}</span>
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded-full flex-shrink-0 ${
                    check.result === 'pass' ? 'bg-green-100 text-green-700' :
                    check.result === 'fail' ? 'bg-red-100 text-red-700' :
                    check.result === 'needs_review' ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'
                  }`}>{config.label}</span>
                </div>
                {check.note && <p className="text-xs text-slate-500 mt-0.5">{check.note}</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default EligibilityChecklist;
