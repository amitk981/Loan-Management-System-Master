import React, { useState } from 'react';
import { CheckCircle2, Lock, ShieldCheck, Smartphone } from 'lucide-react';
import { changePortalPassword } from '../../../../services/authSession';

const MP25_SecuritySettings: React.FC = () => {
  const [saved, setSaved] = useState(false);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fields = [
    ['Current Password', currentPassword, setCurrentPassword],
    ['New Password', newPassword, setNewPassword],
    ['Confirm New Password', confirmPassword, setConfirmPassword],
  ] as const;

  const handleChangePassword = async () => {
    setSaved(false);
    setError('');
    setIsSubmitting(true);
    try {
      await changePortalPassword({ currentPassword, newPassword, confirmPassword });
      setSaved(true);
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Password could not be updated.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold text-slate-900">Security Settings</h2>
        <p className="text-sm text-slate-500 mt-1">Manage password, OTP preference, and active session information.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-slate-100 p-5">
          <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
            <Lock size={16} className="text-green-600" />
            Change Password
          </h3>
          <div className="space-y-4">
            {fields.map(([label, value, setValue]) => (
              <div key={label}>
                <label className="block text-sm font-medium text-slate-700 mb-1.5">{label}</label>
                <input type="password" value={value} onChange={event => setValue(event.target.value)} className="w-full px-3 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-green-500" />
              </div>
            ))}
            <button onClick={handleChangePassword} disabled={isSubmitting} className="bg-green-600 hover:bg-green-700 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors">
              {isSubmitting ? 'Updating...' : 'Update Password'}
            </button>
            {error && (
              <div className="text-sm text-red-700">
                {error}
              </div>
            )}
            {saved && (
              <div className="flex items-center gap-2 text-sm text-green-700">
                <CheckCircle2 size={15} />
                Security settings saved.
              </div>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-slate-100 p-5">
            <h3 className="font-semibold text-slate-900 mb-4 flex items-center gap-2">
              <Smartphone size={16} className="text-green-600" />
              OTP & Contact
            </h3>
            <div className="space-y-3 text-sm">
              {[
                ['Registered Mobile', '+91 98XXXXXX10'],
                ['Registered Email', 'ga****@example.com'],
                ['OTP Login', 'Enabled'],
                ['Last Login', '25 Jun 2026, 10:30 AM'],
              ].map(([label, value]) => (
                <div key={label} className="flex items-center justify-between border-b border-slate-50 pb-2 last:border-0 last:pb-0">
                  <span className="text-slate-500">{label}</span>
                  <span className="font-medium text-slate-900">{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-green-50 border border-green-100 rounded-xl p-5">
            <h4 className="font-semibold text-green-900 flex items-center gap-2 mb-2">
              <ShieldCheck size={16} />
              Account Protection
            </h4>
            <p className="text-sm text-green-700">Your account uses OTP verification for sensitive document and application actions.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MP25_SecuritySettings;
