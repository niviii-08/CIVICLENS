'use client';

import React from 'react';
import Link from 'next/link';
import {
  Landmark,
  CreditCard,
  Newspaper,
  Network,
  ArrowRight,
  Database,
  ShieldCheck,
  FileText,
  Search,
  Sparkles
} from 'lucide-react';
import { PageHeader } from '../../components/PageHeader';

const advancedModules = [
  {
    title: 'Budget & Expenditure Intelligence',
    description: 'Inspect official Demands for Grants from the GoTN Finance Department. Audit Budget Estimates (BE), Revised Estimates (RE), and Audited Actuals (AE) across financial years.',
    href: '/budget',
    icon: Landmark,
    accent: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
    stats: '₹3.42 Lakh Crore Audited',
    phase: 'Phase 1 & 2'
  },
  {
    title: 'Political Funding & Campaign Disclosures',
    description: 'Track political party funding disclosed under Election Commission of India (ECI) Form 24A. Inspect Electoral Trust contributions and corporate donations with DPDPA PII masking.',
    href: '/funding',
    icon: CreditCard,
    accent: 'text-orange-400 bg-orange-500/10 border-orange-500/20',
    stats: '₹581.5 Cr Declared Donations',
    phase: 'Phase 5'
  },
  {
    title: 'Tamil & English News Framing',
    description: 'Bilingual natural language processing and entity sentiment analysis across 18 leading Tamil and English news publications adhering to non-partisan coverage neutrality indices.',
    href: '/news',
    icon: Newspaper,
    accent: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
    stats: '14,820 Articles Processed',
    phase: 'Phase 4'
  },
  {
    title: 'Multi-Hop Civic Evidence Graph',
    description: 'Traverse an explainable knowledge graph connecting election promises, budget allocations, government gazettes, and outcome studies with 9-factor evidence scoring.',
    href: '/graph',
    icon: Network,
    accent: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
    stats: '4,812 Nodes • 18,490 Edges',
    phase: 'Phase 9'
  }
];

export default function ExploreDirectoryPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        title="Civic Intelligence Lab — All Features"
        description="Advanced analytical capabilities for investigative journalists, researchers, policy analysts, and data auditors. Explore deep public records across state budgets, campaign finance, and media discourse."
        breadcrumbs={[{ label: 'Explore all features' }]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
            Advanced Civic Analytics
          </span>
        }
      />

      {/* Directory Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {advancedModules.map((module) => {
          const Icon = module.icon;
          return (
            <div
              key={module.href}
              className="rounded-2xl bg-slate-900/80 border border-slate-800 p-6 flex flex-col justify-between hover:border-slate-700 transition-all shadow-xl group space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className={`p-2.5 rounded-xl border ${module.accent}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                      {module.phase}
                    </span>
                    <span className="text-xs font-mono font-bold text-white bg-slate-800 px-2.5 py-0.5 rounded-full">
                      {module.stats}
                    </span>
                  </div>
                </div>

                <h3 className="font-bold text-lg text-white group-hover:text-blue-400 transition-colors">
                  {module.title}
                </h3>

                <p className="text-xs text-slate-400 leading-relaxed">
                  {module.description}
                </p>
              </div>

              <div className="pt-4 border-t border-slate-800 flex items-center justify-between">
                <span className="text-xs text-slate-400 font-mono">
                  Route: <code className="text-blue-400">{module.href}</code>
                </span>
                <Link
                  href={module.href}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold shadow-md shadow-blue-600/20 transition-all"
                >
                  <span>Launch Tool</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* Technical Provenance Note */}
      <div className="p-5 rounded-2xl bg-slate-950 border border-slate-800 flex items-start gap-3">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs">
          <div className="font-bold text-white">Non-Causal Epistemic Guardrails & Open Data Standards</div>
          <p className="text-slate-400 leading-relaxed">
            All tools in the Civic Intelligence Lab adhere strictly to non-causal epistemic discipline. Cross-phase graph links reflect statutory jurisdiction and thematic correlation, never unproven causal claims. Raw source gazettes are available upon request through open administrative access.
          </p>
        </div>
      </div>
    </div>
  );
}
