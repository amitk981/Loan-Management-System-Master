import React, { useState } from 'react';
import { Sprout, Eye, EyeOff, LogIn, AlertCircle } from 'lucide-react';

interface LoginScreenProps {
  onLogin: (credentials: { email: string; password: string }) => void | Promise<void>;
  onOpenMemberPortal?: () => void;
  error?: string;
  isSubmitting?: boolean;
  isLoadingSession?: boolean;
  demoRoleSelector?: React.ReactNode;
  demoLoginAction?: React.ReactNode;
}

const LoginScreen: React.FC<LoginScreenProps> = ({
  onLogin,
  onOpenMemberPortal,
  error: externalError = '',
  isSubmitting = false,
  isLoadingSession = false,
  demoRoleSelector,
  demoLoginAction,
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState('');
  const activeError = externalError || error;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Please enter your email and password.');
      return;
    }
    setError('');
    await onLogin({ email, password });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-slate-50 flex">
      {/* Left panel */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-green-700 p-12 text-white">
        <div className="flex items-center gap-3">
          <img src="/logo.png" alt="Logo" className="w-12 h-12 object-contain bg-white rounded-xl p-1" />
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
            <img src="/logo.png" alt="Logo" className="w-10 h-10 object-contain" />
            <div>
              <div className="font-bold text-slate-900">SFPCL Credit Management</div>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-slate-900 mb-2">Sign in to your account</h2>
          <p className="text-slate-500 text-sm mb-8">Authorised personnel only. All access is logged.</p>

          {isLoadingSession && (
            <div className="mb-5 flex items-center gap-2 text-amber-700 text-sm bg-amber-50 border border-amber-100 rounded-lg px-4 py-3">
              <AlertCircle size={16} className="flex-shrink-0" />
              Loading current staff session...
            </div>
          )}

          {onOpenMemberPortal && (
            <button
              type="button"
              onClick={onOpenMemberPortal}
              className="w-full mb-5 flex items-center justify-center gap-2 border border-green-200 bg-green-50 text-green-700 hover:bg-green-100 font-semibold py-2.5 rounded-lg transition-colors"
            >
              <Sprout size={17} />
              Open Member Portal Login
            </button>
          )}

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

            {demoRoleSelector}

            {activeError && (
              <div className="flex items-center gap-2 text-red-600 text-sm bg-red-50 border border-red-100 rounded-lg px-4 py-3">
                <AlertCircle size={16} className="flex-shrink-0" />
                {activeError}
              </div>
            )}

            <button
              type="submit"
              disabled={isSubmitting || isLoadingSession}
              className="w-full flex items-center justify-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold py-2.5 rounded-lg transition-colors"
            >
              <LogIn size={18} />
              {isSubmitting ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {demoLoginAction}

          <p className="mt-8 text-center text-xs text-slate-400">
            Forgot password? Contact your system administrator.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginScreen;
