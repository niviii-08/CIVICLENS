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
  Landmark,
  FileCheck2,
  CheckCircle2,
  Scale,
  Zap,
  Sparkles,
  ExternalLink,
  Phone,
  HelpCircle,
  GraduationCap,
  Sprout,
  Heart,
  ChevronRight,
  Search,
  Check
} from 'lucide-react';
import { fetchRecentPublicRecords, PublicRecordPreview } from '../lib/api';
import { UnifiedSearch } from '../components/UnifiedSearch';
import { SpotlightCard } from '../components/SpotlightCard';
import { CitizenBenefitFinder } from '../components/CitizenBenefitFinder';
import { useLanguage } from '../lib/LanguageContext';

const TICKER_ITEMS = [
  '₹14,694 Cr Welfare Allocation 2024-25',
  '2.2+ Crore Beneficiaries Reached',
  '234 Assembly Constituencies Mapped',
  '100% Primary Government Orders (G.O.) Audited',
  'DMK 2021 Manifesto G.O. Tracing (182 Delivered)',
  'Kalaignar Magalir Urimai Thittam (₹1,000/mo DBT)',
  'Chief Minister Morning Breakfast Scheme (18.5L Children)',
  'Vidiyal Payanam Free Bus Travel (500+ Cr Trips)',
  'Zero Synthetic Data · Official Sources Only',
  'DPDPA 2023 Citizen Privacy Protected',
];

