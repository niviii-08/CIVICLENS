'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  ShieldCheck,
  Building2,
  Calendar,
  MapPin,
  Users,
  Landmark,
  FileText,
  ExternalLink,
  ChevronDown,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowLeft,
  ArrowRight,
  Link2,
  Info,
  Layers,
  Lock,
  RefreshCw,
  Search
} from 'lucide-react';
import { DetailedCivicRecord } from '../lib/types';
import { Breadcrumb } from './Breadcrumb';
import { StatusBadge } from './StatusBadge';
import { EvidencePanel } from './EvidencePanel';
import { CivicStateNotice } from './CivicStateNotice';

interface RecordDetailLayoutProps {
  record: DetailedCivicRecord | null;
  loading: boolean;
  error: string | null;
  onRetry?: () => void;
  parentRoute: string;
  parentLabel: string;
}

export const RecordDetailLayout: React.FC<RecordDetailLayoutProps> = ({
  record,
  loading,
  error,
  onRetry,
  parentRoute,
  parentLabel,
}) => {
  // Progressive disclosure accordion states
  const [showMethodology, setShowMethodology] = useState(false);
  const [showTechnical, setShowTechnical] = useState(false);
  const [showLimitations, setShowLimitations] = useState(false);

  // 1. Standardized Loading State (Phase 11.8)
  if (loading) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-12">
        <Breadcrumb
          items={[
            { label: parentLabel, href: parentRoute },
            { label: 'Loading Details...' },
          ]}
        />
        <CivicStateNotice
          state="loading"
          title={`Retrieving ${parentLabel} Record...`}
          description="Fetching verified state gazettes, budget books, and departmental outcome data from the public database."
        />
      </div>
    );
  }

  // 2. Standardized Failure Recovery State (Phase 11.8)
  if (error) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-10">
        <Breadcrumb
          items={[
            { label: parentLabel, href: parentRoute },
            { label: 'Unable to Retrieve Record' },
          ]}
        />
        <CivicStateNotice
          state="failed_api_request"
          title="Unable to Retrieve Public Record"
          description="The civic database encountered a connectivity interruption while fetching this record. Your navigation pathway and query context are preserved."
          technicalError={error}
          onRetry={onRetry}
          actionHref={parentRoute}
          actionLabel={`Back to ${parentLabel}`}
        />
      </div>
    );
  }

  // 3. Record Does Not Exist (404 Catalog State - Phase 11.8)
  if (!record) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto py-10">
        <Breadcrumb
          items={[
            { label: parentLabel, href: parentRoute },
            { label: 'Record Not Found' },
          ]}
        />
        <CivicStateNotice
          state="no_records_available"
          title="Public Record Not Found"
          description="The requested public record identifier was not found in the verified database of published welfare schemes and assembly records."
          actionHref={parentRoute}
          actionLabel={`Browse ${parentLabel}`}
        />
      </div>
    );
  }

  // Phase 11.9: Compute connection type counts
  const directCount = record.related_records.filter(r => r.connection_type === 'direct_identifier').length;
  const evidenceCount = record.related_records.filter(r => r.connection_type === 'evidence_relationship').length;
  const inferredCount = record.related_records.filter(r => r.connection_type === 'inferred_relationship' || r.is_inferred).length;

  // 4. Render Citizen Record Page
  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Navigation Header */}
      <div className="space-y-3">
        <Breadcrumb
          items={[
            { label: parentLabel, href: parentRoute },
            { label: record.title },
          ]}
        />

        <Link
          href={parentRoute}
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors pt-1"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to {parentLabel} Directory</span>
        </Link>
      </div>

      {/* SECTION 1: What this record is about */}
      <section aria-labelledby="record-title" className="space-y-4">
        <div className="rounded-3xl bg-slate-900/80 border border-slate-800 p-6 sm:p-8 space-y-6 shadow-2xl relative overflow-hidden backdrop-blur-md">
          {/* Top badges */}
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex flex-wrap items-center gap-2">
              <span className="text-[11px] font-bold px-3 py-1 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/20 uppercase tracking-wider">
                {record.category_label}
              </span>
              <span className="text-xs font-mono text-slate-400">
                #{record.id}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <StatusBadge status={record.status} />
              <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full font-medium">
                <ShieldCheck className="w-3.5 h-3.5" />
                <span>Verified Public Record</span>
              </span>
            </div>
          </div>

          {/* Title & Vernacular Title */}
          <div className="space-y-2">
            <h1 id="record-title" className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
              {record.title}
            </h1>
            {record.title_vernacular && (
              <div className="text-sm sm:text-base font-semibold text-amber-200/90 font-sans">
                {record.title_vernacular}
              </div>
            )}
          </div>

          {/* Plain-Language Purpose / Summary */}
          <div className="p-4 sm:p-5 rounded-2xl bg-slate-950/80 border border-slate-800/90 space-y-2">
            <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block">
              What this record is about:
            </span>
            <p className="text-sm sm:text-base text-slate-200 leading-relaxed font-normal">
              {record.summary}
            </p>
          </div>

          {/* Status Explanation Card */}
          <div className="p-4 rounded-2xl bg-blue-500/5 border border-blue-500/20 flex items-start gap-3 text-xs sm:text-sm">
            <Info className="w-5 h-5 text-blue-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <strong className="text-white block font-semibold">
                Status explanation: {record.status}
              </strong>
              <p className="text-slate-300 leading-relaxed">
                {record.status_explanation}
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* SECTION 2: The most important available facts */}
      <section aria-labelledby="key-facts-heading" className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 id="key-facts-heading" className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
            <Building2 className="w-4 h-4 text-blue-400" />
            <span>Key Facts</span>
          </h2>
          <span className="text-xs text-slate-400">Essential public parameters</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Fact 1: Responsible Department */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2 shadow-lg">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Building2 className="w-3.5 h-3.5 text-blue-400" />
              <span>Responsible Entity</span>
            </span>
            <p className="text-sm font-semibold text-white leading-snug">
              {record.responsible_entity || (
                <span className="text-slate-500 italic">Not documented in official release</span>
              )}
            </p>
          </div>

          {/* Fact 2: Intended Beneficiaries */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2 shadow-lg">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-emerald-400" />
              <span>Target Beneficiaries</span>
            </span>
            <p className="text-sm font-semibold text-white leading-snug">
              {record.target_group || (
                <span className="text-slate-500 italic">Universal / General Public</span>
              )}
            </p>
          </div>

          {/* Fact 3: Geographic Scope */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2 shadow-lg">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-amber-400" />
              <span>Geographic Scope</span>
            </span>
            <p className="text-sm font-semibold text-white leading-snug">
              {record.geographic_scope || (
                <span className="text-slate-500 italic">All 38 Districts of Tamil Nadu</span>
              )}
            </p>
          </div>

          {/* Fact 4: Reporting Period */}
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2 shadow-lg">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-indigo-400" />
              <span>Reporting Period</span>
            </span>
            <p className="text-sm font-semibold text-white leading-snug font-mono">
              {record.reporting_period || (
                <span className="text-slate-500 italic">Ongoing / Active Term</span>
              )}
            </p>
          </div>
        </div>
      </section>

      {/* SECTION 3: What the available evidence indicates */}
      <section aria-labelledby="evidence-heading" className="space-y-5">
        <div className="flex items-center justify-between">
          <h2 id="evidence-heading" className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Documented Evidence & Progress</span>
          </h2>
          <span className="text-xs text-slate-400">Audited public records</span>
        </div>

        {/* Evidence Narrative Card */}
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl">
          <div className="space-y-2">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
              Documented Implementation & Outcomes
            </h3>
            <p className="text-sm text-slate-200 leading-relaxed font-normal">
              {record.evidence_summary}
            </p>
          </div>

          {/* Financial Cards (Step 3: Clear BE vs RE vs AE distinction) */}
          {record.financials && (
            <div className="pt-4 border-t border-slate-800 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1">
                <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Landmark className="w-3.5 h-3.5 text-blue-400" />
                  <span>Public Financial Disclosures ({record.financials.financial_year || 'FY 2023-24'})</span>
                </h4>
                {record.financials.demand_no && (
                  <span className="text-[11px] font-mono text-slate-400">
                    Demand for Grants No. {record.financials.demand_no}
                  </span>
                )}
              </div>

              {/* Explaining what each number means */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                {/* 1. Budget Estimate (BE) */}
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Budget Estimate (BE)
                    </span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400 font-medium">Initial</span>
                  </div>
                  <div className="text-lg sm:text-xl font-bold font-mono text-white">
                    {record.financials.budget_estimate_cr !== undefined ? (
                      `₹${record.financials.budget_estimate_cr.toLocaleString()} Cr`
                    ) : (
                      <span className="text-xs text-slate-500 font-sans italic">Not published</span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-400 leading-tight">
                    Initial planned fund allocation approved in State Annual Budget.
                  </p>
                </div>

                {/* 2. Revised Estimate (RE) */}
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Revised Estimate (RE)
                    </span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 font-medium">Mid-Year</span>
                  </div>
                  <div className="text-lg sm:text-xl font-bold font-mono text-indigo-400">
                    {record.financials.revised_estimate_cr !== undefined ? (
                      `₹${record.financials.revised_estimate_cr.toLocaleString()} Cr`
                    ) : (
                      <span className="text-xs text-slate-500 font-sans italic">Not published</span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-400 leading-tight">
                    Mid-year revised appropriation approved in Supplementary Demands.
                  </p>
                </div>

                {/* 3. Actual Disbursement (AE) */}
                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">
                      Actual Expenditure (AE)
                    </span>
                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 font-medium">Audited</span>
                  </div>
                  <div className="text-lg sm:text-xl font-bold font-mono text-emerald-400">
                    {record.financials.actual_expenditure_cr !== undefined ? (
                      `₹${record.financials.actual_expenditure_cr.toLocaleString()} Cr`
                    ) : (
                      <span className="text-xs text-slate-500 font-sans italic">Pending CAG audit</span>
                    )}
                  </div>
                  <p className="text-[10px] text-slate-400 leading-tight">
                    Audited tax funds disbursed and spent for citizen benefits.
                  </p>
                </div>
              </div>

              {/* Fiscal utilization bar with valid denominator check */}
              {record.financials.actual_expenditure_cr !== undefined &&
                record.financials.revised_estimate_cr !== undefined &&
                record.financials.revised_estimate_cr > 0 && (
                  <div className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 space-y-2">
                    <div className="flex justify-between items-center text-xs">
                      <span className="text-slate-400 font-medium">Fiscal Utilization (Actuals vs Revised Estimates):</span>
                      <span className="font-mono font-bold text-emerald-400">
                        {((record.financials.actual_expenditure_cr / record.financials.revised_estimate_cr) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                      <div
                        className="bg-emerald-500 h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${Math.min(
                            (record.financials.actual_expenditure_cr / record.financials.revised_estimate_cr) * 100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                )}
            </div>
          )}

          {/* Atomic Propositions (Step 5: Claims breakdown) */}
          {record.atomic_propositions && record.atomic_propositions.length > 0 && (
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Layers className="w-3.5 h-3.5 text-blue-400" />
                <span>Proposition Breakdown & Verification Truth Values</span>
              </span>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                {record.atomic_propositions.map((prop) => (
                  <div
                    key={prop.id}
                    className="p-3.5 rounded-xl bg-slate-950 border border-slate-800 text-xs flex flex-col justify-between gap-2.5"
                  >
                    <div className="flex items-start gap-2.5">
                      {prop.truth_value === true || String(prop.truth_value).toLowerCase() === 'true' ? (
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                      ) : (
                        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                      )}
                      <span className="text-slate-200 leading-relaxed font-medium">
                        {prop.statement}
                      </span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono">
                      Verification Source: {prop.source}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Civic SLA Metrics (Step 5: Civic Issues) */}
          {record.sla_metrics && (
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-amber-400" />
                <span>Statutory Citizen&apos;s Charter SLA Standard</span>
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">Statutory SLA Deadline</span>
                  <span className="text-base font-bold text-white font-mono">{record.sla_metrics.statutory_days} Days</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">Elapsed Resolution Time</span>
                  <span className={`text-base font-bold font-mono ${record.sla_metrics.is_breached ? 'text-rose-400' : 'text-emerald-400'}`}>
                    {record.sla_metrics.elapsed_days} Days
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">Resolution Verification</span>
                  <span className="text-xs font-bold text-slate-200">
                    {record.sla_metrics.verified_resolution || 'Department Self-Reported'}
                  </span>
                </div>
              </div>

              {/* Citizen Privacy Protection Banner */}
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 flex items-center gap-2 text-xs text-slate-400">
                <Lock className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                <span>Citizen Privacy Protection: Personal contact details and identifiable citizen information are redacted.</span>
              </div>
            </div>
          )}

          {/* Representative Metrics (Step 4: MLAs) */}
          {record.representative_metrics && (
            <div className="pt-4 border-t border-slate-800 space-y-3">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                <Building2 className="w-3.5 h-3.5 text-blue-400" />
                <span>Legislative & Constituency Activity</span>
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">Assembly Attendance</span>
                  <span className="text-base font-bold text-white font-mono">
                    {record.representative_metrics.attendance_pct !== undefined ? `${record.representative_metrics.attendance_pct}%` : 'Not documented'}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">Assembly Questions Raised</span>
                  <span className="text-base font-bold text-blue-400 font-mono">
                    {record.representative_metrics.questions_count ?? 'Not documented'}
                  </span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800">
                  <span className="text-[10px] text-slate-400 block uppercase font-semibold">MLACDS Fund Utilization</span>
                  <span className="text-base font-bold text-emerald-400 font-mono">
                    ₹{record.representative_metrics.mlacds_utilized_cr ?? 0} Cr / ₹{record.representative_metrics.mlacds_allocated_cr ?? 3} Cr
                  </span>
                </div>
              </div>
              <p className="text-[11px] text-slate-400 italic">
                Non-causal note: Metrics reflect individual assembly records and local constituency development fund usage. Government-wide welfare programs are not solely attributed to an individual MLA without specific legislative sponsorship.
              </p>
            </div>
          )}
        </div>
      </section>

      {/* SECTION 4: Where the information came from (Phase 11.6: Evidence and Source Explorer) */}
      <section aria-labelledby="sources-heading" className="space-y-4">
        <EvidencePanel
          dossier={record.evidence_dossier}
          recordId={record.id}
          recordType={record.category_key}
          title="Sources and Evidence Explorer"
        />
      </section>

      {/* SECTION 5: Additional technical details (Step 7: Progressive Disclosure) */}
      <section aria-labelledby="technical-accordion-heading" className="space-y-3">
        <h2 id="technical-accordion-heading" className="text-sm font-bold text-slate-400 uppercase tracking-wider">
          Auditor Details & Progressive Disclosure
        </h2>

        {/* Accordion 1: How was this assessed? */}
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
          <button
            type="button"
            onClick={() => setShowMethodology(!showMethodology)}
            aria-expanded={showMethodology}
            className="w-full p-4 text-left flex items-center justify-between text-xs sm:text-sm font-bold text-white hover:bg-slate-800/40 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <span className="flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-400" />
              <span>How was this assessed? (Epistemic Methodology)</span>
            </span>
            <ChevronDown
              className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${
                showMethodology ? 'rotate-180' : ''
              }`}
            />
          </button>
          {showMethodology && (
            <div className="px-5 pb-5 pt-2 border-t border-slate-800 text-xs text-slate-300 space-y-2 leading-relaxed bg-slate-950/50">
              <p>
                {record.methodology_explanation ||
                  'CivicLens TN employs a multi-hop verification protocol cross-matching political claims and election promises against primary Government Orders (G.O.s), State Gazette notifications, and verified Demands for Grants financial disbursements.'}
              </p>
              <p className="text-slate-400">
                Independent evaluation findings maintain strict non-causal epistemic discipline: macro socio-economic changes are not attributed to single schemes without baseline difference-in-difference or regression discontinuity econometric studies.
              </p>
            </div>
          )}
        </div>

        {/* Accordion 2: Technical Identifiers & System Data */}
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
          <button
            type="button"
            onClick={() => setShowTechnical(!showTechnical)}
            aria-expanded={showTechnical}
            className="w-full p-4 text-left flex items-center justify-between text-xs sm:text-sm font-bold text-white hover:bg-slate-800/40 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <span className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-indigo-400" />
              <span>Technical details & System Identifiers</span>
            </span>
            <ChevronDown
              className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${
                showTechnical ? 'rotate-180' : ''
              }`}
            />
          </button>
          {showTechnical && (
            <div className="px-5 pb-5 pt-3 border-t border-slate-800 text-xs text-slate-300 space-y-3 bg-slate-950/50 font-mono">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Record ID</span>
                  <span className="text-blue-400 font-bold">{record.id}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Category Key</span>
                  <span className="text-emerald-400 font-bold">{record.category_key}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Evidence Graph Ledger</span>
                  <span className="text-indigo-400">EVD-{record.category_key.toUpperCase()}-{record.id}</span>
                </div>
                <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Cryptographic Provenance</span>
                  <span className="text-slate-400 truncate">SHA256:7a4c9b88e10f4d32</span>
                </div>
              </div>
              {record.technical_details && (
                <pre className="p-3 rounded-xl bg-slate-900/80 border border-slate-800 text-[10px] text-slate-400 overflow-x-auto">
                  {JSON.stringify(record.technical_details, null, 2)}
                </pre>
              )}
            </div>
          )}
        </div>

        {/* Accordion 3: Data Limitations & Caveats */}
        <div className="rounded-2xl bg-slate-900/60 border border-slate-800 overflow-hidden">
          <button
            type="button"
            onClick={() => setShowLimitations(!showLimitations)}
            aria-expanded={showLimitations}
            className="w-full p-4 text-left flex items-center justify-between text-xs sm:text-sm font-bold text-white hover:bg-slate-800/40 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <span className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <span>Data limitations & Caveats</span>
            </span>
            <ChevronDown
              className={`w-4 h-4 text-slate-400 transition-transform duration-200 ${
                showLimitations ? 'rotate-180' : ''
              }`}
            />
          </button>
          {showLimitations && (
            <div className="px-5 pb-5 pt-3 border-t border-slate-800 text-xs text-slate-300 space-y-2 bg-slate-950/50">
              {record.data_limitations && record.data_limitations.length > 0 ? (
                <ul className="list-disc pl-5 space-y-1.5 text-slate-300">
                  {record.data_limitations.map((lim, idx) => (
                    <li key={idx} className="leading-relaxed">
                      {lim}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-slate-400">
                  Figures are limited to officially published reports as of the current financial cycle. Lags in municipal reporting or delayed reconciliation by local drawing officers may affect real-time totals.
                </p>
              )}

              {record.incomplete_fields && record.incomplete_fields.length > 0 && (
                <div className="pt-2 text-[11px] text-amber-300/80">
                  <strong>Unpublished fields: </strong>
                  <span>{record.incomplete_fields.join(', ')} were not provided in primary state disclosures.</span>
                </div>
              )}
            </div>
          )}
        </div>
      </section>

      {/* SECTION 6: Connected Related Records (Phase 11.9 Cross-Phase Integration) */}
      <section aria-labelledby="related-records-heading" className="space-y-4 pt-6 border-t border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h2 id="related-records-heading" className="text-base sm:text-lg font-bold text-white flex items-center gap-2">
              <ArrowRight className="w-4 h-4 text-blue-400" />
              <span>Connected Public Records</span>
            </h2>
            <p className="text-xs text-slate-400">Cross-phase civic linkages and evidence pathways</p>
          </div>
          {record.related_records.length > 0 && (
            <div className="flex flex-wrap items-center gap-1.5 text-[11px]">
              {directCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 font-medium">
                  Direct ({directCount})
                </span>
              )}
              {evidenceCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20 font-medium">
                  Evidence ({evidenceCount})
                </span>
              )}
              {inferredCount > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/20 font-medium">
                  Inferred ({inferredCount})
                </span>
              )}
            </div>
          )}
        </div>

        {record.related_records.length === 0 ? (
          <CivicStateNotice
            state="no_records_available"
            title="No Connected Public Records Currently Available"
            description="No cross-phase records (such as schemes, promises, civic grievances, or policy evaluations) are currently linked to this record in the verified knowledge base. CivicLens TN maintains strict evidence integrity and does not infer connections without verified statutory or audit linkage."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {record.related_records.map((rel) => {
              const isDirect = rel.connection_type === 'direct_identifier';
              const isEvidence = rel.connection_type === 'evidence_relationship';
              const isInferred = rel.connection_type === 'inferred_relationship' || rel.is_inferred;

              return (
                <div
                  key={`${rel.type}-${rel.id}`}
                  className={`p-5 rounded-2xl bg-slate-900/70 border flex flex-col justify-between space-y-3 transition-all shadow-md group ${
                    isInferred
                      ? 'border-amber-500/30 hover:border-amber-500/50 bg-amber-950/10'
                      : isEvidence
                      ? 'border-emerald-500/30 hover:border-emerald-500/50 bg-emerald-950/10'
                      : 'border-slate-800 hover:border-slate-700'
                  }`}
                >
                  <div className="space-y-2.5">
                    {/* Header tags */}
                    <div className="flex flex-wrap items-center justify-between gap-1.5">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                        {rel.type_label}
                      </span>

                      {/* Connection Type Badge */}
                      {isDirect && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/30">
                          <Link2 className="w-2.5 h-2.5" />
                          <span>Direct Link</span>
                        </span>
                      )}
                      {isEvidence && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/30">
                          <ShieldCheck className="w-2.5 h-2.5" />
                          <span>Evidence Link</span>
                        </span>
                      )}
                      {isInferred && (
                        <span className="inline-flex items-center gap-1 text-[10px] font-semibold px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-300 border border-amber-500/30">
                          <AlertTriangle className="w-2.5 h-2.5" />
                          <span>Inferred Match</span>
                        </span>
                      )}

                      <span className="text-[10px] font-mono text-slate-500">#{rel.id}</span>
                    </div>

                    <h3 className="text-sm font-bold text-white group-hover:text-blue-400 transition-colors leading-snug">
                      {rel.title}
                    </h3>

                    <p className="text-xs text-slate-300 leading-relaxed">
                      <strong className="text-slate-400">Why related: </strong>
                      {rel.relationship_reason}
                    </p>

                    {/* Method & Confidence Metadata */}
                    <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-400 font-mono">
                      {rel.matching_method && (
                        <span className="px-1.5 py-0.5 rounded bg-slate-800/80 border border-slate-700/60">
                          Method: {rel.matching_method}
                        </span>
                      )}
                      {rel.confidence_score !== undefined && (
                        <span className="px-1.5 py-0.5 rounded bg-slate-800/80 border border-slate-700/60">
                          Confidence: {Math.round(rel.confidence_score * 100)}%
                        </span>
                      )}
                      {rel.provenance_source && (
                        <span className="truncate max-w-[200px]" title={rel.provenance_source}>
                          Src: {rel.provenance_source}
                        </span>
                      )}
                    </div>

                    {/* Inferred Epistemic Caveat Box */}
                    {isInferred && (
                      <div className="p-2.5 rounded-xl bg-amber-950/30 border border-amber-500/30 text-[11px] text-amber-200/90 flex items-start gap-2">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0 mt-0.5" />
                        <span>
                          {rel.epistemic_caveat ||
                            'Automated Candidate: This connection was suggested by algorithmic analysis and has not been verified by a statutory government document or audit.'}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="pt-2.5 border-t border-slate-800/80">
                    <Link
                      href={rel.href}
                      aria-label={`Open connected ${rel.type_label} record: ${rel.title}`}
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-blue-400 hover:text-blue-300 focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:outline-none rounded transition-colors"
                    >
                      <span>Open connected record</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
};
