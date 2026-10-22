'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  ScrollText,
  Landmark,
  ShieldCheck,
  AlertTriangle,
  Users,
  CreditCard,
  Newspaper,
  TrendingUp,
  Network,
  Compass,
  FileCheck2,
  Bookmark,
} from 'lucide-react';

const navItems = [
  { name: 'Dashboard Overview', href: '/', icon: LayoutDashboard },
  { name: 'Manifesto Promises', href: '/promises', icon: ScrollText, badge: '1,074' },
  { name: 'Budget & Demands', href: '/budget', icon: Landmark },
  { name: 'Claim Verifier', href: '/claims', icon: ShieldCheck },
  { name: 'Civic Grievances & SLA', href: '/civic', icon: AlertTriangle },
  { name: 'MLAs & Assembly', href: '/representatives', icon: Users, badge: '234' },
  { name: 'Political Funding', href: '/funding', icon: CreditCard },
  { name: 'Bilingual News Framing', href: '/news', icon: Newspaper },
  { name: 'Policy Outcome Audit', href: '/policy-evaluation', icon: TrendingUp },
  { name: 'Evidence Graph', href: '/graph', icon: Network },
  { name: 'Tracked & Saved', href: '/saved', icon: Bookmark, badge: 'Local' },
];

export const Sidebar: React.FC = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 bg-slate-950/95 border-r border-slate-800/80 flex flex-col h-screen sticky top-0 backdrop-blur-xl z-40 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800/70 flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20">
          <Compass className="w-5 h-5 text-white" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-extrabold text-base tracking-tight text-white">CIVICLENS</span>
            <span className="text-xs font-bold px-1.5 py-0.2 rounded bg-red-600/20 text-red-400 border border-red-500/30">
              TN
            </span>
          </div>
          <p className="text-[10px] text-slate-400 font-medium">Public Intelligence Engine</p>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1 custom-scrollbar">
        <div className="px-3 pb-2 text-[10px] font-bold text-slate-500 uppercase tracking-wider">
          Intelligence Modules
        </div>
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all duration-200 group ${
                isActive
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 border border-blue-500/40'
                  : 'text-slate-300 hover:text-white hover:bg-slate-900 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-3 min-w-0">
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors ${
                    isActive ? 'text-white' : 'text-slate-400 group-hover:text-blue-400'
                  }`}
                />
                <span className="truncate">{item.name}</span>
              </div>
              {item.badge && (
                <span
                  className={`text-[10px] px-2 py-0.5 rounded-full font-bold ml-1.5 ${
                    isActive
                      ? 'bg-blue-800/70 text-blue-100'
                      : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700 text-[10px]'
                  }`}
                >
                  {item.badge}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/60">
        <div className="flex items-center gap-2 mb-1.5">
          <FileCheck2 className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-[11px] font-semibold text-slate-300">Auditable Provenance</span>
        </div>
        <p className="text-[10px] text-slate-400 leading-relaxed">
          Ground-truth evidence strictly anchored in GoTN Gazettes & Demands.
        </p>
      </div>
    </aside>
  );
};