export default function HomePage() {
  const { language, t } = useLanguage();
  const [recentRecords, setRecentRecords] = useState<PublicRecordPreview[]>([]);
  const [loadingRecent, setLoadingRecent] = useState(true);
  const [recentError, setRecentError] = useState(false);
  const [activeTab, setActiveTab] = useState<'finder' | 'modules'>('finder');

  useEffect(() => {
    async function loadRecent() {
      try {
        setLoadingRecent(true);
        const data = await fetchRecentPublicRecords();
        setRecentRecords(data);
      } catch {
        setRecentError(true);
      } finally {
        setLoadingRecent(false);
      }
    }
    loadRecent();
  }, []);

  const tickerContent = [...TICKER_ITEMS, ...TICKER_ITEMS];

  return (
    <div className="space-y-10 -mt-2">

      {/* ═══════════════════════════════════════
          SECTION 1 — WELCOMING CITIZEN HERO
      ═══════════════════════════════════════ */}
      <section className="relative pt-8 pb-4 md:pt-14 md:pb-8 text-center overflow-hidden">
        {/* Soft atmospheric ambient glow */}
        <div className="absolute inset-0 pointer-events-none">
          <div className="absolute top-0 left-1/4 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px]" />
          <div className="absolute top-10 right-1/4 w-[400px] h-[400px] bg-indigo-500/12 rounded-full blur-[130px]" />
          <div className="absolute -bottom-10 left-1/2 -translate-x-1/2 w-[600px] h-[200px] bg-sky-500/8 rounded-full blur-[100px]" />
        </div>

        <div className="relative z-10 space-y-6 max-w-5xl mx-auto">
          {/* Welcoming state banner pill */}
          <div className="inline-flex items-center gap-2.5 px-4 py-1.5 rounded-full bg-gradient-to-r from-cyan-500/10 via-indigo-500/10 to-blue-500/10 border border-cyan-500/25 shadow-sm text-xs font-semibold text-cyan-300 backdrop-blur-xl">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-400" />
            </span>
            <span>
              {language === 'ta'
                ? '🏛️ தமிழ்நாடு குடிமக்கள் நலன் & உண்மைத் தகவல் தளம்'
                : '🏛️ TAMIL NADU CITIZEN INFORMATION & WELFARE PORTAL'}
            </span>
          </div>

          {/* Warm display headline with high readability */}
          <div className="space-y-2 select-none">
            <h1 className="text-4xl sm:text-6xl md:text-7xl font-black tracking-tight text-white leading-tight">
              {language === 'ta' ? (
                <>
                  உங்கள் அரசு. உங்கள் திட்டங்கள்.{' '}
                  <span className="text-shimmer block sm:inline">உண்மைத் தகவல்கள்.</span>
                </>
              ) : (
                <>
                  Tamil Nadu&apos;s Public Record{' '}
                  <span className="text-shimmer block sm:inline">Made Simple.</span>
                </>
              )}
            </h1>
            <p className="text-base sm:text-xl font-medium text-amber-300/90 font-sans">
              {language === 'ta'
                ? 'எளிய முறையில் அரசு நலத்திட்டங்கள், தேர்தல் வாக்குறுதிகள் & உண்மை சரிபார்ப்பு'
                : 'Welfare Schemes · Election Promises · MLA Works · Fact Checks · Primary Records'}
            </p>
          </div>

          {/* Friendly plain-language explanation */}
          <p className="max-w-2xl mx-auto text-sm sm:text-base text-slate-300 leading-relaxed font-normal">
            {language === 'ta'
              ? '30 வினாடிகளில் உங்களுக்கான அரசுத் திட்டங்களைத் தெரிந்து கொள்ளுங்கள்; தேர்தல் வாக்குறுதிகள், உங்கள் தொகுதி எம்.எல்.ஏ பணிகள் மற்றும் உண்மைத் தகவல்களை அதிகாரப்பூர்வ அரசாணைகள் மூலம் சரிபாருங்கள்.'
              : 'Easily discover welfare benefits for you and your family, check eligibility in 30 seconds, track election promises delivered, inspect your local MLA, and verify facts backed by official Government Orders.'}
          </p>

          {/* Primary Quick CTAs */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <button
              type="button"
              onClick={() => {
                setActiveTab('finder');
                const el = document.getElementById('citizen-interactive-section');
                if (el) el.scrollIntoView({ behavior: 'smooth' });
              }}
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-sm shadow-xl shadow-cyan-500/25 transition-all duration-300 hover:scale-[1.03] active:scale-[0.98]"
            >
              <Sparkles className="w-4 h-4 text-cyan-200" />
              <span>{language === 'ta' ? 'எனக்கான திட்டங்களை தேடு' : 'Find My Welfare Benefits'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <Link
              href="/promises"
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-2xl bg-white/[0.05] border border-white/[0.15] hover:border-cyan-400/50 text-cyan-300 hover:text-white font-semibold text-sm transition-all duration-300 hover:bg-white/[0.09] backdrop-blur-xl"
            >
              <ScrollText className="w-4 h-4 text-rose-400" />
              <span>{language === 'ta' ? '2021 வாக்குறுதிகள் நிலை' : 'Track 2021 Promises →'}</span>
            </Link>

            <Link
              href="/representatives"
              className="inline-flex items-center gap-2 px-5 py-3.5 rounded-2xl bg-white/[0.03] border border-white/[0.1] hover:border-blue-400/40 text-slate-300 hover:text-white font-semibold text-sm transition-all duration-300 hover:bg-white/[0.07]"
            >
              <Users className="w-4 h-4 text-blue-400" />
              <span>{language === 'ta' ? 'என் தொகுதி எம்.எல்.ஏ' : 'Find My MLA'}</span>
            </Link>
          </div>

          {/* Quick Jump Search Pills */}
          <div className="flex flex-wrap items-center justify-center gap-2 pt-2 text-xs text-slate-400">
            <span className="text-slate-500 font-medium">
              {language === 'ta' ? 'விரைவு தேடல்:' : 'Popular Searches:'}
            </span>
            <Link
              href="/schemes?q=KMUT"
              className="glass-pill text-cyan-300 hover:text-white hover:border-cyan-400/50 transition-colors"
            >
              👩 KMUT (₹1,000/mo)
            </Link>
            <Link
              href="/schemes?q=breakfast"
              className="glass-pill text-emerald-300 hover:text-white hover:border-emerald-400/50 transition-colors"
            >
              🥣 Morning Breakfast
            </Link>
            <Link
              href="/schemes?q=pudhumai"
              className="glass-pill text-purple-300 hover:text-white hover:border-purple-400/50 transition-colors"
            >
              🎓 Pudhumai Penn (₹1,000)
            </Link>
            <Link
              href="/schemes?q=vidiyal"
              className="glass-pill text-rose-300 hover:text-white hover:border-rose-400/50 transition-colors"
            >
              🚌 Free Bus Travel
            </Link>
            <Link
              href="/promises?status=Fulfilled"
              className="glass-pill text-amber-300 hover:text-white hover:border-amber-400/50 transition-colors"
            >
              ✅ 182 Promises Fulfilled
            </Link>
          </div>
        </div>
      </section>

      {/* ═══════════════════════════════════════
          SECTION 2 — REASSURING WELFARE PULSE BAR
      ═══════════════════════════════════════ */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-[#0c1435]/90 to-[#060a1d]/90 border border-white/[0.08] backdrop-blur-xl">
          <div className="flex items-center gap-2 text-cyan-400 text-xs font-semibold mb-1">
            <BookOpen className="w-4 h-4" />
            <span>{language === 'ta' ? 'அரசு நலச் செலவு' : 'Annual Welfare Outlay'}</span>
          </div>
          <p className="text-2xl sm:text-3xl font-black text-white stat-number-glow">₹14,694 Cr</p>
          <p className="text-[11px] text-slate-400 mt-1">
            {language === 'ta' ? '2024-25 நிதிநிலை ஒதுக்கீடு' : 'Official Demands for Grants'}
          </p>
        </div>

        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-[#0c1435]/90 to-[#060a1d]/90 border border-white/[0.08] backdrop-blur-xl">
          <div className="flex items-center gap-2 text-emerald-400 text-xs font-semibold mb-1">
            <Users className="w-4 h-4" />
            <span>{language === 'ta' ? 'பயனடைந்த குடிமக்கள்' : 'Citizen Beneficiaries'}</span>
          </div>
          <p className="text-2xl sm:text-3xl font-black text-emerald-300 stat-number-glow">2.2+ Crore</p>
          <p className="text-[11px] text-slate-400 mt-1">
            {language === 'ta' ? 'மகளிர், மாணவர்கள், விவசாயிகள்' : 'Women, students, and farmers'}
          </p>
        </div>

        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-[#0c1435]/90 to-[#060a1d]/90 border border-white/[0.08] backdrop-blur-xl">
          <div className="flex items-center gap-2 text-rose-400 text-xs font-semibold mb-1">
            <ScrollText className="w-4 h-4" />
            <span>{language === 'ta' ? 'நிறைவேறிய வாக்குறுதிகள்' : 'Manifesto Delivery'}</span>
          </div>
          <p className="text-2xl sm:text-3xl font-black text-rose-300 stat-number-glow">182 / 234</p>
          <p className="text-[11px] text-slate-400 mt-1">
            {language === 'ta' ? '78% அரசாணை மூலம் நிறைவேறியது' : '78% Implemented via G.O.'}
          </p>
        </div>

        <div className="p-4 sm:p-5 rounded-2xl bg-gradient-to-br from-[#0c1435]/90 to-[#060a1d]/90 border border-white/[0.08] backdrop-blur-xl">
          <div className="flex items-center gap-2 text-amber-400 text-xs font-semibold mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>{language === 'ta' ? 'அதிகாரப்பூர்வ ஆதாரங்கள்' : 'Primary Source Audit'}</span>
          </div>
          <p className="text-2xl sm:text-3xl font-black text-amber-300 stat-number-glow">100%</p>
          <p className="text-[11px] text-slate-400 mt-1">
            {language === 'ta' ? 'அரசாணை & தணிக்கை ஆவணங்கள்' : 'G.O. & CAG accounts linked'}
          </p>
        </div>
      </section>

      {/* ═══════════════════════════════════════
          SECTION 3 — LIVE MARQUEE TICKER
      ═══════════════════════════════════════ */}
      <div className="relative overflow-hidden border-y border-white/[0.06] bg-white/[0.015] py-3 rounded-xl">
        <div className="marquee-track">
          {tickerContent.map((item, i) => (
            <span key={i} className="inline-flex items-center gap-3 px-5 whitespace-nowrap">
              <span className="text-xs font-medium text-slate-300 tracking-wide">{item}</span>
              <span className="text-cyan-400/50 text-sm">✦</span>
            </span>
          ))}
        </div>
      </div>

      {/* ═══════════════════════════════════════
          SECTION 4 — UNIFIED FULL CITIZEN SEARCH
      ═══════════════════════════════════════ */}
      <section className="max-w-3xl mx-auto pt-2">
        <UnifiedSearch />
      </section>

      {/* ═══════════════════════════════════════
          SECTION 5 — INTERACTIVE CITIZEN HUB (TABS)
      ═══════════════════════════════════════ */}
      <section id="citizen-interactive-section" className="space-y-6 pt-4">
        {/* View Switcher Tabs */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 border-b border-white/[0.08] pb-4">
          <div>
            <h2 className="text-xl sm:text-2xl font-black text-white flex items-center gap-2">
              <span>{language === 'ta' ? 'குடிமக்கள் வழிகாட்டி' : 'Citizen Information Hub'}</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
              {language === 'ta'
                ? 'உங்கள் தேவைகேற்ப திட்டங்களை தேடவும் அல்லது அனைத்து பிரிவுகளையும் பார்வையிடவும்'
                : 'Calculate benefits you qualify for or explore all 10 intelligence modules'}
            </p>
          </div>

          <div className="flex items-center gap-1.5 p-1 rounded-2xl bg-white/[0.04] border border-white/[0.08] backdrop-blur-md shrink-0">
            <button
              type="button"
              onClick={() => setActiveTab('finder')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'finder'
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{language === 'ta' ? 'உடனடி திட்ட தேடல்' : '30-Sec Scheme Finder'}</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveTab('modules')}
              className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'modules'
                  ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md shadow-cyan-500/20'
                  : 'text-slate-300 hover:text-white hover:bg-white/[0.04]'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>{language === 'ta' ? 'அனைத்து பிரிவுகள் (10)' : 'Browse All Portals'}</span>
            </button>
          </div>
        </div>

        {/* Tab 1: Embedded Citizen Benefit Finder */}
        {activeTab === 'finder' && (
          <div className="animate-fade-in">
            <CitizenBenefitFinder />
          </div>
        )}

        {/* Tab 2: Bento Grid of All 10 Intelligence Modules */}
        {activeTab === 'modules' && (
          <div className="grid grid-cols-12 gap-4 animate-fade-in" aria-label="Civic Intelligence Modules">

            {/* ─── CARD 1: Government Welfare Schemes (7 cols) ─── */}
            <div className="col-span-12 md:col-span-7">
              <SpotlightCard
                href="/schemes"
                spotlightColor="rgba(16, 185, 129, 0.16)"
                borderColor="rgba(16, 185, 129, 0.4)"
                aria-label="Explore Government Welfare Schemes"
                className="min-h-[280px]"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="p-3 rounded-2xl bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 w-fit">
                      <BookOpen className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-emerald-500/15 text-emerald-300 border border-emerald-500/30">
                      ✓ Direct Citizen Benefits
                    </span>
                  </div>

                  <h3 className="text-2xl font-black text-white group-hover:text-emerald-300 transition-colors leading-tight">
                    {language === 'ta' ? 'அரசு நலத்திட்டங்கள்' : 'Government Welfare Schemes'}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed max-w-lg">
                    {language === 'ta'
                      ? 'மகளிர் உரிமைத் தொகை (₹1,000), புதுமைப் பெண், காலை உணவுத் திட்டம் மற்றும் இலவச பேருந்து பயணத் திட்டங்களுக்கான தகுதி மற்றும் விண்ணப்பிக்கும் முறைகள்.'
                      : 'Verified welfare programs, monthly direct benefit transfers (KMUT ₹1,000/mo), student subsidies, eligibility rules, and required application documents.'}
                  </p>
                </div>

                <div className="mt-6 flex items-end justify-between pt-2 border-t border-white/[0.06]">
                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-2xl sm:text-3xl font-black text-emerald-400 stat-number-glow">₹14,694 Cr</p>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">Demands for Grants</p>
                    </div>
                    <div>
                      <p className="text-2xl sm:text-3xl font-black text-emerald-300 stat-number-glow">2.2+ Cr</p>
                      <p className="text-[11px] text-slate-400 font-mono mt-0.5">Citizens Reached</p>
                    </div>
                  </div>
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-400 group-hover:gap-2.5 transition-all">
                    <span>{language === 'ta' ? 'திட்டங்களை காண்க' : 'Explore Schemes'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </SpotlightCard>
            </div>

            {/* ─── CARD 2: Promises & Delivery Tracker (5 cols) ─── */}
            <div className="col-span-12 md:col-span-5">
              <SpotlightCard
                href="/promises"
                spotlightColor="rgba(244, 63, 94, 0.16)"
                borderColor="rgba(244, 63, 94, 0.4)"
                aria-label="Track Promises and Manifesto Delivery"
                className="min-h-[280px]"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="p-3 rounded-2xl bg-rose-950/80 border border-rose-500/30 text-rose-400 w-fit">
                      <ScrollText className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold px-2.5 py-1 rounded-full bg-rose-500/15 text-rose-300 border border-rose-500/30">
                      ✓ 2021 Election Manifesto
                    </span>
                  </div>

                  <h3 className="text-2xl font-black text-white group-hover:text-rose-300 transition-colors leading-tight">
                    {language === 'ta' ? 'தேர்தல் வாக்குறுதிகள்' : 'Promises & Delivery Tracker'}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {language === 'ta'
                      ? '2021 தேர்தல் அறிக்கையில் அளித்த 234 வாக்குறுதிகள் — எவை நிறைவேற்றப்பட்டன, எவை நிலுவையில் உள்ளன என்பதை அரசாணைகள் மூலம் அறியலாம்.'
                      : 'Trace 234 election commitments from the 2021 manifesto directly to signed Government Orders and budget lines.'}
                  </p>
                </div>

                <div className="mt-6 flex items-end justify-between pt-2 border-t border-white/[0.06]">
                  <div>
                    <p className="text-3xl font-black text-white">182 <span className="text-xs font-bold text-emerald-400 font-mono">Delivered (78%)</span></p>
                    <p className="text-[11px] text-slate-400 mt-0.5">38 In Progress · 14 Stalled</p>
                  </div>
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-rose-400 group-hover:gap-2.5 transition-all">
                    <span>{language === 'ta' ? 'சரிபார்க்க' : 'Track All'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </SpotlightCard>
            </div>

            {/* ─── CARD 3: Verify Claims (5 cols) ─── */}
            <div className="col-span-12 md:col-span-5">
              <SpotlightCard
                href="/claims"
                spotlightColor="rgba(6, 182, 212, 0.16)"
                borderColor="rgba(6, 182, 212, 0.4)"
                aria-label="Verify Public Claims"
                className="min-h-[220px]"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="p-3 rounded-2xl bg-cyan-950/80 border border-cyan-500/30 text-cyan-400 w-fit">
                      <ShieldCheck className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
                      ✓ CAG &amp; Gazette Verified
                    </span>
                  </div>

                  <h3 className="text-xl font-black text-white group-hover:text-cyan-300 transition-colors">
                    {language === 'ta' ? 'உண்மை சரிபார்ப்பு' : 'Verify Public Claims'}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {language === 'ta'
                      ? 'அரசியல் தலைவர்களின் அறிக்கைகள் மற்றும் பரவும் செய்திகளின் உண்மைத்தன்மை தணிக்கை அறிக்கைகள் மூலம் சரிபார்க்கப்படுகிறது.'
                      : 'Fact-check dossiers testing political statements against primary treasury accounts and assembly debate records.'}
                  </p>
                </div>

                <div className="mt-4 flex items-center justify-between pt-2 border-t border-white/[0.06]">
                  <div className="flex gap-1.5">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-300 border border-emerald-500/25">
                      VERIFIED TRUE
                    </span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/15 text-rose-300 border border-rose-500/25">
                      DISPUTED
                    </span>
                  </div>
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-cyan-400 group-hover:gap-2.5 transition-all">
                    <span>{language === 'ta' ? 'சரிபார்க்க' : 'Inspect'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </SpotlightCard>
            </div>

            {/* ─── CARD 4: Elected Representatives (7 cols) ─── */}
            <div className="col-span-12 md:col-span-7">
              <SpotlightCard
                href="/representatives"
                spotlightColor="rgba(59, 130, 246, 0.16)"
                borderColor="rgba(59, 130, 246, 0.4)"
                aria-label="View Elected Representatives"
                className="min-h-[220px]"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="p-3 rounded-2xl bg-blue-950/80 border border-blue-500/30 text-blue-400 w-fit">
                      <Users className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-blue-500/15 text-blue-300 border border-blue-500/30">
                      ✓ 234 Assembly Seats
                    </span>
                  </div>

                  <h3 className="text-xl font-black text-white group-hover:text-blue-300 transition-colors">
                    {language === 'ta' ? 'சட்டமன்ற உறுப்பினர்கள் & தொகுதி நிதி' : 'MLAs & Constituency Development (MLACDS)'}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed max-w-lg">
                    {language === 'ta'
                      ? 'தமிழ்நாட்டின் 234 சட்டமன்ற உறுப்பினர்களின் தொகுதி மேம்பாட்டு நிதி (₹3 கோடி/ஆண்டு) செலவுகள், உள்ளூர் வளர்ச்சிப் பணிகள் மற்றும் சட்டசபை வருகைப் பதிவுகள்.'
                      : 'Profiles, assembly debate questions, local public works, and MLACDS spending for all 234 Tamil Nadu MLAs.'}
                  </p>
                </div>

                <div className="mt-4 flex items-center justify-between pt-2 border-t border-white/[0.06]">
                  <div className="flex items-center gap-2 text-xs text-slate-300 font-medium">
                    <span className="font-bold text-white">234 MLAs</span>
                    <span>· 133 DMK · 66 AIADMK · 18 INC · 17 Other</span>
                  </div>
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-blue-400 group-hover:gap-2.5 transition-all">
                    <span>{language === 'ta' ? 'எம்.எல்.ஏ தேட' : 'Find MLA'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </SpotlightCard>
            </div>

            {/* ─── CARD 5: Civic Complaints & SLAs (6 cols) ─── */}
            <div className="col-span-12 md:col-span-6">
              <SpotlightCard
                href="/civic"
                spotlightColor="rgba(245, 158, 11, 0.16)"
                borderColor="rgba(245, 158, 11, 0.4)"
                aria-label="Civic Issues and SLA Tracking"
                className="min-h-[200px]"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="p-3 rounded-2xl bg-amber-950/80 border border-amber-500/30 text-amber-400 w-fit">
                      <AlertCircle className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-300 border border-amber-500/30">
                      ✓ 14-Day Resolution SLA
                    </span>
                  </div>

                  <h3 className="text-xl font-black text-white group-hover:text-amber-300 transition-colors">
                    {language === 'ta' ? 'மக்கள் குறைகள் & தீர்வு வரம்பு' : 'Civic Issues & Grievance SLAs'}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {language === 'ta'
                      ? 'மாநகராட்சி சாலைகள், மின்வாரி புகார் (1912), குடிநீர் வாரியம் மற்றும் முதலமைச்சரின் உதவி மையம் (1100) மூலம் தீர்க்கப்படும் மக்கள் குறைகள்.'
                      : 'Citizen grievances, departmental resolution turnaround, and SLA audits across GCC (1913), TANGEDCO (1912), and CMWSSB.'}
                  </p>
                </div>

                <div className="mt-4 flex items-center justify-between pt-2 border-t border-white/[0.06]">
                  <span className="text-xs text-amber-300 font-medium">72% Resolved within Citizen Charter SLA</span>
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-amber-400 group-hover:gap-2.5 transition-all">
                    <span>{language === 'ta' ? 'குறைகளை அறிய' : 'Review SLAs'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </SpotlightCard>
            </div>

            {/* ─── CARD 6: Budget & Spending (6 cols) ─── */}
            <div className="col-span-12 md:col-span-6">
              <SpotlightCard
                href="/budget"
                spotlightColor="rgba(99, 102, 241, 0.16)"
                borderColor="rgba(99, 102, 241, 0.4)"
                aria-label="Budget and Spending Analysis"
                className="min-h-[200px]"
              >
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="p-3 rounded-2xl bg-indigo-950/80 border border-indigo-500/30 text-indigo-400 w-fit">
                      <Landmark className="w-6 h-6" />
                    </div>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-500/15 text-indigo-300 border border-indigo-500/30">
                      ✓ FY 2024-25 Demands
                    </span>
                  </div>

                  <h3 className="text-xl font-black text-white group-hover:text-indigo-300 transition-colors">
                    {language === 'ta' ? 'அரசு நிதிநிலை அறிக்கை' : 'Budget Allocations & Actual Spending'}
                  </h3>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {language === 'ta'
                      ? 'ஒவ்வொரு துறைக்கும் ஒதுக்கப்பட்ட நிதி (BE) மற்றும் உண்மையில் மக்களுக்காக செலவிடப்பட்ட நிதி (AE) ஒப்பீடு.'
                      : 'Demands for Grants, department budget estimates, and fiscal accounts audited against primary state finance accounts.'}
                  </p>
                </div>

                <div className="mt-4 flex items-center justify-between pt-2 border-t border-white/[0.06]">
                  <span className="text-xs text-indigo-300 font-medium">₹13,720 Cr Welfare Allocation Tracked</span>
                  <span className="inline-flex items-center gap-1.5 text-xs font-bold text-indigo-400 group-hover:gap-2.5 transition-all">
                    <span>{language === 'ta' ? 'வரவு செலவு காண்க' : 'Analyse Budget'}</span>
                    <ArrowRight className="w-4 h-4" />
                  </span>
                </div>
              </SpotlightCard>
            </div>

          </div>
        )}
      </section>

      {/* ═══════════════════════════════════════
          SECTION 6 — RECENT CITIZEN RECORDS FEED
      ═══════════════════════════════════════ */}
      <section className="space-y-3 pt-2" aria-label="Recent Civic Records">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">
              {language === 'ta' ? 'அண்மைய அதிகாரப்பூர்வ அரசுப் பதிவுகள்' : 'Live Audited Government Updates'}
            </h2>
          </div>
          <Link
            href="/explore"
            className="text-xs text-cyan-400 hover:text-cyan-300 font-semibold inline-flex items-center gap-1 transition-colors"
          >
            <span>{language === 'ta' ? 'அனைத்தும் காண்க' : 'View All Records'}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        {loadingRecent ? (
          <div className="space-y-2">
            {[0, 1, 2, 3].map((i) => (
              <div key={i} className="h-12 rounded-2xl bg-white/[0.03] border border-white/[0.05] animate-pulse" />
            ))}
          </div>
        ) : recentError || recentRecords.length === 0 ? (
          <div className="p-4 rounded-2xl bg-white/[0.02] border border-white/[0.06] text-xs text-slate-400">
            Official government records are regularly verified. Browse categories above to view verified information.
          </div>
        ) : (
          <div className="space-y-2">
            {recentRecords.map((rec) => (
              <Link
                key={rec.id}
                href={rec.href}
                className="flex items-center gap-3 sm:gap-4 px-4 py-3 rounded-2xl bg-[#090e24]/70 hover:bg-[#0e173a]/80 border border-white/[0.06] hover:border-cyan-500/30 transition-all duration-200 group"
              >
                <span className={`shrink-0 text-[10px] font-bold px-2 py-0.5 rounded border ${rec.badgeClass}`}>
                  {rec.category.toUpperCase()}
                </span>
                <span className="flex-1 text-xs font-semibold text-slate-200 group-hover:text-white truncate transition-colors">
                  {rec.title}
                </span>
                <span className="shrink-0 text-[10px] text-slate-400 hidden sm:block truncate max-w-[150px]">
                  {rec.source}
                </span>
                <span className="shrink-0 text-[10px] font-bold text-emerald-400">{rec.status}</span>
                <ArrowRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all shrink-0" />
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* ═══════════════════════════════════════
          SECTION 7 — CITIZEN TRUST & INTEGRITY PILLARS
      ═══════════════════════════════════════ */}
      <section className="rounded-3xl bg-gradient-to-r from-indigo-950/80 via-[#0a102a]/90 to-blue-950/80 border border-indigo-500/25 p-6 sm:p-8 backdrop-blur-2xl shadow-xl relative overflow-hidden">
        <div className="relative z-10 space-y-6">
          <div className="text-center space-y-2">
            <span className="text-xs font-bold text-cyan-300 uppercase tracking-wider">
              {language === 'ta' ? 'நம்பகத்தன்மை & நெறிமுறைகள்' : 'Constitutional Trust & Neutrality'}
            </span>
            <h3 className="text-xl sm:text-2xl font-black text-white">
              {language === 'ta'
                ? 'ஒவ்வொரு தகவலும் அதிகாரப்பூர்வ அரசு ஆவணங்களால் உறுதிப்படுத்தப்பட்டது'
                : 'Every Figure Backed by an Official Primary Record'}
            </h3>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl mx-auto leading-relaxed">
              {language === 'ta'
                ? 'அரசியல் சார்பின்றி, அரசாணைகள் (G.O.), இந்திய தணிக்கை அறிக்கை (CAG) மற்றும் சட்டசபை பதிவுகள் அடிப்படையில் மட்டுமே தகவல்கள் தொகுக்கப்படுகின்றன.'
                : 'Strict non-partisan discipline: budget allocations are never conflated with actual expenditures, and claims are verified against primary records without editorial bias.'}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="rounded-2xl border border-emerald-500/25 bg-emerald-950/50 p-4 space-y-1.5">
              <div className="flex items-center gap-2 text-emerald-400 text-xs font-bold">
                <ShieldCheck className="w-4 h-4" />
                <span>{language === 'ta' ? 'அதிகாரப்பூர்வ ஆவணங்கள்' : '100% Primary Sources'}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {language === 'ta'
                  ? 'அரசாணைகள், சட்டசபை பதிவுகள் மற்றும் CAG நிதி கணக்குகள் மட்டுமே ஆதாரம்.'
                  : 'Sourced from Tamil Nadu Government Gazettes, CAG findings, and DBT audit trails.'}
              </p>
            </div>

            <div className="rounded-2xl border border-cyan-500/25 bg-cyan-950/50 p-4 space-y-1.5">
              <div className="flex items-center gap-2 text-cyan-400 text-xs font-bold">
                <Scale className="w-4 h-4" />
                <span>{language === 'ta' ? 'அரசியல் நடுநிலை' : 'Strict Non-Partisanship'}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {language === 'ta'
                  ? 'எந்தவொரு அரசியல் கட்சி சார்பும் இன்றி சமநிலையான factual பகுப்பாய்வு.'
                  : 'Zero political framing or opinions — factual state records and stated policies only.'}
              </p>
            </div>

            <div className="rounded-2xl border border-indigo-500/25 bg-indigo-950/50 p-4 space-y-1.5">
              <div className="flex items-center gap-2 text-indigo-400 text-xs font-bold">
                <FileCheck2 className="w-4 h-4" />
                <span>{language === 'ta' ? 'குடிமக்கள் தனியுரிமை பாதுகாப்பு' : 'DPDPA 2023 Citizen Privacy'}</span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed">
                {language === 'ta'
                  ? 'குடிமக்களின் தனிப்பட்ட தகவல்கள் எதுவும் சேமிக்கப்படாது; முழுமையான பாதுகாப்பு.'
                  : 'Complies with Indian Digital Personal Data Protection Act 2023; zero PII leakage.'}
              </p>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
