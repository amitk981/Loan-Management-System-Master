import React, { useEffect, useState } from 'react';
import {
  Settings, Users, Shield, FileText, ChevronRight, History,
  Check, Plus, Trash2, Edit, Save, X, AlertTriangle, Key
} from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';
import { ROLE_LABELS } from '../../contexts/RoleContext';
import { Role } from '../../types';
import { ApprovalMatrixSettingsPanel } from './ApprovalMatrixSettingsPanel';

type SettingsTab = 'policy' | 'approval_matrix' | 'templates' | 'users';

const SettingsHub: React.FC = () => {
  const { can, currentUser } = useRole();
  const matrixOnly = can('view_approval_matrix') && !can('view_settings');
  const [activeTab, setActiveTab] = useState<SettingsTab>(matrixOnly ? 'approval_matrix' : 'policy');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (matrixOnly) setActiveTab('approval_matrix');
  }, [matrixOnly]);

  if (!can('view_settings') && !can('view_approval_matrix')) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center py-20 text-center">
          <Shield size={40} className="text-slate-300 mb-4" />
          <h2 className="text-lg font-semibold text-slate-700 mb-2">Access Restricted</h2>
          <p className="text-sm text-slate-400">Settings are only accessible to Admin, CFO, and Company Secretary roles.</p>
        </div>
      </div>
    );
  }

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2500);
  };

  const allTabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
    { id: 'policy',          label: 'Policy & Product Configuration', icon: <Settings size={15} /> },
    { id: 'approval_matrix', label: 'Approval Matrix',                icon: <Shield size={15} /> },
    { id: 'templates',       label: 'Template Management',            icon: <FileText size={15} /> },
    { id: 'users',           label: 'User & Role Management',         icon: <Users size={15} /> },
  ];
  const tabs = allTabs.filter(tab => !matrixOnly || tab.id === 'approval_matrix');

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-bold text-slate-900">Settings</h1>
        <p className="text-sm text-slate-500 mt-1">Configure system-wide policy, approval rules, document templates and user access.</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-slate-200 mb-6">
        <div className="flex gap-1 overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700'
              }`}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Policy & Product Configuration */}
      {activeTab === 'policy' && (
        <div className="max-w-3xl space-y-6">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3 text-sm text-amber-800">
            <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
            Policy changes affect future calculations after activation. Existing loans retain the policy version used at sanction.
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-900">Policy Version Summary</h3>
              <span className="bg-slate-100 text-slate-700 text-xs font-semibold px-2 py-0.5 rounded-full border border-slate-200">Draft</span>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-slate-500">Policy version</span>
                <div className="font-medium text-slate-900 mt-1">POL-2026-01</div>
              </div>
              <div>
                <span className="text-slate-500">Effective from</span>
                <div className="font-medium text-slate-900 mt-1">Pending</div>
              </div>
              <div>
                <span className="text-slate-500">Approved by</span>
                <div className="font-medium text-slate-900 mt-1">Pending Approval</div>
              </div>
              <div>
                <span className="text-slate-500">Board approval reference</span>
                <div className="font-medium text-slate-900 mt-1">Required before activation</div>
              </div>
              <div>
                <span className="text-slate-500">Last changed by</span>
                <div className="font-medium text-slate-900 mt-1">Admin User</div>
              </div>
              <div>
                <span className="text-slate-500">Last changed on</span>
                <div className="font-medium text-slate-900 mt-1">26 Jun 2026</div>
              </div>
            </div>
          </div>

          {[
            {
              section: 'Loan Parameters',
              fields: [
                { label: 'Maximum loan amount (₹)', value: '1000000', type: 'number', note: 'Section 186 cap applies separately' },
                { label: 'Short-term loan tenure (months)', value: '12', type: 'number' },
                { label: 'Long-term loan tenure (max months)', value: '36', type: 'number' },
                { label: 'Standard interest rate (% p.a.)', value: '12', type: 'number' },
                { label: 'Penal interest rate on overdue (% p.a.)', value: '2', type: 'number', note: 'Added to standard rate' },
                { label: 'Interest rate type', value: 'Fixed', type: 'text' },
                { label: 'Interest benchmark / source', value: 'Internal Board', type: 'text' },
                { label: 'Interest spread', value: '0', type: 'number' },
                { label: 'Rate effective date', value: '2026-01-01', type: 'date' },
                { label: 'Rate communication status', value: 'Published', type: 'text' },
              ],
            },
            {
              section: 'Eligibility Rules',
              warning: 'Policy clarification required: SOP references 30%, 10%, and ₹200 per-share cap. Select the active Board-approved rule before activation.',
              fields: [
                { label: 'Share value for limit calculation (₹ per share)', value: '2000', type: 'number', note: 'Active rule must match Board-approved policy.' },
                { label: 'Shareholding multiplier (%)', value: '30', type: 'number', note: 'Calculation is stored with the active policy version.' },
                { label: 'Per-acre land limit (₹/acre)', value: '20000', type: 'number' },
                { label: 'Minimum supply years for eligibility', value: '1', type: 'number' },
                { label: 'Minimum shares for eligibility', value: '1', type: 'number' },
                { label: 'Share valuation date', value: '2026-03-31', type: 'date' },
                { label: 'Valuation source / audited financials reference', value: 'FY25 Audited Balance Sheet', type: 'text' },
                { label: 'Share limit rule', value: '30% of share value', type: 'select', options: ['30% of share value', '10% of share value', '₹200 per-share cap', 'Custom Board-approved rule'] },
                { label: 'Per-share cap (₹)', value: '200', type: 'number' },
                { label: 'Board approval reference', value: 'BR-2026-04', type: 'text' },
              ],
            },
            {
              section: 'Compliance Thresholds',
              fields: [
                { label: 'Section 186 warning threshold (%)', value: '75', type: 'number', note: 'Warning shown above this utilisation.' },
                { label: 'Section 186 breach threshold (%)', value: '100', type: 'number', note: 'Block new sanction above this utilisation unless approved exception exists.' },
                { label: 'Grace period duration (days)', value: '90', type: 'number' },
                { label: 'Maximum extension period (months)', value: '12', type: 'number' },
                { label: 'TAT for appraisal (working days)', value: '2', type: 'number' },
                { label: 'Re-KYC frequency (months)', value: '36', type: 'number' },
                { label: 'Record retention period (years)', value: '8', type: 'number', note: 'Minimum 8 years after closure.' },
                { label: 'DPD bucket rules', value: 'Standard (30, 90, 365)', type: 'text' },
                { label: 'Reminder schedule', value: 'D-3, D+1, D+7', type: 'text' },
              ],
            },
          ].map(section => (
            <div key={section.section} className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4">{section.section}</h3>
              {section.warning && (
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-3 flex items-start gap-3 text-sm text-amber-800 mb-4">
                  <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
                  {section.warning}
                </div>
              )}
              <div className="grid grid-cols-1 gap-4">
                {section.fields.map((field: { label: string; value: string; type: string; note?: string; options?: string[] }) => (
                  <div key={field.label} className="flex items-start gap-4">
                    <label className="w-72 text-sm text-slate-700 pt-2.5 flex-shrink-0">{field.label}</label>
                    <div className="flex-1">
                      {field.type === 'select' ? (
                        <select
                          defaultValue={field.value}
                          disabled={!(['admin', 'company_secretary', 'cfo', 'director', 'sanction_committee'].includes(currentUser.role))}
                          className="w-64 px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-slate-50 disabled:text-slate-500"
                        >
                          {field.options?.map(opt => <option key={opt} value={opt}>{opt}</option>)}
                        </select>
                      ) : (
                        <input
                          type={field.type}
                          defaultValue={field.value}
                          disabled={!(['admin', 'company_secretary', 'cfo', 'director', 'sanction_committee'].includes(currentUser.role))}
                          className="w-64 px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-slate-50 disabled:text-slate-500"
                        />
                      )}
                      {field.note && <p className="text-xs text-slate-400 mt-1">{field.note}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {/* Audit and History Rules */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs text-slate-500 flex flex-col gap-1">
            <p>• Every policy change requires a change reason.</p>
            <p>• Board approval evidence is required before activation.</p>
            <p>• Historical loan calculations retain the policy version used at sanction.</p>
            <p>• Every save, submit, approve, activate, deactivate, or discard action creates an audit event.</p>
          </div>

          <div className="flex flex-wrap gap-3">
            {['admin', 'company_secretary', 'cfo', 'director', 'sanction_committee'].includes(currentUser.role) && (
              <>
                <button
                  onClick={handleSave}
                  className="flex items-center gap-2 border border-slate-200 bg-white text-slate-700 px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors hover:bg-slate-50"
                >
                  {saved ? <Check size={16} className="text-green-600" /> : <Save size={16} />}
                  {saved ? 'Saved' : 'Save Draft'}
                </button>
                <button className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                  Submit for Approval
                </button>
                {['cfo', 'director', 'sanction_committee'].includes(currentUser.role) && (
                  <button className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors">
                    <Check size={16} />
                    Activate Policy Version
                  </button>
                )}
                <div className="flex-1"></div>
              </>
            )}
            
            <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors ml-auto">
              <History size={16} />
              View Change History
            </button>
            {['admin', 'company_secretary', 'cfo', 'director', 'sanction_committee'].includes(currentUser.role) && (
              <button className="flex items-center gap-2 border border-slate-200 text-red-600 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-red-50 transition-colors">
                <X size={16} />
                Discard Draft Changes
              </button>
            )}
          </div>
        </div>
      )}

      {/* Approval Matrix */}
      {activeTab === 'approval_matrix' && (
        <div className="max-w-4xl space-y-5">
          {/* OWNED S71 START: API-backed by 007J. */}
          <ApprovalMatrixSettingsPanel />
          {/* OWNED S71 END */}

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden mt-6">
            <div className="px-6 py-4 border-b border-slate-100">
              <h3 className="font-semibold text-slate-900">Workflow TAT & Escalation Rules</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Workflow stage</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Owner</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">TAT</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Escalates to</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Escalation type</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { stage: 'Completeness Check', owner: 'Deputy Manager – Finance', tat: '1 working day', escTo: 'Credit Manager', escType: 'Notification' },
                    { stage: 'Appraisal', owner: 'Deputy Manager – Finance', tat: '2 working days', escTo: 'Credit Manager', escType: 'Notification' },
                    { stage: 'Credit Manager Review', owner: 'Credit Manager', tat: '1 working day', escTo: 'CFO / Credit Head', escType: 'Review escalation' },
                    { stage: 'Sanction Committee', owner: 'Sanction Committee', tat: '3 working days', escTo: 'Sanction Committee Chairperson', escType: 'Approval follow-up' },
                    { stage: 'Documentation', owner: 'Compliance / Company Secretary', tat: '5 working days', escTo: 'Company Secretary', escType: 'Documentation follow-up' },
                    { stage: 'Disbursement', owner: 'Senior Manager – Finance / CFC', tat: '2 working days', escTo: 'Senior Manager – Finance', escType: 'Payment follow-up' },
                  ].map(rule => (
                    <tr key={rule.stage} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">{rule.stage}</td>
                      <td className="px-4 py-3 text-slate-600">{rule.owner}</td>
                      <td className="px-4 py-3 text-slate-700">{rule.tat}</td>
                      <td className="px-4 py-3 text-slate-600">{rule.escTo}</td>
                      <td className="px-4 py-3 text-amber-700 text-xs">
                        <span className="bg-amber-50 px-2 py-1 rounded">{rule.escType}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Template Management */}
      {activeTab === 'templates' && (
        <div className="max-w-4xl space-y-5">
          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3 text-sm text-amber-800">
            <AlertTriangle size={16} className="mt-0.5 flex-shrink-0" />
            Annexure numbering requires confirmation. Template IDs should remain independent of annexure labels.
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Document & Communication Templates</h3>
              {['admin', 'company_secretary', 'compliance_team'].includes(currentUser.role) && (
                <button className="flex items-center gap-2 text-sm text-green-700 font-medium border border-green-200 bg-green-50 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-colors">
                  <Plus size={14} />
                  Upload Template
                </button>
              )}
            </div>
            
            <div className="border-b border-slate-200 bg-slate-50/50 px-4 py-2 flex gap-2 overflow-x-auto">
              {['All', 'Active', 'Draft', 'Pending Approval', 'Retired'].map(f => (
                <button key={f} className={`px-3 py-1.5 text-xs font-medium rounded-lg whitespace-nowrap transition-colors ${f === 'All' ? 'bg-white border border-slate-200 shadow-sm text-slate-900' : 'text-slate-600 hover:bg-slate-100'}`}>
                  {f}
                </button>
              ))}
            </div>

            <div className="divide-y divide-slate-50">
              {[
                { name: 'Loan Application Form', type: 'Docx', version: 'v1.0', borrower: 'All', lang: 'English/Marathi', date: '2026-01-01', approver: 'Admin', status: 'Active', updated: '2026-01-01' },
                { name: 'Loan Appraisal Note', type: 'Docx', version: 'v2.1', borrower: 'All', lang: 'English', date: '2026-05-15', approver: 'CFO', status: 'Active', updated: '2026-05-10' },
                { name: 'Power of Attorney', type: 'Docx', version: 'v1.8', borrower: 'All', lang: 'English', date: '2024-08-12', approver: 'Company Secretary', status: 'Active', updated: '2024-08-10' },
                { name: 'Tri-party Agreement / Declaration', type: 'Docx', version: 'v1.2', borrower: 'FPO', lang: 'English', date: '2025-11-20', approver: 'Company Secretary', status: 'Active', updated: '2025-11-15' },
                { name: 'SH-4 Checklist / Reference', type: 'Docx', version: 'v1.0', borrower: 'All', lang: 'English', date: '2025-06-01', approver: 'Company Secretary', status: 'Active', updated: '2025-05-25' },
                { name: 'Term Sheet', type: 'Docx', version: 'v2.0', borrower: 'All', lang: 'English', date: '2026-02-01', approver: 'CFO', status: 'Active', updated: '2026-01-20' },
                { name: 'Loan Agreement', type: 'Docx', version: 'v3.0', borrower: 'All', lang: 'English', date: '-', approver: '-', status: 'Draft', updated: '2026-06-25' },
                { name: 'Bank Verification Letter', type: 'Docx', version: 'v1.1', borrower: 'All', lang: 'English', date: '2025-01-10', approver: 'Admin', status: 'Active', updated: '2025-01-05' },
                { name: 'Document Checklist', type: 'Docx', version: 'v2.2', borrower: 'All', lang: 'English', date: '2026-03-15', approver: 'Company Secretary', status: 'Active', updated: '2026-03-10' },
                { name: 'Customer Code Creation Excel Template', type: 'Xlsx', version: 'v1.4', borrower: 'All', lang: 'English', date: '2025-08-22', approver: 'Admin', status: 'Active', updated: '2025-08-20' },
                { name: 'Credit Sanction Register Export Template', type: 'Xlsx', version: 'v1.0', borrower: 'All', lang: 'English', date: '2025-09-01', approver: 'Admin', status: 'Active', updated: '2025-08-30' },
                { name: 'Grievance Form', type: 'Docx', version: 'v1.1', borrower: 'All', lang: 'English/Marathi', date: '2025-12-05', approver: 'Company Secretary', status: 'Active', updated: '2025-12-01' },
                { name: 'Sanction Letter', type: 'Docx', version: 'v3.2', borrower: 'All', lang: 'English', date: '2024-08-12', approver: 'Sanction Committee', status: 'Active', updated: '2024-08-12' },
                { name: 'Rejection Note', type: 'Docx', version: 'v1.3', borrower: 'All', lang: 'English', date: '2024-07-20', approver: 'CFO', status: 'Active', updated: '2024-07-20' },
                { name: 'Disbursement Advice', type: 'Docx', version: 'v2.0', borrower: 'All', lang: 'English', date: '2026-04-10', approver: 'Senior Manager - Finance', status: 'Active', updated: '2026-04-05' },
                { name: 'NOC', type: 'Docx', version: 'v1.5', borrower: 'All', lang: 'English', date: '2024-08-12', approver: 'Company Secretary', status: 'Active', updated: '2024-08-12' },
                { name: 'Security Return Acknowledgement', type: 'Docx', version: 'v1.0', borrower: 'All', lang: 'English', date: '2025-10-10', approver: 'Company Secretary', status: 'Active', updated: '2025-10-05' },
                { name: 'Extension Note', type: 'Docx', version: 'v1.1', borrower: 'All', lang: 'English', date: '-', approver: '-', status: 'Pending Approval', updated: '2026-06-20' },
                { name: 'Note for Non-Payment', type: 'Docx', version: 'v1.1', borrower: 'All', lang: 'English', date: '2024-06-10', approver: 'Credit Manager', status: 'Active', updated: '2024-06-10' },
                { name: 'Borrower Intimation Letter for Interest Capitalisation', type: 'Docx', version: 'v1.0', borrower: 'All', lang: 'English', date: '2025-04-01', approver: 'CFO', status: 'Active', updated: '2025-03-25' },
                { name: 'Interest Rate Revision Notice', type: 'Docx', version: 'v1.0', borrower: 'All', lang: 'English', date: '2024-01-01', approver: 'CFO', status: 'Retired', updated: '2024-01-01' },
              ].map(tmpl => (
                <div key={tmpl.name} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <FileText size={16} className="text-blue-600" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-800">{tmpl.name}</div>
                      <div className="text-xs text-slate-500 mt-0.5">
                        {tmpl.type} · {tmpl.version} · {tmpl.borrower} · {tmpl.lang}
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        Effective: {tmpl.date} · Approved by: {tmpl.approver} · Updated: {tmpl.updated}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                      tmpl.status === 'Active' ? 'bg-green-100 text-green-700' : 
                      tmpl.status === 'Draft' ? 'bg-slate-100 text-slate-700' :
                      tmpl.status === 'Pending Approval' ? 'bg-amber-100 text-amber-700' :
                      'bg-slate-200 text-slate-500'
                    }`}>
                      {tmpl.status}
                    </span>
                    {['admin', 'company_secretary', 'compliance_team'].includes(currentUser.role) && (
                      <div className="relative group">
                        <button className="text-slate-500 hover:text-slate-900 font-medium text-xs px-2 py-1.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1">
                          Actions <ChevronRight size={12} className="rotate-90" />
                        </button>
                        <div className="absolute right-0 mt-1 w-44 bg-white border border-slate-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 flex flex-col text-left overflow-hidden">
                          <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">View</button>
                          <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Preview merge fields</button>
                          <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Create draft version</button>
                          {tmpl.status !== 'Active' && <button className="px-3 py-2 text-xs text-green-700 hover:bg-green-50 text-left">Activate</button>}
                          {tmpl.status === 'Active' && <button className="px-3 py-2 text-xs text-amber-700 hover:bg-amber-50 text-left">Retire</button>}
                          <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">View history</button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs text-slate-500 flex flex-col gap-1">
            <p>• Active templates cannot be deleted.</p>
            <p>• Templates already used to generate documents cannot be deleted.</p>
            <p>• Activation requires approved-by and approval-date fields.</p>
            <p>• Generated documents preserve the template version used.</p>
          </div>
        </div>
      )}

      {/* User & Role Management */}
      {activeTab === 'users' && (
        <div className="max-w-5xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">System Users</h3>
              {currentUser.role === 'admin' && (
                <button className="flex items-center gap-2 text-sm text-green-700 font-medium border border-green-200 bg-green-50 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-colors">
                  <Plus size={14} />
                  Add User
                </button>
              )}
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">User</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Role & Team</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Authority & Delegation</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Access</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                    {currentUser.role === 'admin' && <th className="text-right px-6 py-3 text-xs font-semibold text-slate-500 uppercase">Action</th>}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { name: 'Rajesh Sharma', email: 'rajesh.sharma@sfpcl.in', mobile: '+91 9876543210', role: 'Credit Manager', team: 'Credit Assessment', authority: 'Sanction up to ₹2L', del: 'None', login: 'Today, 09:30 AM', status: 'Active' },
                    { name: 'Meera Patil', email: 'meera.patil@sfpcl.in', mobile: '+91 9876543211', role: 'Company Secretary', team: 'Compliance', authority: 'Legal Documentation', del: 'None', login: 'Today, 10:15 AM', status: 'Active' },
                    { name: 'Amit Deshmukh', email: 'amit.deshmukh@sfpcl.in', mobile: '+91 9876543212', role: 'Chief Financial Controller', team: 'Treasury', authority: 'Final Bank Transfer', del: 'None', login: 'Yesterday, 04:00 PM', status: 'Active' },
                    { name: 'Anita Kulkarni', email: 'anita.kulkarni@sfpcl.in', mobile: '+91 9876543213', role: 'Internal Auditor', team: 'Audit', authority: 'None', del: 'None', login: '2 Days ago', status: 'Inactive' },
                    { name: 'System Admin', email: 'admin@sfpcl.in', mobile: '-', role: 'System Administrator', team: 'IT', authority: 'None', del: 'None', login: 'Current session', status: 'Current user' },
                  ].map(user => (
                    <tr key={user.name} className="hover:bg-slate-50">
                      <td className="px-6 py-4">
                        <div className="font-medium text-slate-900">{user.name}</div>
                        <div className="text-xs text-slate-500">{user.email}</div>
                        <div className="text-xs text-slate-400 mt-0.5">{user.mobile}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-slate-800">{user.role}</div>
                        <div className="text-xs text-slate-500 mt-0.5">{user.team}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-slate-800">{user.authority}</div>
                        <div className="text-xs text-slate-500 mt-0.5">Delegation: {user.del}</div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-slate-600 text-xs">Last login:</div>
                        <div className="text-slate-800 text-xs">{user.login}</div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                          user.status === 'Current user' ? 'bg-indigo-100 text-indigo-700' :
                          user.status === 'Active' ? 'bg-green-100 text-green-700' :
                          user.status === 'Inactive' ? 'bg-slate-100 text-slate-600' :
                          'bg-amber-100 text-amber-700'
                        }`}>
                          {user.status}
                        </span>
                      </td>
                      {currentUser.role === 'admin' && (
                        <td className="px-6 py-4 text-right">
                          <div className="relative group">
                            <button className="text-slate-500 hover:text-slate-900 font-medium text-xs px-2 py-1.5 rounded hover:bg-slate-100 transition-colors flex items-center gap-1 ml-auto">
                              Actions <ChevronRight size={12} className="rotate-90" />
                            </button>
                            <div className="absolute right-0 mt-1 w-44 bg-white border border-slate-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 flex flex-col text-left overflow-hidden">
                              <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">View profile</button>
                              <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Edit roles</button>
                              <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Reset password</button>
                              <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">Delegate tasks</button>
                              <button className="px-3 py-2 text-xs text-slate-700 hover:bg-slate-50 text-left">View access log</button>
                              {user.status !== 'Current user' && <button className="px-3 py-2 text-xs text-red-600 hover:bg-red-50 text-left">Deactivate user</button>}
                            </div>
                          </div>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 text-xs text-slate-500 flex flex-col gap-1">
            <p>• Inactive and suspended users cannot access the system.</p>
            <p>• Role changes, password resets, approval authority changes, and delegations are audit logged.</p>
            <p>• Delegation must have a start date and an end date.</p>
            <p>• Sensitive data reveal permission is separate from normal read permission.</p>
            <p>• Export permission is separate from screen view permission.</p>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden mt-6">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Role Directory</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Role Name</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Code</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Team</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Role Type</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Authority</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Sensitive Access</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Dashboard</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { name: 'System Administrator', code: 'SYS_ADMIN', team: 'IT', type: 'Admin', auth: 'No', sens: 'Restricted', dash: 'Settings' },
                    { name: 'IT Head', code: 'IT_HEAD', team: 'IT', type: 'Admin', auth: 'No', sens: 'Restricted', dash: 'System' },
                    { name: 'Field Officer', code: 'FLD_OFFICER', team: 'Field Intake', type: 'Operational', auth: 'No', sens: 'None', dash: 'Task Inbox' },
                    { name: 'Deputy Manager – Finance', code: 'DEP_MGR_FIN', team: 'Credit', type: 'Operational', auth: 'No', sens: 'None', dash: 'Task Inbox' },
                    { name: 'Credit Manager', code: 'CREDIT_MGR', team: 'Credit', type: 'Operational', auth: 'No', sens: 'Masked', dash: 'Credit Dashboard' },
                    { name: 'Compliance Team Member', code: 'COMPLIANCE', team: 'Legal', type: 'Operational', auth: 'No', sens: 'Masked', dash: 'Compliance Hub' },
                    { name: 'Company Secretary', code: 'COMP_SEC', team: 'Secretarial', type: 'Operational', auth: 'Yes (Legal)', sens: 'Reveal with reason', dash: 'Compliance Hub' },
                    { name: 'Sanction Committee Member', code: 'SANC_COMM', team: 'Board', type: 'Approval', auth: 'Yes', sens: 'Reveal with reason', dash: 'Sanction Hub' },
                    { name: 'CFO', code: 'CFO', team: 'Executive', type: 'Approval', auth: 'Yes', sens: 'Reveal with reason', dash: 'Management Dash' },
                    { name: 'Director', code: 'DIRECTOR', team: 'Board', type: 'Approval', auth: 'Yes', sens: 'Reveal with reason', dash: 'Sanction Hub' },
                    { name: 'Senior Manager – Finance', code: 'SR_MGR_FIN', team: 'Finance', type: 'Finance', auth: 'Yes (Payment Init)', sens: 'None', dash: 'Disbursement Hub' },
                    { name: 'Chief Financial Controller', code: 'CFC', team: 'Treasury', type: 'Finance', auth: 'Yes (Payment Final)', sens: 'None', dash: 'Disbursement Hub' },
                    { name: 'Accounts User / Accounts Head', code: 'ACCOUNTS', team: 'Accounts', type: 'Finance', auth: 'No', sens: 'None', dash: 'Repayments' },
                    { name: 'Sales Team User', code: 'SALES', team: 'Sales', type: 'Operational', auth: 'No', sens: 'None', dash: 'Optional' },
                    { name: 'Internal Auditor', code: 'AUDITOR', team: 'Audit', type: 'Audit', auth: 'No', sens: 'Reveal with reason', dash: 'Audit Dash' },
                    { name: 'Management Viewer', code: 'MGMT_VIEW', team: 'Executive', type: 'Operational', auth: 'No', sens: 'None', dash: 'Management Dash' },
                    { name: 'Borrower Portal User', code: 'BORROWER', team: 'Portal', type: 'Future portal', auth: 'No', sens: 'Own data only', dash: 'Borrower Portal' },
                  ].map(role => (
                    <tr key={role.name} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">{role.name}</td>
                      <td className="px-4 py-3 font-mono text-xs text-slate-500">{role.code}</td>
                      <td className="px-4 py-3 text-slate-600">{role.team}</td>
                      <td className="px-4 py-3 text-slate-600">{role.type}</td>
                      <td className="px-4 py-3 text-slate-600">{role.auth}</td>
                      <td className="px-4 py-3 text-slate-600">{role.sens}</td>
                      <td className="px-4 py-3 text-slate-600">{role.dash}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-2">Role Permission Summary</h3>
            <p className="text-sm text-slate-500 mb-4">Permission summary is for admin review. Backend permission checks remain the source of truth.</p>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-3 py-2 font-semibold text-slate-500">Role</th>
                    <th className="text-left px-2 py-2 font-semibold text-slate-500">Application access</th>
                    <th className="text-left px-2 py-2 font-semibold text-slate-500">Sanction authority</th>
                    <th className="text-left px-2 py-2 font-semibold text-slate-500">Documentation access</th>
                    <th className="text-left px-2 py-2 font-semibold text-slate-500">Payment authority</th>
                    <th className="text-left px-2 py-2 font-semibold text-slate-500">Compliance access</th>
                    <th className="text-left px-2 py-2 font-semibold text-slate-500">Settings access</th>
                    <th className="text-left px-2 py-2 font-semibold text-slate-500">Notes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {[
                    ['Field Officer', 'Assisted intake only', 'None', 'Upload intake documents only', 'None', 'None', 'None', ''],
                    ['Deputy Manager – Finance', 'Completeness + appraisal prep', 'None', 'Upload / review intake evidence only', 'None', 'None', 'None', ''],
                    ['Credit Manager', 'Review + appraisal handoff', 'Submit / recommend only', 'View status', 'None', 'Limited monitoring', 'None', ''],
                    ['Compliance Team Member', 'Limited / doc queue only', 'None', 'Prepare documents', 'None', 'KYC / compliance support', 'Template access only (if config)', ''],
                    ['Company Secretary', 'View compliance context', 'None', 'Approve legal doc / security custody', 'None', 'Compliance admin', 'Policy/template/approval matrix (where config)', 'Not user management'],
                    ['Sanction Committee Member', 'Assigned sanction cases only', 'Approve / reject / abstain', 'View only if needed for decision', 'None', 'None', 'None', ''],
                    ['CFO', 'Executive / approval context', 'Approve / exception approval', 'View', 'None', 'Section 186 / NBFC / MIS', 'Policy and approval matrix governance only', 'Not user management'],
                    ['Director', 'Assigned approval cases only', 'Approve / reject / abstain', 'None or view only if needed', 'None', 'None', 'None', ''],
                    ['Senior Manager – Finance', 'Finance handoff context', 'None', 'Finance verification', 'Initiate only', 'None', 'None', ''],
                    ['Chief Financial Controller', 'Payment package context only', 'None', 'View payment evidence only', 'Final bank authorisation', 'None', 'None', ''],
                    ['Accounts', 'Loan account / repayment context', 'None', 'None', 'None', 'Accounting / DPD support', 'None', ''],
                    ['Sales Team User', 'Invoice support context only', 'None', 'None', 'None', 'Invoice follow-up support only', 'None', 'Optional if invoice workflow enabled'],
                    ['Internal Auditor', 'Read-only', 'Read-only', 'Read-only', 'Read-only', 'Read-only audit review', 'Read-only history only', ''],
                    ['System Administrator', 'None by default', 'None', 'None by default', 'None', 'Technical only', 'User, role, permission and system config admin', 'Break-glass app access if configured'],
                    ['Management Viewer', 'View dashboards / reports only', 'None', 'View only where permitted', 'None', 'View only', 'None', ''],
                    ['Borrower Portal User', 'Own application only', 'None', 'Own uploads only', 'None', 'None', 'None', 'Future / portal only'],
                  ].map(row => (
                    <tr key={row[0]} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium text-slate-700">{row[0]}</td>
                      <td className="px-2 py-2 text-slate-600">{row[1]}</td>
                      <td className="px-2 py-2 text-slate-600">{row[2]}</td>
                      <td className="px-2 py-2 text-slate-600">{row[3]}</td>
                      <td className="px-2 py-2 text-slate-600">{row[4]}</td>
                      <td className="px-2 py-2 text-slate-600">{row[5]}</td>
                      <td className="px-2 py-2 text-slate-600">{row[6]}</td>
                      <td className="px-2 py-2 text-slate-500 italic">{row[7]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsHub;
