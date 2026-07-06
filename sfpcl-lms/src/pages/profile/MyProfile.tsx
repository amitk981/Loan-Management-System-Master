import React from 'react';
import { ShieldAlert } from 'lucide-react';
import { useRole, type User } from '../../contexts/RoleContext';

const MyProfile: React.FC = () => {
  const { currentUser } = useRole();
  return <MyProfileView currentUser={currentUser} />;
};

export const MyProfileView: React.FC<{ currentUser: User }> = ({ currentUser }) => {
  const initials = currentUser.name.split(' ').map(name => name[0]).join('');
  const status = currentUser.status || 'active';
  const roles = currentUser.roleCodes.length ? currentUser.roleCodes : [currentUser.role];
  const teams = currentUser.teamCodes.length ? currentUser.teamCodes : (currentUser.team ? [currentUser.team] : []);

  return (
    <div className="p-6 space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">My Profile</h1>
          <p className="text-sm text-slate-500 mt-1">
            Read-only account details from the current authenticated user record.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <div className="space-y-6 xl:col-span-1">
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="p-6 flex flex-col items-center text-center">
              <div className="w-20 h-20 bg-indigo-100 text-indigo-700 rounded-full flex items-center justify-center text-2xl font-bold mb-4">
                {initials}
              </div>
              <h2 className="text-lg font-bold text-slate-900">{currentUser.name}</h2>
              <div className="mt-1 flex items-center gap-2">
                <span className="text-xs font-semibold text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded-full">
                  {currentUser.roleName}
                </span>
                <span className="text-xs font-semibold text-green-700 bg-green-50 px-2 py-0.5 rounded-full">
                  {status}
                </span>
              </div>
              <p className="text-sm text-slate-500 mt-2">
                <a href={`mailto:${currentUser.email}`} className="text-indigo-600 hover:underline">
                  {currentUser.email}
                </a>
              </p>
            </div>
            <div className="border-t border-slate-100 p-4 bg-slate-50">
              <div className="space-y-3">
                <SummaryRow label="Backend user ID" value={currentUser.id} />
                <SummaryRow label="Team" value={currentUser.teamName || currentUser.team || 'Unassigned'} />
                <SummaryRow label="Session source" value={currentUser.isBackendSession ? 'Backend API' : 'Demo session'} />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 p-6">
            <h3 className="text-base font-semibold text-slate-900 mb-4">Account Status</h3>
            <div className="space-y-3">
              <SummaryRow label="Status" value={status} />
              <SummaryRow label="Mobile" value={currentUser.mobileNumber || 'Not recorded'} />
              <SummaryRow label="Email" value={currentUser.email} />
            </div>
          </div>
        </div>

        <div className="space-y-6 xl:col-span-2">
          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
              <h3 className="text-base font-semibold text-slate-900">Account Details</h3>
            </div>
            <div className="p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                <Field label="Full name" value={currentUser.name} />
                <Field label="Email" value={currentUser.email} />
                <Field label="Mobile number" value={currentUser.mobileNumber || 'Not recorded'} />
                <Field label="Backend user ID" value={currentUser.id} />
                <Field label="Department / Team" value={currentUser.teamName || currentUser.team || 'Unassigned'} />
                <Field label="Account status" value={status} valueClassName="text-green-700" />
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50 flex justify-between items-center">
              <h3 className="text-base font-semibold text-slate-900">Role & Access</h3>
            </div>
            <div className="p-6 space-y-6">
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 flex gap-3">
                <ShieldAlert size={20} className="text-slate-400 shrink-0" />
                <div className="text-sm text-slate-600">
                  Role, team and access changes must be made by an authorised administrator.
                  <p className="font-medium text-slate-900 mt-1">
                    This page displays the current `/api/v1/auth/me/` identity only.
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                <Field label="Primary role" value={currentUser.roleName} />
                <Field label="Backend role code" value={roles[0] || 'Not recorded'} />
                <Field label="Backend team code" value={teams[0] || 'Not recorded'} />
                <Field label="Prototype route role" value={currentUser.role} />
              </div>
            </div>
          </div>

          <CodeTable title="Backend Roles" label="Role code" values={roles} />
          <CodeTable title="Backend Teams" label="Team code" values={teams} />
          <CodeTable
            title="Backend Permissions"
            label="Permission code"
            values={currentUser.permissions}
            emptyLabel="No backend permissions returned."
          />
          <CodeTable
            title="Available Actions"
            label="Action code"
            values={currentUser.availableActions}
            emptyLabel="No backend actions returned."
          />
        </div>
      </div>
    </div>
  );
};

const SummaryRow: React.FC<{ label: string; value: string }> = ({ label, value }) => (
  <div className="flex justify-between gap-4 text-sm">
    <span className="text-slate-500">{label}</span>
    <span className="font-medium text-slate-900 text-right break-all">{value}</span>
  </div>
);

const Field: React.FC<{ label: string; value: string; valueClassName?: string }> = ({
  label,
  value,
  valueClassName = 'text-slate-900',
}) => (
  <div>
    <label className="block text-xs font-medium text-slate-500 mb-1">{label}</label>
    <div className={`text-sm font-medium break-all ${valueClassName}`}>{value}</div>
  </div>
);

const CodeTable: React.FC<{
  title: string;
  label: string;
  values: string[];
  emptyLabel?: string;
}> = ({ title, label, values, emptyLabel = 'None' }) => (
  <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
    <div className="px-6 py-4 border-b border-slate-100 bg-slate-50/50">
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
    </div>
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 border-b border-slate-200">
            <th className="table-header text-left">{label}</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {values.length === 0 ? (
            <tr>
              <td className="table-cell text-slate-500">{emptyLabel}</td>
            </tr>
          ) : values.map(value => (
            <tr key={value} className="hover:bg-slate-50">
              <td className="table-cell font-medium text-slate-900">{value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

export default MyProfile;
