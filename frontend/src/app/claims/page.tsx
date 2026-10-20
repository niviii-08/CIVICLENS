'use client';

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  ShieldCheck,
  Search,
  CheckCircle2,
  AlertTriangle,
  FileText,
  ExternalLink,
  HelpCircle,
  Sparkles,
  Layers,
  ArrowRight
} from 'lucide-react';
import { ClaimVerification } from '../../lib/types';
import { fetchClaims } from '../../lib/api';
import { StatusBadge } from '../../components/StatusBadge';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';

export default function ClaimsPage() {
  const [claims, setClaims] = useState<ClaimVerification[]>([]);
  const [loading, setLoading] = useState(true);
  const [userQuery, setUserQuery] = useState('');
  const [selectedVerdict, setSelectedVerdict] = useState('ALL');
  const [selectedClaimant, setSelectedClaimant] = useState('ALL');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const v = sp.get('verdict');
      const c = sp.get('claimant');
      if (q) setUserQuery(q);
      if (v) setSelectedVerdict(v);
      if (c) setSelectedClaimant(c);
    }
  }, []);

  const updateUrl = (q: string, v: string, c: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (v && v !== 'ALL') url.searchParams.set('verdict', v); else url.searchParams.delete('verdict');
    if (c && c !== 'ALL') url.searchParams.set('claimant', c); else url.searchParams.delete('claimant');
    window.history.replaceState({}, '', url.toString());
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchClaims();
      setClaims(data);
      setLoading(false);
    }
    load();
  }, []);

  const claimants = useMemo(() => {
    const set = new Set<string>();
    claims.forEach((c) => {
      if (c.claimant) set.add(c.claimant);
    });
    return Array.from(set).sort();
  }, [claims]);

  const handleSearchChange = (q: string) => {
    setUserQuery(q);
    updateUrl(q, selectedVerdict, selectedClaimant);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let v = selectedVerdict;
    let c = selectedClaimant;

    if (groupId === 'verdict') {
      v = val;
      setSelectedVerdict(val);
    } else if (groupId === 'claimant') {
      c = val;
      setSelectedClaimant(val);
    }

    updateUrl(userQuery, v, c);
  };

  const handleClearAll = () => {
    setUserQuery('');
    setSelectedVerdict('ALL');
    setSelectedClaimant('ALL');
    updateUrl('', 'ALL', 'ALL');
  };

  const filteredClaims = useMemo(() => {
    return claims.filter((c) => {
      if (selectedVerdict !== 'ALL' && c.verdict !== selectedVerdict) return false;
      if (selectedClaimant !== 'ALL' && c.claimant !== selectedClaimant) return false;
      if (userQuery.trim()) {
        const q = userQuery.toLowerCase();
        return (
          c.claim_text.toLowerCase().includes(q) ||
          c.claimant?.toLowerCase().includes(q) ||
          c.explanation.toLowerCase().includes(q)
        );
      }
      return true;
    });
  }, [claims, selectedVerdict, selectedClaimant, userQuery]);

  const filterGroups: FilterGroup[] = [
    {
      id: 'verdict',
      label: 'Fact-Check Verdict',
      value: selectedVerdict,
      options: [
        { label: 'Evidence verified', value: 'Verified True' },
        { label: 'Conflicting information', value: 'Partially True' },
        { label: 'Contradicted by evidence', value: 'False' },
        { label: 'Not enough information', value: 'Misleading' }
      ]
    },
    {
      id: 'claimant',
      label: 'Claimant / Speaker',
      value: selectedClaimant,
      isAdvanced: true,
      options: claimants.map((c) => ({ label: c, value: c }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Verify Claims"
        description="Independent, evidence-based fact-checking of political speeches and government announcements. Every claim is cross-referenced with primary Government Orders (G.O.s), assembly debate records, and state audit disclosures."
        breadcrumbs={[{ label: 'Verify Claims' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Fact-Check & Verification
          </span>
        }
      />

      {/* Simplified Filter Bar */}
      <SimpleFilterBar
        searchQuery={userQuery}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search audited political claims, claimants, or policy keywords..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={claims.length}
        filteredResults={filteredClaims.length}
        resultNoun="claims verified"
      />

      {/* Claims List */}
      {loading ? (
        <CivicStateNotice
          state="loading"
          title="Loading Public Claim Fact-Checks..."
          description="Verifying claims against state assembly debates, budget documents, and Government Orders."
        />
      ) : filteredClaims.length === 0 ? (
        <CivicStateNotice
          state="no_matching_results"
          title="No Matching Claims Found"
          description="No fact-checked political claims matched the selected verdict or speaker criteria."
          onClearFilters={handleClearAll}
        />
      ) : (
        <div className="space-y-4">
          {filteredClaims.map((claim) => (
            <div
              key={claim.id}
              className="rounded-2xl bg-slate-900/70 border border-slate-800 p-6 space-y-4 shadow-lg hover:border-slate-700 transition-all"
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-xs text-slate-400">
                      Speaker: <strong className="text-white">{claim.claimant || 'Public Announcement'}</strong>
                    </span>
                    {claim.date_made && (
                      <span className="text-xs text-slate-500">• {claim.date_made}</span>
                    )}
                  </div>
                  <h3 className="font-bold text-base sm:text-lg text-white leading-snug">
                    "{claim.claim_text}"
                  </h3>
                </div>

                <div className="shrink-0 flex items-center gap-2">
                  <StatusBadge status={claim.verdict} isStatutoryVerified={claim.verdict === 'Verified True'} />
                </div>
              </div>

              {/* Citizen Explanation */}
              <div className="p-4 rounded-xl bg-slate-950 border border-slate-800/80 text-xs sm:text-sm text-slate-300 space-y-1 leading-relaxed">
                <strong className="text-slate-200 block text-xs uppercase tracking-wider font-semibold">
                  What the public evidence shows:
                </strong>
                <p>{claim.explanation}</p>
              </div>

              {/* Bottom Actions */}
              <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80 text-xs">
                <span className="text-slate-400 font-mono text-[11px]">
                  Audited with Primary Assembly & Gazette Records
                </span>

                <Link
                  href={`/claims/${claim.id}`}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold px-3 py-1.5 rounded-xl bg-blue-600/20 text-blue-300 border border-blue-500/30 hover:bg-blue-600/30 transition-all"
                >
                  <span>View Full Evidence Dossier</span>
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
