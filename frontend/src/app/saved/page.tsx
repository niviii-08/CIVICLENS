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
} from 'lucide-react';
import { useSavedCivicItems, SavedCivicRecord } from '@/lib/useSavedCivicItems';

const TYPE_CONFIG = {
  promise: {
    label: 'Manifesto Promise',
    icon: ScrollText,
    badgeBg: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  },
  scheme: {
    label: 'Government Scheme',
    icon: Landmark,
    badgeBg: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  },
  representative: {
    label: 'Elected Representative',
    icon: Users,
    badgeBg: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
  },
  claim: {
    label: 'Claim Assessment',
    icon: ShieldCheck,
    badgeBg: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  },
  civic: {
    label: 'Civic Grievance',
    icon: AlertTriangle,
    badgeBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
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
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 md:p-10 space-y-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center gap-2.5 mb-2">
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
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
        <div className="flex items-center gap-3">
          <button
            onClick={toggleHighlightUpdates}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              highlightUpdates
                ? 'bg-indigo-600/20 text-indigo-300 border-indigo-500/40 hover:bg-indigo-600/30'
                : 'bg-slate-900 text-slate-400 border-slate-800 hover:bg-slate-800'
            }`}
            title="Toggle update highlighting"
          >
            {highlightUpdates ? <Bell className="w-3.5 h-3.5" /> : <BellOff className="w-3.5 h-3.5" />}
            <span>{highlightUpdates ? 'Update Alerts Active' : 'Alerts Muted'}</span>
          </button>

          <button
            onClick={handleRefresh}
            disabled={isRefreshing || savedItems.length === 0}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-200 transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-indigo-400' : ''}`} />
            <span>Check Updates</span>
          </button>

          {savedItems.length > 0 && (
            <button
              onClick={() => {
                if (window.confirm('Are you sure you want to remove all saved civic records?')) {
                  clearAll();
                }
              }}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-red-950/20 border border-red-900/30 text-red-400 hover:bg-red-950/40 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear All</span>
            </button>
          )}
        </div>
      </div>

      {/* Privacy Notice Banner */}
      <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800/80 flex items-start gap-3">
        <Shield className="w-5 h-5 text-indigo-400 mt-0.5 shrink-0" />
        <div className="text-xs text-slate-300 space-y-1">
          <p className="font-semibold text-slate-200">
            Local-First & Privacy-Preserving Citizen Tracking
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
        <div className="flex items-center gap-1.5 p-1 bg-slate-900 border border-slate-800/80 rounded-lg text-xs">
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
              className={`px-3 py-1.5 rounded-md font-medium transition-colors ${
                activeFilter === tab.id
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {updatesCount > 0 && highlightUpdates && (
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
            <span>{updatesCount} Tracked {updatesCount === 1 ? 'Item Has' : 'Items Have'} Recent Changes</span>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="p-12 text-center text-slate-500 text-sm">
          Loading your tracked civic records...
        </div>
      )}

      {/* Empty State */}
      {!loading && savedItems.length === 0 && (
        <div className="p-12 rounded-2xl bg-slate-900/40 border border-slate-800/80 text-center max-w-xl mx-auto space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 flex items-center justify-center mx-auto">
            <BookmarkCheck className="w-6 h-6" />
          </div>
          <div className="space-y-1">
            <h3 className="text-base font-bold text-white">No Tracked Civic Records Yet</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Track election manifesto promises, welfare schemes, elected representatives, fact-checked claims,
              or municipal grievances to receive in-app change alerts when new government ledgers are published.
            </p>
          </div>
          <div className="pt-2 flex flex-wrap items-center justify-center gap-2">
            <Link
              href="/promises"
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              Browse Promises
            </Link>
            <Link
              href="/schemes"
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              Browse Schemes
            </Link>
            <Link
              href="/representatives"
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              Browse MLAs
            </Link>
            <Link
              href="/claims"
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              Browse Claims
            </Link>
            <Link
              href="/civic"
              className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
            >
              Browse Grievances
            </Link>
          </div>
        </div>
      )}

      {/* Filtered Empty State */}
      {!loading && savedItems.length > 0 && filteredItems.length === 0 && (
        <div className="p-8 text-center text-slate-500 text-xs bg-slate-900/30 rounded-xl border border-slate-800/60">
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
                className={`p-5 rounded-xl border transition-all flex flex-col justify-between gap-4 ${
                  !isValid
                    ? 'bg-red-950/10 border-red-900/30'
                    : hasUpdate
                    ? 'bg-slate-900/90 border-amber-500/40 shadow-lg shadow-amber-500/5'
                    : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="space-y-3">
                  {/* Top Category Badge & Actions */}
                  <div className="flex items-center justify-between gap-2">
                    <span
                      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-[11px] font-semibold border ${config.badgeBg}`}
                    >
                      <IconComponent className="w-3 h-3" />
                      <span>{config.label}</span>
                    </span>

                    <button
                      onClick={() => removeRecord(item.record_type, item.record_id)}
                      className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-950/30 transition-colors"
                      title="Untrack / Remove from saved items"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>

                  {/* Title & Link */}
                  <div>
                    <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug">
                      {item.title}
                    </h3>
                    <p className="text-[11px] text-slate-400 font-mono mt-1">
                      ID: {item.record_id}
                    </p>
                  </div>

                  {/* Live Status Tag */}
                  <div className="flex items-center gap-2 text-xs">
                    <span className="text-slate-400">Status:</span>
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-200 border border-slate-700 font-medium">
                      {liveStatus?.current_record?.current_status || item.last_known_status}
                    </span>
                  </div>

                  {/* Change Detection Notice */}
                  {hasUpdate && liveStatus?.update_event && (
                    <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs space-y-1">
                      <div className="flex items-center gap-1.5 font-bold">
                        <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
                        <span>Update Detected ({liveStatus.update_event.change_type.replace(/_/g, ' ')})</span>
                      </div>
                      <p className="text-amber-200/90 text-[11px] leading-relaxed">
                        {liveStatus.update_event.change_description}
                      </p>
                      <p className="text-[10px] text-amber-400/70">
                        Source: {liveStatus.update_event.change_source}
                      </p>
                    </div>
                  )}

                  {/* Record Retired / Deleted Notice */}
                  {!isValid && (
                    <div className="p-3 rounded-lg bg-red-950/20 border border-red-900/30 text-red-300 text-xs space-y-1">
                      <div className="flex items-center gap-1.5 font-bold">
                        <AlertCircle className="w-3.5 h-3.5 text-red-400" />
                        <span>Record De-registered or Archived</span>
                      </div>
                      <p className="text-red-200/80 text-[11px]">
                        This record is no longer active in the public registry. You can safely remove it from your tracked list.
                      </p>
                    </div>
                  )}
                </div>

                {/* Footer Navigation Link */}
                <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
                  <span className="text-[11px]">
                    Tracked on {new Date(item.saved_at).toLocaleDateString()}
                  </span>

                  <Link
                    href={item.detail_url}
                    className="flex items-center gap-1 text-indigo-400 hover:text-indigo-300 font-medium transition-colors"
                  >
                    <span>View Record</span>
                    <ExternalLink className="w-3 h-3" />
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
