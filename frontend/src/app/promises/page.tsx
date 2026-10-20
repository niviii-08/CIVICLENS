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
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';

export default function PromisesPage() {
  const [promises, setPromises] = useState<PoliticalPromise[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedParty, setSelectedParty] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');
  const [selectedCategory, setSelectedCategory] = useState('ALL');
  const [expandedId, setExpandedId] = useState<string | null>(null);

  // Load URL state on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const party = sp.get('party');
      const st = sp.get('status');
      const cat = sp.get('category');
      if (q) setSearch(q);
      if (party) setSelectedParty(party);
      if (st) setSelectedStatus(st);
      if (cat) setSelectedCategory(cat);
    }
  }, []);

  const updateUrl = (q: string, party: string, st: string, cat: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (party && party !== 'ALL') url.searchParams.set('party', party); else url.searchParams.delete('party');
    if (st && st !== 'ALL') url.searchParams.set('status', st); else url.searchParams.delete('status');
    if (cat && cat !== 'ALL') url.searchParams.set('category', cat); else url.searchParams.delete('category');
    window.history.replaceState({}, '', url.toString());
  };

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

  const handleSearchChange = (q: string) => {
    setSearch(q);
    updateUrl(q, selectedParty, selectedStatus, selectedCategory);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let p = selectedParty;
    let s = selectedStatus;
    let c = selectedCategory;

    if (groupId === 'party') {
      p = val;
      setSelectedParty(val);
    } else if (groupId === 'status') {
      s = val;
      setSelectedStatus(val);
    } else if (groupId === 'category') {
      c = val;
      setSelectedCategory(val);
    }

    updateUrl(search, p, s, c);
  };

  const handleClearAll = () => {
    setSearch('');
    setSelectedParty('ALL');
    setSelectedStatus('ALL');
    setSelectedCategory('ALL');
    updateUrl('', 'ALL', 'ALL', 'ALL');
  };

  const filteredPromises = useMemo(() => {
    return promises.filter((p) => {
      // Party filter
      if (selectedParty !== 'ALL' && p.party.toUpperCase() !== selectedParty.toUpperCase()) {
        return false;
      }
      // Status filter
      if (selectedStatus !== 'ALL') {
        const s = (p.status || '').toLowerCase();
        if (selectedStatus === 'Fulfilled' && !s.includes('fulfill')) return false;
        if (selectedStatus === 'In-Progress' && !s.includes('progress') && !s.includes('ongoing')) return false;
        if (selectedStatus === 'Stalled' && !s.includes('stall') && !s.includes('delay')) return false;
        if (selectedStatus === 'Broken' && !s.includes('broke') && !s.includes('dropped')) return false;
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
    const fulfilled = promises.filter((p) => (p.status || '').toLowerCase().includes('fulfill')).length;
    const inProgress = promises.filter((p) => (p.status || '').toLowerCase().includes('progress')).length;
    const stalled = promises.filter((p) => (p.status || '').toLowerCase().includes('stall')).length;
    return { total, fulfilled, inProgress, stalled };
  }, [promises]);

  const filterGroups: FilterGroup[] = [
    {
      id: 'party',
      label: 'Political Party',
      value: selectedParty,
      options: [
        { label: 'DMK (Ruling)', value: 'DMK' },
        { label: 'AIADMK (Opposition)', value: 'AIADMK' }
      ]
    },
    {
      id: 'status',
      label: 'Delivery Status',
      value: selectedStatus,
      options: [
        { label: 'Reported complete', value: 'Fulfilled' },
        { label: 'In progress', value: 'In-Progress' },
        { label: 'Delayed / Under review', value: 'Stalled' },
        { label: 'Unfulfilled / Inactive', value: 'Broken' }
      ]
    },
    {
      id: 'category',
      label: 'Sector',
      value: selectedCategory,
      isAdvanced: true,
      options: categories.map((c) => ({ label: c, value: c }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Promises & Progress"
        description="Tracking election manifesto commitments from the 2021 Tamil Nadu Assembly Manifestos (DMK & AIADMK). See which welfare commitments have been delivered, which are in progress, and which remain unfulfilled."
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
          <span className="text-slate-400">Total Cataloged: </span>
          <span className="font-bold text-white">{stats.total}</span>
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400">
          <span className="opacity-80">Reported Complete: </span>
          <span className="font-bold">{stats.fulfilled}</span>
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-xs text-blue-400">
          <span className="opacity-80">In Progress: </span>
          <span className="font-bold">{stats.inProgress}</span>
        </div>
        <div className="px-3 py-1.5 rounded-xl bg-amber-500/10 border border-amber-500/20 text-xs text-amber-400">
          <span className="opacity-80">Delayed / In Review: </span>
          <span className="font-bold">{stats.stalled}</span>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search promise text in English or தமிழ் (e.g. குடும்பத் தலைவிகளுக்கு, மகளிர், breakfast)..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={promises.length}
        filteredResults={filteredPromises.length}
        resultNoun="manifesto commitments"
      />

      {/* Promises List */}
      {loading ? (
        <CivicStateNotice
          state="loading"
          title="Loading Manifesto Commitments..."
          description="Retrieving audited political promises and delivery records across Tamil Nadu assembly manifestos."
        />
      ) : filteredPromises.length === 0 ? (
        <CivicStateNotice
          state="no_matching_results"
          title="No Matching Manifesto Promises"
          description="No election promises matched the selected party, status, or sector filters. Use 'Reset all filters' to browse all commitments."
          onClearFilters={handleClearAll}
        />
      ) : (
        <div className="space-y-3">
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
                          isDmk ? 'bg-red-500/20 text-red-300' : 'bg-emerald-500/20 text-emerald-300'
                        }`}
                      >
                        {p.party}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-400">
                        {p.category}
                      </span>
                      <StatusBadge status={p.status} />
                    </div>

                    <h3 className="font-bold text-sm sm:text-base text-white leading-snug">
                      {p.text}
                    </h3>

                    {p.original_text && (
                      <p className="text-xs text-amber-200/90 font-medium font-sans">
                        {p.original_text}
                      </p>
                    )}

                    {p.target && (
                      <div className="text-[11px] text-slate-400">
                        Target Beneficiaries: <strong className="text-slate-300">{p.target}</strong>
                      </div>
                    )}
                  </div>

                  <div className="shrink-0 flex md:flex-col items-center md:items-end justify-between gap-2 pt-2 md:pt-0">
                    <Link
                      href={`/promises/${p.id}`}
                      onClick={(e) => e.stopPropagation()}
                      className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 transition-colors"
                    >
                      <span>View Record</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-2 border-t border-slate-800/80 bg-slate-950/40 space-y-3 text-xs">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-300">
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block">Manifesto Source</span>
                        <p>{p.party} 2021 Assembly Election Manifesto (Ref: #{p.id})</p>
                      </div>
                      <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-1">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block">Budget Line Allocation</span>
                        <p className="font-mono">{p.budget_allocation || 'Integrated into Line Department Demands'}</p>
                      </div>
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
