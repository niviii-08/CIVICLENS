'use client';

import React from 'react';
import Link from 'next/link';
import { Compass, ShieldCheck, Heart, Sparkles, CheckCircle2 } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="relative border-t border-indigo-500/20 bg-[#060c22]/90 backdrop-blur-2xl text-slate-400 text-xs py-12 mt-20 shadow-2xl overflow-hidden">
      {/* Tamil Nadu watermark */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 pointer-events-none select-none text-[7rem] sm:text-[9rem] md:text-[12rem] font-black text-white/[0.03] whitespace-nowrap leading-none">
        தமிழ்நாடு
      </div>
      {/* Ambient background glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-[800px] h-48 bg-gradient-to-t from-cyan-500/5 via-indigo-500/5 to-transparent blur-3xl pointer-events-none" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          {/* Brand Column */}
          <div className="md:col-span-1 space-y-3.5">
            <Link href="/" className="flex items-center gap-2.5 text-white font-extrabold text-base tracking-tight group">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-cyan-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/25 group-hover:scale-105 transition-transform">
                <Compass className="w-4 h-4 text-white" />
              </div>
              <div className="flex items-center gap-1.5">
                <span className="group-hover:text-cyan-300 transition-colors">CIVICLENS</span>
                <span className="text-[10px] font-black px-1.5 py-0.5 rounded bg-gradient-to-r from-rose-500/20 to-amber-500/20 text-rose-300 border border-rose-500/40">TN</span>
              </div>
            </Link>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              Evidence-grounded civic intelligence, welfare scheme benefits, manifesto tracking, and public accountability platform for Tamil Nadu.
            </p>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-500/30 text-[11px] text-emerald-300">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Auditable Primary Provenance</span>
            </div>
          </div>

          {/* Citizen Services */}
          <div>
            <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-3.5 flex items-center gap-1.5">
              <span>Citizen Services</span>
            </h4>
            <ul className="space-y-2.5">
              <li>
                <Link href="/schemes" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Government Schemes</span>
                </Link>
              </li>
              <li>
                <Link href="/promises" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Promises & Progress</span>
                </Link>
              </li>
              <li>
                <Link href="/representatives" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Representatives (MLAs)</span>
                </Link>
              </li>
              <li>
                <Link href="/civic" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Civic Issues & SLAs</span>
                </Link>
              </li>
              <li>
                <Link href="/claims" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Verify Claims</span>
                </Link>
              </li>
              <li>
                <Link href="/policy-evaluation" className="hover:text-cyan-300 transition-colors flex items-center gap-1">
                  <span>Policy Results</span>
                </Link>
              </li>
            </ul>
          </div>

          {/* Advanced Analytics */}
          <div>
            <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-3.5">
              Civic Intelligence Lab
            </h4>
            <ul className="space-y-2.5">
              <li>
                <Link href="/budget" className="hover:text-cyan-300 transition-colors">
                  Budget & Spending
                </Link>
              </li>
              <li>
                <Link href="/funding" className="hover:text-cyan-300 transition-colors">
                  Political Funding
                </Link>
              </li>
              <li>
                <Link href="/news" className="hover:text-cyan-300 transition-colors">
                  News Coverage
                </Link>
              </li>
              <li>
                <Link href="/graph" className="hover:text-cyan-300 transition-colors">
                  Explore Evidence Graph
                </Link>
              </li>
              <li>
                <Link href="/explore" className="hover:text-cyan-300 transition-colors">
                  Explore All Features
                </Link>
              </li>
            </ul>
          </div>

          {/* Data Provenance & Legal */}
          <div className="space-y-3">
            <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-widest mb-3.5">
              Constitutional Rigor
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed font-normal">
              All records are cross-referenced against Tamil Nadu Government Gazettes, Demands for Grants, Legislative Debates, and Comptroller & Auditor General (CAG) audit findings.
            </p>
            <div className="p-3 rounded-2xl bg-indigo-950/50 border border-indigo-500/20 text-[11px] text-slate-300 space-y-1">
              <div className="flex items-center gap-1.5 text-cyan-300 font-semibold">
                <CheckCircle2 className="w-3.5 h-3.5 text-cyan-400" />
                <span>Zero Synthetic Fabrication</span>
              </div>
              <div className="text-slate-400">
                DPDPA 2023 Compliant • Non-Causal Epistemic Integrity
              </div>
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-indigo-500/15 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-400 font-medium">
          <div>
            © 2026 CIVICLENS TN. Built with open public intelligence for Tamil Nadu (தமிழ்நாடு).
          </div>
          <div className="flex items-center gap-3">
            <span className="text-cyan-400 font-semibold">State of Tamil Nadu</span>
            <span>•</span>
            <span>Next.js 14 & Flask REST API</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
