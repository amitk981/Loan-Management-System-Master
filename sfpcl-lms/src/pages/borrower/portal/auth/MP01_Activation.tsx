import React, { useState } from 'react';
import { ArrowLeft, User, Phone, CheckCircle2 } from 'lucide-react';
import { completePortalActivation, startPortalActivation } from '../../../../services/authSession';

interface MP01_ActivationProps {
  onBackToLogin: () => void;
  onActivate: () => void;
}

const MP01_Activation: React.FC<MP01_ActivationProps> = ({ onBackToLogin, onActivate }) => {
  const [step, setStep] = useState(1);
  const [folioOrMemberId, setFolioOrMemberId] = useState('');
  const [contact, setContact] = useState('');
  const [panLast4, setPanLast4] = useState('');
  const [aadhaarLast4, setAadhaarLast4] = useState('');
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
      const result = await startPortalActivation({ folioOrMemberId, contact, panLast4, aadhaarLast4 });
      setChallengeId(result.challengeId);
      setMaskedContact(result.maskedContact || contact);
      setStep(2);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Activation could not be started.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = async () => {
    setError('');
    setIsSubmitting(true);
    try {
      await completePortalActivation({ challengeId, otp, password, confirmPassword });
      onActivate();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Activation could not be completed.');
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
        <h2 className="text-2xl font-bold text-slate-900">Activate Member Account</h2>
        <p className="mt-2 text-sm text-slate-600">Verify your SFPCL membership to access the portal.</p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow-xl shadow-slate-200/40 sm:rounded-2xl sm:px-10 border border-slate-100">
          {error && (
            <div className="mb-5 rounded-lg border border-red-100 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </div>
          )}
          
          {/* Stepper */}
          <div className="flex items-center justify-between mb-8">
            <div className={`flex flex-col items-center ${step >= 1 ? 'text-green-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 1 ? 'bg-green-100' : 'bg-slate-100'}`}>1</div>
              <span className="text-xs mt-1 font-medium">Identify</span>
            </div>
            <div className={`flex-1 h-1 mx-2 ${step >= 2 ? 'bg-green-500' : 'bg-slate-100'}`}></div>
            <div className={`flex flex-col items-center ${step >= 2 ? 'text-green-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 2 ? 'bg-green-100' : 'bg-slate-100'}`}>2</div>
              <span className="text-xs mt-1 font-medium">Verify OTP</span>
            </div>
            <div className={`flex-1 h-1 mx-2 ${step >= 3 ? 'bg-green-500' : 'bg-slate-100'}`}></div>
            <div className={`flex flex-col items-center ${step >= 3 ? 'text-green-600' : 'text-slate-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 3 ? 'bg-green-100' : 'bg-slate-100'}`}>3</div>
              <span className="text-xs mt-1 font-medium">Secure</span>
            </div>
          </div>

          {step === 1 && (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700">Folio Number / Member ID</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User size={16} className="text-slate-400" />
                  </div>
                  <input type="text" value={folioOrMemberId} onChange={e => setFolioOrMemberId(e.target.value)} className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50" placeholder="e.g. M-00042" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Registered Mobile or Email</label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Phone size={16} className="text-slate-400" />
                  </div>
                  <input type="text" value={contact} onChange={e => setContact(e.target.value)} className="block w-full pl-10 pr-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50" placeholder="+91" />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700">PAN (Last 4)</label>
                  <input type="text" value={panLast4} onChange={e => setPanLast4(e.target.value)} className="mt-1 block w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50 text-center tracking-widest" placeholder="1234" maxLength={4} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-700">Aadhaar (Last 4)</label>
                  <input type="text" value={aadhaarLast4} onChange={e => setAadhaarLast4(e.target.value)} className="mt-1 block w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50 text-center tracking-widest" placeholder="7788" maxLength={4} />
                </div>
              </div>
              <button onClick={handleStart} disabled={isSubmitting} className="w-full py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm transition-colors mt-2">
                {isSubmitting ? 'Checking...' : 'Find My Record'}
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="space-y-5">
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200 text-center">
                <CheckCircle2 className="mx-auto text-green-500 mb-2" size={24} />
                <p className="text-sm font-medium text-slate-900">Member record verified</p>
                <p className="text-xs text-slate-500 mt-1">An OTP has been sent to {maskedContact}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 text-center mb-2">Enter 6-digit OTP</label>
                <input type="text" value={otp} onChange={e => setOtp(e.target.value)} className="block w-full px-3 py-3 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-xl font-mono tracking-[0.5em] text-center bg-slate-50" placeholder="••••••" maxLength={6} />
              </div>
              <div className="flex gap-3">
                <button onClick={() => setStep(1)} className="flex-1 py-2.5 px-4 bg-white border border-slate-200 text-slate-700 rounded-lg font-medium text-sm transition-colors">
                  Back
                </button>
                <button onClick={() => setStep(3)} className="flex-1 py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm transition-colors">
                  Verify OTP
                </button>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-5">
              <div>
                <label className="block text-sm font-medium text-slate-700">Set Portal Password</label>
                <input type="password" value={password} onChange={e => setPassword(e.target.value)} className="mt-1 block w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50" placeholder="••••••••" />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700">Confirm Password</label>
                <input type="password" value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} className="mt-1 block w-full px-3 py-2.5 border border-slate-200 rounded-lg focus:ring-green-500 focus:border-green-500 sm:text-sm bg-slate-50" placeholder="••••••••" />
              </div>
              <button onClick={handleComplete} disabled={isSubmitting} className="w-full py-2.5 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm transition-colors">
                {isSubmitting ? 'Activating...' : 'Activate Account'}
              </button>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default MP01_Activation;
