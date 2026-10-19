'use client';

import React, { useState } from 'react';
import { Network, Search, GitBranch, ArrowRight, ShieldCheck, Layers, FileText } from 'lucide-react';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';

export default function GraphPage() {
  const [selectedEntity, setSelectedEntity] = useState('POL-TN-KMUT');

  const nodes = [
    { id: 'POL-TN-KMUT', label: 'Policy: Kalaignar Magalir Urimai (KMUT)', type: 'Policy', color: 'border-purple-500 bg-purple-500/10 text-purple-300' },
    { id: 'PROMISE-DMK-001', label: 'Promise: DMK-2021-001 (Rs.1000 for Women)', type: 'Manifesto Commitment', color: 'border-red-500 bg-red-500/10 text-red-300' },
    { id: 'DEMAND-41', label: 'Budget: Demand 41 (Social Welfare)', type: 'Appropriation Head', color: 'border-emerald-500 bg-emerald-500/10 text-emerald-300' },
    { id: 'GO-MS-41', label: 'Document: G.O. Ms No. 41 (Gazette 2023)', type: 'Primary Gazette', color: 'border-blue-500 bg-blue-500/10 text-blue-300' },
    { id: 'STUDY-TNSPC-001', label: 'Study: TN State Planning Commission Audit', type: 'Empirical Study', color: 'border-amber-500 bg-amber-500/10 text-amber-300' },
  ];

  const edges = [
    { source: 'PROMISE-DMK-001', target: 'POL-TN-KMUT', relation: 'MATERIALIZED_INTO', score: 0.99 },
    { source: 'POL-TN-KMUT', target: 'DEMAND-41', relation: 'APPROPRIATED_UNDER', score: 0.98 },
    { source: 'POL-TN-KMUT', target: 'GO-MS-41', relation: 'NOTIFIED_BY', score: 1.0 },
    { source: 'POL-TN-KMUT', target: 'STUDY-TNSPC-001', relation: 'EVALUATED_BY', score: 0.95 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Explore Evidence"
        description="Traverse an explainable civic evidence network connecting election promises, budget allocations, government gazettes, and policy outcome evaluations."
        breadcrumbs={[
          { label: 'Explore all features', href: '/explore' },
          { label: 'Explore Evidence' },
        ]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-purple-500/10 text-purple-400 border border-purple-500/20">
            Knowledge Graph
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Indexed Graph Nodes"
          value="4,812"
          icon={<Network className="w-5 h-5 text-cyan-400" />}
          subtitle="Entities across 10 Phases"
        />
        <MetricCard
          title="Verified Multi-Hop Edges"
          value="18,490"
          change="9-Factor Scoring"
          changeType="positive"
          icon={<GitBranch className="w-5 h-5 text-indigo-400" />}
          subtitle="Cryptographically hashed"
        />
        <MetricCard
          title="Audit Provenance Ledger"
          value="SHA-256"
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
          subtitle="Tamper-proof traceability"
        />
      </div>

      {/* Graph Visual Explorer Canvas */}
      <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            <h3 className="text-sm font-bold text-white">Traversing Entity: <code className="text-blue-400">{selectedEntity}</code></h3>
          </div>
          <span className="text-xs text-slate-400">Multi-Hop Traversal Depth: 3 hops</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Node Cards */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Connected Graph Nodes</h4>
            {nodes.map((n) => (
              <div
                key={n.id}
                onClick={() => setSelectedEntity(n.id)}
                className={`p-4 rounded-2xl border cursor-pointer transition-all ${
                  selectedEntity === n.id
                    ? 'border-blue-500 bg-blue-500/20 shadow-lg shadow-blue-500/10'
                    : 'border-slate-800 bg-slate-950/70 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-slate-400">{n.id}</span>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${n.color}`}>
                    {n.type}
                  </span>
                </div>
                <div className="mt-1 text-xs font-bold text-white">{n.label}</div>
              </div>
            ))}
          </div>

          {/* Relations Inspector */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Dialectical Evidence Links</h4>
            <div className="space-y-2">
              {edges.map((e, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-2xl bg-slate-950 border border-slate-800/80 space-y-2 text-xs"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-[11px] font-bold text-blue-400">
                      {e.relation}
                    </span>
                    <span className="text-[10px] font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                      Confidence: {(e.score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-slate-300 font-mono text-[11px]">
                    <span className="text-slate-400 truncate max-w-[140px]">{e.source}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    <span className="text-white truncate max-w-[140px]">{e.target}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
