'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import { Users, Search, Award, MessageSquare, Landmark, ArrowRight, ShieldCheck } from 'lucide-react';
import { Representative } from '../../lib/types';
import { fetchRepresentatives } from '../../lib/api';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';

export default function RepresentativesPage() {
  const [reps, setReps] = useState<Representative[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedParty, setSelectedParty] = useState('ALL');
  const [selectedAttendance, setSelectedAttendance] = useState('ALL');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const party = sp.get('party');
      const att = sp.get('attendance');
      if (q) setSearch(q);
      if (party) setSelectedParty(party);
      if (att) setSelectedAttendance(att);
    }
  }, []);

  const updateUrl = (q: string, party: string, att: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (party && party !== 'ALL') url.searchParams.set('party', party); else url.searchParams.delete('party');
    if (att && att !== 'ALL') url.searchParams.set('attendance', att); else url.searchParams.delete('attendance');
    window.history.replaceState({}, '', url.toString());
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchRepresentatives();
      setReps(data);
      setLoading(false);
    }
    load();
  }, []);

  const parties = useMemo(() => {
    const set = new Set<string>();
    reps.forEach((r) => {
      if (r.party) set.add(r.party);
    });
    return Array.from(set).sort();
  }, [reps]);

  const handleSearchChange = (q: string) => {
    setSearch(q);
    updateUrl(q, selectedParty, selectedAttendance);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let p = selectedParty;
    let a = selectedAttendance;

    if (groupId === 'party') {
      p = val;
      setSelectedParty(val);
    } else if (groupId === 'attendance') {
      a = val;
      setSelectedAttendance(val);
    }

    updateUrl(search, p, a);
  };

  const handleClearAll = () => {
    setSearch('');
    setSelectedParty('ALL');
    setSelectedAttendance('ALL');
    updateUrl('', 'ALL', 'ALL');
  };

  const filtered = useMemo(() => {
    return reps.filter((r) => {
      if (selectedParty !== 'ALL' && r.party !== selectedParty) return false;
      if (selectedAttendance !== 'ALL') {
        const att = r.attendance_percentage || 0;
        if (selectedAttendance === 'HIGH' && att < 80) return false;
        if (selectedAttendance === 'MODERATE' && (att < 60 || att >= 80)) return false;
        if (selectedAttendance === 'LOW' && att >= 60) return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          r.name.toLowerCase().includes(q) ||
          r.constituency.toLowerCase().includes(q) ||
          r.party.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [reps, selectedParty, selectedAttendance, search]);

  const filterGroups: FilterGroup[] = [
    {
      id: 'party',
      label: 'Political Party',
      value: selectedParty,
      options: parties.map((p) => ({ label: p, value: p }))
    },
    {
      id: 'attendance',
      label: 'Assembly Attendance',
      value: selectedAttendance,
      options: [
        { label: 'High (≥80%)', value: 'HIGH' },
        { label: 'Moderate (60–79%)', value: 'MODERATE' },
        { label: 'Below 60%', value: 'LOW' }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Representatives (234 MLAs)"
        description="Find your local Member of Legislative Assembly (MLA) in Tamil Nadu. Review assembly attendance, constituency questions raised, and local MLA Constituency Development Scheme (MLACDS) fund execution."
        breadcrumbs={[{ label: 'Representatives' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Assembly Scorecard
          </span>
        }
      />

      {/* Simplified Filter Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search by MLA name, constituency, or party..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={reps.length}
        filteredResults={filtered.length}
        resultNoun="representatives"
      />

      {/* Grid of MLA cards */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading representative records...</span>
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-slate-900/40 rounded-2xl border border-slate-800 space-y-2">
          <p className="font-semibold text-slate-300">No representatives match your filter criteria.</p>
          <button
            type="button"
            onClick={handleClearAll}
            className="text-blue-400 hover:text-blue-300 font-semibold underline"
          >
            Reset all filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((rep) => {
            const isDmk = rep.party === 'DMK';
            const isAiadmk = rep.party === 'AIADMK';
            const partyBadge = isDmk
              ? 'bg-red-500/15 text-red-400 border-red-500/30'
              : isAiadmk
              ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
              : 'bg-orange-500/15 text-orange-400 border-orange-500/30';

            const mlacdsAllocated = rep.mlacds_allocated || 3.0; // Statutory ₹3 Cr per year
            const mlacdsSpent = rep.mlacds_utilized ?? 2.4;
            const utilizationPct = ((mlacdsSpent / mlacdsAllocated) * 100).toFixed(0);

            return (
              <div
                key={rep.id}
                className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all shadow-lg space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-bold text-base text-white">{rep.name}</h3>
                      <p className="text-xs text-slate-400">
                        Constituency: <strong className="text-slate-200">{rep.constituency}</strong>
                      </p>
                    </div>
                    <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${partyBadge}`}>
                      {rep.party}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">Assembly Attendance</span>
                      <span className="font-bold text-white text-sm font-mono">{rep.attendance_percentage}%</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">Questions Raised</span>
                      <span className="font-bold text-blue-400 text-sm font-mono">{rep.questions_raised}</span>
                    </div>
                  </div>

                  {/* MLACDS Spending */}
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs space-y-1.5">
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-slate-400 font-semibold uppercase text-[10px]">MLACDS Fund Utilization:</span>
                      <span className="font-bold text-emerald-400 font-mono">
                        ₹{mlacdsSpent.toFixed(2)} Cr / ₹{mlacdsAllocated.toFixed(1)} Cr ({utilizationPct}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full transition-all"
                        style={{ width: `${Math.min(Number(utilizationPct), 100)}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-between border-t border-slate-800/80 text-xs">
                  <span className="text-[10px] text-slate-500 italic">
                    Assembly Term 2021–2026
                  </span>

                  <Link
                    href={`/representatives/${rep.id}`}
                    className="inline-flex items-center gap-1 font-semibold text-xs text-blue-400 hover:text-blue-300"
                  >
                    <span>View Scorecard</span>
                    <ArrowRight className="w-3.5 h-3.5" />
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
