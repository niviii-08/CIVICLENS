'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  FileText,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  AlertCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  GitBranch,
  CheckCircle2,
  Lock,
  Layers,
  Sparkles,
  BookOpen,
  Info,
  Calendar,
  Building2,
  Hash,
  Scale
} from 'lucide-react';
import {
  EvidenceDossier,
  EvidenceItem,
  EvidenceState
} from '../lib/types';
import { fetchRecordEvidence } from '../lib/api';

interface EvidencePanelProps {
  dossier?: EvidenceDossier | null;
  recordId?: string;
  recordType?: string;
  title?: string;
  className?: string;
}

export function EvidencePanel({
  dossier: initialDossier,
  recordId,
  recordType = 'scheme',
  title = 'Sources and Evidence Explorer',
  className = ''
}: EvidencePanelProps) {
  const [dossier, setDossier] = useState<EvidenceDossier | null>(initialDossier || null);
  const [loading, setLoading] = useState<boolean>(!initialDossier && !!recordId);
  const [activeTab, setActiveTab] = useState<'all' | 'supporting' | 'conflicting' | 'contextual'>('all');
  const [technicalView, setTechnicalView] = useState<boolean>(false);
  const [showPrinciples, setShowPrinciples] = useState<boolean>(false);
  const [expandedOfflineDoc, setExpandedOfflineDoc] = useState<string | null>(null);

  useEffect(() => {
    if (initialDossier) {
      setDossier(initialDossier);
      setLoading(false);
      return;
    }

    if (recordId) {
      let isMounted = true;
      setLoading(true);
      fetchRecordEvidence(recordType, recordId).then((data) => {
        if (isMounted) {
          setDossier(data);
          setLoading(false);
        }
      }).catch(() => {
        if (isMounted) setLoading(false);
      });

      return () => {
        isMounted = false;
      };
    }
  }, [initialDossier, recordId, recordType]);

  if (loading) {
    return (
      <div className="p-8 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4 animate-pulse">
        <div className="h-5 w-48 bg-slate-800 rounded-md" />
        <div className="h-12 w-full bg-slate-950/80 rounded-2xl" />
        <div className="h-32 w-full bg-slate-950/50 rounded-2xl" />
      </div>
    );
  }

  if (!dossier) {
    return (
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 text-xs text-slate-400 flex items-center gap-3">
        <Info className="w-5 h-5 text-amber-400 shrink-0" />
        <div>
          <strong className="text-white block font-semibold mb-0.5">Evidence Pending Official Collation</strong>
          <p>
            Primary gazette notifications and official citations for this record are scheduled for routine statutory reconciliation.
          </p>
        </div>
      </div>
    );
  }

  const supporting = dossier.supporting_evidence || [];
  const conflicting = dossier.conflicting_evidence || [];
  const contextual = dossier.contextual_evidence || [];
  const totalCount = supporting.length + conflicting.length + contextual.length;

  const displayedDocs =
    activeTab === 'supporting'
      ? supporting
      : activeTab === 'conflicting'
      ? conflicting
      : activeTab === 'contextual'
      ? contextual
      : [...supporting, ...conflicting, ...contextual];

  return (
    <div className={`space-y-6 ${className}`}>
      {/* 1. Header & Evidence State Badge */}
      <div className="rounded-3xl bg-slate-900/90 border border-slate-800 p-6 sm:p-7 space-y-6 shadow-2xl relative backdrop-blur-md">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-400" />
              <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                {title}
              </h2>
            </div>
            <p className="text-xs text-slate-400">
              Verifiable public provenance, primary government orders, and epistemic audit trail
            </p>
          </div>

          {/* Citizen vs Technical View Toggle */}
          <div className="flex items-center gap-2 self-start sm:self-auto">
            <button
              type="button"
              onClick={() => setTechnicalView(!technicalView)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all flex items-center gap-1.5 ${
                technicalView
                  ? 'bg-blue-600/20 text-blue-300 border-blue-500/40 shadow-sm'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white'
              }`}
            >
              <Hash className="w-3.5 h-3.5" />
              <span>{technicalView ? 'Technical Audit Mode' : 'Citizen View'}</span>
            </button>

            {dossier.graph_node_id && (
              <Link
                href={`/graph?node=${encodeURIComponent(dossier.graph_node_id)}`}
                className="px-3 py-1.5 rounded-xl text-xs font-semibold bg-purple-500/10 text-purple-300 border border-purple-500/20 hover:bg-purple-500/20 transition-all flex items-center gap-1.5"
                title="View in Multi-hop Evidence Graph"
              >
                <GitBranch className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Graph Explorer</span>
              </Link>
            )}
          </div>
        </div>

        {/* 2. Five Distinct Evidence States Badge & Explanation */}
        <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/90 space-y-3">
          <div className="flex flex-wrap items-center justify-between gap-2.5">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider">
              Verification Status
            </span>
            <EvidenceStatePill state={dossier.evidence_state} label={dossier.evidence_state_label} />
          </div>

          {/* Citizen Plain Summary */}
          <div className="space-y-1.5 pt-1">
            <span className="text-xs font-semibold text-slate-300 block">
              Finding / Statement Under Review:
            </span>
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 text-xs sm:text-sm text-slate-200 font-medium leading-relaxed">
              "{dossier.statement_explained}"
            </div>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed pt-1">
              <strong className="text-white">What the records show: </strong>
              {dossier.plain_summary}
            </p>
          </div>
        </div>

        {/* 3. Epistemic Principles Disclaimer (Accordion) */}
        <div className="rounded-2xl border border-slate-800/80 bg-slate-950/60 overflow-hidden">
          <button
            type="button"
            onClick={() => setShowPrinciples(!showPrinciples)}
            className="w-full px-4 py-3 text-left flex items-center justify-between gap-2 text-xs font-semibold text-slate-300 hover:text-white transition-colors"
          >
            <div className="flex items-center gap-2">
              <Scale className="w-4 h-4 text-amber-400" />
              <span>CivicLens TN Evidence Standards & Epistemic Principles</span>
            </div>
            {showPrinciples ? (
              <ChevronUp className="w-4 h-4 text-slate-400" />
            ) : (
              <ChevronDown className="w-4 h-4 text-slate-400" />
            )}
          </button>

          {showPrinciples && (
            <div className="px-4 pb-4 pt-1 space-y-3 border-t border-slate-800 text-xs text-slate-300">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-2">
                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                  <div className="flex items-center gap-1.5 text-blue-400 font-bold text-[11px]">
                    <Layers className="w-3.5 h-3.5" />
                    <span>Statutory Provenance Over Volume</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    A statement repeated across 10 media articles is not stronger than one primary State Gazette order (G.O.) or CAG audit. Legal provenance dictates evidence weight.
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                  <div className="flex items-center gap-1.5 text-amber-400 font-bold text-[11px]">
                    <HelpCircle className="w-3.5 h-3.5" />
                    <span>Absence ≠ Statement Falsehood</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    The absence of an online digital PDF does not mean an event did not occur. Pre-digital archives and department files reside in physical government record rooms.
                  </p>
                </div>

                <div className="p-3 rounded-xl bg-slate-900/70 border border-slate-800 space-y-1">
                  <div className="flex items-center gap-1.5 text-purple-400 font-bold text-[11px]">
                    <GitBranch className="w-3.5 h-3.5" />
                    <span>Correlation ≠ Direct Policy Causation</span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    Macro indicators (e.g. maternal mortality, local literacy) cannot be uncritically attributed to a single scheme or MLA without econometric difference-in-difference controls.
                  </p>
                </div>
              </div>

              {dossier.limitations && dossier.limitations.length > 0 && (
                <div className="p-3 rounded-xl bg-amber-500/5 border border-amber-500/20 space-y-1.5">
                  <span className="text-[11px] font-bold text-amber-400 block uppercase tracking-wider">
                    Specific Data & Verification Limitations for this Record:
                  </span>
                  <ul className="list-disc list-inside space-y-1 text-[11px] text-slate-300">
                    {dossier.limitations.map((lim, idx) => (
                      <li key={idx}>{lim}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* 4. Tabs: Filter by Relationship */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-800/80">
          <button
            type="button"
            onClick={() => setActiveTab('all')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              activeTab === 'all'
                ? 'bg-blue-600 text-white shadow-md'
                : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            All Evidence ({totalCount})
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('supporting')}
            className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
              activeTab === 'supporting'
                ? 'bg-emerald-600 text-white shadow-md'
                : 'bg-slate-950 text-emerald-400/90 hover:text-emerald-300 border border-slate-800'
            }`}
          >
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Supporting ({supporting.length})</span>
          </button>

          {conflicting.length > 0 && (
            <button
              type="button"
              onClick={() => setActiveTab('conflicting')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'conflicting'
                  ? 'bg-amber-600 text-white shadow-md animate-pulse'
                  : 'bg-amber-500/10 text-amber-300 hover:text-amber-200 border border-amber-500/30'
              }`}
            >
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>Conflicting / Challenges ({conflicting.length})</span>
            </button>
          )}

          {contextual.length > 0 && (
            <button
              type="button"
              onClick={() => setActiveTab('contextual')}
              className={`px-3.5 py-1.5 rounded-xl text-xs font-semibold transition-all flex items-center gap-1.5 ${
                activeTab === 'contextual'
                  ? 'bg-indigo-600 text-white shadow-md'
                  : 'bg-slate-950 text-slate-400 hover:text-white border border-slate-800'
              }`}
            >
              <Info className="w-3.5 h-3.5" />
              <span>Context & Response ({contextual.length})</span>
            </button>
          )}
        </div>

        {/* 5. Document Cards List */}
        <div className="space-y-3.5">
          {displayedDocs.length === 0 ? (
            <div className="p-6 rounded-2xl bg-slate-950/60 border border-slate-800/80 text-center text-xs text-slate-400">
              No evidence documents found in this filter category.
            </div>
          ) : (
            displayedDocs.map((item) => (
              <DocumentEvidenceCard
                key={item.id}
                item={item}
                technicalView={technicalView}
                isExpandedOffline={expandedOfflineDoc === item.id}
                onToggleOffline={() =>
                  setExpandedOfflineDoc(expandedOfflineDoc === item.id ? null : item.id)
                }
              />
            ))
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Single Document Citation Card
 */
function DocumentEvidenceCard({
  item,
  technicalView,
  isExpandedOffline,
  onToggleOffline
}: {
  item: EvidenceItem;
  technicalView: boolean;
  isExpandedOffline: boolean;
  onToggleOffline: () => void;
}) {
  return (
    <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 hover:border-slate-700 transition-all space-y-3.5 shadow-md">
      {/* Top badges */}
      <div className="flex flex-wrap items-center justify-between gap-2.5">
        <div className="flex flex-wrap items-center gap-2">
          {/* Relationship badge */}
          <RelationshipPill type={item.relationship_type || item.relationship} />
          {/* Source Tier Badge */}
          <SourceTierPill tier={item.source_tier} />
        </div>

        {/* Date and period */}
        {(item.publication_date || item.reporting_period) && (
          <div className="flex items-center gap-1 text-[11px] text-slate-400">
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span>
              {item.publication_date || ''}
              {item.publication_date && item.reporting_period ? ' • ' : ''}
              {item.reporting_period || ''}
            </span>
          </div>
        )}
      </div>

      {/* Document Title & Issuing Org */}
      <div className="space-y-1">
        <h3 className="text-sm sm:text-base font-bold text-white leading-snug">
          {item.title}
        </h3>
        <div className="flex items-center gap-1.5 text-xs text-slate-400">
          <Building2 className="w-3.5 h-3.5 text-blue-400 shrink-0" />
          <span>
            Issuing Entity: <strong className="text-slate-200">{item.issuing_org}</strong>
          </span>
          {item.page_number && (
            <span className="text-slate-500 font-mono text-[11px]">
              ({item.page_number})
            </span>
          )}
        </div>
      </div>

      {/* Excerpt if present */}
      {item.excerpt && (
        <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 italic leading-relaxed border-l-2 border-l-blue-400">
          "{item.excerpt}"
        </div>
      )}

      {/* Technical Metadata Row (when in Technical Audit View) */}
      {technicalView && (
        <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 font-mono text-[11px] space-y-1.5 text-slate-400">
          <div className="flex flex-wrap justify-between gap-1">
            <span>Document ID: <strong className="text-slate-200">{item.id}</strong></span>
            <span>Statutory Official: <strong className={item.is_official ? 'text-emerald-400' : 'text-slate-400'}>{item.is_official ? 'True (State Org)' : 'False (Civic/Secondary)'}</strong></span>
          </div>
          {item.checksum && (
            <div className="text-[10px] break-all text-slate-500">
              SHA-256 Checksum: <span className="text-slate-300">{item.checksum}</span>
            </div>
          )}
        </div>
      )}

      {/* Action: Open Public Document OR Offline Assistance */}
      <div className="pt-2 flex flex-wrap items-center justify-between gap-3 border-t border-slate-800/80">
        <div className="text-[11px] text-slate-400">
          Status: {item.available ? (
            <span className="text-emerald-400 font-medium inline-flex items-center gap-1">
              <CheckCircle2 className="w-3 h-3" />
              Verified Public Digital Record
            </span>
          ) : (
            <span className="text-amber-400/90 font-medium inline-flex items-center gap-1">
              <HelpCircle className="w-3 h-3" />
              Physical Archive / Offline Record
            </span>
          )}
        </div>

        <div>
          {item.available && item.url ? (
            <a
              href={item.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold transition-colors shadow-sm"
            >
              <span>Open Public Document</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          ) : (
            <button
              type="button"
              onClick={onToggleOffline}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-amber-300 border border-amber-500/20 text-xs font-semibold transition-colors"
            >
              <span>How to Access Offline</span>
              {isExpandedOffline ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* Expandable Offline / Safe Alternative Explainer */}
      {isExpandedOffline && !item.available && (
        <div className="p-4 rounded-xl bg-amber-500/5 border border-amber-500/20 text-xs space-y-2.5 transition-all">
          <div className="flex items-center gap-2 text-amber-400 font-bold text-[11px]">
            <BookOpen className="w-4 h-4" />
            <span>Citizen Physical & Alternative Record Access Guide</span>
          </div>

          <p className="text-slate-300 leading-relaxed">
            <strong className="text-white">Why is this document not directly downloadable? </strong>
            {item.offline_reason || 'This record is maintained in physical state secretariat or departmental archives and has not yet been digitized on public web portals.'}
          </p>

          <p className="text-slate-300 leading-relaxed">
            <strong className="text-white">How citizens can verify or inspect this record: </strong>
            {item.safe_alternative || 'Citizens may consult the issuing department secretariat library under the Tamil Nadu Public Records Act or submit an RTI query quoting the document reference number.'}
          </p>

          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-mono bg-slate-950 p-2.5 rounded-lg border border-slate-800">
            <Lock className="w-3 h-3 text-emerald-400" />
            <span>Civic Privacy Assurance: No internal server pathways, credentials, or private citizen submissions are exposed.</span>
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * 5 Evidence States Pill
 */
function EvidenceStatePill({ state, label }: { state: EvidenceState | string; label?: string }) {
  switch (state) {
    case 'EVIDENCE_AVAILABLE':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          <CheckCircle2 className="w-3.5 h-3.5" />
          <span>{label || 'Evidence Available'}</span>
        </span>
      );
    case 'EVIDENCE_CONFLICTS':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/30">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>{label || 'Conflicting Evidence Found'}</span>
        </span>
      );
    case 'INSUFFICIENT_EVIDENCE':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-purple-500/10 text-purple-400 border border-purple-500/20">
          <HelpCircle className="w-3.5 h-3.5" />
          <span>{label || 'Insufficient Evidence to Verify'}</span>
        </span>
      );
    case 'SOURCE_UNAVAILABLE':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
          <AlertCircle className="w-3.5 h-3.5" />
          <span>{label || 'Source Temporarily Unavailable'}</span>
        </span>
      );
    case 'ASSESSMENT_NOT_PERFORMED':
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-500/10 text-blue-400 border border-blue-500/20">
          <Info className="w-3.5 h-3.5" />
          <span>{label || 'Assessment Not Yet Performed'}</span>
        </span>
      );
    default:
      return (
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold bg-slate-800 text-slate-300 border border-slate-700">
          <Info className="w-3.5 h-3.5" />
          <span>{label || state}</span>
        </span>
      );
  }
}

/**
 * Document Relationship Pill
 */
function RelationshipPill({ type }: { type: string }) {
  const norm = (type || '').toLowerCase();

  if (norm.includes('support')) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
        <CheckCircle2 className="w-3 h-3" />
        <span>Supports this finding</span>
      </span>
    );
  }

  if (norm.includes('contradict') || norm.includes('challeng') || norm.includes('dispute')) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
        <AlertTriangle className="w-3 h-3" />
        <span>Challenges this finding</span>
      </span>
    );
  }

  if (norm.includes('respond') || norm.includes('answer')) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
        <ShieldCheck className="w-3 h-3" />
        <span>Records an official response</span>
      </span>
    );
  }

  if (norm.includes('outcome') || norm.includes('report') || norm.includes('evaluat')) {
    return (
      <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
        <Layers className="w-3 h-3" />
        <span>Reports an outcome</span>
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20">
      <Info className="w-3 h-3" />
      <span>Provides background</span>
    </span>
  );
}

/**
 * Source Provenance Tier Pill
 */
function SourceTierPill({ tier }: { tier?: string }) {
  const norm = (tier || '').toUpperCase();

  if (norm.includes('TIER_1') || norm.includes('STATUTORY')) {
    return (
      <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
        Tier 1: Statutory / Gazette
      </span>
    );
  }

  if (norm.includes('TIER_2') || norm.includes('OFFICIAL')) {
    return (
      <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
        Tier 2: Official Line Agency
      </span>
    );
  }

  if (norm.includes('TIER_3') || norm.includes('FACTCHECK') || norm.includes('AUDIT')) {
    return (
      <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
        Tier 3: Audit / Empirical Study
      </span>
    );
  }

  if (norm.includes('TIER_4') || norm.includes('SECONDARY')) {
    return (
      <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700">
        Tier 4: Secondary Civic / Media
      </span>
    );
  }

  return (
    <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
      Tier 5: Public Submission
    </span>
  );
}
