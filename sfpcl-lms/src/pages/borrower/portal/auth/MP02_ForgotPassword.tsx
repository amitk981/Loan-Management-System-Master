import React, { useState } from 'react';
import { ArrowLeft, Mail, Smartphone, Lock } from 'lucide-react';
import { completePortalPasswordReset, startPortalPasswordReset } from '../../../../services/authSession';

interface MP02_ForgotPasswordProps {
  onBackToLogin: () => void;
  onResetComplete: () => void;
}

const MP02_ForgotPassword: React.FC<MP02_ForgotPasswordProps> = ({ onBackToLogin, onResetComplete }) => {
  const [step, setStep] = useState(1);
  const [identifier, setIdentifier] = useState('');
  const [challengeId, setChallengeId] = useState('');
  const [maskedContact, setMaskedContact] = useState('');
  const [otp, setOtp] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleStart = async () => {
    setError('');
    setIsSubmitting(true);
    try {
      const result = await startPortalPasswordReset({ identifier });
      setChallengeId(result.challengeId);
      setMaskedContact(result.maskedContact || identifier);
      setStep(2);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Password reset could not be started.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = async () => {
    setError('');
    setIsSubmitting(true);
    try {
      await completePortalPasswordReset({ challengeId, otp, password, confirmPassword });
      onResetComplete();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Password reset could not be completed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <button onClick={onBackToLogin} className="flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-slate-700 mb-6">
          <ArrowLeft size={16} /> Back to Login
        </button>
        <h2 className="text-2xl font-bold text-slate-900">Reset Password</h2>
        <p className="mt-2 text-sm text-slate-600">Enter your registered mobile number or email.</p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-xl shadow-slate-200/40 sm:rounded-2xl sm:px-10 border border-slate-100">
          {error && (
            <div className="mb-5 rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
          
          {step === 1 && (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700">Mobile Number or Email</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    {identifier.includes('@') ? <Mail size={16} className="text-slate-400" /> : <Smartphone size={16} className="text-slate-400" />}
                  </div>
                  <input
                    type="text"
                    value={identifier}
                    onChange={e => setIdentifier(e.target.value)}
                    className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50"
                    placeholder="Enter registered contact"
                  />
                </div>
              </div>
              <button onClick={handleStart} disabled={isSubmitting} className="w-full py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm transition-colors">
                {isSubmitting ? 'Sending...' : 'Send OTP'}
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700 text-center mb-2">Enter 6-digit OTP sent to {maskedContact}</label>
                <input type="text" value={otp} onChange={e => setOtp(e.target.value)} className="block w-full px-3 py-3 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-xl font-mono tracking-[0.5em] text-center bg-slate-50" placeholder="••••••" maxLength={6} />
              </div>
              <button onClick={() => setStep(3)} className="w-full py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm transition-colors">
                Verify
              </button>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700">New Password</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock size={16} className="text-slate-400" />
                  </div>
                  <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50" placeholder="••••••••" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Confirm New Password</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock size={16} className="text-slate-400" />
                  </div>
                  <input type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50" placeholder="••••••••" />
                </div>
              </div>
              <button onClick={handleComplete} disabled={isSubmitting} className="w-full py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm transition-colors">
                {isSubmitting ? 'Resetting...' : 'Reset Password'}
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default MP02_ForgotPassword;
