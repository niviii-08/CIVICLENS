'use client';

import React from 'react';
import Link from 'next/link';
import { Compass, ShieldCheck, Heart, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950/80 text-slate-400 text-xs py-10 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand Column */}
          <div className="md:col-span-1 space-y-3">
            <Link href="/" className="flex items-center gap-2 text-white font-extrabold text-base tracking-tight">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center">
                <Compass className="w-4 h-4 text-white" />
              </div>
              <span>CIVICLENS <span className="text-red-500">TN</span></span>
            </Link>
            <p className="text-xs text-slate-400 leading-relaxed">
              Public information platform providing evidence-grounded accountability, scheme benefits, and policy tracking for Tamil Nadu.
            </p>
            <div className="flex items-center gap-1.5 text-[11px] text-emerald-400">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Auditable Primary Provenance</span>
            </div>
          </div>

          {/* Citizen Services */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
              Citizen Services
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/schemes" className="hover:text-blue-400 transition-colors">
                  Government Schemes
                </Link>
              </li>
              <li>
                <Link href="/promises" className="hover:text-blue-400 transition-colors">
                  Promises & Progress
                </Link>
              </li>
              <li>
                <Link href="/representatives" className="hover:text-blue-400 transition-colors">
                  Representatives (MLAs)
                </Link>
              </li>
              <li>
                <Link href="/civic" className="hover:text-blue-400 transition-colors">
                  Civic Issues & SLAs
                </Link>
              </li>
              <li>
                <Link href="/claims" className="hover:text-blue-400 transition-colors">
                  Verify Claims
                </Link>
              </li>
              <li>
                <Link href="/policy-evaluation" className="hover:text-blue-400 transition-colors">
                  Policy Results
                </Link>
              </li>
            </ul>
          </div>

          {/* Advanced Analytics */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
              Civic Intelligence Lab
            </h4>
            <ul className="space-y-2">
              <li>
                <Link href="/budget" className="hover:text-blue-400 transition-colors">
                  Budget & Spending
                </Link>
              </li>
              <li>
                <Link href="/funding" className="hover:text-blue-400 transition-colors">
                  Political Funding
                </Link>
              </li>
              <li>
                <Link href="/news" className="hover:text-blue-400 transition-colors">
                  News Coverage
                </Link>
              </li>
              <li>
                <Link href="/graph" className="hover:text-blue-400 transition-colors">
                  Explore Evidence Graph
                </Link>
              </li>
              <li>
                <Link href="/explore" className="hover:text-blue-400 transition-colors">
                  Explore All Features
                </Link>
              </li>
            </ul>
          </div>

          {/* Data Provenance & Legal */}
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-3">
              Data Provenance
            </h4>
            <p className="text-xs text-slate-400 leading-relaxed mb-3">
              All records are strictly cross-referenced against Tamil Nadu Government Gazettes, Demands for Grants, Legislative Assembly Debates, and official ECI disclosures.
            </p>
            <div className="text-[11px] text-slate-400">
              Zero fabrication • Epistemic non-causal discipline • Open Public Data
            </div>
          </div>
        </div>

        <div className="pt-6 border-t border-slate-800/60 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px]">
          <div>
            © 2026 CIVICLENS TN. Open source public intelligence.
          </div>
          <div className="flex items-center gap-4">
            <span>State of Tamil Nadu</span>
            <span>•</span>
            <span className="text-slate-400">Next.js 14 & Flask API</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
