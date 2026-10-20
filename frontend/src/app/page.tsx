'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  BookOpen,
  ScrollText,
  Users,
  AlertCircle,
  ShieldCheck,
  TrendingUp,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { fetchRecentPublicRecords, PublicRecordPreview } from '../lib/api';
import { UnifiedSearch } from '../components/UnifiedSearch';

export default function HomePage() {
  const [recentRecords, setRecentRecords] = useState<PublicRecordPreview[]>([]);
  const [loadingRecent, setLoadingRecent] = useState(true);
  const [recentError, setRecentError] = useState(false);

  useEffect(() => {
    async function loadRecent() {
      try {
        setLoadingRecent(true);
        const data = await fetchRecentPublicRecords();
        setRecentRecords(data);
      } catch (err) {
        setRecentError(true);
      } finally {
        setLoadingRecent(false);
      }
    }
    loadRecent();
  }, []);

  const entryCards = [
    {
      title: 'Explore Government Schemes',
      description: 'Find schemes, their objectives, budgets and available progress information.',
      href: '/schemes',
      cta: 'Explore Schemes',
      icon: BookOpen,
      accent: 'group-hover:border-emerald-500/50 text-emerald-400'
    },
    {
      title: 'Follow Promises',
      description: 'Explore public promises and the documented evidence of progress.',
      href: '/promises',
      cta: 'Track Promises',
      icon: ScrollText,
      accent: 'group-hover:border-red-500/50 text-red-400'
    },
    {
      title: 'Find Representatives',
      description: 'Explore available information about elected representatives and their public records.',
      href: '/representatives',
      cta: 'View MLAs',
      icon: Users,
      accent: 'group-hover:border-blue-500/50 text-blue-400'
    },
    {
      title: 'Explore Civic Issues',
      description: 'Find reported public issues, department responses and available resolution evidence.',
      href: '/civic',
      cta: 'Review Issues',
      icon: AlertCircle,
      accent: 'group-hover:border-amber-500/50 text-amber-400'
    },
    {
      title: 'Verify a Public Claim',
      description: 'Explore evidence supporting, challenging or leaving a public claim unresolved.',
      href: '/claims',
      cta: 'Verify Claims',
      icon: ShieldCheck,
      accent: 'group-hover:border-teal-500/50 text-teal-400'
    },
    {
      title: 'Understand Policy Results',
      description: 'Review available spending, implementation information and documented outcomes.',
      href: '/policy-evaluation',
      cta: 'Inspect Results',
      icon: TrendingUp,
      accent: 'group-hover:border-purple-500/50 text-purple-400'
    }
  ];

  return (
    <div className="space-y-12 pb-12">
      {/* 1. Hero & Clear First Impression */}
      <section className="text-center max-w-3xl mx-auto space-y-4 pt-4 md:pt-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Official Public Information for Tamil Nadu</span>
        </div>
        <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
          Understand how public policies affect Tamil Nadu
        </h1>
        <p className="text-slate-300 text-sm sm:text-base leading-relaxed max-w-2xl mx-auto">
          Explore government schemes, public spending, promises, representatives and civic issues using available public records and supporting evidence.
        </p>

        {/* 2. Reusable Unified Search Integration */}
        <div className="pt-2">
          <UnifiedSearch
            variant="hero"
            placeholder="Search a scheme, department, representative or issue..."
          />
        </div>
      </section>

      {/* 3. Six Clear Entry Points */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              Explore Information by Category
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Browse public records, welfare entitlements, elected officials and government responses.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {entryCards.map((card) => {
            const Icon = card.icon;
            return (
              <Link
                key={card.title}
                href={card.href}
                className="group relative rounded-3xl bg-slate-900/60 hover:bg-slate-900 border border-slate-800 hover:border-slate-700 p-6 flex flex-col justify-between transition-all hover:shadow-xl hover:-translate-y-0.5 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <div className="space-y-3">
                  <div className={`p-3 rounded-2xl bg-slate-950 border border-slate-800 w-fit ${card.accent}`}>
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-base font-bold text-white group-hover:text-blue-400 transition-colors">
                    {card.title}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                    {card.description}
                  </p>
                </div>

                <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs font-semibold text-slate-400 group-hover:text-white transition-colors">
                  <span>{card.cta}</span>
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </Link>
            );
          })}
        </div>
      </section>

      {/* 4. Compact Section: Explore public records */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
              Explore public records
            </h2>
            <p className="text-xs sm:text-sm text-slate-400">
              Recent public records verified from Tamil Nadu government gazettes, budget books, and election manifestos.
            </p>
          </div>
          <Link
            href="/explore"
            className="text-xs font-semibold text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
          >
            <span>All features</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loadingRecent ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
              <div key={i} className="h-32 rounded-2xl bg-slate-900/40 border border-slate-800 animate-pulse p-4 space-y-2">
                <div className="h-4 w-24 bg-slate-800 rounded" />
                <div className="h-4 w-full bg-slate-800 rounded" />
                <div className="h-3 w-32 bg-slate-800 rounded" />
              </div>
            ))}
          </div>
        ) : recentError || recentRecords.length === 0 ? (
          <div className="p-4 rounded-2xl bg-slate-900/40 border border-slate-800 text-xs text-slate-400">
            Records are currently being updated from official government sources. Browse individual categories above to view verified information.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {recentRecords.map((rec) => (
              <div
                key={rec.id}
                className="rounded-2xl bg-slate-900/60 border border-slate-800 p-5 flex flex-col justify-between space-y-3 hover:border-slate-700 transition-all"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${rec.badgeClass}`}>
                      {rec.category}
                    </span>
                    <span className="text-[11px] text-slate-400 font-mono">
                      {rec.dateOrYear}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-white line-clamp-2 leading-snug">
                    {rec.title}
                  </h3>
                  <p className="text-xs text-slate-400 truncate">
                    Source: <span className="text-slate-300">{rec.source}</span>
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-xs">
                  <span className="text-emerald-400 font-medium">
                    {rec.status}
                  </span>
                  <Link
                    href={rec.href}
                    aria-label={`View public record details for ${rec.title}`}
                    className="text-blue-400 hover:text-blue-300 font-semibold inline-flex items-center gap-1 focus-visible:ring-2 focus-visible:ring-blue-500 rounded px-1.5 py-0.5"
                  >
                    <span>View record</span>
                    <ArrowRight className="w-3 h-3" />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
