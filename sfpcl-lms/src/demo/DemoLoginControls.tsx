import React, { useState } from 'react';
import { LogIn } from 'lucide-react';
import { ROLE_LABELS, type User } from '../contexts/RoleContext';
import LoginScreen from '../pages/auth/LoginScreen';
import type { Role } from '../types';
import { ROLE_USERS, STAFF_DEMO_ROLES } from './demoUsers';


interface DemoLoginScreenProps {
  onLogin: (credentials: { email: string; password: string }) => void | Promise<void>;
  onDemoLogin: (user: User) => void;
  onOpenMemberPortal?: () => void;
  error?: string;
  isSubmitting?: boolean;
  isLoadingSession?: boolean;
}

const DemoLoginScreen: React.FC<DemoLoginScreenProps> = ({
  onLogin,
  onDemoLogin,
  onOpenMemberPortal,
  error,
  isSubmitting,
  isLoadingSession,
}) => {
  const [demoRole, setDemoRole] = useState<Role>('credit_manager');

  return (
    <LoginScreen
      onLogin={onLogin}
      onOpenMemberPortal={onOpenMemberPortal}
      error={error}
      isSubmitting={isSubmitting}
      isLoadingSession={isLoadingSession}
      demoRoleSelector={(
        <div>
        <label className="block text-sm font-medium text-slate-700 mb-1.5">
          Demo role (select to preview as a staff user)
        </label>
        <select
          value={demoRole}
          onChange={event => setDemoRole(event.target.value as Role)}
          className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
        >
          {STAFF_DEMO_ROLES.map(role => (
            <option key={role} value={role}>{ROLE_LABELS[role]}</option>
          ))}
        </select>
        <p className="text-xs text-slate-400 mt-1">
          Signing in as: <span className="font-medium text-slate-600">{ROLE_USERS[demoRole].name}</span> · {ROLE_USERS[demoRole].email}
        </p>
        </div>
      )}
      demoLoginAction={(
        <button
          type="button"
          onClick={() => onDemoLogin(ROLE_USERS[demoRole])}
          className="w-full mt-3 flex items-center justify-center gap-2 border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 font-semibold py-2.5 rounded-lg transition-colors"
        >
          <LogIn size={18} />
          Continue with demo role
        </button>
      )}
    />
  );
};

export default DemoLoginScreen;
