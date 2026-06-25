import React from 'react';
import { TrendingUp, TrendingDown, Minus, LucideIcon } from 'lucide-react';

interface KPICardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  trend?: 'up' | 'down' | 'flat';
  trendLabel?: string;
  icon: LucideIcon;
  iconBg?: string;
  iconColor?: string;
  onClick?: () => void;
  highlight?: 'normal' | 'warning' | 'danger' | 'success';
}

const highlightStyles = {
  normal:  { card: 'bg-white border-slate-200', icon: 'bg-slate-100', iconColor: 'text-slate-600' },
  warning: { card: 'bg-amber-50 border-amber-200', icon: 'bg-amber-100', iconColor: 'text-amber-700' },
  danger:  { card: 'bg-red-50 border-red-200', icon: 'bg-red-100', iconColor: 'text-red-700' },
  success: { card: 'bg-green-50 border-green-200', icon: 'bg-green-100', iconColor: 'text-green-700' },
};

const KPICard: React.FC<KPICardProps> = ({
  title, value, subtitle, trend, trendLabel, icon: Icon,
  iconBg, iconColor, onClick, highlight = 'normal',
}) => {
  const styles = highlightStyles[highlight];

  return (
    <div
      className={`rounded-lg border p-4 min-h-[132px] ${styles.card} ${onClick ? 'cursor-pointer hover:-translate-y-0.5 hover:shadow-md transition-all' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div className={`p-2.5 rounded-lg ${iconBg || styles.icon}`}>
          <Icon size={20} className={iconColor || styles.iconColor} />
        </div>
        {trend && (
          <span className={`flex items-center gap-1 text-xs font-medium ${trend === 'up' ? 'text-red-600' : trend === 'down' ? 'text-green-600' : 'text-slate-500'}`}>
            {trend === 'up' ? <TrendingUp size={12} /> : trend === 'down' ? <TrendingDown size={12} /> : <Minus size={12} />}
            {trendLabel}
          </span>
        )}
      </div>
      <div className="mt-3 min-w-0">
        <div className="text-2xl font-bold text-slate-900 num">{value}</div>
        <div className="text-sm text-slate-600 mt-0.5">{title}</div>
        {subtitle && <div className="text-xs text-slate-400 mt-1">{subtitle}</div>}
      </div>
    </div>
  );
};

export default KPICard;
