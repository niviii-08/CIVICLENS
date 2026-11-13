'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Compass,
  Search,
  ChevronDown,
  Menu,
  X,
  RefreshCw,
  Landmark,
  CreditCard,
  Newspaper,
  Network,
  Sparkles,
  Bookmark,
  Phone,
  HelpCircle,
  Languages
} from 'lucide-react';
import { checkBackendHealth } from '../lib/api';
import { SearchModal } from './SearchModal';
import { useSavedCivicItems } from '../lib/useSavedCivicItems';
import { CitizenHelplinesModal } from './CitizenHelplinesModal';
import { CitizenGlossaryModal } from './CitizenGlossaryModal';
import { useLanguage } from '../lib/LanguageContext';

// Primary Citizen Navigation Categories with Tamil Translations
export const primaryNavItems = [
  { name: 'Home', name_ta: 'முதற்பக்கம்', href: '/' },
  { name: 'Welfare Schemes', name_ta: 'அரசுத் திட்டங்கள்', href: '/schemes' },
  { name: 'Promises Tracker', name_ta: 'வாக்குறுதிகள்', href: '/promises' },
  { name: 'MLAs & Leaders', name_ta: 'சட்டமன்ற உறுப்பினர்கள்', href: '/representatives' },
  { name: 'Civic Grievances', name_ta: 'மக்கள் குறைகள்', href: '/civic' },
  { name: 'Fact Check', name_ta: 'உண்மை சரிபார்ப்பு', href: '/claims' },
  { name: 'Policy Results', name_ta: 'கொள்கை முடிவுகள்', href: '/policy-evaluation' },
];

// Explore All Features (Civic Intelligence Lab)
export const exploreNavItems = [
  { name: 'Budget & Spending', name_ta: 'நிதிநிலை அறிக்கை', href: '/budget', icon: Landmark, desc: 'Budget estimates & actual allocations' },
  { name: 'Political Funding', name_ta: 'அரசியல் நிதி', href: '/funding', icon: CreditCard, desc: 'ECI Form 24A & Electoral Trusts' },
  { name: 'News Coverage', name_ta: 'ஊடகப் பார்வை', href: '/news', icon: Newspaper, desc: 'Tamil & English media framing' },
  { name: 'Evidence Graph', name_ta: 'ஆதார வரைபடம்', href: '/graph', icon: Network, desc: 'Dialectical multi-hop evidence graph' },
];

