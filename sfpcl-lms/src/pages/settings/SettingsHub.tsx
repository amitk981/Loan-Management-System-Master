import React, { useEffect, useState } from 'react';
import { FileText, Settings, Shield } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import { useRole } from '../../contexts/RoleContext';
import { ApprovalMatrixSettingsPanel } from './ApprovalMatrixSettingsPanel';
import { LoanPolicySettingsPanel } from './LoanPolicySettingsPanel';

type SettingsTab = 'policy' | 'approval_matrix' | 'templates';

const SettingsHub: React.FC = () => {
  const { can } = useRole();
  const matrixOnly = can('view_approval_matrix') && !can('view_settings');
  const [activeTab, setActiveTab] = useState<SettingsTab>(matrixOnly ? 'approval_matrix' : 'policy');

  useEffect(() => {
    if (matrixOnly) setActiveTab('approval_matrix');
  }, [matrixOnly]);

  if (!can('view_settings') && !can('view_approval_matrix')) {
    return <div className="p-6"><div className="flex flex-col items-center py-20 text-center">
      <Shield size={40} className="text-slate-300 mb-4" />
      <h2 className="text-lg font-semibold text-slate-700 mb-2">Access Restricted</h2>
      <p className="text-sm text-slate-400">Your account has no permission to view configuration.</p>
    </div></div>;
  }

  const allTabs: Array<{ id: SettingsTab; label: string; icon: React.ReactNode }> = [
    { id: 'policy', label: 'Policy & Product Configuration', icon: <Settings size={15} /> },
    { id: 'approval_matrix', label: 'Approval Matrix', icon: <Shield size={15} /> },
    { id: 'templates', label: 'Template Management', icon: <FileText size={15} /> },
  ];
  const tabs = allTabs.filter(tab => !matrixOnly || tab.id === 'approval_matrix');

  return <div className="p-6">
    <div className="mb-6">
      <h1 className="text-xl font-bold text-slate-900">Settings</h1>
      <p className="text-sm text-slate-500 mt-1">View governed configuration and the delivery status of settings domains.</p>
    </div>
    <div className="border-b border-slate-200 mb-6"><div className="flex gap-1 overflow-x-auto">{tabs.map(tab => <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${activeTab === tab.id ? 'border-green-600 text-green-700' : 'border-transparent text-slate-500 hover:text-slate-700'}`}>{tab.icon}{tab.label}</button>)}</div></div>

    {activeTab === 'policy' && <LoanPolicySettingsPanel />}
    {activeTab === 'approval_matrix' && <div className="max-w-4xl space-y-5">
      {/* OWNED S71 START: API-backed by 007J. */}
      <ApprovalMatrixSettingsPanel />
      {/* OWNED S71 END */}
      <div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4">
        <h3 className="font-semibold text-slate-900">Workflow TAT & Escalation Rules</h3>
        <p className="text-sm text-slate-600">Workflow task generation will become the authoritative source for stage owners, due dates, and escalations.</p>
        <AlertBanner type="warning" title="Read-only configuration" message="Configuration is managed outside the product until slice 012EA. No save or escalation mutation is available here." />
      </div>
    </div>}
    {activeTab === 'templates' && <div className="max-w-4xl space-y-5"><div className="bg-white border border-slate-200 rounded-xl p-6 space-y-4">
      <h3 className="font-semibold text-slate-900">Document Template Management</h3>
      <p className="text-sm text-slate-600">S72 document files, borrower applicability, approval evidence, effective dates, and retained versions require the document-template model. Communication-template content remains a separate 003F resource.</p>
      <AlertBanner type="warning" title="Read-only configuration" message="Configuration is managed outside the product until slice 008A. No upload, activation, retirement, or history mutation is available here." />
    </div></div>}
  </div>;
};

export default SettingsHub;
