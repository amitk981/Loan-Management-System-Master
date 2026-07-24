import React, { useState } from 'react';
import { ChevronRight, RefreshCw } from 'lucide-react';
import type { User } from '../contexts/RoleContext';
import { ROLE_LABELS } from '../contexts/RoleContext';
import { DEMO_ROLE_OPTIONS, ROLE_USERS } from './demoUsers';


interface DemoRoleSwitcherProps {
  currentUser: User;
  onSwitch: (user: User) => void;
  onOpen: () => void;
}

const DemoRoleSwitcher: React.FC<DemoRoleSwitcherProps> = ({
  currentUser,
  onSwitch,
  onOpen,
}) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => {
          setIsOpen(!isOpen);
          onOpen();
        }}
        className="h-10 flex items-center gap-1.5 text-xs font-semibold px-3 border border-slate-200 rounded-lg text-slate-600 bg-white hover:bg-slate-50 hover:border-slate-300 transition-colors"
        title="Switch demo role"
      >
        <RefreshCw size={12} />
        <span className="hidden sm:inline">Switch Role</span>
      </button>
      {isOpen && (
        <div className="absolute right-0 top-full mt-2 w-72 bg-white border border-slate-200 rounded-lg shadow-xl shadow-slate-200/80 z-50 overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-100">
            <span className="text-sm font-semibold text-slate-900">Switch Demo Role</span>
            <p className="text-xs text-slate-400 mt-0.5">Currently: <span className="text-green-700 font-medium">{currentUser.roleName}</span></p>
            <p className="text-xs text-amber-600 mt-1">Internal roles only. Borrower uses separate login.</p>
          </div>
          <div className="max-h-80 overflow-y-auto py-1">
            {DEMO_ROLE_OPTIONS.map(({ role, group }, index) => (
              <React.Fragment key={role}>
                {(index === 0 || DEMO_ROLE_OPTIONS[index - 1].group !== group) && (
                  <div className="px-4 py-1.5 text-xs font-semibold text-slate-400 uppercase tracking-wide bg-slate-50 border-t border-slate-100 first:border-0">
                    {group}
                  </div>
                )}
                <button
                  onClick={() => {
                    onSwitch(ROLE_USERS[role]);
                    setIsOpen(false);
                  }}
                  className={`w-full flex items-center justify-between px-4 py-2.5 text-sm transition-colors hover:bg-slate-50 ${
                    currentUser.role === role ? 'text-green-700 bg-green-50 font-medium' : 'text-slate-700'
                  }`}
                >
                  <span>{ROLE_LABELS[role]}</span>
                  {currentUser.role === role && <ChevronRight size={14} className="text-green-500" />}
                </button>
              </React.Fragment>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DemoRoleSwitcher;
