'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Bookmark,
  BookmarkCheck,
  Trash2,
  RefreshCw,
  Bell,
  BellOff,
  Shield,
  ExternalLink,
  AlertCircle,
  CheckCircle2,
  ScrollText,
  Landmark,
  Users,
  ShieldCheck,
  AlertTriangle,
  Info,
  ArrowRight
} from 'lucide-react';
import { useSavedCivicItems, SavedCivicRecord } from '@/lib/useSavedCivicItems';

const TYPE_CONFIG = {
  promise: {
    label: 'Manifesto Promise',
    icon: ScrollText,
    badgeBg: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  },
  scheme: {
    label: 'Government Scheme',
    icon: Landmark,
    badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  },
  representative: {
    label: 'Elected Representative',
    icon: Users,
    badgeBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
  },
  claim: {
    label: 'Claim Assessment',
    icon: ShieldCheck,
    badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  },
  civic: {
    label: 'Civic Grievance',
    icon: AlertTriangle,
    badgeBg: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  },
};

export default function SavedRecordsPage() {
  const {
    savedItems,
    liveStatuses,
    loading,
    highlightUpdates,
    removeRecord,
    clearAll,
    toggleHighlightUpdates,
    refreshUpdates,
  } = useSavedCivicItems();

  const [activeFilter, setActiveFilter] = useState<string>('all');
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await refreshUpdates();
    setTimeout(() => setIsRefreshing(false), 500);
  };

  const filteredItems = savedItems.filter((item) => {
    if (activeFilter === 'all') return true;
    return item.record_type === activeFilter;
  });

  const updatesCount = Object.values(liveStatuses).filter((s) => s.has_update).length;

  return (
    <div className="space-y-8 pb-12">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-6 relative">
        <div className="absolute -bottom-[1px] left-0 w-32 h-[1px] bg-gradient-to-r from-cyan-500 to-transparent" />
        <div>
          <div className="flex items-center gap-2.5 mb-2">
            <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 text-cyan-400 border border-cyan-500/30">
              <Bookmark className="w-5 h-5" />
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-white">
              Tracked Civic Records
            </h1>
          </div>
          <p className="text-sm text-slate-400 max-w-2xl leading-relaxed">
            Monitor real-world changes, legislative notifications, and budget updates across your selected
            manifesto pledges, welfare schemes, elected representatives, claims, and public grievances.
          </p>
        </div>

        {/* Global Action Bar */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <button
            onClick={toggleHighlightUpdates}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all duration-200 ${
              highlightUpdates
                ? 'bg-gradient-to-r from-indigo-600/30 to-cyan-600/30 text-cyan-300 border-cyan-500/40 shadow-sm'
                : 'bg-slate-900/80 text-slate-400 border-white/10 hover:bg-slate-800'
            }`}
            title="Toggle update highlighting"
          >
            {highlightUpdates ? <Bell className="w-3.5 h-3.5 text-cyan-400" /> : <BellOff className="w-3.5 h-3.5" />}
            <span>{highlightUpdates ? 'Update Alerts Active' : 'Alerts Muted'}</span>
          </button>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing || savedItems.length === 0}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-slate-900/80 border border-white/10 hover:border-white/20 text-slate-200 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-cyan-400' : ''}`} />
            <span>Check Updates</span>
          </button>

          {savedItems.length > 0 && (
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to remove all saved civic records?')) {
                  clearAll();
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-rose-500/10 border border-rose-500/20 text-rose-300 hover:bg-rose-500/20 transition-all"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear All</span>
            </button>
          )}
        </div>
      </div>

      {/* Privacy Notice Banner */}
      <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-r from-indigo-950/30 via-slate-900/70 to-slate-900/70 border border-white/10 flex items-start gap-3.5 backdrop-blur-md">
        <Shield className="w-5 h-5 text-cyan-400 mt-0.5 shrink-0" />
        <div className="text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-white">
            Local-First &amp; Privacy-Preserving Citizen Tracking
          </p>
          <p className="text-slate-400 leading-relaxed">
            Your tracked items are saved strictly in your device&apos;s local browser storage. No account,
            email, or phone number is collected. CIVICLENS TN performs zero telemetry, cross-device profiling,
            or automated behavioral tracking.
          </p>
        </div>
      </div>

      {/* Filter Tabs & Counter */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-1.5 p-1 bg-slate-900/80 border border-white/10 rounded-xl text-xs overflow-x-auto custom-scrollbar">
          {[
            { id: 'all', label: `All (${savedItems.length})` },
            { id: 'promise', label: 'Promises' },
            { id: 'scheme', label: 'Schemes' },
            { id: 'representative', label: 'MLAs' },
            { id: 'claim', label: 'Claims' },
            { id: 'civic', label: 'Civic Grievances' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveFilter(tab.id)}
              className={`px-3 py-1.5 rounded-lg font-semibold transition-all duration-200 whitespace-nowrap ${
                activeFilter === tab.id
                  ? 'bg-gradient-to-r from-indigo-600 to-cyan-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800/60'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {updatesCount > 0 && highlightUpdates && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold animate-pulse">
            <span className="w-2 h-2 rounded-full bg-amber-400" />
            <span>{updatesCount} Tracked {updatesCount === 1 ? 'Item Has' : 'Items Have'} Recent Changes</span>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="p-12 text-center text-slate-500 text-sm animate-pulse">
          Loading your tracked civic records...
        </div>
      )}

      {/* Empty State */}
      {!loading && savedItems.length === 0 && (
        <div className="p-10 rounded-3xl bg-slate-900/50 border border-white/10 text-center max-w-xl mx-auto space-y-5 backdrop-blur-xl">
          <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-cyan-500/20 text-cyan-400 border border-cyan-500/30 flex items-center justify-center mx-auto">
            <BookmarkCheck className="w-7 h-7" />
          </div>
          <div className="space-y-1.5">
            <h3 className="text-lg font-bold text-white">No Tracked Items Yet</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Save promises, welfare schemes, MLAs, and civic issues to monitor updates and progress over time.
            </p>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
            <Link
              href="/schemes"
              className="px-3.5 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-xs font-semibold text-cyan-300 border border-cyan-500/20 transition-all"
            >
              Browse Schemes
            </Link>
            <Link
              href="/representatives"
              className="px-3.5 py-1.5 rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 text-xs font-semibold text-indigo-300 border border-indigo-500/20 transition-all"
            >
              Browse MLAs
            </Link>
            <Link
              href="/claims"
              className="px-3.5 py-1.5 rounded-xl bg-amber-500/10 hover:bg-amber-500/20 text-xs font-semibold text-amber-300 border border-amber-500/20 transition-all"
            >
              Browse Claims
            </Link>
            <Link
              href="/civic"
              className="px-3.5 py-1.5 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-xs font-semibold text-rose-300 border border-rose-500/20 transition-all"
            >
              Browse Grievances
            </Link>
          </div>
        </div>
      )}

      {/* Filtered Empty State */}
      {!loading && savedItems.length > 0 && filteredItems.length === 0 && (
        <div className="p-8 text-center text-slate-400 text-xs bg-slate-900/40 rounded-2xl border border-white/5">
          No tracked records found for category &apos;{activeFilter}&apos;.
        </div>
      )}

      {/* Tracked Items Grid */}
      {!loading && filteredItems.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredItems.map((item) => {
            const config = TYPE_CONFIG[item.record_type] || TYPE_CONFIG.promise;
            const IconComponent = config.icon;
            const liveStatus = liveStatuses[`${item.record_type}:${item.record_id}`];
            const hasUpdate = highlightUpdates && liveStatus?.has_update;
            const isValid = liveStatus ? liveStatus.is_valid : true;

            return (
              <div
                key={`${item.record_type}:${item.record_id}`}
                className={`civic-card p-5 flex flex-col justify-between gap-4 group transition-all duration-300 ${
                  !isValid
                    ? 'border-rose-900/40 bg-rose-950/10'
                    : hasUpdate
                    ? 'border-amber-500/40 shadow-lg shadow-amber-500/10'
                    : ''
                }`}
              >
                <div className="space-y-3">
                  {/* Top Category Badge & Actions */}
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${config.badgeBg}`}
                    >
                      <IconComponent className="w-3 h-3" />
                      <span>{config.label}</span>
                    </span>

                    <button
                      onClick={() => removeRecord(item.record_type, item.record_id)}
                      className="p-1.5 rounded-lg text-slate-500 hover:text-rose-400 hover:bg-rose-950/30 transition-colors"
                      title="Untrack / Remove from saved items"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Title & Link */}
                  <div>
                    <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug group-hover:text-cyan-300 transition-colors">
                      {item.title}
                    </h3>
                    <p className="text-[11px] text-slate-400 font-mono mt-1">
                      ID: {item.record_id}
                    </p>
                  </div>

                  {/* Live Status Tag */}
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-slate-400">Status:</span>
                    <span className="px-2 py-0.5 rounded-md bg-slate-800 text-slate-200 border border-white/10 font-medium">
                      {liveStatus?.current_record?.current_status || item.last_known_status}
                    </span>
                  </div>

                  {/* Change Detection Notice */}
                  {hasUpdate && liveStatus?.update_event && (
                    <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs space-y-1">
                      <div className="flex items-center gap-1.5 font-bold">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                        <span>Update Detected ({liveStatus.update_event.change_type.replace(/_/g, ' ')})</span>
                      </div>
                      <p className="text-amber-200/90 text-[11px] leading-relaxed">
                        {liveStatus.update_event.change_description}
                      </p>
                      <p className="text-[10px] text-amber-400/70 font-mono">
                        Source: {liveStatus.update_event.change_source}
                      </p>
                    </div>
                  )}

                  {/* Record Retired / Deleted Notice */}
                  {!isValid && (
                    <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-900/30 text-rose-300 text-xs space-y-1">
                      <div className="flex items-center gap-1.5 font-bold">
                        <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                        <span>Record De-registered or Archived</span>
                      </div>
                      <p className="text-rose-200/80 text-[11px]">
                        This record is no longer active in the public registry. You can safely remove it from your tracked list.
                      </p>
                    </div>
                  )}
                </div>

                {/* Footer Navigation Link */}
                <div className="pt-3 border-t border-white/5 flex items-center justify-between text-xs text-slate-400">
                  <span className="text-[11px] font-mono">
                    Tracked on {new Date(item.saved_at).toLocaleDateString()}
                  </span>

                  <Link
                    href={item.detail_url}
                    className="flex items-center gap-1 text-cyan-400 hover:text-cyan-300 font-semibold transition-colors group-hover:translate-x-0.5"
                  >
                    <span>View Record</span>
                    <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
