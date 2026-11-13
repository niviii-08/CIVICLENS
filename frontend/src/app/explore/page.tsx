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
    accent: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
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
    accent: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
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
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
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
              className="civic-card p-6 flex flex-col justify-between group space-y-4 transition-all duration-300"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className={`p-2.5 rounded-xl border ${module.accent} transition-transform group-hover:scale-110 duration-200`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-950/80 text-slate-400 border border-white/5 font-mono">
                      {module.phase}
                    </span>
                    <span className="text-xs font-mono font-bold text-white bg-slate-800/90 border border-white/10 px-2.5 py-0.5 rounded-full">
                      {module.stats}
                    </span>
                  </div>
                </div>

                <h3 className="font-bold text-lg text-white group-hover:text-cyan-300 transition-colors">
                  {module.title}
                </h3>

                <p className="text-xs text-slate-400 leading-relaxed">
                  {module.description}
                </p>
              </div>

              <div className="pt-4 border-t border-white/5 flex items-center justify-between">
                <span className="text-xs text-slate-400 font-mono">
                  Route: <code className="text-cyan-400">{module.href}</code>
                </span>
                <Link
                  href={module.href}
                  className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/20 transition-all group-hover:shadow-cyan-500/25 active:scale-95"
                >
                  <span>Launch Tool</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                </Link>
              </div>
            </div>
          );
        })}
      </div>

      {/* Technical Provenance Note */}
      <div className="p-5 rounded-2xl bg-slate-950/70 border border-white/10 flex items-start gap-3.5 backdrop-blur-md">
        <ShieldCheck className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
        <div className="space-y-1 text-xs">
          <div className="font-bold text-white">Non-Causal Epistemic Guardrails &amp; Open Data Standards</div>
          <p className="text-slate-400 leading-relaxed">
            All tools in the Civic Intelligence Lab adhere strictly to non-causal epistemic discipline. Cross-phase graph links reflect statutory jurisdiction and thematic correlation, never unproven causal claims. Raw source gazettes are available upon request through open administrative access.
          </p>
        </div>
      </div>
    </div>
  );
}
