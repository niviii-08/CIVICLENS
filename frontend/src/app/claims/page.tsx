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
  ArrowRight,
  Bookmark,
  BookmarkCheck
} from 'lucide-react';
import { ClaimVerification } from '../../lib/types';
import { fetchClaims } from '../../lib/api';
import { StatusBadge } from '../../components/StatusBadge';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';
import { CivicStateNotice } from '../../components/CivicStateNotice';
import { SpotlightCard } from '../../components/SpotlightCard';
import { useSavedCivicItems } from '../../lib/useSavedCivicItems';
import { useLanguage } from '../../lib/LanguageContext';

export default function ClaimsPage() {
  const { language } = useLanguage();
  const { isSaved, saveRecord, removeRecord } = useSavedCivicItems();
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
      label: language === 'ta' ? 'முடிவு' : 'Fact-Check Verdict',
      value: selectedVerdict,
      options: [
        { label: '🟢 Evidence verified (உண்மை)', value: 'Verified True' },
        { label: '🟡 Conflicting information (பகுதி உண்மை)', value: 'Partially True' },
        { label: '🔴 Contradicted by evidence (தவறு)', value: 'False' },
        { label: '⚠️ Misleading (தவறாக வழிநடத்துகிறது)', value: 'Misleading' }
      ]
    },
    {
      id: 'claimant',
      label: language === 'ta' ? 'அறிக்கை அளித்தவர்' : 'Claimant / Speaker',
      value: selectedClaimant,
      isAdvanced: true,
      options: claimants.map((c) => ({ label: c, value: c }))
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title={language === 'ta' ? 'அரசியல் கூற்றுகள் உண்மை சரிபார்ப்பு' : 'Verify Public Claims & Fact Checks'}
        description={
          language === 'ta'
            ? 'அரசியல் தலைவர்களின் பொதுக் கூட்ட உரைகள் மற்றும் சமூக வலைத்தளங்களில் பரவும் தகவல்கள் அரசாணைகள், இந்திய தணிக்கை அறிக்கை (CAG) மற்றும் சட்டசபை பதிவுகள் மூலம் நடுநிலையுடன் சரிபார்க்கப்படுகின்றன.'
            : 'Independent, evidence-based fact-checking of political speeches and government announcements. Every claim is cross-referenced with primary Government Orders (G.O.s), assembly debate records, and state audit disclosures.'
        }
        breadcrumbs={[{ label: language === 'ta' ? 'உண்மை சரிபார்ப்பு' : 'Verify Claims' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            {language === 'ta' ? 'ஆதாரபூர்வ தணிக்கை' : 'Fact-Check & Verification'}
          </span>
        }
      />

      {/* Quick Verdict Selector Pills */}
      <div className="flex flex-wrap items-center gap-2 pt-1">
        <span className="text-xs font-medium text-slate-400 mr-1">Filter by Verdict:</span>
        <button
          type="button"
          onClick={() => handleFilterChange('verdict', 'ALL')}
          className={`px-3 py-1.5 rounded-xl text-xs font-bold transition-all ${
            selectedVerdict === 'ALL'
              ? 'bg-white/20 text-white border border-white/30'
              : 'bg-white/[0.04] text-slate-300 border border-white/[0.08]'
          }`}
        >
          All Verdicts ({claims.length})
        </button>
        <button
          type="button"
          onClick={() => handleFilterChange('verdict', 'Verified True')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            selectedVerdict === 'Verified True'
              ? 'bg-emerald-500/25 text-emerald-200 border border-emerald-400 shadow-sm'
              : 'bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 hover:bg-emerald-500/15'
          }`}
        >
          <span>🟢 Verified True</span>
        </button>
        <button
          type="button"
          onClick={() => handleFilterChange('verdict', 'Partially True')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            selectedVerdict === 'Partially True'
              ? 'bg-amber-500/25 text-amber-200 border border-amber-400 shadow-sm'
              : 'bg-amber-500/10 text-amber-300 border border-amber-500/20 hover:bg-amber-500/15'
          }`}
        >
          <span>🟡 Partially True</span>
        </button>
        <button
          type="button"
          onClick={() => handleFilterChange('verdict', 'False')}
          className={`px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 ${
            selectedVerdict === 'False'
              ? 'bg-rose-500/25 text-rose-200 border border-rose-400 shadow-sm'
              : 'bg-rose-500/10 text-rose-300 border border-rose-500/20 hover:bg-rose-500/15'
          }`}
        >
          <span>🔴 False / Disputed</span>
        </button>
      </div>

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
          {filteredClaims.map((claim) => {
            const glowColor =
              claim.verdict === 'Verified True'
                ? 'rgba(16, 185, 129, 0.16)'
                : claim.verdict === 'Partially True'
                ? 'rgba(245, 158, 11, 0.16)'
                : claim.verdict === 'False'
                ? 'rgba(244, 63, 94, 0.16)'
                : 'rgba(168, 85, 247, 0.16)';

            const borderColor =
              claim.verdict === 'Verified True'
                ? 'rgba(16, 185, 129, 0.35)'
                : claim.verdict === 'Partially True'
                ? 'rgba(245, 158, 11, 0.35)'
                : claim.verdict === 'False'
                ? 'rgba(244, 63, 94, 0.35)'
                : 'rgba(168, 85, 247, 0.35)';

            const saved = isSaved('claim', claim.id);

            return (
              <SpotlightCard
                key={claim.id}
                spotlightColor={glowColor}
                borderColor={borderColor}
                className="p-6 space-y-4 group transition-all duration-300"
              >
                <div className="flex flex-col md:flex-row md:items-start justify-between gap-3">
                  <div className="space-y-2 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="text-xs text-slate-300 font-medium">
                        Speaker: <strong className="text-white font-bold">{claim.claimant || 'Public Announcement'}</strong>
                      </span>
                      {claim.date_made && (
                        <span className="text-xs text-cyan-400 font-mono">• {claim.date_made}</span>
                      )}
                      <span className="text-[10px] text-slate-500 font-mono">[Claim #{claim.id}]</span>
                    </div>
                    <h3 className="font-bold text-base sm:text-lg text-white leading-snug group-hover:text-cyan-300 transition-colors">
                      &ldquo;{claim.claim_text}&rdquo;
                    </h3>
                  </div>

                  <div className="shrink-0 flex items-center gap-2">
                    <StatusBadge status={claim.verdict} isStatutoryVerified={claim.verdict === 'Verified True'} />

                    {/* Bookmark Claim button */}
                    <button
                      type="button"
                      onClick={() => {
                        if (saved) {
                          removeRecord('claim', claim.id);
                        } else {
                          saveRecord({
                            record_type: 'claim',
                            record_id: claim.id,
                            title: `Claim by ${claim.claimant || 'Public'}: ${claim.claim_text.substring(0, 50)}...`,
                            detail_url: `/claims/${claim.id}`,
                            current_status: claim.verdict
                          });
                        }
                      }}
                      className={`p-1.5 rounded-xl border transition-all ${
                        saved
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                          : 'bg-white/[0.04] text-slate-400 hover:text-white border-white/[0.08]'
                      }`}
                      title={saved ? 'Remove Bookmark' : 'Save Fact-Check'}
                    >
                      {saved ? <BookmarkCheck className="w-4 h-4 text-cyan-400" /> : <Bookmark className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Citizen Explanation */}
                <div className="p-4 rounded-2xl bg-black/60 border border-white/[0.08] text-xs sm:text-sm text-slate-300 space-y-1.5 leading-relaxed backdrop-blur-md">
                  <strong className="text-cyan-300 block text-xs uppercase tracking-wider font-semibold">
                    What the public record &amp; audit evidence shows:
                  </strong>
                  <p>{claim.explanation}</p>
                </div>

                {/* Bottom Actions */}
                <div className="pt-3 flex flex-wrap items-center justify-between gap-3 border-t border-white/[0.08] text-xs">
                  <span className="text-slate-400 font-mono text-[11px] flex items-center gap-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Audited with Primary Assembly &amp; Gazette Records</span>
                  </span>

                  <Link
                    href={`/claims/${claim.id}`}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold px-3.5 py-1.5 rounded-xl bg-cyan-500/10 text-cyan-300 border border-cyan-500/25 hover:bg-cyan-500/20 transition-all group-hover:border-cyan-500/50 shadow-sm"
                  >
                    <span>View Evidence Dossier</span>
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
