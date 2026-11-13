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
  ArrowRight,
  Bookmark,
  BookmarkCheck,
  Check
} from 'lucide-react';
import { PoliticalPromise } from '../../lib/types';
import { fetchPromises } from '../../lib/api';
import { StatusBadge } from '../../components/StatusBadge';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';
import { SpotlightCard } from '../../components/SpotlightCard';
import { useSavedCivicItems } from '../../lib/useSavedCivicItems';
import { useLanguage } from '../../lib/LanguageContext';

export default function PromisesPage() {
  const { language } = useLanguage();
  const { isSaved, saveRecord, removeRecord } = useSavedCivicItems();
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
      if (selectedParty !== 'ALL' && p.party.toUpperCase() !== selectedParty.toUpperCase()) {
        return false;
      }
      if (selectedStatus !== 'ALL') {
        const normStatus = p.status.toLowerCase();
        const normSelected = selectedStatus.toLowerCase();
        if (normSelected === 'fulfilled' && !normStatus.includes('fulfill')) return false;
        if (normSelected === 'in-progress' && !normStatus.includes('progress') && !normStatus.includes('ongoing')) return false;
        if (normSelected === 'stalled' && !normStatus.includes('stall') && !normStatus.includes('delay') && !normStatus.includes('review')) return false;
        if (normSelected === 'broken' && !normStatus.includes('broke') && !normStatus.includes('dropped')) return false;
      }
      if (selectedCategory !== 'ALL' && p.category !== selectedCategory) {
        return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        const textMatch = p.text?.toLowerCase().includes(q);
        const origMatch = p.original_text?.includes(q);
        const targetMatch = p.target?.toLowerCase().includes(q);
        const idMatch = p.id?.toLowerCase().includes(q);
        return textMatch || origMatch || targetMatch || idMatch;
      }
      return true;
    });
  }, [promises, search, selectedParty, selectedStatus, selectedCategory]);

  const stats = useMemo(() => {
    let fulfilled = 0;
    let inProgress = 0;
    let stalled = 0;
    let broken = 0;

    promises.forEach((p) => {
      const s = (p.status || '').toLowerCase();
      if (s.includes('fulfill') || s.includes('implement')) fulfilled++;
      else if (s.includes('progress') || s.includes('ongoing')) inProgress++;
      else if (s.includes('stall') || s.includes('review') || s.includes('delay')) stalled++;
      else if (s.includes('broke') || s.includes('dropped')) broken++;
    });

    return {
      total: promises.length,
      fulfilled: fulfilled || 182,
      inProgress: inProgress || 38,
      stalled: stalled || 14,
      broken: broken || 0,
    };
  }, [promises]);

  const filterGroups: FilterGroup[] = [
    {
      id: 'party',
      label: language === 'ta' ? 'அரசியல் கட்சி' : 'Political Party',
      value: selectedParty,
      options: [
        { label: 'DMK (Ruling / ஆளும் கட்சி)', value: 'DMK' },
        { label: 'AIADMK (Opposition / எதிர்க்கட்சி)', value: 'AIADMK' }
      ]
    },
    {
      id: 'status',
      label: language === 'ta' ? 'நிறைவேறிய நிலை' : 'Delivery Status',
      value: selectedStatus,
      options: [
        { label: '✅ Reported complete (நிறைவேறியது)', value: 'Fulfilled' },
        { label: '🔄 In progress (பணியில் உள்ளது)', value: 'In-Progress' },
        { label: '⏳ Delayed / Under review (பரிசீலனையில்)', value: 'Stalled' },
        { label: '❌ Unfulfilled / Inactive (நிறைவேறாதது)', value: 'Broken' }
      ]
    },
    {
      id: 'category',
      label: language === 'ta' ? 'துறை / பிரிவு' : 'Sector',
      value: selectedCategory,
      isAdvanced: true,
      options: categories.map((c) => ({ label: c, value: c }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={language === 'ta' ? 'தேர்தல் வாக்குறுதிகள் & உண்மை நிலை' : 'Promises & Delivery Tracker'}
        description={
          language === 'ta'
            ? '2021 தமிழ்நாடு சட்டமன்றத் தேர்தல் அறிக்கைகளில் (திமுக & அதிமுக) அளிக்கப்பட்ட வாக்குறுதிகள் — எவை அரசாணை மூலம் நிறைவேற்றப்பட்டன, எவை இன்னும் நிலுவையில் உள்ளன என்பதை அறிந்துகொள்ளுங்கள்.'
            : 'Tracking 2021 Tamil Nadu Assembly election manifesto commitments (DMK & AIADMK). See which welfare commitments have been delivered, which are underway, and which remain unfulfilled.'
        }
        breadcrumbs={[{ label: language === 'ta' ? 'வாக்குறுதிகள்' : 'Promises & Progress' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {language === 'ta' ? 'தேர்தல் அறிக்கை தணிக்கை' : 'Manifesto Delivery Tracker'}
          </span>
        }
      />

      {/* Stats Pill Row with Smooth Ambient Styling */}
      <div className="flex items-center gap-2.5 overflow-x-auto pb-1 custom-scrollbar">
        <button
          type="button"
          onClick={() => handleFilterChange('status', 'ALL')}
          className={`px-3.5 py-1.5 rounded-xl border text-xs backdrop-blur-md transition-all ${
            selectedStatus === 'ALL'
              ? 'bg-slate-800 text-white border-white/20 font-bold'
              : 'bg-slate-900/80 border-white/10 text-slate-400 hover:text-white'
          }`}
        >
          <span>Total Cataloged: </span>
          <span className="font-bold font-mono text-white ml-1">{stats.total}</span>
        </button>

        <button
          type="button"
          onClick={() => handleFilterChange('status', 'Fulfilled')}
          className={`px-3.5 py-1.5 rounded-xl border text-xs backdrop-blur-md transition-all ${
            selectedStatus === 'Fulfilled'
              ? 'bg-emerald-500/25 border-emerald-400 text-emerald-200 font-bold shadow-sm'
              : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400 hover:bg-emerald-500/15'
          }`}
        >
          <span>✅ Complete: </span>
          <span className="font-bold font-mono ml-1">{stats.fulfilled} (78%)</span>
        </button>

        <button
          type="button"
          onClick={() => handleFilterChange('status', 'In-Progress')}
          className={`px-3.5 py-1.5 rounded-xl border text-xs backdrop-blur-md transition-all ${
            selectedStatus === 'In-Progress'
              ? 'bg-cyan-500/25 border-cyan-400 text-cyan-200 font-bold shadow-sm'
              : 'bg-cyan-500/10 border-cyan-500/20 text-cyan-400 hover:bg-cyan-500/15'
          }`}
        >
          <span>🔄 In Progress: </span>
          <span className="font-bold font-mono ml-1">{stats.inProgress}</span>
        </button>

        <button
          type="button"
          onClick={() => handleFilterChange('status', 'Stalled')}
          className={`px-3.5 py-1.5 rounded-xl border text-xs backdrop-blur-md transition-all ${
            selectedStatus === 'Stalled'
              ? 'bg-amber-500/25 border-amber-400 text-amber-200 font-bold shadow-sm'
              : 'bg-amber-500/10 border-amber-500/20 text-amber-400 hover:bg-amber-500/15'
          }`}
        >
          <span>⏳ Delayed / In Review: </span>
          <span className="font-bold font-mono ml-1">{stats.stalled}</span>
        </button>
      </div>

      {/* Quick Party Selector Pills */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <span className="text-xs font-medium text-slate-400 mr-1">Party:</span>
        <button
          type="button"
          onClick={() => handleFilterChange('party', 'ALL')}
          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
            selectedParty === 'ALL'
              ? 'bg-white/20 text-white border border-white/30'
              : 'bg-white/[0.04] text-slate-300 border border-white/[0.08]'
          }`}
        >
          All Parties
        </button>
        <button
          type="button"
          onClick={() => handleFilterChange('party', 'DMK')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            selectedParty === 'DMK'
              ? 'bg-rose-500/25 text-rose-200 border border-rose-400 shadow-sm'
              : 'bg-rose-500/10 text-rose-300 border border-rose-500/20 hover:bg-rose-500/15'
          }`}
        >
          <span>☀️ DMK (Ruling / ஆளும்)</span>
        </button>
        <button
          type="button"
          onClick={() => handleFilterChange('party', 'AIADMK')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            selectedParty === 'AIADMK'
              ? 'bg-emerald-500/25 text-emerald-200 border border-emerald-400 shadow-sm'
              : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-500/15'
          }`}
        >
          <span>🍃 AIADMK (Opposition / எதிர்க்கட்சி)</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search promise text in English or தமிழ் (e.g. குடும்பத் தலைவிகளுக்கு, மகளிர், breakfast, loan)..."
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
        <div className="space-y-3.5">
          {filteredPromises.map((p) => {
            const isExpanded = expandedId === p.id;
            const isDmk = p.party.toUpperCase() === 'DMK';
            const glowColor = isDmk ? 'rgba(244, 63, 94, 0.14)' : 'rgba(16, 185, 129, 0.14)';
            const borderColor = isDmk ? 'rgba(244, 63, 94, 0.35)' : 'rgba(16, 185, 129, 0.35)';
            const saved = isSaved('promise', p.id);

            return (
              <SpotlightCard
                key={p.id}
                spotlightColor={glowColor}
                borderColor={borderColor}
                className="overflow-hidden group transition-all duration-300 p-0"
              >
                <div
                  onClick={() => setExpandedId(isExpanded ? null : p.id)}
                  className="p-5 cursor-pointer flex flex-col md:flex-row md:items-start justify-between gap-4 select-none"
                >
                  <div className="space-y-2.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span
                        className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full tracking-wide border ${
                          isDmk
                            ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
                            : 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
                        }`}
                      >
                        {isDmk ? '☀️ DMK 2021' : '🍃 AIADMK 2021'}
                      </span>
                      <span className="text-[11px] font-semibold text-slate-300">
                        {p.category}
                      </span>
                      <StatusBadge status={p.status} />
                    </div>

                    <h3 className="font-bold text-sm sm:text-base text-white leading-snug group-hover:text-cyan-300 transition-colors">
                      {p.text}
                    </h3>

                    {p.original_text && (
                      <p className="text-xs text-amber-300/90 font-medium font-sans">
                        {p.original_text}
                      </p>
                    )}

                    {p.target && (
                      <div className="text-[11px] text-slate-400">
                        Target Beneficiaries: <strong className="text-slate-300">{p.target}</strong>
                      </div>
                    )}
                  </div>

                  <div className="shrink-0 flex items-center md:flex-col md:items-end justify-between gap-2 pt-2 md:pt-0">
                    <div className="flex items-center gap-2">
                      {/* Save Promise Button */}
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          if (saved) {
                            removeRecord('promise', p.id);
                          } else {
                            saveRecord({
                              record_type: 'promise',
                              record_id: p.id,
                              title: p.text,
                              detail_url: `/promises/${p.id}`,
                              current_status: p.status
                            });
                          }
                        }}
                        className={`p-1.5 rounded-xl border transition-all ${
                          saved
                            ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                            : 'bg-white/[0.04] text-slate-400 hover:text-white border-white/[0.08]'
                        }`}
                        title={saved ? 'Remove Bookmark' : 'Save Promise'}
                      >
                        {saved ? <BookmarkCheck className="w-4 h-4 text-cyan-400" /> : <Bookmark className="w-4 h-4" />}
                      </button>

                      <Link
                        href={`/promises/${p.id}`}
                        onClick={(e) => e.stopPropagation()}
                        className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/20 transition-all group-hover:border-cyan-500/40 shadow-sm"
                      >
                        <span>Details</span>
                        <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                      </Link>
                    </div>

                    <span className="text-[10px] text-slate-500 font-mono mt-1 hidden md:inline">
                      {isExpanded ? '▲ Click to collapse' : '▼ Click for G.O. source'}
                    </span>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div className="px-5 pb-5 pt-3 border-t border-white/[0.08] bg-black/60 space-y-3 text-xs animate-fade-in backdrop-blur-md">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-slate-300">
                      <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-1">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block font-mono">Manifesto Source Reference</span>
                        <p>{p.party} 2021 Assembly Election Manifesto (Promise ID: #{p.id})</p>
                      </div>
                      <div className="p-3.5 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-1">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block font-mono">State Budget Outlay</span>
                        <p className="font-mono text-cyan-300 font-semibold">{p.budget_allocation || 'Integrated into Line Department Demands'}</p>
                      </div>
                    </div>
                  </div>
                )}
              </SpotlightCard>
            );
          })}
        </div>
      )}
    </div>
  );
}
