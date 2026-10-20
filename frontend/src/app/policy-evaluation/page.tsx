'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  TrendingUp,
  ShieldCheck,
  FileText,
  Download,
  Award,
  CheckCircle2,
  ArrowRight,
  Scale
} from 'lucide-react';
import { PolicyEvaluation } from '../../lib/types';
import { fetchPolicyEvaluations } from '../../lib/api';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';

export default function PolicyEvaluationPage() {
  const [policies, setPolicies] = useState<PolicyEvaluation[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedSector, setSelectedSector] = useState('ALL');
  const [selectedYear, setSelectedYear] = useState('ALL');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const sec = sp.get('sector');
      const yr = sp.get('year');
      if (q) setSearch(q);
      if (sec) setSelectedSector(sec);
      if (yr) setSelectedYear(yr);
    }
  }, []);

  const updateUrl = (q: string, sec: string, yr: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (sec && sec !== 'ALL') url.searchParams.set('sector', sec); else url.searchParams.delete('sector');
    if (yr && yr !== 'ALL') url.searchParams.set('year', yr); else url.searchParams.delete('year');
    window.history.replaceState({}, '', url.toString());
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchPolicyEvaluations();
      setPolicies(data);
      setLoading(false);
    }
    load();
  }, []);

  const sectors = useMemo(() => {
    const set = new Set<string>();
    policies.forEach((p) => {
      if (p.target_sector) set.add(p.target_sector);
    });
    return Array.from(set).sort();
  }, [policies]);

  const years = useMemo(() => {
    const set = new Set<string>();
    policies.forEach((p) => {
      if (p.launch_year) set.add(String(p.launch_year));
    });
    return Array.from(set).sort((a, b) => Number(b) - Number(a));
  }, [policies]);

  const handleSearchChange = (q: string) => {
    setSearch(q);
    updateUrl(q, selectedSector, selectedYear);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let s = selectedSector;
    let y = selectedYear;

    if (groupId === 'sector') {
      s = val;
      setSelectedSector(val);
    } else if (groupId === 'year') {
      y = val;
      setSelectedYear(val);
    }

    updateUrl(search, s, y);
  };

  const handleClearAll = () => {
    setSearch('');
    setSelectedSector('ALL');
    setSelectedYear('ALL');
    updateUrl('', 'ALL', 'ALL');
  };

  const filtered = useMemo(() => {
    return policies.filter((p) => {
      if (selectedSector !== 'ALL' && p.target_sector !== selectedSector) return false;
      if (selectedYear !== 'ALL' && String(p.launch_year) !== selectedYear) return false;
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          p.policy_name.toLowerCase().includes(q) ||
          p.target_sector.toLowerCase().includes(q) ||
          p.outcome_summary.toLowerCase().includes(q) ||
          p.baseline_status.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [policies, selectedSector, selectedYear, search]);

  const filterGroups: FilterGroup[] = [
    {
      id: 'sector',
      label: 'Target Sector',
      value: selectedSector,
      options: sectors.map((s) => ({ label: s, value: s }))
    },
    {
      id: 'year',
      label: 'Launch Year',
      value: selectedYear,
      isAdvanced: true,
      options: years.map((y) => ({ label: y, value: y }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Policy Results"
        description="Did major Tamil Nadu government programs achieve their intended outcomes? Review audited beneficiary counts, actual budget expenditure, and evaluation study findings with strict non-causal epistemic discipline."
        breadcrumbs={[{ label: 'Policy Results' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
            Public Impact Report Card
          </span>
        }
        actions={
          <button
            onClick={() => alert('Exporting complete Policy Evaluation Dossier (JSON/MD)...')}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/30 transition-all"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Audit Dossier</span>
          </button>
        }
      />

      {/* Simplified Filter Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search policy evaluations by program name, sector, or outcome keywords..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={policies.length}
        filteredResults={filtered.length}
        resultNoun="policy evaluations"
      />

      {/* Policy Dossiers List */}
      {loading ? (
        <CivicStateNotice
          state="loading"
          title="Loading Policy Outcome Evaluations..."
          description="Retrieving empirical State Planning Commission evaluations and audited beneficiary metrics."
        />
      ) : filtered.length === 0 ? (
        <CivicStateNotice
          state="no_matching_results"
          title="No Policy Evaluations Found"
          description="No outcome evaluations matched the selected sector or launch year."
          onClearFilters={handleClearAll}
        />
      ) : (
        <div className="space-y-6">
          {filtered.map((p) => (
            <div
              key={p.id}
              className="rounded-3xl bg-slate-900/80 border border-slate-800 p-6 md:p-8 space-y-6 shadow-2xl backdrop-blur-md"
            >
              {/* Header row */}
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-4">
                <div>
                  <span className="text-xs text-blue-400 font-semibold block mb-1">
                    Sector: {p.target_sector} • Launched {p.launch_year}
                  </span>
                  <h2 className="text-xl font-extrabold text-white">{p.policy_name}</h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                    Beneficiaries: {p.beneficiaries_count}
                  </span>
                </div>
              </div>

              {/* Financial Appropriations Bar with clear BE vs RE vs AE labels */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Budget Estimate (BE)
                    </span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">Planned</span>
                  </div>
                  <span className="text-xl font-bold text-white font-mono">
                    ₹{p.allocated_funds_cr.toLocaleString()} Cr
                  </span>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Revised Estimate (RE)
                    </span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300">Mid-Year</span>
                  </div>
                  <span className="text-xl font-bold text-indigo-400 font-mono">
                    ₹{p.re_allocation_cr.toLocaleString()} Cr
                  </span>
                </div>
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                  <div className="flex justify-between items-center mb-1">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Actual Disbursement (AE)
                    </span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300">Audited</span>
                  </div>
                  <span className="text-xl font-bold text-emerald-400 font-mono">
                    ₹{p.actual_spent_cr.toLocaleString()} Cr
                  </span>
                </div>
              </div>

              {/* Indicator & Baseline Assessment */}
              <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Zero-Baseline Epistemic Guardrail Protected</span>
                </div>
                <p className="text-xs text-slate-300 leading-relaxed font-mono">
                  {p.baseline_status}
                </p>
              </div>

              {/* Findings & Evidence */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                  Auditor Finding & Empirical Outcome Summary
                </h4>
                <p className="text-xs md:text-sm text-slate-200 leading-relaxed bg-slate-950 p-4 rounded-2xl border border-slate-800">
                  {p.outcome_summary}
                </p>
              </div>

              {/* Sources & Action */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-semibold text-slate-400">Empirical Sources:</span>
                  {p.evidence_links && p.evidence_links.map((link, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-blue-400 font-medium"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>{link}</span>
                    </span>
                  ))}
                </div>

                <Link
                  href={`/policy-evaluation/${p.id}`}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-600/20 text-blue-300 border border-blue-500/30 hover:bg-blue-600/30 transition-all ml-auto"
                >
                  <span>View Evaluation Dossier</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
