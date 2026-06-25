import React, { useState } from 'react';
import { Sprout, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';
import { Role } from '../../types';
import { ROLE_LABELS, ROLE_USERS } from '../../contexts/RoleContext';

interface LoginScreenProps {
  onLogin: (role: Role) => void;
}

const ALL_ROLES: Role[] = [
  'credit_manager', 'deputy_manager_finance', 'compliance_team',
  'company_secretary', 'sanction_committee', 'cfo', 'director',
  'senior_manager_finance', 'cfc', 'accounts', 'auditor', 'admin', 'borrower',
];

const LoginScreen: React.FC<LoginScreenProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const [demoRole, setDemoRole] = useState<Role>('credit_manager');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter your email and password.');
      return;
    }
    // In demo mode, always succeed — role is set via dropdown
    setError('');
    onLogin(demoRole);
  };

  const handleDemoLogin = (role: Role) => {
    onLogin(role);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-slate-50 flex">
      {/* Left panel */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-green-700 p-12 text-white">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
            <Sprout size={22} className="text-white" />
          </div>
          <div>
            <div className="text-lg font-bold leading-tight">SFPCL</div>
            <div className="text-green-200 text-sm">Credit Management System</div>
          </div>
        </div>
        <div>
          <h1 className="text-4xl font-bold leading-tight mb-4">
            Member Credit<br />Administration &<br />Loan Management
          </h1>
          <p className="text-green-100 text-lg leading-relaxed">
            Sahyadri Farmers Producer Company Limited — end-to-end loan lifecycle management for farmer-members.
          </p>
          <div className="mt-8 grid grid-cols-2 gap-4">
            {[
              { label: 'Active Loans', value: '₹2.4 Cr' },
              { label: 'Members Served', value: '147' },
              { label: 'Sec 186 Used', value: '64%' },
              { label: 'Repayment Rate', value: '91%' },
            ].map(stat => (
              <div key={stat.label} className="bg-white/10 rounded-xl p-4">
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-green-200 text-sm mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
        <div className="text-green-300 text-sm">
          SOP Reference: SOP_SFPCL_LOANDISBURSEMENT v1.0 · August 2025
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex flex-col justify-center px-8 sm:px-16 lg:px-20 py-12">
        <div className="max-w-md w-full mx-auto">
          {/* Mobile logo */}
          <div className="flex items-center gap-3 mb-8 lg:hidden">
            <div className="w-9 h-9 bg-green-600 rounded-xl flex items-center justify-center">
              <Sprout size={20} className="text-white" />
            </div>
            <div>
              <div className="font-bold text-slate-900">SFPCL Credit Management</div>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-slate-900 mb-2">Sign in to your account</h2>
          <p className="text-slate-500 text-sm mb-8">Authorised personnel only. All access is logged.</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Email address</label>
              <input
                type="email"
                value={email}
                onChange={e => { setEmail(e.target.value); setError(''); }}
                placeholder="you@sfpcl.in"
                className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">Password</label>
              <div className="relative">
                <input
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={e => { setPassword(e.target.value); setError(''); }}
                  placeholder="••••••••"
                  className="w-full px-4 py-2.5 pr-10 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                >
                  {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            {/* Demo role selector */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                Demo role (select to preview as any user)
              </label>
              <select
                value={demoRole}
                onChange={e => setDemoRole(e.target.value as Role)}
                className="w-full px-4 py-2.5 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent bg-white"
              >
                {ALL_ROLES.map(r => (
                  <option key={r} value={r}>{ROLE_LABELS[r]}</option>
                ))}
              </select>
              <p className="text-xs text-slate-400 mt-1">
                Signing in as: <span className="font-medium text-slate-600">{ROLE_USERS[demoRole].name}</span> · {ROLE_USERS[demoRole].email}
              </p>
            </div>

            {error && (
              <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 border border-red-100 rounded-lg px-4 py-3">
                <AlertCircle size={16} className="flex-shrink-0" />
                {error}
              </div>
            )}

            <button
              type="submit"
              className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5 rounded-lg transition-colors"
            >
              <LogIn size={18} />
              Sign in
            </button>
          </form>

          <div className="mt-8">
            <div className="text-xs text-slate-400 text-center mb-4">— Quick demo login as —</div>
            <div className="grid grid-cols-2 gap-2">
              {ALL_ROLES.filter(r => r !== 'borrower').slice(0, 6).map(role => (
                <button
                  key={role}
                  onClick={() => handleDemoLogin(role)}
                  className="text-xs px-3 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-green-50 hover:border-green-200 hover:text-green-700 transition-colors text-left"
                >
                  {ROLE_LABELS[role]}
                </button>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              {ALL_ROLES.filter(r => r !== 'borrower').slice(6).map(role => (
                <button
                  key={role}
                  onClick={() => handleDemoLogin(role)}
                  className="text-xs px-3 py-2 border border-slate-200 rounded-lg text-slate-600 hover:bg-green-50 hover:border-green-200 hover:text-green-700 transition-colors text-left"
                >
                  {ROLE_LABELS[role]}
                </button>
              ))}
              <button
                onClick={() => handleDemoLogin('borrower')}
                className="text-xs px-3 py-2 border border-amber-200 rounded-lg text-amber-700 hover:bg-amber-50 transition-colors text-left"
              >
                Borrower / Farmer
              </button>
            </div>
          </div>

          <p className="mt-8 text-center text-xs text-slate-400">
            Forgot password? Contact your system administrator.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
