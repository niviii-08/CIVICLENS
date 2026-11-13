import React from 'react';

interface MetricCardProps {
  title: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
  icon: React.ReactNode;
  subtitle?: string;
  accentColor?: 'blue' | 'emerald' | 'amber' | 'rose' | 'cyan' | 'purple';
}

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  change,
  changeType = 'neutral',
  icon,
  subtitle,
  accentColor = 'blue',
}) => {
  const glowMap = {
    blue: 'bg-blue-500/10 group-hover:bg-blue-500/20 text-blue-400 border-blue-500/30',
    emerald: 'bg-emerald-500/10 group-hover:bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    amber: 'bg-amber-500/10 group-hover:bg-amber-500/20 text-amber-400 border-amber-500/30',
    rose: 'bg-rose-500/10 group-hover:bg-rose-500/20 text-rose-400 border-rose-500/30',
    cyan: 'bg-cyan-500/10 group-hover:bg-cyan-500/20 text-cyan-400 border-cyan-500/30',
    purple: 'bg-purple-500/10 group-hover:bg-purple-500/20 text-purple-400 border-purple-500/30',
  };

  return (
    <div className="civic-card p-5 group shadow-xl">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">{title}</span>
        <div className={`p-2.5 rounded-xl border backdrop-blur-md transition-all duration-300 group-hover:scale-110 shadow-sm ${glowMap[accentColor]}`}>
          {icon}
        </div>
      </div>

      <div className="mt-4 flex items-baseline gap-2.5">
        <span className="text-2xl sm:text-3xl font-black tracking-tight text-white group-hover:text-cyan-300 transition-colors">
          {value}
        </span>
        {change && (
          <span
            className={`text-[11px] font-bold px-2 py-0.5 rounded-full border transition-transform duration-200 group-hover:scale-105 ${
              changeType === 'positive'
                ? 'text-emerald-300 bg-emerald-500/15 border-emerald-500/30'
                : changeType === 'negative'
                ? 'text-rose-300 bg-rose-500/15 border-rose-500/30'
                : 'text-slate-300 bg-slate-800/80 border-slate-700'
            }`}
          >
            {change}
          </span>
        )}
      </div>

      {subtitle && (
        <p className="mt-2 text-xs text-slate-400 font-medium leading-relaxed">
          {subtitle}
        </p>
      )}
    </div>
  );
};
