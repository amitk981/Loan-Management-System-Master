import React, { useState } from 'react';
import { useRole } from '../../contexts/RoleContext';
import { Role } from '../../types';
import { Shield, ShieldAlert, MonitorSmartphone, Clock, LogOut, Key, Search, ChevronRight } from 'lucide-react';

const MyProfile: React.FC = () => {
  const { currentUser, can } = useRole();
  const [mobileNumber, setMobileNumber] = useState('+91 98765 43210');

  const isBorrower = currentUser.role === 'borrower';

  const getRoleNote = (role: Role): string => {
    switch (role) {
      case 'field_officer': return "Assisted intake access only. No sanction, payment or settings authority.";
      case 'deputy_manager_finance': return "Completeness and appraisal preparation access. No sanction or payment authority.";
      case 'credit_manager': return "Credit review, appraisal handoff and monitoring access. No final sanction or payment authority.";
      case 'compliance_team': return "Documentation and compliance support access. No sanction or payment authority.";
      case 'company_secretary': return "Legal documentation, security custody, NOC, grievance and compliance access.";
      case 'sanction_committee': return "Assigned sanction decision access only. No documentation or payment execution authority.";
      case 'cfo': return "Sanction, exception and compliance governance access. No operational payment execution.";
      case 'director': return "Assigned approval cases only. No operational workflow actions.";
      case 'senior_manager_finance': return "SAP setup and payment initiation access. Cannot authorise final bank transfer.";
      case 'cfc': return "Final bank transfer authorisation access. No sanction approval authority.";
      case 'accounts': return "Repayment, ledger, interest, accrual and DPD access. No sanction or payment authority.";
      case 'sales_team_user': return "Invoice support and borrower follow-up access only. No approval authority.";
      case 'auditor': return "Read-only audit access. No create, edit, approve, disburse or post actions.";
      case 'admin': return "System configuration and user access administration only. No business approval authority unless separately assigned.";
      case 'borrower': return "Own application, own documents, own loan account and own grievances only.";
      default: return "";
    }
  };

  const employeeCode = isBorrower ? `MEM-${currentUser.id.padStart(4, '0')}` : `EMP-${currentUser.id.padStart(4, '0')}`;
  const teamOrMemberType = isBorrower ? 'Borrower' : (currentUser.team?.replace(/_/g, ' ') || 'Unassigned');

  // Helpers to check mock internal permissions purely for display text since they are predefined in context
  const hasSettings = currentUser.role === 'admin' || can('view_settings');
  const hasExport = can('export_registers');
  const hasSensitive = !isBorrower && (currentUser.role === 'admin' || currentUser.role === 'auditor' || currentUser.role === 'company_secretary' || currentUser.role === 'compliance_team');

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">My Profile</h1>
          <p className="text-sm text-slate-500 mt-1">
            View your account details, role access, security settings and recent activity.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="space-y-6 xl:col-span-1">
          {/* Profile Summary Card */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="p-6 flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                {currentUser.name.split(' ').map(n => n[0]).join('')}
              </div>
              <h2 className="text-lg font-bold text-slate-900">{currentUser.name}</h2>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full">
                  {currentUser.roleName}
                </span>
                <span className="text-xs font-semibold text-green-700 bg-green-50 px-2 py-0.5 rounded-full">
                  Active
                </span>
              </div>
              <p className="text-sm text-slate-500 mt-2"><a href={`mailto:${currentUser.email}`} className="text-indigo-600 hover:underline">{currentUser.email}</a></p>
            </div>
            <div className="border-t border-slate-100 p-4 bg-slate-50">
              <div className="space-y-3">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">{isBorrower ? 'Member Type' : 'Team'}</span>
                  <span className="font-medium text-slate-900 capitalize">{teamOrMemberType}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">Last login</span>
                  <span className="font-medium text-slate-900">26 Jun 2026, 03:45 PM</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-slate-500">MFA</span>
                  <span className="font-medium text-green-700">Enabled</span>
                </div>
              </div>
            </div>
          </div>

          {/* Delegation Card */}
          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="text-base font-semibold text-slate-900 mb-4">Delegation</h3>
            {!isBorrower && currentUser.role === 'sanction_committee' ? (
              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 text-sm text-amber-800">
                <div className="font-medium mb-1">Active delegation</div>
                <p>Delegated to: <strong>CFO</strong></p>
                <p>From: 28 Jun 2026</p>
                <p>To: 05 Jul 2026</p>
                <p>Permissions: Sanction approvals</p>
              </div>
            ) : (
              <div className="text-sm text-slate-500 italic">No active delegation.</div>
            )}
          </div>
        </div>

        <div className="space-y-6 xl:col-span-2">
          {/* Account Details Card */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-base font-semibold text-slate-900">Account Details</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Full name</label>
                  <div className="text-sm font-medium text-slate-900">{currentUser.name}</div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Email</label>
                  <div className="text-sm font-medium text-slate-900">{currentUser.email}</div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Mobile number</label>
                  <input
                    type="text"
                    value={mobileNumber}
                    onChange={(e) => setMobileNumber(e.target.value)}
                    className="text-sm font-medium text-slate-900 border-b border-slate-200 focus:border-indigo-500 outline-none pb-1 w-full"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">
                    {isBorrower ? 'Member ID / Folio number' : 'Employee code'}
                  </label>
                  <div className="text-sm font-medium text-slate-900">{employeeCode}</div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">
                    {isBorrower ? 'Member type' : 'Department / Team'}
                  </label>
                  <div className="text-sm font-medium text-slate-900 capitalize">{teamOrMemberType}</div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Account status</label>
                  <div className="text-sm font-medium text-green-700">Active</div>
                </div>
              </div>
            </div>
          </div>

          {/* Role & Access Card */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h3 className="text-base font-semibold text-slate-900">Role & Access</h3>
            </div>
            <div className="p-6 space-y-6">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex gap-3">
                <ShieldAlert size={20} className="text-slate-400 shrink-0" />
                <div className="text-sm text-slate-600">
                  Role and access changes must be made by an authorised administrator.
                  <p className="font-medium text-slate-900 mt-1">{getRoleNote(currentUser.role)}</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Primary role</label>
                  <div className="text-sm font-medium text-slate-900">{currentUser.roleName}</div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Additional roles</label>
                  <div className="text-sm font-medium text-slate-500 italic">None</div>
                </div>
                {!isBorrower && (
                  <>
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1">Approval authority</label>
                      <div className="text-sm font-medium text-slate-900">
                        {currentUser.role === 'sanction_committee' || currentUser.role === 'cfo' || currentUser.role === 'director' ? 'Sanction limit up to ₹50L' :
                         currentUser.role === 'cfc' ? 'Final Payment Authorisation' : 'None'}
                      </div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1">Sensitive access</label>
                      <div className="text-sm font-medium text-slate-900">{hasSensitive ? 'Yes' : 'No'}</div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1">Export access</label>
                      <div className="text-sm font-medium text-slate-900">{hasExport ? 'Yes' : 'No'}</div>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1">Settings access</label>
                      <div className="text-sm font-medium text-slate-900">{hasSettings ? 'Yes' : 'No'}</div>
                    </div>
                  </>
                )}
                <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Default landing page</label>
                  <div className="text-sm font-medium text-slate-900">Dashboard</div>
                </div>
              </div>
            </div>
          </div>

          {/* Security Card */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-base font-semibold text-slate-900">Security</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Password last changed</label>
                    <div className="text-sm font-medium text-slate-900">45 days ago</div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">MFA status</label>
                    <div className="text-sm font-medium text-slate-900">Configured (Authenticator App)</div>
                  </div>
                  <div className="flex gap-2 pt-2">
                    <button className="btn-secondary text-sm px-4 py-2 flex items-center gap-2">
                      <Key size={14} /> Change password
                    </button>
                    <button className="btn-secondary text-sm px-4 py-2 flex items-center gap-2">
                      <Shield size={14} /> Manage MFA
                    </button>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Active sessions</label>
                    <div className="text-sm font-medium text-slate-900">2 sessions</div>
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">Current session device / IP</label>
                    <div className="text-sm font-medium text-slate-900">Mac OS • 192.168.1.100</div>
                  </div>
                  <div className="flex gap-2 pt-2">
                    <button className="text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 border border-red-200">
                      <MonitorSmartphone size={14} /> Sign out other sessions
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Recent Account Activity Card */}
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-base font-semibold text-slate-900">Recent Account Activity</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 border-b border-slate-200">
                    <th className="table-header text-left">Date & Time</th>
                    <th className="table-header text-left">Action</th>
                    <th className="table-header text-left">Device / IP</th>
                    <th className="table-header text-left">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  <tr className="hover:bg-slate-50">
                    <td className="table-cell text-slate-600">26 Jun 2026, 03:45 PM</td>
                    <td className="table-cell font-medium text-slate-900">Login successful</td>
                    <td className="table-cell text-slate-500">Mac OS • 192.168.1.100</td>
                    <td className="table-cell"><span className="text-xs font-medium text-green-700 bg-green-50 px-2 py-0.5 rounded-full">Success</span></td>
                  </tr>
                  <tr className="hover:bg-slate-50">
                    <td className="table-cell text-slate-600">25 Jun 2026, 11:30 AM</td>
                    <td className="table-cell font-medium text-slate-900">Login successful</td>
                    <td className="table-cell text-slate-500">Mac OS • 192.168.1.100</td>
                    <td className="table-cell"><span className="text-xs font-medium text-green-700 bg-green-50 px-2 py-0.5 rounded-full">Success</span></td>
                  </tr>
                  <tr className="hover:bg-slate-50">
                    <td className="table-cell text-slate-600">12 May 2026, 09:15 AM</td>
                    <td className="table-cell font-medium text-slate-900">Password changed</td>
                    <td className="table-cell text-slate-500">Mac OS • 192.168.1.100</td>
                    <td className="table-cell"><span className="text-xs font-medium text-green-700 bg-green-50 px-2 py-0.5 rounded-full">Success</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyProfile;
