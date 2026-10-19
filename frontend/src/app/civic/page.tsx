'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { AlertTriangle, Clock, CheckCircle2, ShieldAlert, Building2 } from 'lucide-react';
import { CivicGrievance } from '../../lib/types';
import { fetchCivicGrievances } from '../../lib/api';
import { StatusBadge } from '../../components/StatusBadge';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';

export default function CivicPage() {
  const [grievances, setGrievances] = useState<CivicGrievance[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchCivicGrievances();
      setGrievances(data);
      setLoading(false);
    }
    load();
  }, []);

  const total = grievances.length;
  const breaches = grievances.filter((g) => g.status === 'SLA Breached').length;
  const resolved = grievances.filter((g) => g.status === 'Resolved').length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Civic Issues & Service Standards"
        description="Track how fast municipal and government departments resolve citizen complaints — from drinking water and road potholes to electricity and sanitation — against statutory Citizen's Charter redressal deadlines."
        breadcrumbs={[{ label: 'Civic Issues' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            Citizen's Charter SLA Monitor
          </span>
        }
      />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Total Complaints Audited"
          value={total}
          icon={<Building2 className="w-5 h-5" />}
          subtitle="Mudhalvar Mugavari & Urban portals"
        />
        <MetricCard
          title="SLA Breached Cases"
          value={breaches}
          change={`${((breaches / total) * 100).toFixed(0)}% Breach Rate`}
          changeType="negative"
          icon={<ShieldAlert className="w-5 h-5 text-rose-400" />}
          subtitle="Exceeded Citizen's Charter limit"
        />
        <MetricCard
          title="Resolved Cases"
          value={resolved}
          change="Turnaround Avg 8.2d"
          changeType="positive"
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />}
          subtitle="Within statutory deadlines"
        />
      </div>

      {/* Grievance Ledger Table */}
      <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <th className="py-3 px-4">Ticket ID</th>
                <th className="py-3 px-4">Category & Issue</th>
                <th className="py-3 px-4">District / Dept</th>
                <th className="py-3 px-4 text-center">Status</th>
                <th className="py-3 px-4 text-right">Statutory SLA</th>
                <th className="py-3 px-4 text-right">Elapsed Days</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {grievances.map((g) => {
                const isBreached = g.elapsed_days > g.sla_days;
                return (
                  <tr key={g.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-4 px-4 font-mono font-bold">
                      <Link
                        href={`/civic/${g.id}`}
                        className="text-blue-400 hover:text-blue-300 underline decoration-blue-500/40 hover:decoration-blue-400 transition-colors"
                      >
                        {g.id}
                      </Link>
                    </td>
                    <td className="py-4 px-4">
                      <Link href={`/civic/${g.id}`} className="font-semibold text-white hover:text-blue-400 transition-colors block">
                        {g.category}
                      </Link>
                      <div className="text-[11px] text-slate-400 line-clamp-1">{g.description}</div>
                    </td>
                    <td className="py-4 px-4">
                      <div className="text-slate-200 font-medium">{g.district}</div>
                      <div className="text-[10px] text-slate-400">{g.department}</div>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <StatusBadge status={g.status} />
                    </td>
                    <td className="py-4 px-4 text-right font-mono text-slate-300">
                      {g.sla_days} days
                    </td>
                    <td className={`py-4 px-4 text-right font-mono font-bold ${isBreached ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {g.elapsed_days} days
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
