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
  BookOpen
} from 'lucide-react';
import { PageHeader } from '../../components/PageHeader';
import { MetricCard } from '../../components/MetricCard';
import { StatusBadge } from '../../components/StatusBadge';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';

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
    provenanceGO: 'G.O. Ms No. 41 Social Welfare'
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
    provenanceGO: 'G.O. Ms No. 19 Social Welfare'
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
    provenanceGO: 'Directorate of Collegiate Education Guidelines'
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
    provenanceGO: 'G.O. Ms No. 12 Transport Dept'
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
    provenanceGO: 'Agriculture Demand No. 05 Policy Note'
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
    provenanceGO: 'MAWS Demand No. 34 Budget Allocations'
  }
];

export default function SchemesPage() {
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
      if (q) setSearchQuery(q);
      if (grp) setSelectedGroup(grp);
      if (dept) setSelectedDept(dept);
      if (st) setSelectedStatus(st);
    }
  }, []);

  // Sync state to URL
  const updateUrl = (q: string, grp: string, dept: string, st: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (grp && grp !== 'ALL') url.searchParams.set('group', grp); else url.searchParams.delete('group');
    if (dept && dept !== 'ALL') url.searchParams.set('dept', dept); else url.searchParams.delete('dept');
    if (st && st !== 'ALL') url.searchParams.set('status', st); else url.searchParams.delete('status');
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
      label: 'Target Group',
      value: selectedGroup,
      options: [
        { label: 'Women', value: 'Women' },
        { label: 'Students', value: 'Students' },
        { label: 'Farmers', value: 'Farmers' },
        { label: 'General Citizens', value: 'General' }
      ]
    },
    {
      id: 'department',
      label: 'Department',
      value: selectedDept,
      options: departments.map((d) => ({ label: d, value: d }))
    },
    {
      id: 'status',
      label: 'Status',
      value: selectedStatus,
      isAdvanced: true,
      options: statuses.map((s) => ({ label: s, value: s }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Government Welfare Schemes"
        description="Official welfare programs provided by the Government of Tamil Nadu. Learn about eligibility, direct citizen benefits, and verified government expenditure."
        breadcrumbs={[{ label: 'Government Schemes' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
            Citizen Benefits Directory
          </span>
        }
      />

      {/* KPI Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Flagship Schemes Cataloged"
          value={canonicalSchemes.length}
          icon={<BookOpen className="w-5 h-5 text-blue-400" />}
          subtitle="Verified with official G.O. references"
        />
        <MetricCard
          title="Direct Beneficiary Reach"
          value="2.2+ Crore"
          icon={<Users className="w-5 h-5 text-emerald-400" />}
          subtitle="Women, students, farmers, & elders"
        />
        <MetricCard
          title="Annual Budget Outlay"
          value="₹14,694 Cr"
          icon={<Landmark className="w-5 h-5 text-indigo-400" />}
          subtitle="Verified Demands for Grants expenditure"
        />
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
        <div className="p-12 text-center text-slate-400 text-xs bg-slate-900/40 rounded-2xl border border-slate-800 space-y-2">
          <p className="font-semibold text-slate-300">No welfare schemes match the selected filters.</p>
          <button
            type="button"
            onClick={handleClearAll}
            className="text-blue-400 hover:text-blue-300 font-semibold underline"
          >
            Reset all filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredSchemes.map((scheme) => (
            <div
              key={scheme.id}
              className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 flex flex-col justify-between hover:border-slate-700 transition-all shadow-lg space-y-4"
            >
              <div className="space-y-2.5">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="text-[11px] font-semibold text-slate-400 block mb-1">
                      {scheme.department}
                    </span>
                    <h3 className="font-bold text-base text-white leading-snug">
                      {scheme.name}
                    </h3>
                    <div className="text-xs font-medium text-amber-200/90 mt-0.5 font-sans">
                      {scheme.name_ta}
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 shrink-0">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
                      {scheme.beneficiaryGroup}
                    </span>
                    <StatusBadge status={scheme.status} isStatutoryVerified={true} />
                  </div>
                </div>

                {/* Benefit Box */}
                <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs space-y-1">
                  <span className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider block">
                    Citizen Benefit:
                  </span>
                  <p className="text-slate-200 leading-relaxed font-medium">
                    {scheme.benefit}
                  </p>
                </div>

                {/* Eligibility */}
                <div className="text-xs text-slate-400 leading-relaxed">
                  <strong className="text-slate-300">Who is eligible: </strong>
                  {scheme.eligibility}
                </div>
              </div>

              {/* Bottom Metadata */}
              <div className="pt-3 border-t border-slate-800/80 space-y-3">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">
                    Budget Disbursed: <strong className="text-white font-bold">₹{scheme.annualAllocationCr.toLocaleString()} Cr</strong>
                  </span>
                  <span className="text-slate-400">
                    Reach: <strong className="text-emerald-400 font-bold">{scheme.beneficiaryCount}</strong>
                  </span>
                </div>

                <div className="flex items-center justify-between text-[11px] pt-1">
                  <span className="text-slate-400 flex items-center gap-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-blue-400" />
                    <span>{scheme.provenanceGO}</span>
                  </span>
                  <div className="flex items-center gap-3">
                    <Link
                      href={`/claims?q=${encodeURIComponent(scheme.name)}`}
                      className="text-slate-400 hover:text-slate-200 inline-flex items-center gap-1 font-medium text-[11px]"
                    >
                      <span>Verify claims</span>
                    </Link>
                    <Link
                      href={`/schemes/${scheme.id}`}
                      className="text-blue-400 hover:text-blue-300 inline-flex items-center gap-1 font-semibold text-xs bg-blue-500/10 hover:bg-blue-500/20 px-2.5 py-1 rounded-lg border border-blue-500/20 transition-all"
                    >
                      <span>View Details</span>
                      <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
