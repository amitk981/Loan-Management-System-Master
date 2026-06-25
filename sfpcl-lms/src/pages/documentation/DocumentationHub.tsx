import React, { useState } from 'react';
import { FolderOpen, ChevronRight, Check } from 'lucide-react';
import StatusBadge from '../../components/ui/StatusBadge';
import DocumentChecklist from '../../components/loan/DocumentChecklist';
import { loanApplications, securities } from '../../data/mockData';

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const SECURITY_TYPE_LABELS: Record<string, string> = {
  poa: 'Power of Attorney',
  sh4: 'SH-4 Share Transfer',
  cdsl_pledge: 'CDSL Pledge',
  blank_cheque: 'Blank-Dated Cheque',
  tri_party: 'Tri-Party Agreement',
};

interface DocumentationHubProps {
  onOpenApplication: (id: string) => void;
}

const DocumentationHub: React.FC<DocumentationHubProps> = ({ onOpenApplication }) => {
  const docQueue = loanApplications.filter(a =>
    a.status === 'sanctioned' && ['not_started', 'in_progress', 'pending_signature', 'pending_stamp'].includes(a.documentationStatus)
  );
  const [selected, setSelected] = useState<string | null>(docQueue[0]?.id || null);

  const app = docQueue.find(a => a.id === selected);
  const appSecurities = securities.filter(s => s.applicationId === selected);

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Documentation Hub</h1>
          <p className="text-sm text-slate-500 mt-0.5">{docQueue.length} application{docQueue.length !== 1 ? 's' : ''} pending documentation</p>
        </div>
      </div>

      {docQueue.length === 0 ? (
        <div className="card text-center py-16">
          <Check size={32} className="text-green-500 mx-auto mb-3" />
          <p className="text-slate-600 font-semibold">All documentation is complete</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Queue */}
          <div className="card p-0 overflow-hidden lg:col-span-1">
            <div className="p-4 bg-slate-50 border-b border-slate-200">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Doc Queue ({docQueue.length})</p>
            </div>
            <div className="divide-y divide-slate-100">
              {docQueue.map(a => (
                <button
                  key={a.id}
                  onClick={() => setSelected(a.id)}
                  className={`w-full flex items-center gap-3 p-4 hover:bg-slate-50 transition-colors text-left ${selected === a.id ? 'bg-green-50 border-l-4 border-l-green-500' : ''}`}
                >
                  <FolderOpen size={16} className="text-amber-500 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="font-semibold text-slate-900 num text-sm">{a.applicationNumber}</div>
                    <div className="text-xs text-slate-500 truncate">{a.memberName}</div>
                    <div className="text-xs text-slate-400 num">{fmt(a.requestedAmount)}</div>
                  </div>
                  <StatusBadge label={a.documentationStatus} size="sm" />
                </button>
              ))}
            </div>
          </div>

          {/* Detail */}
          {app && (
            <div className="lg:col-span-2 space-y-4">
              <div className="card">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <h2 className="text-lg font-bold text-slate-900 num">{app.applicationNumber}</h2>
                      <StatusBadge label={app.documentationStatus} size="sm" />
                    </div>
                    <p className="text-sm text-slate-500">{app.memberName} · {fmt(app.requestedAmount)}</p>
                    {app.sapCustomerCode && (
                      <p className="text-xs text-slate-400 mt-0.5">SAP Code: <span className="num font-medium">{app.sapCustomerCode}</span></p>
                    )}
                  </div>
                  <button onClick={() => onOpenApplication(app.id)} className="text-xs text-green-600 hover:underline flex items-center gap-1">
                    Full view <ChevronRight size={12} />
                  </button>
                </div>

                <DocumentChecklist applicationId={app.id} />
              </div>

              {/* Security instruments */}
              <div className="card">
                <h3 className="text-sm font-semibold text-slate-700 mb-3">Security Instruments</h3>
                {appSecurities.length === 0 ? (
                  <p className="text-sm text-slate-400">No security instruments recorded.</p>
                ) : (
                  <div className="space-y-2">
                    {appSecurities.map(sec => (
                      <div key={sec.id} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-200">
                        <div className="flex-1 min-w-0">
                          <div className="text-sm font-medium text-slate-900">
                            {SECURITY_TYPE_LABELS[sec.securityType] || sec.securityType}
                          </div>
                          <div className="text-xs text-slate-500 mt-0.5">
                            Custodian: {sec.custodian || 'Unassigned'}
                            {sec.executionDate && ` · Executed: ${sec.executionDate}`}
                            {sec.psnNumber && ` · PSN: ${sec.psnNumber}`}
                          </div>
                          <div className="flex gap-3 mt-1 text-xs">
                            {sec.stampDutyStatus !== undefined && sec.stampDutyStatus !== 'not_required' && (
                              <span className={sec.stampDutyStatus === 'complete' ? 'text-green-600' : 'text-amber-600'}>
                                Stamp: {sec.stampDutyStatus}
                              </span>
                            )}
                            {sec.notarisationStatus !== undefined && sec.notarisationStatus !== 'not_required' && (
                              <span className={sec.notarisationStatus === 'complete' ? 'text-green-600' : 'text-amber-600'}>
                                Notarised: {sec.notarisationStatus}
                              </span>
                            )}
                          </div>
                        </div>
                        <StatusBadge label={sec.status} size="sm" />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DocumentationHub;
