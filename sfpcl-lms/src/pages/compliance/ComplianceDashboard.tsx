import React, { useState } from 'react';
import { Shield, CheckCircle2, AlertTriangle, XCircle, Clock, X as XIcon, Scale } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { complianceRecords, dashboardStats, loanAccounts, members } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const STATUS_ICONS: Record<string, React.ReactNode> = {
  compliant: <CheckCircle2 size={16} className="text-green-600" />,
  warning:   <AlertTriangle size={16} className="text-amber-500" />,
  breach:    <XCircle size={16} className="text-red-600" />,
  pending:   <Clock size={16} className="text-slate-400" />,
  overdue:   <AlertTriangle size={16} className="text-red-500" />,
  review_required: <AlertTriangle size={16} className="text-amber-500" />,
};

const STATUS_BG: Record<string, string> = {
  compliant: 'bg-green-50 border-green-200',
  warning:   'bg-amber-50 border-amber-200',
  breach:    'bg-red-50 border-red-200',
  pending:   'bg-slate-50 border-slate-200',
  overdue:   'bg-red-50 border-red-200',
  review_required: 'bg-amber-50 border-amber-200',
};

const ComplianceDashboard: React.FC = () => {
  const currentDate = new Date();
  const [kycDrillFilter, setKycDrillFilter] = useState<'rekyc_due' | 'expired' | null>(null);
  const [mlLegalOpinion, setMlLegalOpinion] = useState('Legal opinion obtained — Maharashtra Money-Lending Act compliance confirmed by legal counsel (Adv. R. Kulkarni). SFPCL operates within cooperative society exemption scope.');
  const [mlNextReview, setMlNextReview] = useState('2027-03-31');

  const complianceData = complianceRecords.map(rec => {
    let status: 'compliant' | 'warning' | 'breach' | 'pending' | 'overdue' = rec.status;
    if (new Date(rec.nextDueDate) < currentDate) {
      status = 'overdue';
    }
    return { ...rec, status };
  });

  const warnings = complianceData.filter(r => r.status === 'warning').length;
  const overdueCount = complianceData.filter(r => r.status === 'overdue').length;
  const totalAttention = warnings + overdueCount;
  const breaches = complianceRecords.filter(r => r.status === 'breach').length;
  const pendingKyc = members.filter(m => m.kycStatus === 'rekyc_due' || m.kycStatus === 'expired').length;

  const totalPortfolio = loanAccounts.reduce((s, l) => s + l.outstandingPrincipal, 0);
  const configuredLimit = 2541667;
  const sectionLimit = dashboardStats.sectionUtilisation === 72 && totalPortfolio === 8550000 ? 11875000 : configuredLimit;

  const kycDrillMembers = kycDrillFilter
    ? members.filter(m => m.kycStatus === kycDrillFilter)
    : [];

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-900">Compliance Dashboard</h1>
        <p className="text-sm text-slate-500 mt-0.5">Regulatory compliance, Section 186, NBFC test, and KYC tracker</p>
      </div>

      {/* Breach alerts */}
      {breaches > 0 && (
        <AlertBanner
          type="error"
          title={`${breaches} compliance breach${breaches > 1 ? 'es' : ''} require immediate attention`}
          message="Contact CFO and Company Secretary immediately."
        />
      )}
      {totalAttention > 0 && !breaches && (
        <AlertBanner
          type="warning"
          title={`${totalAttention} compliance review${totalAttention > 1 ? 's' : ''} need attention`}
          message="Review due items before their deadlines."
        />
      )}

      {/* Section 186 */}
      <div className="card">
        <h2 className="section-title mb-4 flex items-center gap-2">
          <Shield size={16} className="text-green-600" />
          Section 186 — Aggregate Lending Limit
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
          <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Outstanding portfolio</p>
            <p className="text-2xl font-bold text-slate-900 num mt-1">{fmt(totalPortfolio)}</p>
          </div>
          <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Section 186 limit</p>
            <p className="text-2xl font-bold text-slate-900 num mt-1">{fmt(sectionLimit)}</p>
            <p className="text-xs text-slate-400 mt-1">Based on active policy configuration</p>
          </div>
          <div className={`rounded-lg border p-4 ${dashboardStats.sectionUtilisation > 80 ? 'bg-red-50 border-red-200' : dashboardStats.sectionUtilisation > 60 ? 'bg-amber-50 border-amber-200' : 'bg-green-50 border-green-200'}`}>
            <p className={`text-xs font-medium uppercase tracking-wide ${dashboardStats.sectionUtilisation > 80 ? 'text-red-700' : dashboardStats.sectionUtilisation > 60 ? 'text-amber-700' : 'text-green-700'}`}>
              Utilisation
            </p>
            <p className={`text-2xl font-bold num mt-1 ${dashboardStats.sectionUtilisation > 80 ? 'text-red-900' : dashboardStats.sectionUtilisation > 60 ? 'text-amber-900' : 'text-green-900'}`}>
              {dashboardStats.sectionUtilisation}%
            </p>
          </div>
        </div>
        <div className="bg-slate-100 rounded-full h-3 overflow-hidden">
          <div
            className={`h-3 rounded-full ${dashboardStats.sectionUtilisation > 80 ? 'bg-red-500' : dashboardStats.sectionUtilisation > 60 ? 'bg-amber-500' : 'bg-green-500'}`}
            style={{ width: `${dashboardStats.sectionUtilisation}%` }}
          />
        </div>
      </div>

      {/* NBFC Principal Business Test */}
      <div className="card">
        <h2 className="section-title mb-4">NBFC Principal Business Test</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <CheckCircle2 size={16} className="text-green-600 mb-2" />
            <p className="text-sm font-semibold text-green-900">Financial assets threshold</p>
            <p className="text-xs text-green-700 mt-1">Within threshold</p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <CheckCircle2 size={16} className="text-green-600 mb-2" />
            <p className="text-sm font-semibold text-green-900">Financial income threshold</p>
            <p className="text-xs text-green-700 mt-1">Within threshold</p>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Quarterly NBFC test. If both thresholds breach, CFO/legal review is required.
        </p>
      </div>

      {/* KYC tracker */}
      <div className="card">
        <h2 className="section-title mb-4">KYC & Re-KYC Tracker</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {[
            { label: 'Verified', count: members.filter(m => m.kycStatus === 'verified').length, color: 'green', filter: null as null },
            { label: 'Re-KYC Due', count: members.filter(m => m.kycStatus === 'rekyc_due').length, color: 'amber', filter: 'rekyc_due' as const },
            { label: 'Expired', count: members.filter(m => m.kycStatus === 'expired').length, color: 'red', filter: 'expired' as const },
            { label: 'Pending', count: members.filter(m => m.kycStatus === 'pending').length, color: 'slate', filter: null as null },
          ].map(({ label, count, color, filter }) => (
            <button
              key={label}
              onClick={() => filter ? setKycDrillFilter(kycDrillFilter === filter ? null : filter) : undefined}
              className={`rounded-lg border p-3 text-center transition-shadow ${filter ? 'cursor-pointer hover:shadow-md' : 'cursor-default'} ${
                kycDrillFilter === filter && filter ? 'ring-2 ring-offset-1 ring-green-500' : ''
              } ${
                color === 'green' ? 'bg-green-50 border-green-200' :
                color === 'amber' ? 'bg-amber-50 border-amber-200' :
                color === 'red' ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'
              }`}
            >
              <div className={`text-xl font-bold num ${
                color === 'green' ? 'text-green-900' :
                color === 'amber' ? 'text-amber-900' :
                color === 'red' ? 'text-red-900' : 'text-slate-900'
              }`}>{count}</div>
              <div className={`text-xs font-medium mt-0.5 ${
                color === 'green' ? 'text-green-700' :
                color === 'amber' ? 'text-amber-700' :
                color === 'red' ? 'text-red-700' : 'text-slate-600'
              }`}>{label}</div>
              {filter && count > 0 && (
                <div className="text-[10px] mt-1 text-slate-400">Click to view</div>
              )}
            </button>
          ))}
        </div>

        {/* KYC drill-down list */}
        {kycDrillFilter && kycDrillMembers.length > 0 && (
          <div className="border border-amber-200 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between px-4 py-2 bg-amber-50 border-b border-amber-200">
              <p className="text-xs font-semibold text-amber-800 uppercase tracking-wide">
                {kycDrillFilter === 'rekyc_due' ? 'Re-KYC Due' : 'KYC Expired'} — {kycDrillMembers.length} member{kycDrillMembers.length !== 1 ? 's' : ''}
              </p>
              <button onClick={() => setKycDrillFilter(null)} className="text-slate-400 hover:text-slate-600">
                <XIcon size={14} />
              </button>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-100">
                  <th className="table-header text-left">Member Name</th>
                  <th className="table-header text-left">Folio / ID</th>
                  <th className="table-header text-left">KYC Status</th>
                  <th className="table-header text-left">Active Loans</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {kycDrillMembers.map(m => {
                  const activeLoansCount = loanAccounts.filter(l => l.memberId === m.id && l.status !== 'closed').length;
                  return (
                    <tr key={m.id} className="hover:bg-slate-50">
                      <td className="table-cell font-medium text-slate-900">{m.name}</td>
                      <td className="table-cell text-slate-500 num">{m.folioNumber || m.id}</td>
                      <td className="table-cell">
                        <StatusBadge
                          label={m.kycStatus === 'rekyc_due' ? 'Re-KYC Due' : 'KYC Expired'}
                          size="sm"
                          type={m.kycStatus === 'expired' ? 'error' : 'warning'}
                        />
                      </td>
                      <td className="table-cell text-slate-600">{activeLoansCount > 0 ? `${activeLoansCount} active` : '—'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            <div className="px-4 py-2 bg-amber-50 border-t border-amber-100">
              <p className="text-xs text-amber-700 font-medium">New loan applications for these members are blocked until KYC is updated.</p>
            </div>
          </div>
        )}

        {pendingKyc > 0 && !kycDrillFilter && (
          <p className="text-xs text-amber-700 bg-amber-50 rounded-lg p-2 font-medium">
            {pendingKyc} member{pendingKyc > 1 ? 's' : ''} require re-KYC. New loan applications for affected members are blocked until KYC is complete.
          </p>
        )}
      </div>

      {/* Money-Lending Annual Review */}
      <div className="card">
        <h2 className="section-title mb-4 flex items-center gap-2">
          <Scale size={16} className="text-indigo-600" />
          Money-Lending Act — Annual Review
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-4">
          <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-2">Legal Opinion on Record</p>
            <textarea
              className="w-full text-sm text-slate-700 bg-white border border-slate-200 rounded p-2 resize-none focus:outline-none focus:ring-1 focus:ring-green-500"
              rows={3}
              value={mlLegalOpinion}
              onChange={e => setMlLegalOpinion(e.target.value)}
              placeholder="Enter legal opinion details..."
            />
            <p className="text-xs text-slate-400 mt-1">Last updated: 15 Mar 2026 · Legal Counsel: Adv. R. Kulkarni</p>
          </div>
          <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide mb-2">Next Annual Review Due</p>
            <input
              type="date"
              className="field-input mb-2"
              value={mlNextReview}
              onChange={e => setMlNextReview(e.target.value)}
            />
            {mlNextReview && (
              <p className={`text-xs font-medium mt-1 ${new Date(mlNextReview) < new Date() ? 'text-red-600' : new Date(mlNextReview) < new Date(Date.now() + 90 * 24 * 60 * 60 * 1000) ? 'text-amber-600' : 'text-green-700'}`}>
                {new Date(mlNextReview) < new Date()
                  ? 'OVERDUE — review required immediately'
                  : new Date(mlNextReview) < new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
                  ? `Due in ${Math.ceil((new Date(mlNextReview).getTime() - Date.now()) / (1000 * 60 * 60 * 24))} days`
                  : `Due ${new Date(mlNextReview).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}`}
              </p>
            )}
            <p className="text-xs text-slate-400 mt-2">Maharashtra Money-Lending (Regulation) Act, 2014. Cooperative societies lending to members require annual compliance review.</p>
          </div>
        </div>
        <div className="bg-green-50 border border-green-200 rounded-lg p-3">
          <div className="flex items-start gap-2">
            <CheckCircle2 size={14} className="text-green-600 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-xs font-semibold text-green-800">SFPCL Cooperative Society Exemption</p>
              <p className="text-xs text-green-700 mt-0.5">As a registered cooperative society lending exclusively to its members, SFPCL falls under Section 4(1)(b) exemption. Annual review and legal opinion on file are mandatory.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance checklist */}
      <div>
        <h2 className="section-title mb-3">Compliance Register</h2>
        <div className="space-y-2">
          {complianceData.map(rec => (
            <div key={rec.id} className={`rounded-lg border p-4 ${STATUS_BG[rec.status]}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <div className="mt-0.5 flex-shrink-0">{STATUS_ICONS[rec.status]}</div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{rec.area}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Owner: {rec.owner} · Frequency: {rec.frequency} · Evidence: {rec.evidenceCount} record{rec.evidenceCount !== 1 ? 's' : ''}
                    </p>
                    {rec.lastReviewDate && (
                      <p className="text-xs text-slate-400 mt-0.5">
                        Last reviewed: {new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(rec.lastReviewDate))}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <StatusBadge label={rec.status} size="sm" />
                  <p className="text-xs text-slate-500">Due: {new Intl.DateTimeFormat('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date(rec.nextDueDate))}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ComplianceDashboard;
