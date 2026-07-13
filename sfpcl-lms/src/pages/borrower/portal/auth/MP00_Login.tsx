import React, { useState } from 'react';
import { Leaf, Lock, Mail, Smartphone, ArrowRight, CheckCircle2 } from 'lucide-react';

interface MP00_LoginProps {
  onSubmitLogin: (credentials: { identifier: string; password: string }) => Promise<void>;
  onNavigateToActivation: () => void;
  onNavigateToForgot: () => void;
  onBackToStaffLogin?: () => void;
  error?: string;
  isSubmitting?: boolean;
}

const MP00_Login: React.FC<MP00_LoginProps> = ({ onSubmitLogin, onNavigateToActivation, onNavigateToForgot, onBackToStaffLogin, error, isSubmitting = false }) => {
  const [method, setMethod] = useState<'password' | 'otp'>('password');
  const [identifier, setIdentifier] = useState('');
  const [secret, setSecret] = useState('');
  const [localError, setLocalError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalError('');
    if (method === 'otp') {
      setLocalError('OTP login will be available after portal OTP preference setup.');
      return;
    }
    if (!identifier || !secret) {
      setLocalError('Enter your registered contact and password.');
      return;
    }
    await onSubmitLogin({ identifier, password: secret });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center mb-6">
          <img src="/logo.png" alt="Logo" className="w-16 h-16 object-contain" />
        </div>
        <h2 className="text-center text-2xl font-bold text-slate-900">Member Portal</h2>
        <p className="mt-2 text-center text-sm text-slate-600">Sahyadri Farmers Producer Company Limited</p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-xl shadow-slate-200/40 sm:rounded-2xl sm:px-10 border border-slate-100">
          
          <div className="flex p-1 bg-slate-100 rounded-xl mb-6">
            <button
              type="button"
              onClick={() => setMethod('password')}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${method === 'password' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Password
            </button>
            <button
              type="button"
              onClick={() => setMethod('otp')}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${method === 'otp' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
            >
              Login with OTP
            </button>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            {(error || localError) && (
              <div className="rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-700">
                {error || localError}
              </div>
            )}
            <div>
              <label htmlFor="identifier" className="block text-sm font-medium text-slate-700">
                Mobile Number or Email
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  {identifier.includes('@') ? <Mail size={16} className="text-slate-400" /> : <Smartphone size={16} className="text-slate-400" />}
                </div>
                <input
                  id="identifier"
                  type="text"
                  value={identifier}
                  onChange={e => setIdentifier(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50 focus:bg-white transition-colors"
                  placeholder="Enter registered contact"
                />
              </div>
            </div>

            <div>
              <label htmlFor="secret" className="block text-sm font-medium text-slate-700">
                {method === 'password' ? 'Password' : 'Enter OTP'}
              </label>
              <div className="mt-1 relative rounded-md shadow-sm">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  {method === 'password' ? <Lock size={16} className="text-slate-400" /> : <CheckCircle2 size={16} className="text-slate-400" />}
                </div>
                <input
                  id="secret"
                  type={method === 'password' ? 'password' : 'text'}
                  value={secret}
                  onChange={e => setSecret(e.target.value)}
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50 focus:bg-white transition-colors"
                  placeholder={method === 'password' ? '••••••••' : '6-digit OTP'}
                />
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-green-600 focus:ring-green-500 border-slate-300 rounded"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-600">
                  Remember device
                </label>
              </div>

              {method === 'password' && (
                <div className="text-sm">
                  <button type="button" onClick={onNavigateToForgot} className="font-medium text-green-600 hover:text-green-500">
                    Forgot password?
                  </button>
                </div>
              )}
            </div>

            <div>
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                {isSubmitting ? 'Signing in...' : method === 'password' ? 'Sign in securely' : 'Verify OTP & Login'}
              </button>
            </div>
          </form>

          <div className="mt-6 border-t border-slate-100 pt-6">
            <div className="rounded-xl bg-green-50 p-4 border border-green-100">
              <div className="flex">
                <div className="ml-3 flex-1">
                  <h3 className="text-sm font-medium text-green-800">First time here?</h3>
                  <div className="mt-2 text-sm text-green-700">
                    <p>If you are an SFPCL member, you can activate your portal account using your Folio Number and Aadhaar details.</p>
                  </div>
                  <div className="mt-3">
                    <button
                      type="button"
                      onClick={onNavigateToActivation}
                      className="inline-flex flex-row items-center gap-1.5 text-sm font-semibold text-green-700 hover:text-green-800 bg-white px-3 py-1.5 rounded-lg shadow-sm border border-green-200"
                    >
                      Activate Account <ArrowRight size={14} />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
        <p className="text-center text-xs text-slate-400 mt-8">
          This portal is protected by industry-standard encryption.<br/>
          No PAN or bank details are required to log in.
        </p>
        {onBackToStaffLogin && (
          <div className="mt-4 text-center">
            <button
              type="button"
              onClick={onBackToStaffLogin}
              className="text-sm font-medium text-slate-500 hover:text-slate-700"
            >
              Back to staff login
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default MP00_Login;
