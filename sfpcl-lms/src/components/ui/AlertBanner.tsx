import React from 'react';
import { AlertTriangle, AlertOctagon, Info, CheckCircle2, X } from 'lucide-react';

type AlertType = 'info' | 'warning' | 'error' | 'success' | 'exception';

interface AlertBannerProps {
  type: AlertType;
  title: string;
  message?: string;
  onDismiss?: () => void;
  actions?: React.ReactNode;
}

const typeConfig = {
  info:      { bg: 'bg-blue-50 border-blue-200',    text: 'text-blue-900',    sub: 'text-blue-700',    icon: <Info size={16} className="text-blue-600 flex-shrink-0 mt-0.5" /> },
  warning:   { bg: 'bg-amber-50 border-amber-200',  text: 'text-amber-900',   sub: 'text-amber-700',   icon: <AlertTriangle size={16} className="text-amber-600 flex-shrink-0 mt-0.5" /> },
  error:     { bg: 'bg-red-50 border-red-200',      text: 'text-red-900',     sub: 'text-red-700',     icon: <AlertTriangle size={16} className="text-red-600 flex-shrink-0 mt-0.5" /> },
  success:   { bg: 'bg-green-50 border-green-200',  text: 'text-green-900',   sub: 'text-green-700',   icon: <CheckCircle2 size={16} className="text-green-600 flex-shrink-0 mt-0.5" /> },
  exception: { bg: 'bg-violet-50 border-violet-200',text: 'text-violet-900',  sub: 'text-violet-700',  icon: <AlertOctagon size={16} className="text-violet-600 flex-shrink-0 mt-0.5" /> },
};

const AlertBanner: React.FC<AlertBannerProps> = ({ type, title, message, onDismiss, actions }) => {
  const config = typeConfig[type];

  return (
    <div className={`rounded-lg border px-4 py-3 ${config.bg}`}>
      <div className="flex items-start gap-2.5">
        {config.icon}
        <div className="flex-1 min-w-0">
          <p className={`text-sm font-semibold ${config.text}`}>{title}</p>
          {message && <p className={`text-sm mt-0.5 ${config.sub}`}>{message}</p>}
          {actions && <div className="mt-2 flex gap-2">{actions}</div>}
        </div>
        {onDismiss && (
          <button onClick={onDismiss} className="text-slate-400 hover:text-slate-600 flex-shrink-0">
            <X size={14} />
          </button>
        )}
      </div>
    </div>
  );
};

export default AlertBanner;
