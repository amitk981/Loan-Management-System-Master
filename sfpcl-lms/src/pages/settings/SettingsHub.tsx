import React, { useState } from 'react';
import {
  Settings, Users, Shield, FileText, ChevronRight,
  Check, Plus, Trash2, Edit, Save, X, AlertTriangle, Key
} from 'lucide-react';
import { useRole } from '../../contexts/RoleContext';
import { ROLE_LABELS } from '../../contexts/RoleContext';
import { Role } from '../../types';

type SettingsTab = 'policy' | 'approval_matrix' | 'templates' | 'users';

const SettingsHub: React.FC = () => {
  const { can, currentUser } = useRole();
  const [activeTab, setActiveTab] = useState<SettingsTab>('policy');
  const [saved, setSaved] = useState(false);

  if (!can('view_settings')) {
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

  const tabs: { id: SettingsTab; label: string; icon: React.ReactNode }[] = [
    { id: 'policy',          label: 'Policy & Product Configuration', icon: <Settings size={15} /> },
    { id: 'approval_matrix', label: 'Approval Matrix',                icon: <Shield size={15} /> },
    { id: 'templates',       label: 'Template Management',            icon: <FileText size={15} /> },
    { id: 'users',           label: 'User & Role Management',         icon: <Users size={15} /> },
  ];

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
            Changes to policy configuration affect all active and future loan applications. Review carefully before saving.
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
              ],
            },
            {
              section: 'Eligibility Rules',
              fields: [
                { label: 'Share value for limit calculation (₹ per share)', value: '2000', type: 'number', note: 'SOP 30% of shareholding × share value' },
                { label: 'Shareholding multiplier (%)', value: '30', type: 'number', note: 'Loan limit = shares × ₹2,000 × 30%' },
                { label: 'Per-acre land limit (₹/acre)', value: '20000', type: 'number' },
                { label: 'Minimum supply years for eligibility', value: '1', type: 'number' },
                { label: 'Minimum shares for eligibility', value: '1', type: 'number' },
              ],
            },
            {
              section: 'Compliance Thresholds',
              fields: [
                { label: 'Section 186 warning threshold (%)', value: '75', type: 'number', note: 'Amber alert above this %' },
                { label: 'Section 186 breach threshold (%)', value: '100', type: 'number', note: 'Red alert / block at this %' },
                { label: 'Grace period duration (days)', value: '90', type: 'number' },
                { label: 'Maximum extension period (months)', value: '12', type: 'number' },
                { label: 'TAT for appraisal (working days)', value: '2', type: 'number' },
              ],
            },
          ].map(section => (
            <div key={section.section} className="bg-white border border-slate-200 rounded-xl p-6">
              <h3 className="font-semibold text-slate-900 mb-4">{section.section}</h3>
              <div className="grid grid-cols-1 gap-4">
                {section.fields.map(field => (
                  <div key={field.label} className="flex items-start gap-4">
                    <label className="w-72 text-sm text-slate-700 pt-2.5 flex-shrink-0">{field.label}</label>
                    <div className="flex-1">
                      <input
                        type={field.type}
                        defaultValue={field.value}
                        disabled={!can('manage_settings')}
                        className="w-48 px-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-slate-50 disabled:text-slate-500"
                      />
                      {field.note && <p className="text-xs text-slate-400 mt-1">{field.note}</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}

          {can('manage_settings') && (
            <div className="flex gap-3">
              <button
                onClick={handleSave}
                className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-colors"
              >
                {saved ? <Check size={16} /> : <Save size={16} />}
                {saved ? 'Saved' : 'Save Configuration'}
              </button>
              <button className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2.5 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors">
                <X size={16} />
                Reset to Defaults
              </button>
            </div>
          )}
        </div>
      )}

      {/* Approval Matrix */}
      {activeTab === 'approval_matrix' && (
        <div className="max-w-3xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Sanction Committee Authority Matrix</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Loan Amount Range</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Required Approvers</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Minimum Votes</th>
                    <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Notes</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {[
                    { range: 'Up to ₹5,00,000',    approvers: 'CFO + 1 Director',  votes: '2',            notes: 'Standard sanction' },
                    { range: 'Above ₹5,00,000',    approvers: 'CFO + 2 Directors', votes: '3',            notes: 'High-value sanction' },
                    { range: 'Director/Relative',  approvers: 'Full SC + GM/CFO',  votes: 'Unanimous',    notes: 'Special case approval required' },
                    { range: 'Above eligible limit', approvers: 'CFO + all Directors', votes: 'Unanimous', notes: 'Exception approval required' },
                  ].map(row => (
                    <tr key={row.range} className="hover:bg-slate-50">
                      <td className="px-4 py-3 font-medium text-slate-800">{row.range}</td>
                      <td className="px-4 py-3 text-slate-700">{row.approvers}</td>
                      <td className="px-4 py-3 text-slate-700">{row.votes}</td>
                      <td className="px-4 py-3 text-slate-500 text-xs">{row.notes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">TAT & Escalation Rules</h3>
            <div className="space-y-3">
              {[
                { stage: 'Completeness Check',  tat: '1 working day',  escalation: 'Credit Manager' },
                { stage: 'Appraisal',           tat: '2 working days', escalation: 'Credit Manager' },
                { stage: 'Credit Manager Review', tat: '1 working day', escalation: 'CFO' },
                { stage: 'Sanction Committee', tat: '3 working days',  escalation: 'Chairperson' },
                { stage: 'Documentation',       tat: '5 working days', escalation: 'Company Secretary' },
                { stage: 'Disbursement',        tat: '2 working days', escalation: 'Senior Manager – Finance' },
              ].map(rule => (
                <div key={rule.stage} className="flex items-center justify-between p-3 border border-slate-100 rounded-lg text-sm">
                  <span className="font-medium text-slate-800">{rule.stage}</span>
                  <span className="text-slate-500">{rule.tat}</span>
                  <span className="text-xs text-amber-700 bg-amber-50 px-2 py-1 rounded">Escalates to: {rule.escalation}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Template Management */}
      {activeTab === 'templates' && (
        <div className="max-w-3xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">Document Templates</h3>
              {can('manage_settings') && (
                <button className="flex items-center gap-2 text-sm text-green-700 font-medium border border-green-200 bg-green-50 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-colors">
                  <Plus size={14} />
                  Add Template
                </button>
              )}
            </div>
            <div className="divide-y divide-slate-50">
              {[
                { name: 'Sanction Letter',            type: 'Docx', version: 'v3.2', lastUpdated: '2024-08-12', owner: 'Company Secretary', active: true },
                { name: 'Loan Agreement',              type: 'Docx', version: 'v2.1', lastUpdated: '2024-08-12', owner: 'Company Secretary', active: true },
                { name: 'Power of Attorney',           type: 'Docx', version: 'v1.8', lastUpdated: '2024-08-12', owner: 'Compliance Team',    active: true },
                { name: 'Loan Appraisal Note',         type: 'Docx', version: 'v2.0', lastUpdated: '2024-08-01', owner: 'Credit Manager',     active: true },
                { name: 'Rejection Note',              type: 'Docx', version: 'v1.3', lastUpdated: '2024-07-20', owner: 'Credit Manager',     active: true },
                { name: 'NOC Template',                type: 'Docx', version: 'v1.5', lastUpdated: '2024-08-12', owner: 'Compliance Team',    active: true },
                { name: 'Non-Payment Note',            type: 'Docx', version: 'v1.1', lastUpdated: '2024-06-10', owner: 'Credit Manager',     active: true },
                { name: 'Extension Note',              type: 'Docx', version: 'v1.0', lastUpdated: '2024-06-10', owner: 'Credit Manager',     active: false },
              ].map(tmpl => (
                <div key={tmpl.name} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <FileText size={16} className="text-blue-600" />
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-800">{tmpl.name}</div>
                      <div className="text-xs text-slate-400 mt-0.5">{tmpl.type} · {tmpl.version} · {tmpl.owner} · Updated {tmpl.lastUpdated}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${tmpl.active ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                      {tmpl.active ? 'Active' : 'Inactive'}
                    </span>
                    {can('manage_settings') && (
                      <div className="flex gap-1">
                        <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors"><Edit size={14} /></button>
                        <button className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"><Trash2 size={14} /></button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* User & Role Management */}
      {activeTab === 'users' && (
        <div className="max-w-3xl space-y-5">
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
              <h3 className="font-semibold text-slate-900">System Users</h3>
              {can('manage_users') && (
                <button className="flex items-center gap-2 text-sm text-green-700 font-medium border border-green-200 bg-green-50 hover:bg-green-100 px-3 py-1.5 rounded-lg transition-colors">
                  <Plus size={14} />
                  Add User
                </button>
              )}
            </div>
            <div className="divide-y divide-slate-50">
              {(Object.entries(ROLE_LABELS) as [Role, string][]).map(([role, label]) => (
                <div key={role} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-semibold text-sm flex-shrink-0">
                      {label.charAt(0)}
                    </div>
                    <div>
                      <div className="text-sm font-medium text-slate-800">{label}</div>
                      <div className="text-xs text-slate-400 mt-0.5 font-mono">{role}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs px-2 py-1 rounded-full font-medium ${role === currentUser.role ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-500'}`}>
                      {role === currentUser.role ? 'Current' : 'Active'}
                    </span>
                    {can('manage_users') && (
                      <div className="flex gap-1">
                        <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors" title="Edit permissions">
                          <Key size={14} />
                        </button>
                        <button className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors">
                          <Edit size={14} />
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-6">
            <h3 className="font-semibold text-slate-900 mb-4">Role Permissions Overview</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-xs">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="text-left px-3 py-2 font-semibold text-slate-500">Role</th>
                    <th className="text-center px-2 py-2 font-semibold text-slate-500">Applications</th>
                    <th className="text-center px-2 py-2 font-semibold text-slate-500">Sanction</th>
                    <th className="text-center px-2 py-2 font-semibold text-slate-500">Documentation</th>
                    <th className="text-center px-2 py-2 font-semibold text-slate-500">Disbursement</th>
                    <th className="text-center px-2 py-2 font-semibold text-slate-500">Compliance</th>
                    <th className="text-center px-2 py-2 font-semibold text-slate-500">Settings</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {([
                    ['Deputy Manager – Finance', true, false, true, false, false, false],
                    ['Credit Manager',           true, true, true, false, true, false],
                    ['Compliance Team',          false, false, true, false, true, false],
                    ['Company Secretary',        false, false, true, false, true, true],
                    ['Sanction Committee',       true, true, false, false, false, false],
                    ['CFO',                      true, true, true, false, true, true],
                    ['Director',                 true, true, false, false, false, false],
                    ['Senior Manager – Finance', false, false, true, true, false, false],
                    ['CFC',                      false, false, false, true, false, false],
                    ['Accounts',                 true, false, false, false, false, false],
                    ['Auditor',                  true, true, true, false, true, false],
                    ['Admin',                    true, false, false, false, false, true],
                  ] as [string, ...boolean[]][]).map(row => (
                    <tr key={row[0]} className="hover:bg-slate-50">
                      <td className="px-3 py-2 font-medium text-slate-700">{row[0]}</td>
                      {(row.slice(1) as boolean[]).map((v, i) => (
                        <td key={i} className="px-2 py-2 text-center">
                          {v ? <Check size={14} className="mx-auto text-green-600" /> : <X size={14} className="mx-auto text-slate-200" />}
                        </td>
                      ))}
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
