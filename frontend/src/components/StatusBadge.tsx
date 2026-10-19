import React from 'react';

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className = '' }) => {
  const s = (status || '').toLowerCase();

  let styles = 'bg-slate-800 text-slate-300 border-slate-700';

  if (s.includes('fulfill') || s.includes('implement') || s.includes('verified true') || s.includes('resolved')) {
    styles = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
  } else if (s.includes('progress') || s.includes('partially') || s.includes('ongoing')) {
    styles = 'bg-blue-500/15 text-blue-400 border-blue-500/30';
  } else if (s.includes('broken') || s.includes('false') || s.includes('breach')) {
    styles = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
  } else if (s.includes('misleading') || s.includes('stall') || s.includes('escalated')) {
    styles = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
  } else if (s.includes('pending') || s.includes('review') || s.includes('unsubstantiated')) {
    styles = 'bg-purple-500/15 text-purple-400 border-purple-500/30';
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors ${styles} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-80" />
      {status}
    </span>
  );
};
