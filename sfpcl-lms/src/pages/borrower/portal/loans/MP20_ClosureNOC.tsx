import React, { useEffect, useState } from 'react';
import { Archive, CheckCircle2, Download, Shield, Unlock } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import {
  downloadPortalNotice,
  fetchPortalClosures,
  type PortalClosure,
} from '../../../../services/portalApi';

export const MP20ClosureView: React.FC<{
  closures: PortalClosure[];
  loading: boolean;
  error: string | null;
  onDownload: (closure: PortalClosure) => void;
}> = ({ closures, loading, error, onDownload }) => (
  <div className="space-y-6">
    <div>
      <h2 className="text-xl font-bold text-slate-900">Closure & NOC</h2>
      <p className="text-sm text-slate-500 mt-1">Track final closure, NOC issuance, and security return status.</p>
    </div>
    {error && <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-red-700">{error}</div>}
    {loading ? (
      <div className="bg-white rounded-xl border border-slate-100 p-8 text-center text-sm text-slate-500">Loading closure status…</div>
    ) : closures.length === 0 ? (
      <div className="bg-white rounded-xl border border-slate-100 p-8 text-center text-sm text-slate-500">No loan closure records are available yet.</div>
    ) : closures.map(closure => {
      const items = [
        ['Full repayment', closure.full_repayment_status, closure.full_repayment_status === 'confirmed' ? 'All recorded dues are fully repaid.' : 'Closure starts after full repayment.'],
        ['Closure review', closure.closure_review_status, closure.closed_at ? `Completed ${new Date(closure.closed_at).toLocaleDateString()}.` : 'Not started.'],
        ['NOC', closure.noc_status, closure.noc_status === 'issued' ? 'The authorised NOC is available.' : 'Pending authorised issuance.'],
        ['Security return', closure.security_return_status, 'Only return and acknowledgement status is shown.'],
        ['CDSL unpledge', closure.cdsl_unpledge_status, 'Depository release status, where applicable.'],
      ];
      const ready = closure.full_repayment_status === 'confirmed';
      return (
        <div key={closure.loan_account_id} className="space-y-4">
          <div className="bg-white rounded-xl border border-amber-200 p-5">
            <div className="flex items-start gap-3">
              <Archive size={20} className="text-amber-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-amber-900">{closure.loan_account_number}</h3>
                <p className="text-sm text-amber-700 mt-1">
                  {ready ? 'Full repayment is confirmed.' : 'Closure is not ready yet.'}
                </p>
              </div>
            </div>
          </div>
          <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
            <div className="px-6 py-4 bg-slate-50 border-b border-slate-100">
              <h3 className="font-semibold text-slate-900 flex items-center gap-2"><Unlock size={17} className="text-green-600" />Closure Checklist</h3>
            </div>
            <div className="divide-y divide-slate-50">
              {items.map(([label, status, note]) => (
                <div key={label} className="px-6 py-4 flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3 min-w-0">
                    {['confirmed', 'complete', 'issued', 'completed', 'returned', 'released'].includes(status)
                      ? <CheckCircle2 size={17} className="text-green-600 mt-0.5" />
                      : <Shield size={17} className="text-slate-300 mt-0.5" />}
                    <div><p className="text-sm font-semibold text-slate-900">{label}</p><p className="text-xs text-slate-500 mt-0.5">{note}</p></div>
                  </div>
                  <StatusBadge label={status} size="sm" />
                </div>
              ))}
            </div>
          </div>
          {closure.noc_download_url && (
            <button onClick={() => onDownload(closure)} className="flex items-center justify-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50">
              <Download size={16} />Download NOC
            </button>
          )}
        </div>
      );
    })}
  </div>
);

const MP20_ClosureNOC: React.FC = () => {
  const [closures, setClosures] = useState<PortalClosure[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    let active = true;
    fetchPortalClosures()
      .then(rows => { if (active) setClosures(rows); })
      .catch(reason => {
        if (active) setError(reason instanceof AuthSessionError && reason.status === 403
          ? 'You are not authorised to view loan closure details.'
          : 'Closure details could not be loaded. Please try again.');
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  const download = async (closure: PortalClosure) => {
    if (!closure.noc_download_url) return;
    try { await downloadPortalNotice(closure.noc_download_url); }
    catch { setError('The NOC could not be downloaded. Please try again.'); }
  };
  return <MP20ClosureView closures={closures} loading={loading} error={error} onDownload={download} />;
};

export default MP20_ClosureNOC;
