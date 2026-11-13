'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  Users,
  CheckCircle2,
  Filter,
  Search,
  ExternalLink,
  ShieldCheck,
  Landmark,
  ArrowRight,
  BookOpen,
  Bookmark,
  BookmarkCheck,
  GraduationCap,
  Sprout,
  Heart,
  Home
} from 'lucide-react';
import { PageHeader } from '../../components/PageHeader';
import { MetricCard } from '../../components/MetricCard';
import { StatusBadge } from '../../components/StatusBadge';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';
import { SpotlightCard } from '../../components/SpotlightCard';
import { CitizenBenefitFinder } from '../../components/CitizenBenefitFinder';
import { useSavedCivicItems } from '../../lib/useSavedCivicItems';
import { useLanguage } from '../../lib/LanguageContext';

interface SchemeCard {
  id: string;
  name: string;
  name_ta: string;
  department: string;
  beneficiaryGroup: 'Women' | 'Students' | 'Farmers' | 'General';
  eligibility: string;
  benefit: string;
  annualAllocationCr: number;
  beneficiaryCount: string;
  status: string;
  provenanceGO: string;
  portalUrl?: string;
}

const canonicalSchemes: SchemeCard[] = [
  {
    id: 'SCH-SW-KMUT',
    name: 'Kalaignar Magalir Urimai Thittam (KMUT)',
    name_ta: 'கலைஞர் மகளிர் உரிமைத் திட்டம்',
    department: 'Social Welfare & Women Empowerment',
    beneficiaryGroup: 'Women',
    eligibility: 'Women heads of eligible households meeting annual income (<₹2.5L) & landholding criteria.',
    benefit: '₹1,000 monthly universal basic income transfer via Aadhaar Direct Benefit Transfer (DBT).',
    annualAllocationCr: 7850.12,
    beneficiaryCount: '1.16 Crore Women',
    status: 'Active / Implemented',
    provenanceGO: 'G.O. Ms No. 41 Social Welfare',
    portalUrl: 'https://kmut.tn.gov.in'
  },
  {
    id: 'SCH-EDU-BREAKFAST',
    name: "Chief Minister's Morning Breakfast Scheme",
    name_ta: 'முதலமைச்சரின் காலை உணவுத் திட்டம்',
    department: 'School Education / Social Welfare',
    beneficiaryGroup: 'Students',
    eligibility: 'All students enrolled in Classes 1 through 5 in government primary schools across Tamil Nadu.',
    benefit: 'Fresh, nutritious hot cooked breakfast served every school day morning.',
    annualAllocationCr: 472.10,
    beneficiaryCount: '18.5 Lakh Children',
    status: 'Active / Implemented',
    provenanceGO: 'G.O. Ms No. 19 Social Welfare',
    portalUrl: 'https://tnschools.gov.in'
  },
  {
    id: 'SCH-HE-PUDHUMAI',
    name: 'Moovalur Ramamirtham Ammaiyar Pudhumai Penn Scheme',
    name_ta: 'புதுமைப் பெண் திட்டம்',
    department: 'Higher Education Department',
    beneficiaryGroup: 'Students',
    eligibility: 'Girl students who studied Classes 6 to 12 in state government schools and join college or polytechnic.',
    benefit: '₹1,000 monthly financial incentive deposited directly to student bank accounts until graduation.',
    annualAllocationCr: 1098.40,
    beneficiaryCount: '4.8 Lakh Girl Students',
    status: 'Active / Implemented',
    provenanceGO: 'Directorate of Collegiate Education Guidelines',
    portalUrl: 'https://www.penkalvi.tn.gov.in'
  },
  {
    id: 'SCH-TR-VIDIYAL',
    name: 'Vidiyal Payanam (Fare-Free Bus Travel for Women)',
    name_ta: 'விடியல் பயணம் (மகளிருக்கான கட்டணமில்லாப் பேருந்து)',
    department: 'Transport Department',
    beneficiaryGroup: 'Women',
    eligibility: 'All women citizens, transwomen, and visually impaired persons across Tamil Nadu.',
    benefit: '100% fare-free travel on standard town and city transport corporation buses.',
    annualAllocationCr: 3085.60,
    beneficiaryCount: '500+ Crore Cumulative Trips',
    status: 'Active / Implemented',
    provenanceGO: 'G.O. Ms No. 12 Transport Dept',
    portalUrl: 'https://www.tnstc.in'
  },
  {
    id: 'SCH-AG-KALAIGNAR',
    name: 'Kalaignarin All Village Integrated Agricultural Development Programme',
    name_ta: 'அனைத்து கிராம ஒருங்கிணைந்த வேளாண் வளர்ச்சித் திட்டம்',
    department: 'Agriculture and Farmers Welfare',
    beneficiaryGroup: 'Farmers',
    eligibility: 'Small and marginal farmers across selected gram panchayats in all 37 rural districts.',
    benefit: 'Free coconut saplings, horticulture toolkits, micro-irrigation subsidies, and soil health cards.',
    annualAllocationCr: 208.50,
    beneficiaryCount: '16.4 Lakh Farmers',
    status: 'Active / Implemented',
    provenanceGO: 'Agriculture Demand No. 05 Policy Note',
    portalUrl: 'https://tnhorticulture.tn.gov.in'
  },
  {
    id: 'SCH-URB-SINGARA',
    name: 'Singara Chennai 2.0 & Urban Flood Mitigation',
    name_ta: 'சிங்காரச் சென்னை 2.0 திட்டம்',
    department: 'Municipal Administration & Water Supply',
    beneficiaryGroup: 'General',
    eligibility: 'Residents of Greater Chennai Corporation and metropolitan suburban wards.',
    benefit: 'Modern stormwater drain networks, urban sponge parks, and water body eco-restoration.',
    annualAllocationCr: 1980.20,
    beneficiaryCount: '85+ Lakh Urban Residents',
    status: 'Active / Ongoing',
    provenanceGO: 'MAWS Demand No. 34 Budget Allocations',
    portalUrl: 'https://chennaicorporation.gov.in'
  }
];

