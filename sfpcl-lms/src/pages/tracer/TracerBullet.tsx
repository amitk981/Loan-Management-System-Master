import React, { useState } from 'react';
import { PlayCircle } from 'lucide-react';
import AlertBanner from '../../components/ui/AlertBanner';
import StatusBadge from '../../components/ui/StatusBadge';
import { AuthSessionError } from '../../services/authSession';
import { runTracerLifecycle, TracerRecord } from '../../services/tracerApi';
import { useRole } from '../../contexts/RoleContext';

interface TracerBulletProps {
  onSessionExpired: () => void;
}

const TracerBullet: React.FC<TracerBulletProps> = ({ onSessionExpired }) => {
  const { currentUser, can } = useRole();
  const [records, setRecords] = useState<TracerRecord[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState('');

  const runTracer = async () => {
    if (!can('run_tracer')) return;
    setIsRunning(true);
    setError('');
    try {
      setRecords(await runTracerLifecycle());
    } catch (caught) {
      if (
        caught instanceof AuthSessionError
        && ['AUTH_REQUIRED', 'INVALID_TOKEN', 'TOKEN_EXPIRED'].includes(caught.code)
      ) {
        onSessionExpired();
        return;
      }
      setError(caught instanceof Error ? caught.message : 'Tracer run failed.');
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Tracer</h1>
          <p className="text-slate-600 mt-1">
            {currentUser.roleName}
            {currentUser.teamName ? ` · ${currentUser.teamName}` : ''}
          </p>
        </div>
        <button
          onClick={runTracer}
          disabled={isRunning || !can('run_tracer')}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 text-white text-sm font-semibold hover:bg-green-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
        >
          <PlayCircle size={16} />
          {isRunning ? 'Running' : 'Run tracer'}
        </button>
      </div>

      {error && <AlertBanner type="warning" title="Tracer failed" message={error} />}

      <div className="bg-white rounded-lg border border-slate-200 overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">Lifecycle evidence</h2>
          <p className="text-sm text-slate-500 mt-1">Real API calls against the authenticated staff session.</p>
        </div>
        <div className="divide-y divide-slate-100">
          {records.length === 0 ? (
            <div className="px-5 py-8 text-sm text-slate-500">
              No tracer run recorded in this session.
            </div>
          ) : records.map(record => (
            <div key={`${record.label}-${record.reference}`} className="px-5 py-4 flex items-center justify-between gap-4">
              <div>
                <div className="text-sm font-semibold text-slate-900">{record.label}</div>
                <div className="text-sm text-slate-500">
                  {record.reference}
                  {record.amount ? ` · Rs. ${record.amount}` : ''}
                </div>
              </div>
              <StatusBadge label={record.status} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TracerBullet;
