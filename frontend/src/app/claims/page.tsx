'use client';

import React, { useState, useEffect } from 'react';
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

export default function ClaimsPage() {
  const [claims, setClaims] = useState<ClaimVerification[]>([]);
  const [loading, setLoading] = useState(true);
  const [userQuery, setUserQuery] = useState('');
  const [selectedVerdict, setSelectedVerdict] = useState('ALL');

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchClaims();
      setClaims(data);
      setLoading(false);
    }
    load();
  }, []);

  const filteredClaims = claims.filter((c) => {
    if (selectedVerdict !== 'ALL' && c.verdict !== selectedVerdict) return false;
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

      {/* Filter and Search */}
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={userQuery}
            onChange={(e) => setUserQuery(e.target.value)}
            placeholder="Search audited political claims, claimants, or policy keywords..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-xs text-slate-400 font-semibold mr-1">Verdict:</span>
          {['ALL', 'Verified True', 'Partially True', 'Misleading', 'False'].map((verdict) => (
            <button
              key={verdict}
              onClick={() => setSelectedVerdict(verdict)}
              className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                selectedVerdict === verdict
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                  : 'bg-slate-950 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {verdict}
            </button>
          ))}
        </div>
      </div>

      {/* Claims List */}
      <div className="space-y-4">
        {filteredClaims.map((claim) => (
          <div
            key={claim.id}
            className="rounded-2xl bg-slate-900/70 border border-slate-800 p-6 space-y-4 shadow-lg hover:border-slate-700 transition-all"
          >
            {/* Top row */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className="font-mono text-xs font-bold text-blue-400">#{claim.id}</span>
                {claim.claimant && (
                  <span className="text-xs text-slate-400">
                    Source: <strong className="text-slate-200">{claim.claimant}</strong>
                  </span>
                )}
                {claim.date_made && (
                  <span className="text-[11px] text-slate-400">({claim.date_made})</span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  {claim.confidence_score}% Confidence
                </span>
                <StatusBadge status={claim.verdict} />
              </div>
            </div>

            {/* Statement text */}
            <blockquote className="border-l-2 border-blue-500 pl-4 py-1 text-sm md:text-base font-semibold text-white italic">
              "{claim.claim_text}"
            </blockquote>

            {/* Atomic Propositions */}
            {claim.atomic_propositions && claim.atomic_propositions.length > 0 && (
              <div className="space-y-2 pt-2">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                  <Layers className="w-3.5 h-3.5 text-blue-400" />
                  Atomic Proposition Breakdown
                </span>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {claim.atomic_propositions.map((prop) => (
                    <div
                      key={prop.id}
                      className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 text-xs flex flex-col justify-between gap-2"
                    >
                      <div className="flex items-start gap-2">
                        {prop.truth_value ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        ) : (
                          <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                        )}
                        <span className="text-slate-200 leading-relaxed font-medium">
                          {prop.statement}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400 font-mono">
                        Source: {prop.source}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Explanation & Reasoning */}
            <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800 text-xs text-slate-300 leading-relaxed">
              <strong className="text-white block mb-1">Auditor Finding & Epistemic Reasoning:</strong>
              {claim.explanation}
            </div>

            {/* Documentary Sources */}
              {claim.sources && claim.sources.length > 0 && (
                <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/60">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="text-[11px] font-semibold text-slate-400">Primary Gazettes:</span>
                    {claim.sources.map((s, idx) => (
                      <span
                        key={idx}
                        className="inline-flex items-center gap-1 text-[11px] px-2 py-0.5 rounded bg-slate-800 text-blue-400"
                      >
                        <FileText className="w-3 h-3" />
                        <span>{s}</span>
                      </span>
                    ))}
                  </div>

                  <Link
                    href={`/claims/${claim.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-400 hover:text-blue-300 transition-colors ml-auto pt-1 sm:pt-0"
                  >
                    <span>View Fact-Check Dossier</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              )}
            </div>
          ))}
      </div>
    </div>
  );
}
