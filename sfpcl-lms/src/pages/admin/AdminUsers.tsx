import React, { useCallback, useEffect, useState } from 'react';
import { RefreshCw, Shield, UserCheck, Users } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { useRole } from '../../contexts/RoleContext';
import {
  addAdminUserTeam,
  assignAdminUserRole,
  getAdminUser,
  listAdminUsers,
  removeAdminUserTeam,
  setAdminUserStatus,
  type AdminUser,
} from '../../services/adminUsersApi';
import { AuthSessionError } from '../../services/authSession';

const AdminUsers: React.FC = () => {
  const { can } = useRole();
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [roleCode, setRoleCode] = useState('');
  const [teamCode, setTeamCode] = useState('');
  const [status, setStatus] = useState<'active' | 'suspended'>('active');

  const canManageUsers = can('manage_users');

  const syncControls = (user: AdminUser | null) => {
    setRoleCode(user?.roles[0]?.role_code ?? '');
    setTeamCode('');
    setStatus(user?.status === 'suspended' ? 'suspended' : 'active');
  };

  const loadUsers = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const result = await listAdminUsers();
      setUsers(result.users);
      const firstUser = result.users[0] ?? null;
      setSelectedUser(firstUser);
      syncControls(firstUser);
    } catch (loadError) {
      setError(errorMessage(loadError));
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadUsers();
  }, [loadUsers]);

  const selectUser = async (user: AdminUser) => {
    setError('');
    setSuccess('');
    setSelectedUser(user);
    syncControls(user);
    try {
      const freshUser = await getAdminUser(user.user_id);
      setSelectedUser(freshUser);
      syncControls(freshUser);
    } catch (loadError) {
      setError(errorMessage(loadError));
    }
  };

  const updateSelectedUser = (updatedUser: AdminUser) => {
    setSelectedUser(updatedUser);
    syncControls(updatedUser);
    setUsers(currentUsers => currentUsers.map(user => (
      user.user_id === updatedUser.user_id ? updatedUser : user
    )));
  };

  const runAction = async (action: () => Promise<AdminUser>, message: string) => {
    if (!selectedUser) return;
    setIsSaving(true);
    setError('');
    setSuccess('');
    try {
      updateSelectedUser(await action());
      setSuccess(message);
    } catch (actionError) {
      setError(errorMessage(actionError));
    } finally {
      setIsSaving(false);
    }
  };

  if (!canManageUsers) {
    return (
      <div className="p-6">
        <div className="flex flex-col items-center py-20 text-center">
          <Shield size={40} className="text-slate-300 mb-4" />
          <h2 className="text-lg font-semibold text-slate-700 mb-2">Access Restricted</h2>
          <p className="text-sm text-slate-400">User and role management requires user-administration permission.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">Admin User Management</h1>
          <p className="text-sm text-slate-500 mt-0.5">{users.length} staff users</p>
        </div>
        <button
          onClick={() => void loadUsers()}
          className="flex items-center gap-2 border border-slate-200 text-slate-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-slate-50 transition-colors"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </div>

      {error && (
        <AlertBanner type="error" title="User management action failed" message={error} onDismiss={() => setError('')} />
      )}
      {success && (
        <AlertBanner type="success" title="User management updated" message={success} onDismiss={() => setSuccess('')} />
      )}

      {isLoading ? (
        <div className="card p-8 text-sm text-slate-500">Loading users...</div>
      ) : users.length === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-400">No staff users found.</div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-[minmax(0,1.4fr)_minmax(360px,0.8fr)] gap-4">
          <div className="card p-0 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-200 bg-slate-50">
                    <th className="table-header text-left">User</th>
                    <th className="table-header text-left">Role</th>
                    <th className="table-header text-left">Teams</th>
                    <th className="table-header text-left">Status</th>
                    <th className="table-header text-left">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {users.map(user => (
                    <tr
                      key={user.user_id}
                      onClick={() => void selectUser(user)}
                      className="hover:bg-slate-50 cursor-pointer transition-colors"
                    >
                      <td className="table-cell">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center flex-shrink-0">
                            <Users size={14} className="text-green-700" />
                          </div>
                          <div>
                            <div className="font-semibold text-slate-900">{user.full_name}</div>
                            <div className="text-xs text-slate-400">{user.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="table-cell">
                        <div className="font-medium text-slate-700">{roleLabel(user)}</div>
                        <div className="text-xs text-slate-400">{user.roles[0]?.role_code ?? 'No role'}</div>
                      </td>
                      <td className="table-cell">
                        <div className="text-sm text-slate-700">{teamLabel(user)}</div>
                      </td>
                      <td className="table-cell">
                        <StatusBadge label={user.status} size="sm" />
                      </td>
                      <td className="table-cell">
                        <button
                          onClick={event => {
                            event.stopPropagation();
                            void selectUser(user);
                          }}
                          className="flex items-center gap-1 text-xs text-green-700 hover:text-green-900 px-2 py-1 rounded hover:bg-green-50 transition-colors"
                        >
                          <UserCheck size={12} />
                          Manage
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card p-5 space-y-4">
            {selectedUser ? (
              <>
                <div>
                  <h2 className="font-semibold text-slate-900">{selectedUser.full_name}</h2>
                  <p className="text-sm text-slate-500 mt-0.5">{selectedUser.email}</p>
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-slate-500">Mobile</span>
                    <div className="font-medium text-slate-900 mt-1">{selectedUser.mobile_number || 'Not recorded'}</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Status</span>
                    <div className="mt-1"><StatusBadge label={selectedUser.status} size="sm" /></div>
                  </div>
                  <div>
                    <span className="text-slate-500">Roles</span>
                    <div className="font-medium text-slate-900 mt-1">{roleLabel(selectedUser)}</div>
                  </div>
                  <div>
                    <span className="text-slate-500">Teams</span>
                    <div className="font-medium text-slate-900 mt-1">{teamLabel(selectedUser)}</div>
                  </div>
                </div>

                <div className="border-t border-slate-200 pt-4 space-y-3">
                  <label className="block text-sm font-medium text-slate-700">Role code</label>
                  <div className="flex gap-2">
                    <input
                      value={roleCode}
                      onChange={event => setRoleCode(event.target.value)}
                      className="field-input py-2 text-sm"
                      placeholder="system_admin"
                    />
                    <button
                      disabled={isSaving || !roleCode.trim()}
                      onClick={() => void runAction(
                        () => assignAdminUserRole(selectedUser.user_id, roleCode.trim()),
                        'Role assignment was saved.',
                      )}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-slate-200 disabled:text-slate-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                    >
                      Assign
                    </button>
                  </div>
                </div>

                <div className="border-t border-slate-200 pt-4 space-y-3">
                  <label className="block text-sm font-medium text-slate-700">Team code</label>
                  <div className="flex gap-2">
                    <input
                      value={teamCode}
                      onChange={event => setTeamCode(event.target.value)}
                      className="field-input py-2 text-sm"
                      placeholder="credit_assessment"
                    />
                    <button
                      disabled={isSaving || !teamCode.trim()}
                      onClick={() => void runAction(
                        () => addAdminUserTeam(selectedUser.user_id, teamCode.trim()),
                        'Team membership was added.',
                      )}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-slate-200 disabled:text-slate-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                    >
                      Add
                    </button>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {selectedUser.teams.map(team => (
                      <button
                        key={team.team_code}
                        disabled={isSaving}
                        onClick={() => void runAction(
                          () => removeAdminUserTeam(selectedUser.user_id, team.team_code),
                          'Team membership was removed.',
                        )}
                        className="text-xs px-2 py-1 rounded-full border border-slate-200 text-slate-700 hover:bg-slate-50 disabled:text-slate-400"
                      >
                        Remove {team.team_code}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="border-t border-slate-200 pt-4 space-y-3">
                  <label className="block text-sm font-medium text-slate-700">Status</label>
                  <div className="flex gap-2">
                    <select
                      value={status}
                      onChange={event => setStatus(event.target.value as 'active' | 'suspended')}
                      className="field-select py-2 text-sm"
                    >
                      <option value="active">Active</option>
                      <option value="suspended">Suspended</option>
                    </select>
                    <button
                      disabled={isSaving || selectedUser.status === status}
                      onClick={() => void runAction(
                        () => setAdminUserStatus(selectedUser.user_id, status),
                        'Status change was saved.',
                      )}
                      className="bg-green-600 hover:bg-green-700 disabled:bg-slate-200 disabled:text-slate-500 text-white px-4 py-2 rounded-lg text-sm font-semibold transition-colors"
                    >
                      Save
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-sm text-slate-400">Select a user to view assignments.</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

const roleLabel = (user: AdminUser): string => (
  user.roles.map(role => role.role_name).join(', ') || 'No active role'
);

const teamLabel = (user: AdminUser): string => (
  user.teams.map(team => team.team_name).join(', ') || 'No active team'
);

const errorMessage = (error: unknown): string => {
  if (error instanceof AuthSessionError) return error.message;
  return 'Unable to reach the user-management API.';
};

export default AdminUsers;
