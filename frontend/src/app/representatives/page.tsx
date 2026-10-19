'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Users, Search, Award, MessageSquare, Landmark, ArrowRight } from 'lucide-react';
import { Representative } from '../../lib/types';
import { fetchRepresentatives } from '../../lib/api';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';

export default function RepresentativesPage() {
  const [reps, setReps] = useState<Representative[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchRepresentatives();
      setReps(data);
      setLoading(false);
    }
    load();
  }, []);

  const filtered = reps.filter((r) => {
    const q = search.toLowerCase();
    return (
      r.name.toLowerCase().includes(q) ||
      r.constituency.toLowerCase().includes(q) ||
      r.party.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6">
      <PageHeader
        title="Representatives (234 MLAs)"
        description="Find your local Member of Legislative Assembly (MLA) in Tamil Nadu. Review their attendance in the assembly, questions raised for your constituency, and how much local constituency development fund was spent on public works."
        breadcrumbs={[{ label: 'Representatives' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Assembly Scorecard
          </span>
        }
      />

      {/* Search Input */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by MLA name, constituency, or party..."
          className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-9 pr-4 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
        />
      </div>

      {/* Grid of MLA cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((rep) => {
          const isDmk = rep.party === 'DMK';
          const isAiadmk = rep.party === 'AIADMK';
          const partyBadge = isDmk
            ? 'bg-red-500/15 text-red-400 border-red-500/30'
            : isAiadmk
            ? 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30'
            : 'bg-orange-500/15 text-orange-400 border-orange-500/30';

          return (
            <div
              key={rep.id}
              className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all shadow-lg space-y-4"
            >
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-sm text-white">{rep.name}</h3>
                  <p className="text-xs text-slate-400">Constituency: <strong className="text-slate-200">{rep.constituency}</strong></p>
                </div>
                <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${partyBadge}`}>
                  {rep.party}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                  <span className="text-[10px] text-slate-400 block font-semibold uppercase">Attendance</span>
                  <span className="font-bold text-white text-sm">{rep.attendance_percentage}%</span>
                </div>
                <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80">
                  <span className="text-[10px] text-slate-400 block font-semibold uppercase">Questions</span>
                  <span className="font-bold text-blue-400 text-sm">{rep.questions_raised}</span>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800/80 text-xs">
                <div className="flex justify-between items-center mb-1">
                  <span className="text-[10px] text-slate-400 font-semibold uppercase">MLACDS Fund Utilization</span>
                  <span className="font-bold text-emerald-400">
                    ₹{rep.mlacds_utilized}Cr / ₹{rep.mlacds_allocated}Cr
                  </span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className="bg-emerald-500 h-full rounded-full"
                    style={{ width: `${(rep.mlacds_utilized / rep.mlacds_allocated) * 100}%` }}
                  />
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800 flex items-center justify-end">
                <Link
                  href={`/representatives/${rep.id}`}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors"
                >
                  <span>View MLA Scorecard</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
