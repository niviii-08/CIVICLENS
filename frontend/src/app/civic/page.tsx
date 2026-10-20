'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  AlertTriangle,
  Clock,
  CheckCircle2,
  ShieldAlert,
  Building2,
  MapPin,
  ArrowRight,
  Lock
} from 'lucide-react';
import { CivicGrievance } from '../../lib/types';
import { fetchCivicGrievances } from '../../lib/api';
import { StatusBadge } from '../../components/StatusBadge';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';

export default function CivicPage() {
  const [grievances, setGrievances] = useState<CivicGrievance[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedDistrict, setSelectedDistrict] = useState('ALL');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [selectedStatus, setSelectedStatus] = useState('ALL');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const dist = sp.get('district');
      const dept = sp.get('dept');
      const st = sp.get('status');
      if (q) setSearch(q);
      if (dist) setSelectedDistrict(dist);
      if (dept) setSelectedDept(dept);
      if (st) setSelectedStatus(st);
    }
  }, []);

  const updateUrl = (q: string, dist: string, dept: string, st: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (dist && dist !== 'ALL') url.searchParams.set('district', dist); else url.searchParams.delete('district');
    if (dept && dept !== 'ALL') url.searchParams.set('dept', dept); else url.searchParams.delete('dept');
    if (st && st !== 'ALL') url.searchParams.set('status', st); else url.searchParams.delete('status');
    window.history.replaceState({}, '', url.toString());
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchCivicGrievances();
      setGrievances(data);
      setLoading(false);
    }
    load();
  }, []);

  const districts = useMemo(() => {
    const set = new Set<string>();
    grievances.forEach((g) => {
      if (g.district) set.add(g.district);
    });
    return Array.from(set).sort();
  }, [grievances]);

  const departments = useMemo(() => {
    const set = new Set<string>();
    grievances.forEach((g) => {
      if (g.department) set.add(g.department);
    });
    return Array.from(set).sort();
  }, [grievances]);

  const handleSearchChange = (q: string) => {
    setSearch(q);
    updateUrl(q, selectedDistrict, selectedDept, selectedStatus);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let d = selectedDistrict;
    let dep = selectedDept;
    let s = selectedStatus;

    if (groupId === 'district') {
      d = val;
      setSelectedDistrict(val);
    } else if (groupId === 'department') {
      dep = val;
      setSelectedDept(val);
    } else if (groupId === 'status') {
      s = val;
      setSelectedStatus(val);
    }

    updateUrl(search, d, dep, s);
  };

  const handleClearAll = () => {
    setSearch('');
    setSelectedDistrict('ALL');
    setSelectedDept('ALL');
    setSelectedStatus('ALL');
    updateUrl('', 'ALL', 'ALL', 'ALL');
  };

  const filtered = useMemo(() => {
    return grievances.filter((g) => {
      if (selectedDistrict !== 'ALL' && g.district !== selectedDistrict) return false;
      if (selectedDept !== 'ALL' && g.department !== selectedDept) return false;
      if (selectedStatus !== 'ALL') {
        if (selectedStatus === 'Breached' && g.status !== 'SLA Breached') return false;
        if (selectedStatus === 'Resolved' && g.status !== 'Resolved') return false;
        if (selectedStatus === 'Pending' && g.status !== 'Pending' && g.status !== 'Escalated') return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          g.category.toLowerCase().includes(q) ||
          g.description.toLowerCase().includes(q) ||
          g.district.toLowerCase().includes(q) ||
          g.department.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [grievances, selectedDistrict, selectedDept, selectedStatus, search]);

  const total = grievances.length;
  const breaches = grievances.filter((g) => g.status === 'SLA Breached').length;
  const resolved = grievances.filter((g) => g.status === 'Resolved').length;

  const filterGroups: FilterGroup[] = [
    {
      id: 'district',
      label: 'District',
      value: selectedDistrict,
      options: districts.map((d) => ({ label: d, value: d }))
    },
    {
      id: 'status',
      label: 'Resolution Status',
      value: selectedStatus,
      options: [
        { label: 'Resolved within SLA', value: 'Resolved' },
        { label: 'SLA Breached', value: 'Breached' },
        { label: 'In Progress / Escalated', value: 'Pending' }
      ]
    },
    {
      id: 'department',
      label: 'Department',
      value: selectedDept,
      isAdvanced: true,
      options: departments.map((d) => ({ label: d, value: d }))
    }
  ];

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
          change={total > 0 ? `${((breaches / total) * 100).toFixed(0)}% Breach Rate` : undefined}
          changeType="negative"
          icon={<ShieldAlert className="w-5 h-5 text-rose-400" />}
          subtitle="Exceeded statutory Citizen Charter deadline"
        />
        <MetricCard
          title="Resolved Cases"
          value={resolved}
          change="Turnaround Avg 8.2d"
          changeType="positive"
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />}
          subtitle="Verified by departmental closure"
        />
      </div>

      {/* Simplified Filter Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search civic issues by category, district, or keyword (e.g. drinking water, pothole, electricity)..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={grievances.length}
        filteredResults={filtered.length}
        resultNoun="grievances"
      />

      {/* Grievance Cards List */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading municipal grievance audits...</span>
        </div>
      ) : filtered.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-slate-900/40 rounded-2xl border border-slate-800 space-y-2">
          <p className="font-semibold text-slate-300">No civic issues match your filter criteria.</p>
          <button
            type="button"
            onClick={handleClearAll}
            className="text-blue-400 hover:text-blue-300 font-semibold underline"
          >
            Reset all filters
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map((g) => {
            const isBreached = g.elapsed_days > g.sla_days;
            return (
              <div
                key={g.id}
                className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 space-y-4 shadow-lg hover:border-slate-700 transition-all"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                  <div className="space-y-1.5 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                        {g.category}
                      </span>
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5 text-slate-500" />
                        <span>{g.district}</span>
                      </span>
                      <span className="text-xs text-slate-500">• {g.department}</span>
                    </div>

                    <h3 className="font-bold text-base text-white leading-snug">
                      {g.description}
                    </h3>

                    <div className="text-xs text-slate-400">
                      Filed on: <strong className="text-slate-300">{g.filed_date}</strong>
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    <StatusBadge status={g.status} />
                  </div>
                </div>

                {/* SLA Metrics Bar */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-1">
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Statutory Charter SLA</span>
                    <span className="text-sm font-bold text-white font-mono">{g.sla_days} Days</span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Days Elapsed</span>
                    <span className={`text-sm font-bold font-mono ${isBreached ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {g.elapsed_days} Days {isBreached ? '(Breached)' : '(On Schedule)'}
                    </span>
                  </div>
                  <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 col-span-2 sm:col-span-1">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Civic Redressal Authority</span>
                    <span className="text-xs font-semibold text-slate-200 truncate block">{g.department}</span>
                  </div>
                </div>

                {/* Actions & Privacy Redaction notice */}
                <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80 text-xs">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1.5">
                    <Lock className="w-3.5 h-3.5 text-blue-400" />
                    <span>Citizen Privacy Protected: Identifiable personal contact details are redacted.</span>
                  </span>

                  <Link
                    href={`/civic/${g.id}`}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-600/20 text-blue-300 border border-blue-500/30 hover:bg-blue-600/30 transition-all ml-auto"
                  >
                    <span>Inspect Grievance Audit</span>
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
