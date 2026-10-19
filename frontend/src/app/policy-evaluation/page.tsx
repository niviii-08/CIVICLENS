'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { TrendingUp, ShieldCheck, FileText, Download, Award, CheckCircle2, ArrowRight } from 'lucide-react';
import { PolicyEvaluation } from '../../lib/types';
import { fetchPolicyEvaluations } from '../../lib/api';
import { PageHeader } from '../../components/PageHeader';

export default function PolicyEvaluationPage() {
  const [policies, setPolicies] = useState<PolicyEvaluation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchPolicyEvaluations();
      setPolicies(data);
      setLoading(false);
    }
    load();
  }, []);

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

      {/* Policy Dossiers List */}
      <div className="space-y-6">
        {policies.map((p) => (
          <div
            key={p.id}
            className="rounded-3xl bg-slate-900/80 border border-slate-800 p-6 md:p-8 space-y-6 shadow-2xl backdrop-blur-md"
          >
            {/* Header row */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-slate-800 pb-4">
              <div>
                <span className="font-mono text-xs text-blue-400 font-bold block mb-1">
                  #{p.id} • Launched {p.launch_year}
                </span>
                <h2 className="text-xl font-extrabold text-white">{p.policy_name}</h2>
                <span className="text-xs text-slate-400">Sector: <strong className="text-slate-300">{p.target_sector}</strong></span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-bold px-3 py-1 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                  Beneficiaries: {p.beneficiaries_count}
                </span>
              </div>
            </div>

            {/* Financial Appropriations Bar */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Budget Estimate (BE)
                </span>
                <span className="text-xl font-bold text-white font-mono">
                  ₹{p.allocated_funds_cr.toLocaleString()} Cr
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Revised Estimate (RE)
                </span>
                <span className="text-xl font-bold text-indigo-400 font-mono">
                  ₹{p.re_allocation_cr.toLocaleString()} Cr
                </span>
              </div>
              <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-1">
                  Actual Disbursement (AE)
                </span>
                <span className="text-xl font-bold text-emerald-400 font-mono">
                  ₹{p.actual_spent_cr.toLocaleString()} Cr
                </span>
              </div>
            </div>

            {/* Indicator & Baseline Assessment */}
            <div className="p-4 rounded-2xl bg-slate-950/80 border border-slate-800 space-y-2">
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

            {/* Sources & Gazette Links */}
            <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-slate-800">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-semibold text-slate-400">State Evidence Links:</span>
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
    </div>
  );
}
