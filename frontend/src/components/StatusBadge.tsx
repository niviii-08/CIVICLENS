import React from 'react';

export type StandardizedCivicStatus =
  | 'Information available'
  | 'In progress'
  | 'Reported complete'
  | 'Evidence verified'
  | 'Conflicting information'
  | 'Not enough information'
  | 'Delayed / Under review'
  | 'Contradicted by evidence';

interface StatusBadgeProps {
  status: string;
  isStatutoryVerified?: boolean;
  showTechnical?: boolean;
  className?: string;
}

/**
 * Standardize status labels to plain citizen language (Phase 11.7 Step 5).
 * Preserves the underlying status and explains the display mapping.
 */
export function standardizeStatusLabel(
  rawStatus: string,
  isStatutoryVerified = false
): { label: string; explanation: string; variant: 'complete' | 'progress' | 'conflict' | 'insufficient' | 'neutral' } {
  const s = (rawStatus || '').toLowerCase().trim();

  // 1. Evidence Verified vs Reported Complete
  if (s.includes('verified true') || (isStatutoryVerified && (s.includes('fulfill') || s.includes('resolved')))) {
    return {
      label: 'Evidence verified',
      explanation: 'Statutory orders and empirical audits confirm full implementation or truth value.',
      variant: 'complete'
    };
  }

  if (s.includes('fulfill') || s.includes('resolved') || s.includes('implement') || s.includes('active / implemented')) {
    return {
      label: 'Reported complete',
      explanation: 'Official administrative notifications declare the action complete.',
      variant: 'complete'
    };
  }

  // 2. In progress
  if (s.includes('progress') || s.includes('ongoing') || s.includes('active / ongoing')) {
    return {
      label: 'In progress',
      explanation: 'Active delivery or implementation is underway across departments.',
      variant: 'progress'
    };
  }

  // 3. Conflicting information
  if (
    s.includes('conflict') ||
    s.includes('misleading') ||
    s.includes('partially') ||
    s.includes('dispute')
  ) {
    return {
      label: 'Conflicting information',
      explanation: 'Official records reflect partial delivery or conflicting audit variances.',
      variant: 'conflict'
    };
  }

  // 4. Contradicted by evidence
  if (s.includes('false') || s.includes('broken') || s.includes('breach')) {
    return {
      label: 'Contradicted by evidence',
      explanation: 'Audit reports or statutory records contradict the stated commitment or deadline.',
      variant: 'conflict'
    };
  }

  // 5. Delayed / Under Review
  if (s.includes('stall') || s.includes('delay') || s.includes('escalated')) {
    return {
      label: 'Delayed / Under review',
      explanation: 'Implementation is pending administrative clearance or budget supplementary sanctions.',
      variant: 'insufficient'
    };
  }

  // 6. Not enough information
  if (s.includes('unsubstantiated') || s.includes('review') || s.includes('pending') || s.includes('insufficient')) {
    return {
      label: 'Not enough information',
      explanation: 'Evidence is currently insufficient to determine completion or validity.',
      variant: 'insufficient'
    };
  }

  // 7. Information Available / Default
  return {
    label: rawStatus || 'Information available',
    explanation: 'Civic parameters and public documents are published for citizen reference.',
    variant: 'neutral'
  };
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  isStatutoryVerified = false,
  showTechnical = false,
  className = ''
}) => {
  const { label, explanation, variant } = standardizeStatusLabel(status, isStatutoryVerified);

  let styles = 'bg-slate-800 text-slate-300 border-slate-700';

  if (variant === 'complete') {
    styles = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
  } else if (variant === 'progress') {
    styles = 'bg-blue-500/15 text-blue-400 border-blue-500/30';
  } else if (variant === 'conflict') {
    styles = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
  } else if (variant === 'insufficient') {
    styles = 'bg-purple-500/15 text-purple-400 border-purple-500/30';
  }

  const displayLabel = showTechnical && status && status !== label ? `${label} (${status})` : label;

  return (
    <span
      title={`Status Meaning: ${explanation}${status !== label ? ` • Technical record: "${status}"` : ''}`}
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border transition-colors cursor-help ${styles} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 bg-current opacity-80" />
      <span>{displayLabel}</span>
    </span>
  );
};
