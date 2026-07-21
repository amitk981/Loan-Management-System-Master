import React, { useEffect, useState } from 'react';
import { ArrowLeft, Copy, Landmark } from 'lucide-react';
import AlertBanner from '../../../../components/ui/AlertBanner';
import { fetchPortalDirectRepaymentInstructions, PortalDirectRepaymentInstructions } from '../../../../services/portalApi';
import { money, portalLoanError } from './MP15_MyLoans';

const MP18_DirectRepaymentInfo: React.FC<{ loanAccountId: string | null; onBack: () => void }> = ({ loanAccountId, onBack }) => {
  const [instructions, setInstructions] = useState<PortalDirectRepaymentInstructions | null>(null);
  const [loading, setLoading] = useState(Boolean(loanAccountId));
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let current = true;
    if (!loanAccountId) { setLoading(false); return; }
    fetchPortalDirectRepaymentInstructions(loanAccountId).then(data => { if (current) setInstructions(data); }).catch(reason => { if (current) setError(portalLoanError(reason)); }).finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [loanAccountId]);
  const copy = (value: string | null) => { if (value) void navigator.clipboard?.writeText(value); };
  return <div className="space-y-6"><div><h2 className="text-xl font-bold text-slate-900">Direct Repayment Information</h2><p className="text-sm text-slate-500 mt-1">Approved RTGS / NEFT instructions for your selected loan.</p></div>{loanAccountId && <button type="button" onClick={onBack} className="flex items-center gap-2 text-sm font-medium text-slate-600"><ArrowLeft size={16} />Back to My Loans</button>}{!loanAccountId && <AlertBanner type="info" title="Select a loan from My Loans to view repayment instructions." />}{loading && <AlertBanner type="info" title="Loading repayment instructions…" />}{!loading && error && <AlertBanner type="error" title={error} />}{!loading && !error && instructions && !instructions.available && <AlertBanner type="warning" title="Approved direct repayment instructions are not currently available. Contact SFPCL Accounts before transferring funds." />}{!loading && !error && instructions?.available && <><div className="bg-white rounded-xl border border-slate-100 p-5"><h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2"><Landmark size={16} className="text-green-600" />SFPCL Repayment Bank Details</h3><div className="grid grid-cols-1 sm:grid-cols-2 gap-4">{[['Beneficiary Name', instructions.beneficiary_name], ['Bank Name', instructions.bank_name], ['Account Number', instructions.account_number_masked], ['IFSC Code', instructions.ifsc], ['Required Narration', instructions.required_narration], ['Amount Due', money(instructions.amount_due)]].map(([label, value]) => <div key={label} className="bg-slate-50 rounded-lg p-3 flex items-start justify-between gap-3"><div><p className="text-xs text-slate-500">{label}</p><p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p></div><button type="button" aria-label={`Copy ${label}`} onClick={() => copy(value)}><Copy size={14} className="text-slate-300" /></button></div>)}</div></div><AlertBanner type="info" title="Payment verification" message={instructions.disclaimer} /></>}</div>;
};
export default MP18_DirectRepaymentInfo;
