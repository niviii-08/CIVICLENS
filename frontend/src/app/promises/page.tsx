'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  ScrollText,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  XCircle,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  Layers,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { PoliticalPromise } from '../../lib/types';
import { fetchPromises } from '../../lib/api';
import { StatusBadge } from '../../components/StatusBadge';
import { PageHeader } from '../../components/PageHeader';

export default function PromisesPage() {
  const [promises, setPromises] = useState<PoliticalPromise[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedParty, setSelectedParty] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchPromises();
      setPromises(data);
      setLoading(false);
    }
    load();
  }, []);

  const categories = useMemo(() => {
    const set = new Set<string>();
    promises.forEach((p) => {
      if (p.category) set.add(p.category);
    });
    return Array.from(set).sort();
  }, [promises]);

  const filteredPromises = useMemo(() => {
    return promises.filter((p) => {
      // Party filter
      if (selectedParty !== 'ALL' && p.party.toUpperCase() !== selectedParty.toUpperCase()) {
        return false;
      }
      // Status filter
      if (selectedStatus !== 'ALL') {
        if (selectedStatus === 'Fulfilled' && p.status !== 'Fulfilled') return false;
        if (selectedStatus === 'In-Progress' && p.status !== 'In-Progress') return false;
        if (selectedStatus === 'Broken' && p.status !== 'Broken') return false;
        if (selectedStatus === 'Stalled' && p.status !== 'Stalled') return false;
      }
      // Category filter
      if (selectedCategory !== 'ALL' && p.category !== selectedCategory) {
        return false;
      }
      // Search query
      if (search.trim()) {
        const q = search.toLowerCase();
        const textMatch = p.text?.toLowerCase().includes(q);
        const originalMatch = p.original_text?.toLowerCase().includes(q);
        const idMatch = p.id?.toLowerCase().includes(q);
        const targetMatch = p.target?.toLowerCase().includes(q);
        if (!textMatch && !originalMatch && !idMatch && !targetMatch) return false;
      }
      return true;
    });
  }, [promises, selectedParty, selectedStatus, selectedCategory, search]);

  const stats = useMemo(() => {
    const total = promises.length;
    const fulfilled = promises.filter((p) => p.status === 'Fulfilled').length;
    const inProgress = promises.filter((p) => p.status === 'In-Progress').length;
    const broken = promises.filter((p) => p.status === 'Broken').length;
    const stalled = promises.filter((p) => p.status === 'Stalled').length;
    return { total, fulfilled, inProgress, broken, stalled };
  }, [promises]);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Promises & Progress"
        description="Tracking 1,074 election promises from the 2021 Tamil Nadu Assembly Manifestos (DMK & AIADMK). See which welfare commitments have been delivered, which are in progress, and which remain unfulfilled."
        breadcrumbs={[{ label: 'Promises & Progress' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
            Manifesto Delivery Tracker
          </span>
        }
      />

        {/* Stats Pill Row */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          <div className="px-3 py-1.5 rounded-xl bg-slate-900 border border-slate-800 text-xs">
            <span className="text-slate-400">Total: </span>
            <span className="font-bold text-white">{stats.total}</span>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
            <span className="opacity-80">Fulfilled: </span>
            <span className="font-bold">{stats.fulfilled}</span>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-400">
            <span className="opacity-80">In-Progress: </span>
            <span className="font-bold">{stats.inProgress}</span>
          </div>
          <div className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-400">
            <span className="opacity-80">Stalled: </span>
            <span className="font-bold">{stats.stalled}</span>
          </div>
        </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* Search box */}
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search promise text in English or தமிழ் (e.g. குடும்பத் தலைவிகளுக்கு, மகளிர், breakfast)..."
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-400 hover:text-white"
              >
                Clear
              </button>
            )}
          </div>

          {/* Party Pills */}
          <div className="flex items-center gap-1.5 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
            {['ALL', 'DMK', 'AIADMK'].map((party) => (
              <button
                key={party}
                onClick={() => setSelectedParty(party)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  selectedParty === party
                    ? party === 'DMK'
                      ? 'bg-red-600 text-white shadow-md shadow-red-600/30'
                      : party === 'AIADMK'
                      ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/30'
                      : 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
                }`}
              >
                {party}
              </button>
            ))}
          </div>
        </div>

        {/* Secondary Filter Row: Status & Categories */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
          <div className="flex items-center gap-1 text-xs text-slate-400 mr-1">
            <Filter className="w-3.5 h-3.5" />
            <span>Filter by:</span>
          </div>

          {/* Status selector */}
          {['ALL', 'Fulfilled', 'In-Progress', 'Stalled', 'Broken'].map((status) => (
            <button
              key={status}
              onClick={() => setSelectedStatus(status)}
              className={`px-2.5 py-1 rounded-lg text-[11px] font-semibold transition-colors ${
                selectedStatus === status
                  ? 'bg-slate-700 text-white border border-slate-600'
                  : 'bg-slate-950/70 border border-slate-800/80 text-slate-400 hover:text-slate-200'
              }`}
            >
              {status}
            </button>
          ))}

          {/* Category Dropdown */}
          <div className="ml-auto">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1 text-xs text-slate-300 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="ALL">All Sectors ({categories.length})</option>
              {categories.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Promises List */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading official manifesto commitments...</span>
        </div>
      ) : filteredPromises.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-slate-900/40 rounded-2xl border border-slate-800">
          No promises match your search criteria. Try clearing filters.
        </div>
      ) : (
        <div className="space-y-3">
          <div className="text-xs text-slate-400 px-1">
            Showing <span className="font-semibold text-white">{filteredPromises.length}</span> commitments
          </div>

          {filteredPromises.map((p) => {
            const isExpanded = expandedId === p.id;
            const isDmk = p.party.toUpperCase() === 'DMK';

            return (
              <div
                key={p.id}
                className="rounded-2xl bg-slate-900/70 border border-slate-800/90 hover:border-slate-700 transition-all overflow-hidden"
              >
                <div
                  onClick={() => setExpandedId(isExpanded ? null : p.id)}
                  className="p-5 cursor-pointer flex flex-col md:flex-row md:items-start justify-between gap-4 select-none"
                >
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`text-[10px] font-extrabold px-2 py-0.5 rounded tracking-wide ${
                          isDmk ? 'bg-red-500/15 text-red-400 border border-red-500/30' : 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/30'
                        }`}
                      >
                        {p.party} {p.year || 2021}
                      </span>
                      <span className="text-[10px] font-mono text-slate-500">#{p.id}</span>
                      <StatusBadge status={p.status} />
                      <span className="text-[11px] text-slate-400 ml-auto md:ml-0 px-2 py-0.5 rounded bg-slate-800/60">
                        {p.category}
                      </span>
                    </div>

                    {/* Tamil Text (if available) */}
                    {p.original_text && (
                      <p className="text-xs font-medium text-amber-200/90 leading-relaxed font-sans">
                        {p.original_text}
                      </p>
                    )}

                    {/* English Text */}
                    <p className="text-xs md:text-sm text-slate-200 leading-relaxed font-medium">
                      {p.text}
                    </p>

                    {p.target && (
                      <div className="flex items-center gap-1.5 text-[11px] text-slate-400">
                        <span className="text-slate-400 font-semibold">Target Beneficiary:</span>
                        <span className="text-blue-400">{p.target}</span>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center md:flex-col justify-between md:items-end gap-2 shrink-0">
                    <span className="text-[11px] text-slate-400 flex items-center gap-1">
                      {isExpanded ? 'Hide Details' : 'View Linkage'}
                      <ChevronDown
                        className={`w-3.5 h-3.5 transition-transform duration-200 ${
                          isExpanded ? 'rotate-180' : ''
                        }`}
                      />
                    </span>
                  </div>
                </div>

                {/* Expanded Details Panel */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-3 border-t border-slate-800/80 bg-slate-950/70 space-y-3 animate-fadeIn">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Budget Line Item</span>
                        <span className="text-slate-200 font-medium">
                          {p.budget_allocation ? `₹${p.budget_allocation} Cr` : 'Appropriation Demand Assigned'}
                        </span>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Verification Ledger</span>
                        <span className="text-emerald-400 font-medium">Verified against TN Gazette Records</span>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-xs">
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Evidence Graph ID</span>
                        <span className="font-mono text-blue-400">EVD-PROMISE-{p.id}</span>
                      </div>
                    </div>
                    <div className="pt-2 flex items-center justify-end">
                      <Link
                        href={`/promises/${p.id}`}
                        className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-600/20 text-blue-300 border border-blue-500/30 hover:bg-blue-600/30 transition-all"
                      >
                        <span>Open Citizen Record</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
