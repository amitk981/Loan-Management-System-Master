import React from 'react';
import { Shield, CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import AlertBanner from '../../components/ui/AlertBanner';
import { complianceRecords, dashboardStats, loanAccounts, members } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const STATUS_ICONS = {
  compliant: <CheckCircle2 size={16} className="text-green-600" />,
  warning:   <AlertTriangle size={16} className="text-amber-500" />,
  breach:    <XCircle size={16} className="text-red-600" />,
  pending:   <Clock size={16} className="text-slate-400" />,
};

const STATUS_BG = {
  compliant: 'bg-green-50 border-green-200',
  warning:   'bg-amber-50 border-amber-200',
  breach:    'bg-red-50 border-red-200',
  pending:   'bg-slate-50 border-slate-200',
};

const ComplianceDashboard: React.FC = () => {
  const warnings = complianceRecords.filter(r => r.status === 'warning').length;
  const breaches = complianceRecords.filter(r => r.status === 'breach').length;
  const pendingKyc = members.filter(m => m.kycStatus === 'rekyc_due' || m.kycStatus === 'expired').length;

  const totalPortfolio = loanAccounts.reduce((s, l) => s + l.outstandingPrincipal, 0);
  const sectionLimit = Math.round(totalPortfolio / (dashboardStats.sectionUtilisation / 100));

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
      {warnings > 0 && !breaches && (
        <AlertBanner
          type="warning"
          title={`${warnings} compliance area${warnings > 1 ? 's' : ''} have warnings`}
          message="Review and address before deadline."
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
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Total Portfolio (OS)</p>
            <p className="text-2xl font-bold text-slate-900 num mt-1">{fmt(totalPortfolio)}</p>
          </div>
          <div className="bg-slate-50 rounded-lg border border-slate-200 p-4">
            <p className="text-xs text-slate-500 font-medium uppercase tracking-wide">Aggregate Limit (est.)</p>
            <p className="text-2xl font-bold text-slate-900 num mt-1">{fmt(sectionLimit)}</p>
            <p className="text-xs text-slate-400 mt-1">60% of paid-up capital + free reserves</p>
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
            <p className="text-sm font-semibold text-green-900">Financial Assets &gt; 50% of Total Assets</p>
            <p className="text-xs text-green-700 mt-1">SFPCL qualifies as NBFC if test is met. Currently: <strong>Compliant</strong></p>
          </div>
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <CheckCircle2 size={16} className="text-green-600 mb-2" />
            <p className="text-sm font-semibold text-green-900">Net Income from Financial Assets &gt; 50%</p>
            <p className="text-xs text-green-700 mt-1">Monitored quarterly by CFO. Currently: <strong>Compliant</strong></p>
          </div>
        </div>
        <p className="text-xs text-slate-400 mt-3">
          Note: If SFPCL qualifies as an NBFC-ND (non-deposit taking), RBI registration would be required.
          Current assessment: Producer Company engaged in agricultural services — lending is incidental activity.
        </p>
      </div>

      {/* KYC tracker */}
      <div className="card">
        <h2 className="section-title mb-4">KYC & Re-KYC Tracker</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {[
            { label: 'Verified', count: members.filter(m => m.kycStatus === 'verified').length, color: 'green' },
            { label: 'Re-KYC Due', count: members.filter(m => m.kycStatus === 'rekyc_due').length, color: 'amber' },
            { label: 'Expired', count: members.filter(m => m.kycStatus === 'expired').length, color: 'red' },
            { label: 'Pending', count: members.filter(m => m.kycStatus === 'pending').length, color: 'slate' },
          ].map(({ label, count, color }) => (
            <div key={label} className={`rounded-lg border p-3 text-center ${
              color === 'green' ? 'bg-green-50 border-green-200' :
              color === 'amber' ? 'bg-amber-50 border-amber-200' :
              color === 'red' ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'
            }`}>
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
            </div>
          ))}
        </div>
        {pendingKyc > 0 && (
          <p className="text-xs text-amber-700 bg-amber-50 rounded-lg p-2 font-medium">
            {pendingKyc} member{pendingKyc > 1 ? 's' : ''} require Re-KYC. New loan applications blocked until completed.
          </p>
        )}
      </div>

      {/* Compliance checklist */}
      <div>
        <h2 className="section-title mb-3">Compliance Register</h2>
        <div className="space-y-2">
          {complianceRecords.map(rec => (
            <div key={rec.id} className={`rounded-lg border p-4 ${STATUS_BG[rec.status]}`}>
              <div className="flex items-start justify-between gap-4">
                <div className="flex items-start gap-3 flex-1">
                  <div className="mt-0.5 flex-shrink-0">{STATUS_ICONS[rec.status]}</div>
                  <div>
                    <p className="text-sm font-semibold text-slate-900">{rec.area}</p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Owner: {rec.owner} · Frequency: {rec.frequency} · Evidence: {rec.evidenceCount} records
                    </p>
                    {rec.lastReviewDate && (
                      <p className="text-xs text-slate-400 mt-0.5">
                        Last reviewed: {new Date(rec.lastReviewDate).toLocaleDateString('en-IN')}
                      </p>
                    )}
                  </div>
                </div>
                <div className="flex flex-col items-end gap-1 flex-shrink-0">
                  <StatusBadge label={rec.status} size="sm" />
                  <p className="text-xs text-slate-500">Due: {new Date(rec.nextDueDate).toLocaleDateString('en-IN')}</p>
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