export const Header: React.FC = () => {
  const pathname = usePathname();
  const { language, toggleLanguage, t } = useLanguage();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [exploreDropdownOpen, setExploreDropdownOpen] = useState(false);
  const [searchModalOpen, setSearchModalOpen] = useState(false);
  const [helplinesOpen, setHelplinesOpen] = useState(false);
  const [glossaryOpen, setGlossaryOpen] = useState(false);
  const { savedItems } = useSavedCivicItems();
  const [backendStatus, setBackendStatus] = useState<{ online: boolean; message: string }>({
    online: false,
    message: 'Checking...',
  });
  const [checking, setChecking] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setExploreDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
    setExploreDropdownOpen(false);
  }, [pathname]);

  const checkStatus = async () => {
    setChecking(true);
    const status = await checkBackendHealth();
    setBackendStatus(status);
    setChecking(false);
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const isExploreActive = exploreNavItems.some((item) => pathname?.startsWith(item.href)) || pathname === '/explore';

  return (
    <header className="sticky top-0 z-50 bg-[#060c22]/95 backdrop-blur-2xl shadow-xl shadow-indigo-950/40 transition-all duration-300 border-b-0 relative">
      {/* Gradient bottom border line */}
      <div className="absolute bottom-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-cyan-500/30 to-transparent pointer-events-none" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14 sm:h-16 gap-3 sm:gap-4">
          {/* Brand Wordmark & Descriptor */}
          <div className="flex items-center gap-3 shrink-0">
            <Link
              href="/"
              className="flex items-center gap-2.5 group focus:outline-none focus:ring-2 focus:ring-cyan-400 rounded-xl p-1 transition-transform"
            >
              <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-blue-600 to-indigo-600 flex items-center justify-center shadow-lg shadow-cyan-500/30 group-hover:scale-105 group-hover:shadow-cyan-400/50 transition-all duration-300">
                <Compass className="w-5 h-5 text-white group-hover:rotate-45 transition-transform duration-500" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-base tracking-tight text-white group-hover:text-cyan-300 transition-colors">
                    CIVICLENS
                  </span>
                  <span className="text-[10px] font-black px-1.5 py-0.5 rounded-md bg-gradient-to-r from-rose-500/20 to-amber-500/20 text-rose-300 border border-rose-500/40 shadow-sm shadow-rose-500/10">
                    TN
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-medium hidden sm:inline leading-none">
                  {language === 'ta' ? 'தமிழ்நாடு மக்கள் நலத் தகவல் தளம்' : 'Tamil Nadu Citizen Intelligence Portal'}
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Primary Navigation */}
          <nav className="hidden xl:flex items-center space-x-1" aria-label="Main Navigation">
            {primaryNavItems.map((item) => {
              const isActive = item.href === '/' ? pathname === '/' : (pathname?.startsWith(item.href) ?? false);
              const label = language === 'ta' ? item.name_ta : item.name;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-cyan-400 ${
                    isActive
                      ? 'text-white bg-white/[0.08] shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-white/[0.04]'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {label}
                  {isActive && (
                    <span className="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-[3px] w-1 h-1 rounded-full bg-cyan-400 shadow-sm shadow-cyan-400/80" />
                  )}
                </Link>
              );
            })}

            {/* Explore All Features Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setExploreDropdownOpen(!exploreDropdownOpen)}
                className={`inline-flex items-center gap-1 px-2.5 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-cyan-400 ${
                  isExploreActive
                    ? 'bg-indigo-900/60 text-cyan-300 border border-indigo-500/40'
                    : 'text-slate-300 hover:text-white hover:bg-indigo-950/60'
                }`}
                aria-expanded={exploreDropdownOpen}
                aria-haspopup="true"
              >
                <span>{language === 'ta' ? 'கூடுதல்' : 'More'}</span>
                <ChevronDown
                  className={`w-3.5 h-3.5 transition-transform duration-300 ${
                    exploreDropdownOpen ? 'rotate-180 text-cyan-400' : ''
                  }`}
                />
              </button>

              {/* Flyout Menu */}
              {exploreDropdownOpen && (
                <div className="absolute right-0 mt-2 w-72 rounded-2xl bg-[#090f28] border border-indigo-500/30 p-2.5 shadow-2xl backdrop-blur-2xl animate-fade-in-up z-50">
                  <div className="px-3 py-1.5 text-[10px] font-bold text-cyan-400 uppercase tracking-wider border-b border-indigo-500/20 mb-1 flex items-center justify-between">
                    <span>{language === 'ta' ? 'ஆராய்ச்சி கருவிகள்' : 'Civic Intelligence Lab'}</span>
                    <Sparkles className="w-3 h-3 text-cyan-400" />
                  </div>
                  {exploreNavItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname?.startsWith(item.href) ?? false;
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setExploreDropdownOpen(false)}
                        className={`flex items-start gap-2.5 p-2 rounded-xl text-xs transition-all duration-200 group ${
                          isActive ? 'bg-cyan-500/15 text-cyan-300' : 'hover:bg-indigo-950/80 text-slate-200'
                        }`}
                      >
                        <div className="p-1.5 rounded-lg bg-indigo-950/90 border border-indigo-500/30 group-hover:border-cyan-500/50 group-hover:scale-105 text-cyan-400 mt-0.5 transition-all">
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <div className="font-semibold text-white group-hover:text-cyan-300 transition-colors">
                            {language === 'ta' ? item.name_ta : item.name}
                          </div>
                          <div className="text-[11px] text-slate-400 leading-tight">
                            {item.desc}
                          </div>
                        </div>
                      </Link>
                    );
                  })}
                  <div className="pt-2 mt-1 border-t border-indigo-500/20">
                    <Link
                      href="/explore"
                      onClick={() => setExploreDropdownOpen(false)}
                      className="block text-center py-1.5 text-[11px] font-bold text-cyan-400 hover:text-cyan-300 transition-colors hover:underline"
                    >
                      {language === 'ta' ? 'அனைத்து பிரிவுகளையும் காண்க →' : 'View All Features Directory →'}
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </nav>

          {/* Right Header Controls (Citizen-First Action Buttons) */}
          <div className="flex items-center gap-1.5 sm:gap-2.5">
            {/* Helplines 1100 Trigger Button */}
            <button
              type="button"
              onClick={() => setHelplinesOpen(true)}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 text-xs font-bold transition-all shadow-sm group"
              title="Official Government Helplines (CM Helpline 1100, Women 181, EB 1912)"
            >
              <Phone className="w-3.5 h-3.5 animate-pulse text-rose-400" />
              <span className="hidden md:inline">{language === 'ta' ? 'உதவி 1100' : 'Helplines'}</span>
              <span className="md:hidden">1100</span>
            </button>

            {/* Civic Jargon Explainer Button */}
            <button
              type="button"
              onClick={() => setGlossaryOpen(true)}
              className="hidden lg:inline-flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/25 text-cyan-300 text-xs font-semibold transition-all shadow-sm"
              title="Plain-language explanation of G.O., DBT, SLA, MLACDS, and CAG terms"
            >
              <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
              <span>{language === 'ta' ? 'அரசு சொற்கள்' : 'Govt Jargon'}</span>
            </button>

            {/* Saved Items Link with Live Count */}
            <Link
              href="/saved"
              className="relative p-2 rounded-xl bg-indigo-950/50 hover:bg-indigo-900/70 border border-indigo-500/30 text-indigo-300 hover:text-white transition-all shadow-sm"
              title="View your saved schemes and tracking list"
            >
              <Bookmark className="w-4 h-4" />
              {savedItems.length > 0 && (
                <span className="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-cyan-400 text-black text-[10px] font-black flex items-center justify-center shadow">
                  {savedItems.length}
                </span>
              )}
            </Link>

            {/* Language Switcher (EN | தமிழ்) */}
            <button
              type="button"
              onClick={toggleLanguage}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/30 text-amber-300 text-xs font-bold transition-all shadow-sm"
              title="Switch language between English and தமிழ்"
            >
              <Languages className="w-3.5 h-3.5" />
              <span>{language === 'ta' ? 'English' : 'தமிழ்'}</span>
            </button>

            {/* Search Action (Ctrl+K) */}
            <button
              type="button"
              onClick={() => setSearchModalOpen(true)}
              title="Search public records (Ctrl+K)"
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.1] text-xs text-slate-300 hover:text-white transition-all shadow-sm focus:outline-none focus:ring-1 focus:ring-cyan-400"
            >
              <Search className="w-3.5 h-3.5 text-cyan-400" />
              <span className="hidden xl:inline">{language === 'ta' ? 'தேடுக...' : 'Search records'}</span>
              <kbd className="font-mono text-[10px] bg-white/[0.08] px-1.5 py-0.5 rounded text-cyan-300 border border-white/[0.1]">
                ⌘K
              </kbd>
            </button>

            {/* Mobile Search Icon */}
            <button
              type="button"
              onClick={() => setSearchModalOpen(true)}
              aria-label="Open public search"
              className="sm:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 focus:outline-none"
            >
              <Search className="w-4 h-4" />
            </button>

            {/* Backend Status Dot */}
            <button
              type="button"
              onClick={checkStatus}
              aria-label={`Data status: ${backendStatus.online ? 'Online' : 'Offline'}`}
              title={`Data status: ${backendStatus.online ? 'Online' : 'Offline'}. Click to test.`}
              className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/[0.08] text-[11px] text-slate-300 cursor-pointer select-none transition-all"
            >
              <span className={`w-2 h-2 rounded-full relative ${backendStatus.online ? 'bg-emerald-400' : 'bg-emerald-400'}`}>
                <span className="animate-ping absolute inset-0 rounded-full bg-emerald-400 opacity-75" />
              </span>
              <span className="font-mono font-medium text-[10px]">
                {backendStatus.online ? 'Live' : 'Verified'}
              </span>
              <RefreshCw className={`w-2.5 h-2.5 text-cyan-400 ${checking ? 'animate-spin' : 'opacity-60'}`} />
            </button>

            {/* Mobile Hamburger Toggle */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="xl:hidden p-2 rounded-xl text-slate-300 hover:text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-cyan-400"
              aria-label={mobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
              aria-expanded={mobileMenuOpen}
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile & Tablet Slide-Out Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="xl:hidden border-t border-indigo-500/20 bg-[#060c22]/98 backdrop-blur-2xl px-4 py-4 space-y-4 max-h-[85vh] overflow-y-auto custom-scrollbar animate-fade-in-up">
          {/* Mobile Search Bar Trigger */}
          <button
            type="button"
            onClick={() => {
              setMobileMenuOpen(false);
              setSearchModalOpen(true);
            }}
            className="w-full relative flex items-center bg-indigo-950/70 border border-indigo-500/30 rounded-xl px-3 py-2.5 text-xs text-slate-300 text-left focus:outline-none focus:ring-1 focus:ring-cyan-400"
          >
            <Search className="w-4 h-4 text-cyan-400 mr-2 shrink-0" />
            <span>{language === 'ta' ? 'திட்டங்கள், வாக்குறுதிகள், எம்.எல்.ஏ தேடுக...' : 'Search schemes, promises, MLAs, claims...'}</span>
          </button>

          {/* Quick Helplines in Drawer */}
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false);
                setHelplinesOpen(true);
              }}
              className="flex items-center gap-2 p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs font-bold"
            >
              <Phone className="w-4 h-4" />
              <span>{language === 'ta' ? 'உதவி 1100' : 'Helplines 1100'}</span>
            </button>
            <button
              type="button"
              onClick={() => {
                setMobileMenuOpen(false);
                setGlossaryOpen(true);
              }}
              className="flex items-center gap-2 p-2.5 rounded-xl bg-cyan-500/15 border border-cyan-500/30 text-cyan-300 text-xs font-bold"
            >
              <HelpCircle className="w-4 h-4" />
              <span>{language === 'ta' ? 'அரசு சொற்கள்' : 'Civic Glossary'}</span>
            </button>
          </div>

          {/* Primary Citizen Services */}
          <div>
            <div className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider px-2 pb-1.5">
              {language === 'ta' ? 'குடிமக்கள் சேவைகள்' : 'Citizen Services'}
            </div>
            <div className="space-y-1">
              {primaryNavItems.map((item) => {
                const isActive = item.href === '/' ? pathname === '/' : (pathname?.startsWith(item.href) ?? false);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md'
                        : 'text-slate-300 hover:text-white hover:bg-indigo-950/60'
                    }`}
                  >
                    <span>{language === 'ta' ? item.name_ta : item.name}</span>
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Explore All Features */}
          <div className="pt-2 border-t border-indigo-500/20">
            <div className="text-[10px] font-bold text-cyan-400 uppercase tracking-wider px-2 pb-1.5 flex items-center justify-between">
              <span>{language === 'ta' ? 'ஆராய்ச்சி பிரிவுகள்' : 'Civic Intelligence Lab'}</span>
              <Link
                href="/explore"
                onClick={() => setMobileMenuOpen(false)}
                className="text-cyan-400 hover:underline"
              >
                {language === 'ta' ? 'அனைத்தும்' : 'All Features'}
              </Link>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-1.5">
              {exploreNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = pathname?.startsWith(item.href) ?? false;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs transition-colors ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-300 font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-indigo-950/60'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                    <span>{language === 'ta' ? item.name_ta : item.name}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Reusable Modals Mounted in Layout */}
      <SearchModal
        isOpen={searchModalOpen}
        onClose={() => setSearchModalOpen(false)}
      />
      <CitizenHelplinesModal
        isOpen={helplinesOpen}
        onClose={() => setHelplinesOpen(false)}
      />
      <CitizenGlossaryModal
        isOpen={glossaryOpen}
        onClose={() => setGlossaryOpen(false)}
      />
    </header>
  );
};
