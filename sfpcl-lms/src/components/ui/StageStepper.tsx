import React from 'react';
import { CheckCircle2, AlertTriangle, AlertOctagon, Circle, XCircle } from 'lucide-react';

export interface Step {
  id: string;
  label: string;
  sublabel?: string;
  state: 'not_started' | 'in_progress' | 'completed' | 'blocked' | 'rejected' | 'exception';
}

interface StageStepperProps {
  steps: Step[];
  compact?: boolean;
}

const stateStyles = {
  not_started: { circle: 'bg-slate-100 border-slate-300 text-slate-400', label: 'text-slate-400', connector: 'bg-slate-200' },
  in_progress: { circle: 'bg-amber-50 border-amber-400 text-amber-600', label: 'text-slate-900 font-semibold', connector: 'bg-slate-200' },
  completed:   { circle: 'bg-green-600 border-green-600 text-white', label: 'text-green-800', connector: 'bg-green-400' },
  blocked:     { circle: 'bg-red-50 border-red-400 text-red-600', label: 'text-red-700 font-semibold', connector: 'bg-slate-200' },
  rejected:    { circle: 'bg-red-100 border-red-500 text-red-600', label: 'text-red-700', connector: 'bg-red-300' },
  exception:   { circle: 'bg-violet-50 border-violet-400 text-violet-600', label: 'text-violet-700 font-semibold', connector: 'bg-slate-200' },
};

const stateIcons: Record<string, React.ReactNode> = {
  completed: <CheckCircle2 size={14} />,
  blocked: <AlertTriangle size={14} />,
  rejected: <XCircle size={14} />,
  exception: <AlertOctagon size={14} />,
};

const StageStepper: React.FC<StageStepperProps> = ({ steps, compact = false }) => {
  return (
    <div className={`flex items-start ${compact ? 'gap-0' : 'gap-0'} overflow-x-auto pb-1`}>
      {steps.map((step, idx) => {
        const styles = stateStyles[step.state];
        const isLast = idx === steps.length - 1;

        return (
          <div key={step.id} className="flex items-start flex-1 min-w-0">
            <div className="flex flex-col items-center flex-shrink-0">
              <div className={`flex items-center justify-center w-7 h-7 rounded-full border-2 ${styles.circle} transition-all`}>
                {stateIcons[step.state] || <Circle size={10} />}
              </div>
              {!compact && (
                <div className="text-center mt-1.5 max-w-[80px]">
                  <div className={`text-xs ${styles.label} leading-tight`}>{step.label}</div>
                  {step.sublabel && <div className="text-xs text-slate-400 mt-0.5 leading-tight">{step.sublabel}</div>}
                </div>
              )}
            </div>
            {!isLast && (
              <div className={`flex-1 h-0.5 mt-3.5 mx-1 ${styles.connector} min-w-[16px]`} />
            )}
          </div>
        );
      })}
    </div>
  );
};

export default StageStepper;
