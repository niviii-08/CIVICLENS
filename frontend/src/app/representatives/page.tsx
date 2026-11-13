'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  Users,
  Search,
  Award,
  MessageSquare,
  Landmark,
  ArrowRight,
  ShieldCheck,
  Bookmark,
  BookmarkCheck,
  Building,
  CheckCircle2,
  HelpCircle
} from 'lucide-react';
import { Representative } from '../../lib/types';
import { fetchRepresentatives } from '../../lib/api';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';
import { useSavedCivicItems } from '../../lib/useSavedCivicItems';
import { useLanguage } from '../../lib/LanguageContext';

const TN_DISTRICTS = [
  'All Districts',
  'Chennai',
  'Coimbatore',
  'Madurai',
  'Tiruchirappalli',
  'Salem',
  'Tirunelveli',
  'Erode',
  'Vellore',
  'Thanjavur',
  'Chengalpattu',
  'Kanchipuram',
  'Tiruvallur',
  'Dindigul',
  'Cuddalore',
  'Kanyakumari'
];

export default function RepresentativesPage() {
  const { language } = useLanguage();
  const { isSaved, saveRecord, removeRecord } = useSavedCivicItems();
  const [reps, setReps] = useState<Representative[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedParty, setSelectedParty] = useState('ALL');
  const [selectedAttendance, setSelectedAttendance] = useState('ALL');
  const [selectedDistrict, setSelectedDistrict] = useState('All Districts');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const party = sp.get('party');
      const att = sp.get('attendance');
      const dist = sp.get('district');
      if (q) setSearch(q);
      if (party) setSelectedParty(party);
      if (att) setSelectedAttendance(att);
      if (dist) setSelectedDistrict(dist);
    }
  }, []);

  const updateUrl = (q: string, party: string, att: string, dist: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (party && party !== 'ALL') url.searchParams.set('party', party); else url.searchParams.delete('party');
    if (att && att !== 'ALL') url.searchParams.set('attendance', att); else url.searchParams.delete('attendance');
    if (dist && dist !== 'All Districts') url.searchParams.set('district', dist); else url.searchParams.delete('district');
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
    updateUrl(q, selectedParty, selectedAttendance, selectedDistrict);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let p = selectedParty;
    let a = selectedAttendance;
    let d = selectedDistrict;

    if (groupId === 'party') {
      p = val;
      setSelectedParty(val);
    } else if (groupId === 'attendance') {
      a = val;
      setSelectedAttendance(val);
    } else if (groupId === 'district') {
      d = val;
      setSelectedDistrict(val);
    }

    updateUrl(search, p, a, d);
  };

  const handleClearAll = () => {
    setSearch('');
    setSelectedParty('ALL');
    setSelectedAttendance('ALL');
    setSelectedDistrict('All Districts');
    updateUrl('', 'ALL', 'ALL', 'All Districts');
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
      if (selectedDistrict !== 'All Districts') {
        const d = selectedDistrict.toLowerCase();
        const inConstituency = r.constituency?.toLowerCase().includes(d);
        if (!inConstituency) return false;
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
  }, [reps, selectedParty, selectedAttendance, selectedDistrict, search]);

  const filterGroups: FilterGroup[] = [
    {
      id: 'party',
      label: language === 'ta' ? 'அரசியல் கட்சி' : 'Political Party',
      value: selectedParty,
      options: parties.map((p) => ({ label: p, value: p }))
    },
    {
      id: 'attendance',
      label: language === 'ta' ? 'சட்டசபை வருகை' : 'Assembly Attendance',
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
        title={language === 'ta' ? 'சட்டமன்ற உறுப்பினர்கள் (234 எம்.எல்.ஏ-க்கள்)' : 'Elected Representatives (234 MLAs)'}
        description={
          language === 'ta'
            ? 'உங்கள் தொகுதி சட்டமன்ற உறுப்பினர் யார், அவர்களின் சட்டசபை வருகை மற்றும் தொகுதி மேம்பாட்டு நிதி (₹3 கோடி/ஆண்டு) எவ்வாறு செலவிடப்பட்டுள்ளது என்பதை அறியுங்கள்.'
            : 'Find your local Member of Legislative Assembly (MLA) in Tamil Nadu. Review assembly attendance, constituency questions raised, and local MLA Constituency Development Scheme (MLACDS) fund execution.'
        }
        breadcrumbs={[{ label: language === 'ta' ? 'சட்டமன்ற உறுப்பினர்கள்' : 'Representatives' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {language === 'ta' ? 'தமிழ்நாடு சட்டசபை (16வது சட்டமன்றம்)' : '16th Tamil Nadu Legislative Assembly'}
          </span>
        }
      />

      {/* Citizen Explainer Card for MLACDS */}
      <div className="p-4 rounded-2xl bg-gradient-to-r from-blue-950/40 via-indigo-950/30 to-purple-950/40 border border-blue-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-slate-300">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-blue-500/20 text-blue-400 shrink-0">
            <Building className="w-4 h-4" />
          </div>
          <div>
            <strong className="text-white block font-semibold">
              {language === 'ta' ? 'தொகுதி மேம்பாட்டு நிதி (MLACDS) என்றால் என்ன?' : 'How Does Local MLA Funding (MLACDS) Work?'}
            </strong>
            <span>
              {language === 'ta'
                ? 'தமிழ்நாட்டின் ஒவ்வொரு எம்.எல்.ஏ-வுக்கும் ஆண்டுக்கு ₹3 கோடி நிதி குடிநீர், பள்ளி பழுது, தெருவிளக்கு போன்ற உள்ளூர் பணிகளுக்கு ஒதுக்கப்படுகிறது.'
                : 'Every MLA in Tamil Nadu is statutorily allocated ₹3.0 Crore each year for local essentials like drinking water, school repairs, and streetlights.'}
            </span>
          </div>
        </div>
      </div>

      {/* Quick District Selector Bar */}
      <div className="space-y-1.5">
        <label className="text-xs font-medium text-slate-400 block">
          {language === 'ta' ? 'மாவட்டம் வாரியாக தேர்ந்தெடுக்கவும்:' : 'Quick Filter by District / Region:'}
        </label>
        <div className="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar">
          {TN_DISTRICTS.map((dist) => (
            <button
              key={dist}
              type="button"
              onClick={() => handleFilterChange('district', dist)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedDistrict === dist
                  ? 'bg-cyan-500/25 border-cyan-400 text-cyan-200 border shadow-sm font-bold'
                  : 'bg-white/[0.03] border-white/[0.08] text-slate-300 hover:text-white hover:bg-white/[0.06] border'
              }`}
            >
              {dist}
            </button>
          ))}
        </div>
      </div>

      {/* Simplified Filter Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search by MLA name, constituency (e.g. Kolathur, Edappadi, Chepauk), or party..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={reps.length}
        filteredResults={filtered.length}
        resultNoun="representatives"
      />

      {/* Grid of MLA cards */}
      {loading ? (
        <CivicStateNotice
          state="loading"
          title="Loading MLA Assembly Records..."
          description="Retrieving assembly attendance, constituency questions, and MLACDS fund allocations."
        />
      ) : filtered.length === 0 ? (
        <CivicStateNotice
          state="no_matching_results"
          title="No Representatives Match Your Filters"
          description="No elected MLAs match the chosen district, party, or attendance filters. Try choosing 'All Districts' or clearing search."
          onClearFilters={handleClearAll}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((rep) => {
            const isDmk = rep.party === 'DMK';
            const isAiadmk = rep.party === 'AIADMK';
            const partyBadge = isDmk
              ? 'bg-rose-500/15 text-rose-300 border-rose-500/30'
              : isAiadmk
              ? 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30'
              : 'bg-amber-500/15 text-amber-300 border-amber-500/30';

            const mlacdsAllocated = rep.mlacds_allocated || 3.0;
            const mlacdsSpent = rep.mlacds_utilized ?? 2.4;
            const utilizationPct = ((mlacdsSpent / mlacdsAllocated) * 100).toFixed(0);
            const saved = isSaved('representative', rep.id);

            return (
              <div
                key={rep.id}
                className="civic-card p-5 space-y-4 flex flex-col justify-between group transition-all duration-300"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <h3 className="font-bold text-base text-white group-hover:text-cyan-300 transition-colors">
                        {rep.name}
                      </h3>
                      <p className="text-xs text-slate-400">
                        Constituency: <strong className="text-white font-semibold">{rep.constituency}</strong>
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${partyBadge}`}>
                        {rep.party}
                      </span>
                      {/* Save MLA button */}
                      <button
                        type="button"
                        onClick={() => {
                          if (saved) {
                            removeRecord('representative', rep.id);
                          } else {
                            saveRecord({
                              record_type: 'representative',
                              record_id: rep.id,
                              title: `${rep.name} (${rep.constituency})`,
                              detail_url: `/representatives/${rep.id}`,
                              current_status: rep.party
                            });
                          }
                        }}
                        className={`p-1 rounded-lg border transition-all ${
                          saved
                            ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                            : 'bg-white/[0.04] text-slate-400 hover:text-white border-white/[0.08]'
                        }`}
                        title={saved ? 'Remove Bookmark' : 'Save MLA'}
                      >
                        {saved ? <BookmarkCheck className="w-3.5 h-3.5 text-cyan-400" /> : <Bookmark className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2.5 rounded-xl bg-slate-950/70 border border-white/5 space-y-0.5">
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">Assembly Attendance</span>
                      <span className="font-bold text-white text-sm font-mono">{rep.attendance_percentage}%</span>
                    </div>
                    <div className="p-2.5 rounded-xl bg-slate-950/70 border border-white/5 space-y-0.5">
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">Questions Raised</span>
                      <span className="font-bold text-cyan-400 text-sm font-mono">{rep.questions_raised}</span>
                    </div>
                  </div>

                  {/* MLACDS Spending */}
                  <div className="p-3 rounded-xl bg-slate-950/70 border border-white/5 text-xs space-y-1.5">
                    <div className="flex justify-between items-center text-[11px]">
                      <span className="text-slate-400 font-semibold uppercase text-[10px]">Local Funds Spent:</span>
                      <span className="font-bold text-emerald-400 font-mono">
                        ₹{mlacdsSpent.toFixed(2)} Cr / ₹{mlacdsAllocated.toFixed(1)} Cr ({utilizationPct}%)
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-emerald-500 to-cyan-400 h-full rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(Number(utilizationPct), 100)}%` }}
                      />
                    </div>
                  </div>
                </div>

                <div className="pt-2 flex items-center justify-between border-t border-white/5 text-xs">
                  <span className="text-[10px] text-slate-500 font-mono">
                    Assembly 2021–2026
                  </span>

                  <Link
                    href={`/representatives/${rep.id}`}
                    className="inline-flex items-center gap-1 font-semibold text-xs text-cyan-400 hover:text-cyan-300 group-hover:translate-x-0.5 transition-all"
                  >
                    <span>View Works Profile</span>
                    <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
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
