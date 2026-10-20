'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Search,
  AlertTriangle,
  HelpCircle,
  WifiOff,
  Lock,
  RefreshCw,
  RotateCcw,
  FileQuestion,
  Inbox,
  ArrowLeft,
  ChevronDown,
  ChevronUp,
  ShieldAlert
} from 'lucide-react';

export type CivicNoticeStateType =
  | 'loading'
  | 'no_matching_results'
  | 'no_records_available'
  | 'incomplete_record'
  | 'missing_source_document'
  | 'conflicting_evidence'
  | 'insufficient_evidence'
  | 'failed_api_request'
  | 'unavailable_restricted';

export interface CivicStateNoticeProps {
  state: CivicNoticeStateType;
  title?: string;
  description?: string;
  queryOrFilter?: string;
  onRetry?: () => void | Promise<void>;
  onClearFilters?: () => void;
  actionHref?: string;
  actionLabel?: string;
  technicalError?: string | null;
  className?: string;
}

export const CivicStateNotice: React.FC<CivicStateNoticeProps> = ({
  state,
  title,
  description,
  queryOrFilter,
  onRetry,
  onClearFilters,
  actionHref,
  actionLabel,
  technicalError,
  className = ''
}) => {
  const [retrying, setRetrying] = useState(false);
  const [showTechnical, setShowTechnical] = useState(false);

  const handleRetryClick = async () => {
    if (!onRetry || retrying) return;
    setRetrying(true);
    try {
      await onRetry();
    } finally {
      setRetrying(false);
    }
  };

  // State configurations
  const configs: Record<
    CivicNoticeStateType,
    {
      defaultTitle: string;
      defaultDesc: string;
      icon: React.ReactNode;
      containerClass: string;
      role: 'status' | 'alert';
    }
  > = {
    loading: {
      defaultTitle: 'Loading Public Records...',
      defaultDesc: 'Retrieving verified public documents and departmental data from the state registry.',
      icon: (
        <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
      ),
      containerClass: 'bg-slate-900/40 border-slate-800 text-slate-300',
      role: 'status'
    },
    no_matching_results: {
      defaultTitle: 'No Matching Public Records Found',
      defaultDesc: queryOrFilter
        ? `No published civic records matched "${queryOrFilter}". Please check spelling or adjust selected filters.`
        : 'No published civic records matched your selected filters.',
      icon: <Search className="w-7 h-7 text-amber-400" />,
      containerClass: 'bg-slate-900/60 border-slate-800 text-slate-300',
      role: 'status'
    },
    no_records_available: {
      defaultTitle: 'No Records Cataloged Yet',
      defaultDesc: 'Official records for this section are scheduled for publication following routine departmental submission.',
      icon: <Inbox className="w-7 h-7 text-slate-400" />,
      containerClass: 'bg-slate-900/40 border-slate-800 text-slate-300',
      role: 'status'
    },
    incomplete_record: {
      defaultTitle: 'Incomplete Administrative Record',
      defaultDesc: 'Some statutory parameters (e.g. audited actuals or localized beneficiary breakdowns) are pending departmental gazette notification.',
      icon: <AlertTriangle className="w-7 h-7 text-amber-400" />,
      containerClass: 'bg-amber-500/5 border-amber-500/20 text-slate-300',
      role: 'status'
    },
    missing_source_document: {
      defaultTitle: 'Source Document Pending Digitization',
      defaultDesc: 'The primary Government Order or gazette notification exists in physical state archives and has not yet been digitized on open web portals.',
      icon: <FileQuestion className="w-7 h-7 text-indigo-400" />,
      containerClass: 'bg-indigo-500/5 border-indigo-500/20 text-slate-300',
      role: 'status'
    },
    conflicting_evidence: {
      defaultTitle: 'Conflicting Records Documented',
      defaultDesc: 'Independent audit reports and departmental notifications reflect conflicting metrics or disputed fiscal implementation.',
      icon: <ShieldAlert className="w-7 h-7 text-amber-400" />,
      containerClass: 'bg-amber-500/10 border-amber-500/30 text-slate-200',
      role: 'alert'
    },
    insufficient_evidence: {
      defaultTitle: 'Insufficient Evidence to Verify',
      defaultDesc: 'Publicly indexed documentation is currently insufficient to determine definitive implementation or factual validity.',
      icon: <HelpCircle className="w-7 h-7 text-purple-400" />,
      containerClass: 'bg-purple-500/5 border-purple-500/20 text-slate-300',
      role: 'status'
    },
    failed_api_request: {
      defaultTitle: 'Unable to Connect to Civic Database',
      defaultDesc: 'The state data registry is temporarily unreachable. Your search criteria have been preserved so you can retry safely.',
      icon: <WifiOff className="w-7 h-7 text-rose-400" />,
      containerClass: 'bg-rose-500/10 border-rose-500/25 text-slate-200',
      role: 'alert'
    },
    unavailable_restricted: {
      defaultTitle: 'Access Restricted for Privacy',
      defaultDesc: 'Identifiable citizen grievance submissions or protected records are redacted in compliance with civic privacy statutes.',
      icon: <Lock className="w-7 h-7 text-blue-400" />,
      containerClass: 'bg-slate-900 border-slate-800 text-slate-300',
      role: 'status'
    }
  };

  const current = configs[state];
  const finalTitle = title || current.defaultTitle;
  const finalDesc = description || current.defaultDesc;

  return (
    <div
      role={current.role}
      aria-live={current.role === 'alert' ? 'assertive' : 'polite'}
      className={`p-8 sm:p-10 rounded-3xl border text-center space-y-4 shadow-xl max-w-2xl mx-auto backdrop-blur-md ${current.containerClass} ${className}`}
    >
      {/* Icon */}
      <div className="w-14 h-14 rounded-2xl bg-slate-950/80 border border-slate-800/80 flex items-center justify-center mx-auto shadow-inner">
        {current.icon}
      </div>

      {/* Semantic Text */}
      <div className="space-y-2">
        <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
          {finalTitle}
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed max-w-lg mx-auto">
          {finalDesc}
        </p>
      </div>

      {/* Primary Actions */}
      <div className="pt-2 flex flex-wrap items-center justify-center gap-3">
        {onRetry && (
          <button
            type="button"
            onClick={handleRetryClick}
            disabled={retrying}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-xs font-semibold shadow-lg shadow-blue-600/30 transition-all focus-visible:ring-2 focus-visible:ring-blue-400 focus:outline-none"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${retrying ? 'animate-spin' : ''}`} />
            <span>{retrying ? 'Connecting...' : 'Retry Connection'}</span>
          </button>
        )}

        {onClearFilters && (
          <button
            type="button"
            onClick={onClearFilters}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold border border-slate-700 shadow-md transition-all focus-visible:ring-2 focus-visible:ring-blue-400 focus:outline-none"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset All Filters</span>
          </button>
        )}

        {actionHref && (
          <Link
            href={actionHref}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold transition-colors focus-visible:ring-2 focus-visible:ring-blue-400 focus:outline-none"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>{actionLabel || 'Return to Directory'}</span>
          </Link>
        )}
      </div>

      {/* Technical Diagnostics Accordion (if technical details exist, never exposing file paths or credentials) */}
      {technicalError && (
        <div className="pt-3 border-t border-slate-800/80 text-left">
          <button
            type="button"
            onClick={() => setShowTechnical(!showTechnical)}
            className="inline-flex items-center gap-1.5 text-[11px] text-slate-400 hover:text-white transition-colors focus:outline-none"
            aria-expanded={showTechnical}
          >
            <span>Technical diagnostic summary</span>
            {showTechnical ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          </button>
          {showTechnical && (
            <div className="mt-2 p-3 rounded-xl bg-slate-950 border border-slate-800 font-mono text-[11px] text-rose-300/90 break-words">
              {technicalError.replace(/[A-Z]:\\[^ \n]+/gi, '[redacted_path]').replace(/\/var\/[^ \n]+/gi, '[redacted_path]')}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
