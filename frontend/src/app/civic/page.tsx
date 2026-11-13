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
  Lock,
  Phone,
  Bookmark,
  BookmarkCheck,
  Droplets,
  Zap,
  Trash2,
  AlertCircle,
  ExternalLink
} from 'lucide-react';
import { CivicGrievance } from '../../lib/types';
import { fetchCivicGrievances } from '../../lib/api';
import { StatusBadge } from '../../components/StatusBadge';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';
import { SpotlightCard } from '../../components/SpotlightCard';
import { useSavedCivicItems } from '../../lib/useSavedCivicItems';
import { useLanguage } from '../../lib/LanguageContext';

export default function CivicPage() {
  const { language } = useLanguage();
  const { isSaved, saveRecord, removeRecord } = useSavedCivicItems();
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
      label: language === 'ta' ? 'மாவட்டம்' : 'District',
      value: selectedDistrict,
      options: districts.map((d) => ({ label: d, value: d }))
    },
    {
      id: 'status',
      label: language === 'ta' ? 'தீர்வு நிலை' : 'Resolution Status',
      value: selectedStatus,
      options: [
        { label: '✅ Resolved within SLA (தீர்வு)', value: 'Resolved' },
        { label: '⚠️ SLA Breached (கால வரம்பு மீறல்)', value: 'Breached' },
        { label: '🔄 In Progress / Escalated (பரிசீலனையில்)', value: 'Pending' }
      ]
    },
    {
      id: 'department',
      label: language === 'ta' ? 'துறை' : 'Department',
      value: selectedDept,
      isAdvanced: true,
      options: departments.map((d) => ({ label: d, value: d }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={language === 'ta' ? 'மக்கள் குறைகள் & தீர்வு கால வரம்பு' : 'Civic Issues & Service Standards'}
        description={
          language === 'ta'
            ? 'மாநகராட்சி மற்றும் அரசுத் துறைகள் குடிநீர், சாலைகள், மின்சாரம், துப்புரவு போன்ற மக்கள் புகார்களை சட்டப்பூர்வ கால வரம்பிற்குள் (Citizen Charter) தீர்க்கின்றனவா என்பதை அறியுங்கள்.'
            : "Track how fast municipal and government departments resolve citizen complaints — from drinking water and road potholes to electricity and sanitation — against statutory Citizen's Charter redressal deadlines."
        }
        breadcrumbs={[{ label: language === 'ta' ? 'மக்கள் குறைகள்' : 'Civic Issues' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">
            {language === 'ta' ? 'குடிமக்கள் உரிமைச் சாசனம் (14-நாள் SLA)' : "Citizen's Charter SLA Monitor"}
          </span>
        }
      />

      {/* Prominent Citizen Emergency & Grievance Lodging Action Banner */}
      <div className="p-4 sm:p-5 rounded-3xl bg-gradient-to-r from-amber-950/40 via-rose-950/30 to-indigo-950/40 border border-amber-500/25 space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Phone className="w-4 h-4 text-amber-400 animate-pulse" />
              <h3 className="font-bold text-white text-sm sm:text-base">
                {language === 'ta' ? 'புகார் அளிக்க வேண்டுமா? உடனடி அரசு உதவி எண்கள்:' : 'Need to Lodge a Civic Complaint Right Now?'}
              </h3>
            </div>
            <p className="text-xs text-slate-300">
              {language === 'ta'
                ? 'உங்கள் பகுதியில் உள்ள சாலை, குடிநீர், மின்சாரம், அல்லது தெருவிளக்கு குறைபாடுகளை இந்த எண்களில் அழைக்கலாம்:'
                : 'Free official government helplines with 14-day statutory resolution guarantee:'}
            </p>
          </div>

          <a
            href="https://cmhelpline.tnega.org"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-rose-500 hover:from-amber-400 hover:to-rose-400 text-white font-bold text-xs shadow-md transition-all shrink-0"
          >
            <span>{language === 'ta' ? 'முதலமைச்சர் உதவி மையம் இணையதளம்' : 'CM Helpline Portal'}</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        {/* Quick Click-to-Call Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-1">
          <a
            href="tel:1100"
            className="flex items-center gap-2 p-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs transition-colors"
          >
            <div className="p-1 rounded-lg bg-rose-500/20 text-rose-300 font-bold">1100</div>
            <div>
              <div className="font-bold text-white">CM Helpline</div>
              <div className="text-[10px] text-slate-400">All TN Departments</div>
            </div>
          </a>

          <a
            href="tel:1913"
            className="flex items-center gap-2 p-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs transition-colors"
          >
            <div className="p-1 rounded-lg bg-amber-500/20 text-amber-300 font-bold">1913</div>
            <div>
              <div className="font-bold text-white">Chennai Corp</div>
              <div className="text-[10px] text-slate-400">Roads & Garbage</div>
            </div>
          </a>

          <a
            href="tel:1912"
            className="flex items-center gap-2 p-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs transition-colors"
          >
            <div className="p-1 rounded-lg bg-yellow-500/20 text-yellow-300 font-bold">1912</div>
            <div>
              <div className="font-bold text-white">TANGEDCO (EB)</div>
              <div className="text-[10px] text-slate-400">Power & Wires</div>
            </div>
          </a>

          <a
            href="tel:181"
            className="flex items-center gap-2 p-2.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] text-xs transition-colors"
          >
            <div className="p-1 rounded-lg bg-pink-500/20 text-pink-300 font-bold">181</div>
            <div>
              <div className="font-bold text-white">Women&apos;s Helpline</div>
              <div className="text-[10px] text-slate-400">24x7 Emergency</div>
            </div>
          </a>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title={language === 'ta' ? 'மொத்த தணிக்கை புகார்கள்' : 'Total Complaints Audited'}
          value={total}
          icon={<Building2 className="w-5 h-5 text-cyan-400" />}
          subtitle="Mudhalvar Mugavari & Urban portals"
        />
        <MetricCard
          title={language === 'ta' ? 'கால வரம்பு மீறிய வழக்குகள்' : 'SLA Breached Cases'}
          value={breaches}
          change={total > 0 ? `${((breaches / total) * 100).toFixed(0)}% Breach Rate` : undefined}
          changeType="negative"
          icon={<ShieldAlert className="w-5 h-5 text-rose-400" />}
          subtitle="Exceeded statutory Citizen Charter deadline"
        />
        <MetricCard
          title={language === 'ta' ? 'தீர்வு பெற்ற வழக்குகள்' : 'Resolved Cases'}
          value={resolved}
          change="Turnaround Avg 8.2d"
          changeType="positive"
          icon={<CheckCircle2 className="w-5 h-5 text-emerald-400" />}
          subtitle="Fixed within statutory SLA"
        />
      </div>

      {/* Quick Category Filter Pills */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <span className="text-xs font-medium text-slate-400 mr-1">Filter by Issue:</span>
        {[
          { id: '', label: 'All Issues' },
          { id: 'water', label: '💧 Drinking Water' },
          { id: 'road', label: '🛣️ Roads & Potholes' },
          { id: 'drainage', label: '🌊 Drainage & Sewage' },
          { id: 'electricity', label: '⚡ Electricity (EB)' },
          { id: 'sanitation', label: '🗑️ Garbage / Waste' },
        ].map((cat) => (
          <button
            key={cat.id}
            type="button"
            onClick={() => handleSearchChange(cat.id)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              search === cat.id
                ? 'bg-amber-500/25 text-amber-200 border border-amber-400 shadow-sm font-bold'
                : 'bg-white/[0.03] text-slate-300 border border-white/[0.08] hover:bg-white/[0.06]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Simplified Filter Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search complaints by description, category, or district..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={grievances.length}
        filteredResults={filtered.length}
        resultNoun="grievances"
      />

      {/* Grievances List */}
      {loading ? (
        <CivicStateNotice
          state="loading"
          title="Loading Civic Grievance Log..."
          description="Retrieving DPDPA-scrubbed citizen grievance reports and SLA resolution latencies."
        />
      ) : filtered.length === 0 ? (
        <CivicStateNotice
          state="no_matching_results"
          title="No Grievances Found"
          description="No civic complaints match the selected district, department, or resolution status."
          onClearFilters={handleClearAll}
        />
      ) : (
        <div className="space-y-4">
          {filtered.map((g) => {
            const isBreached = g.status === 'SLA Breached';
            const glowColor = isBreached ? 'rgba(244, 63, 94, 0.16)' : 'rgba(16, 185, 129, 0.16)';
            const borderColor = isBreached ? 'rgba(244, 63, 94, 0.35)' : 'rgba(16, 185, 129, 0.35)';
            const saved = isSaved('civic', g.id);

            return (
              <SpotlightCard
                key={g.id}
                spotlightColor={glowColor}
                borderColor={borderColor}
                className="p-6 space-y-4 group transition-all duration-300"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-[11px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20">
                        {g.category}
                      </span>
                      <span className="text-xs text-slate-300 flex items-center gap-1 font-medium">
                        <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{g.district}</span>
                      </span>
                      <span className="text-xs text-slate-400">• {g.department}</span>
                      <span className="text-[10px] font-mono text-slate-500">[Ticket: #{g.id}]</span>
                    </div>

                    <h3 className="font-bold text-base text-white leading-snug group-hover:text-cyan-300 transition-colors">
                      {g.description}
                    </h3>

                    <div className="text-xs text-slate-400">
                      Filed Date: <strong className="text-slate-300 font-mono">{g.filed_date}</strong>
                    </div>
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    <StatusBadge status={g.status} />

                    {/* Bookmark Grievance button */}
                    <button
                      type="button"
                      onClick={() => {
                        if (saved) {
                          removeRecord('civic', g.id);
                        } else {
                          saveRecord({
                            record_type: 'civic',
                            record_id: g.id,
                            title: `${g.category} (${g.district}) - ${g.description.substring(0, 50)}...`,
                            detail_url: `/civic/${g.id}`,
                            current_status: g.status
                          });
                        }
                      }}
                      className={`p-1.5 rounded-xl border transition-all ${
                        saved
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                          : 'bg-white/[0.04] text-slate-400 hover:text-white border-white/[0.08]'
                      }`}
                      title={saved ? 'Remove Bookmark' : 'Save Complaint'}
                    >
                      {saved ? <BookmarkCheck className="w-4 h-4 text-cyan-400" /> : <Bookmark className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* SLA Metrics Bar */}
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-1">
                  <div className="p-3.5 rounded-2xl bg-black/60 border border-white/[0.08] space-y-0.5 backdrop-blur-md">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Statutory Charter SLA</span>
                    <span className="text-sm font-bold text-white font-mono">{g.sla_days} Days</span>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-black/60 border border-white/[0.08] space-y-0.5 backdrop-blur-md">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Days Elapsed</span>
                    <span className={`text-sm font-bold font-mono ${isBreached ? 'text-rose-400' : 'text-emerald-400'}`}>
                      {g.elapsed_days} Days {isBreached ? '(Breached SLA)' : '(On Schedule)'}
                    </span>
                  </div>
                  <div className="p-3.5 rounded-2xl bg-black/60 border border-white/[0.08] col-span-2 sm:col-span-1 space-y-0.5 backdrop-blur-md">
                    <span className="text-[10px] text-slate-400 uppercase font-semibold block">Department</span>
                    <span className="text-xs font-semibold text-slate-200 truncate block">{g.department}</span>
                  </div>
                </div>

                {/* Actions & Privacy Redaction notice */}
                <div className="pt-3 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.08] text-xs">
                  <span className="text-[11px] text-slate-400 flex items-center gap-1.5 font-mono">
                    <Lock className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Citizen Privacy Protected: DPDPA 2023 redacted.</span>
                  </span>

                  <Link
                    href={`/civic/${g.id}`}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-1.5 rounded-xl bg-cyan-500/10 text-cyan-300 border border-cyan-500/25 hover:bg-cyan-500/20 transition-all group-hover:border-cyan-500/50 shadow-sm ml-auto"
                  >
                    <span>Inspect Grievance Audit</span>
                    <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                  </Link>
                </div>
              </SpotlightCard>
            );
          })}
        </div>
      )}
    </div>
  );
}