export default function SchemesPage() {
  const { language } = useLanguage();
  const { isSaved, saveRecord, removeRecord } = useSavedCivicItems();
  const [activeView, setActiveView] = useState<'catalog' | 'calculator'>('catalog');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [selectedGroup, setSelectedGroup] = useState<string>('ALL');
  const [selectedDept, setSelectedDept] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');

  // Load URL search parameters on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const grp = sp.get('group');
      const dept = sp.get('dept');
      const st = sp.get('status');
      const v = sp.get('view');
      if (q) setSearchQuery(q);
      if (grp) setSelectedGroup(grp);
      if (dept) setSelectedDept(dept);
      if (st) setSelectedStatus(st);
      if (v === 'calculator') setActiveView('calculator');
    }
  }, []);

  // Sync state to URL
  const updateUrl = (q: string, grp: string, dept: string, st: string, v: string = activeView) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (grp && grp !== 'ALL') url.searchParams.set('group', grp); else url.searchParams.delete('group');
    if (dept && dept !== 'ALL') url.searchParams.set('dept', dept); else url.searchParams.delete('dept');
    if (st && st !== 'ALL') url.searchParams.set('status', st); else url.searchParams.delete('status');
    if (v === 'calculator') url.searchParams.set('view', 'calculator'); else url.searchParams.delete('view');
    window.history.replaceState({}, '', url.toString());
  };

  const departments = useMemo(() => {
    return Array.from(new Set(canonicalSchemes.map((s) => s.department))).sort();
  }, []);

  const statuses = useMemo(() => {
    return Array.from(new Set(canonicalSchemes.map((s) => s.status))).sort();
  }, []);

  const handleSearchChange = (q: string) => {
    setSearchQuery(q);
    updateUrl(q, selectedGroup, selectedDept, selectedStatus);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let newGrp = selectedGroup;
    let newDept = selectedDept;
    let newSt = selectedStatus;

    if (groupId === 'group') {
      newGrp = val;
      setSelectedGroup(val);
    } else if (groupId === 'department') {
      newDept = val;
      setSelectedDept(val);
    } else if (groupId === 'status') {
      newSt = val;
      setSelectedStatus(val);
    }

    updateUrl(searchQuery, newGrp, newDept, newSt);
  };

  const handleClearAll = () => {
    setSearchQuery('');
    setSelectedGroup('ALL');
    setSelectedDept('ALL');
    setSelectedStatus('ALL');
    updateUrl('', 'ALL', 'ALL', 'ALL');
  };

  const filteredSchemes = useMemo(() => {
    return canonicalSchemes.filter((scheme) => {
      if (selectedGroup !== 'ALL' && scheme.beneficiaryGroup !== selectedGroup) {
        return false;
      }
      if (selectedDept !== 'ALL' && scheme.department !== selectedDept) {
        return false;
      }
      if (selectedStatus !== 'ALL' && scheme.status !== selectedStatus) {
        return false;
      }
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        return (
          scheme.name.toLowerCase().includes(q) ||
          scheme.name_ta.includes(q) ||
          scheme.department.toLowerCase().includes(q) ||
          scheme.eligibility.toLowerCase().includes(q) ||
          scheme.benefit.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [searchQuery, selectedGroup, selectedDept, selectedStatus]);

  const filterGroups: FilterGroup[] = [
    {
      id: 'group',
      label: language === 'ta' ? 'பயனாளிகள் பிரிவு' : 'Target Group',
      value: selectedGroup,
      options: [
        { label: 'Women (மகளிர்)', value: 'Women' },
        { label: 'Students (மாணவர்கள்)', value: 'Students' },
        { label: 'Farmers (விவசாயிகள்)', value: 'Farmers' },
        { label: 'General Citizens (பொதுமக்கள்)', value: 'General' }
      ]
    },
    {
      id: 'department',
      label: language === 'ta' ? 'அரசு துறை' : 'Department',
      value: selectedDept,
      options: departments.map((d) => ({ label: d, value: d }))
    },
    {
      id: 'status',
      label: language === 'ta' ? 'நிலை' : 'Status',
      value: selectedStatus,
      isAdvanced: true,
      options: statuses.map((s) => ({ label: s, value: s }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={language === 'ta' ? 'அரசு நலத்திட்டங்கள்' : 'Government Welfare Schemes'}
        description={
          language === 'ta'
            ? 'தமிழ்நாடு அரசின் அதிகாரப்பூர்வ நலத்திட்டங்கள், உதவித்தொகை, தகுதி விதிகள், தேவையான ஆவணங்கள் மற்றும் பயன்பெறும் வழிமுறைகள்.'
            : 'Official welfare programs provided by the Government of Tamil Nadu. Learn about eligibility, direct monthly benefits, and verified government expenditure.'
        }
        breadcrumbs={[{ label: language === 'ta' ? 'அரசுத் திட்டங்கள்' : 'Government Schemes' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {language === 'ta' ? 'அதிகாரப்பூர்வ மக்கள் திட்டங்கள்' : 'Citizen Benefits Directory'}
          </span>
        }
      />

      {/* KPI Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title={language === 'ta' ? 'முக்கிய திட்டங்கள்' : 'Flagship Schemes Cataloged'}
          value={canonicalSchemes.length}
          icon={<BookOpen className="w-5 h-5 text-cyan-400" />}
          subtitle="Verified with official G.O. references"
        />
        <MetricCard
          title={language === 'ta' ? 'பயனடைந்த குடிமக்கள்' : 'Direct Beneficiary Reach'}
          value="2.2+ Crore"
          icon={<Users className="w-5 h-5 text-emerald-400" />}
          subtitle="Women, students, farmers, & elders"
        />
        <MetricCard
          title={language === 'ta' ? 'ஆண்டு நிதி ஒதுக்கீடு' : 'Annual Budget Outlay'}
          value="₹14,694 Cr"
          icon={<Landmark className="w-5 h-5 text-indigo-400" />}
          subtitle="Verified Demands for Grants expenditure"
        />
      </div>

      {/* View Switcher: Interactive Calculator vs Catalog */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3 p-3 rounded-2xl bg-white/[0.03] border border-white/[0.08] backdrop-blur-md">
        <div className="text-xs text-slate-300">
          <strong className="text-white font-semibold">Choose Your View: </strong>
          Use the 30-Second Calculator to find schemes you qualify for, or browse the complete catalog below.
        </div>
        <div className="flex items-center gap-2 shrink-0">
          <button
            type="button"
            onClick={() => {
              setActiveView('catalog');
              updateUrl(searchQuery, selectedGroup, selectedDept, selectedStatus, 'catalog');
            }}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
              activeView === 'catalog'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                : 'text-slate-300 hover:text-white hover:bg-white/[0.05]'
            }`}
          >
            📋 {language === 'ta' ? 'முழு திட்ட பட்டியல்' : 'All Schemes Catalog'}
          </button>
          <button
            type="button"
            onClick={() => {
              setActiveView('calculator');
              updateUrl(searchQuery, selectedGroup, selectedDept, selectedStatus, 'calculator');
            }}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all ${
              activeView === 'calculator'
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                : 'text-slate-300 hover:text-white hover:bg-white/[0.05]'
            }`}
          >
            🎯 {language === 'ta' ? '30-வினாடி தகுதி கால்குலேட்டர்' : '30-Sec Eligibility Calculator'}
          </button>
        </div>
      </div>

      {/* Render Calculator if selected */}
      {activeView === 'calculator' ? (
        <CitizenBenefitFinder />
      ) : (
        <>
          {/* Quick Target Group Filter Pills */}
          <div className="flex flex-wrap items-center gap-2 pt-1">
            <span className="text-xs font-medium text-slate-400 mr-1">Filter by Group:</span>
            {[
              { id: 'ALL', label: 'All Schemes (6)', icon: BookOpen },
              { id: 'Women', label: '👩 Women (2)', icon: Users },
              { id: 'Students', label: '🎓 Students (2)', icon: GraduationCap },
              { id: 'Farmers', label: '🌾 Farmers (1)', icon: Sprout },
              { id: 'General', label: '🏙️ General (1)', icon: Home },
            ].map((grp) => (
              <button
                key={grp.id}
                type="button"
                onClick={() => handleFilterChange('group', grp.id)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
                  selectedGroup === grp.id
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400 shadow-sm'
                    : 'bg-white/[0.03] text-slate-300 hover:text-white border border-white/[0.08] hover:bg-white/[0.06]'
                }`}
              >
                {grp.label}
              </button>
            ))}
          </div>

          {/* Simplified Filter Bar */}
          <SimpleFilterBar
            searchQuery={searchQuery}
            onSearchChange={handleSearchChange}
            searchPlaceholder="Search schemes by name in English or தமிழ் (e.g. மகளிர், breakfast, புதுமைப் பெண்)..."
            filterGroups={filterGroups}
            onFilterChange={handleFilterChange}
            onClearAll={handleClearAll}
            totalResults={canonicalSchemes.length}
            filteredResults={filteredSchemes.length}
            resultNoun="welfare schemes"
          />

          {/* Schemes Grid */}
          {filteredSchemes.length === 0 ? (
            <CivicStateNotice
              state="no_matching_results"
              title="No Welfare Schemes Found"
              description="No government welfare schemes matched the selected filters. Try choosing 'All Target Groups' or resetting filters."
              onClearFilters={handleClearAll}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {filteredSchemes.map((scheme) => {
                const glowColor =
                  scheme.beneficiaryGroup === 'Women'
                    ? 'rgba(244, 63, 94, 0.16)'
                    : scheme.beneficiaryGroup === 'Students'
                    ? 'rgba(6, 182, 212, 0.16)'
                    : scheme.beneficiaryGroup === 'Farmers'
                    ? 'rgba(16, 185, 129, 0.16)'
                    : 'rgba(99, 102, 241, 0.16)';

                const borderColor =
                  scheme.beneficiaryGroup === 'Women'
                    ? 'rgba(244, 63, 94, 0.4)'
                    : scheme.beneficiaryGroup === 'Students'
                    ? 'rgba(6, 182, 212, 0.4)'
                    : scheme.beneficiaryGroup === 'Farmers'
                    ? 'rgba(16, 185, 129, 0.4)'
                    : 'rgba(99, 102, 241, 0.4)';

                const saved = isSaved('scheme', scheme.id);

                return (
                  <SpotlightCard
                    key={scheme.id}
                    spotlightColor={glowColor}
                    borderColor={borderColor}
                    className="p-6 flex flex-col justify-between group space-y-4"
                  >
                    <div className="space-y-3">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="text-[11px] font-mono font-semibold text-cyan-400 block mb-1">
                            {scheme.department}
                          </span>
                          <h3 className="font-bold text-lg text-white leading-snug group-hover:text-cyan-300 transition-colors">
                            {scheme.name}
                          </h3>
                          <div className="text-xs font-medium text-amber-300/90 mt-0.5 font-sans">
                            {scheme.name_ta}
                          </div>
                        </div>
                        <div className="flex flex-col items-end gap-1.5 shrink-0">
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/20 font-mono">
                            {scheme.beneficiaryGroup}
                          </span>
                          <StatusBadge status={scheme.status} isStatutoryVerified={true} />
                        </div>
                      </div>

                      {/* Citizen Benefit Box with High-Contrast Clarity */}
                      <div className="p-4 rounded-2xl bg-black/60 border border-white/[0.1] text-xs space-y-1 backdrop-blur-md">
                        <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">
                          Citizen Direct Benefit:
                        </span>
                        <p className="text-white leading-relaxed font-semibold">
                          {scheme.benefit}
                        </p>
                      </div>

                      {/* Eligibility criteria */}
                      <div className="text-xs text-slate-300 leading-relaxed">
                        <strong className="text-slate-200 font-semibold">Who is Eligible: </strong>
                        {scheme.eligibility}
                      </div>
                    </div>

                    {/* Bottom Metadata & Citizen Actions */}
                    <div className="pt-4 border-t border-white/[0.08] space-y-3">
                      <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">
                          Disbursed: <strong className="text-white font-bold stat-number-glow">₹{scheme.annualAllocationCr.toLocaleString()} Cr</strong>
                        </span>
                        <span className="text-slate-400">
                          Beneficiaries: <strong className="text-emerald-400 font-bold">{scheme.beneficiaryCount}</strong>
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-[11px] pt-1">
                        <span className="text-slate-400 flex items-center gap-1.5 font-mono text-[10px]">
                          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                          <span>{scheme.provenanceGO}</span>
                        </span>

                        <div className="flex items-center gap-2">
                          {/* 1-Click Save Scheme Button */}
                          <button
                            type="button"
                            onClick={() => {
                              if (saved) {
                                removeRecord('scheme', scheme.id);
                              } else {
                                saveRecord({
                                  record_type: 'scheme',
                                  record_id: scheme.id,
                                  title: scheme.name,
                                  detail_url: `/schemes/${scheme.id}`,
                                  current_status: scheme.status
                                });
                              }
                            }}
                            className={`p-1.5 rounded-xl border transition-all ${
                              saved
                                ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                                : 'bg-white/[0.04] text-slate-400 hover:text-white border-white/[0.08] hover:bg-white/[0.08]'
                            }`}
                            title={saved ? 'Remove from Saved' : 'Save Scheme for Later'}
                          >
                            {saved ? <BookmarkCheck className="w-4 h-4 text-cyan-400" /> : <Bookmark className="w-4 h-4" />}
                          </button>

                          {scheme.portalUrl && (
                            <a
                              href={scheme.portalUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-slate-300 hover:text-white inline-flex items-center gap-1 font-medium text-[11px] bg-white/[0.04] hover:bg-white/[0.08] px-2.5 py-1.5 rounded-xl border border-white/[0.08] transition-colors"
                            >
                              <span>Official Portal</span>
                              <ExternalLink className="w-3 h-3 text-cyan-400" />
                            </a>
                          )}

                          <Link
                            href={`/schemes/${scheme.id}`}
                            className="text-cyan-300 hover:text-white inline-flex items-center gap-1.5 font-semibold text-xs bg-cyan-500/10 hover:bg-cyan-500/20 px-3.5 py-1.5 rounded-xl border border-cyan-500/25 transition-all group-hover:border-cyan-500/50 shadow-sm"
                          >
                            <span>Details</span>
                            <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                          </Link>
                        </div>
                      </div>
                    </div>
                  </SpotlightCard>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
