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
  Layers,
  Sparkles
} from 'lucide-react';
import { checkBackendHealth } from '../lib/api';
import { SearchModal } from './SearchModal';

// 7 Citizen-First Primary Navigation Categories
export const primaryNavItems = [
  { name: 'Home', href: '/' },
  { name: 'Government Schemes', href: '/schemes' },
  { name: 'Promises & Progress', href: '/promises' },
  { name: 'Representatives', href: '/representatives' },
  { name: 'Civic Issues', href: '/civic' },
  { name: 'Verify Claims', href: '/claims' },
  { name: 'Policy Results', href: '/policy-evaluation' },
];

// Explore All Features (Civic Intelligence Lab)
export const exploreNavItems = [
  { name: 'Budget & Spending', href: '/budget', icon: Landmark, desc: 'Budget estimates & actual allocations' },
  { name: 'Political Funding', href: '/funding', icon: CreditCard, desc: 'ECI Form 24A & Electoral Trusts' },
  { name: 'News Coverage', href: '/news', icon: Newspaper, desc: 'Tamil & English media framing' },
  { name: 'Explore Evidence', href: '/graph', icon: Network, desc: 'Dialectical multi-hop evidence graph' },
];

export const Header: React.FC = () => {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [exploreDropdownOpen, setExploreDropdownOpen] = useState(false);
  const [searchModalOpen, setSearchModalOpen] = useState(false);
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
    <header className="sticky top-0 z-50 bg-slate-950/90 backdrop-blur-xl border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          {/* Brand Wordmark & Descriptor */}
          <div className="flex items-center gap-3 shrink-0">
            <Link
              href="/"
              className="flex items-center gap-2.5 group focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg p-1"
            >
              <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-md shadow-blue-500/20 group-hover:scale-105 transition-transform">
                <Compass className="w-4 h-4 text-white" />
              </div>
              <div className="flex flex-col">
                <div className="flex items-center gap-1.5">
                  <span className="font-extrabold text-base tracking-tight text-white group-hover:text-blue-400 transition-colors">
                    CIVICLENS
                  </span>
                  <span className="text-[10px] font-extrabold px-1.5 py-0.2 rounded bg-red-600/20 text-red-400 border border-red-500/30">
                    TN
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-medium hidden sm:inline leading-none">
                  Public Information for Tamil Nadu
                </span>
              </div>
            </Link>
          </div>

          {/* Desktop Primary Navigation */}
          <nav className="hidden xl:flex items-center space-x-1" aria-label="Main Navigation">
            {primaryNavItems.map((item) => {
              const isActive = item.href === '/' ? pathname === '/' : (pathname?.startsWith(item.href) ?? false);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/70'
                  }`}
                  aria-current={isActive ? 'page' : undefined}
                >
                  {item.name}
                </Link>
              );
            })}

            {/* Explore All Features Dropdown */}
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setExploreDropdownOpen(!exploreDropdownOpen)}
                className={`inline-flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all whitespace-nowrap focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                  isExploreActive
                    ? 'bg-slate-800 text-white border border-slate-700'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/70'
                }`}
                aria-expanded={exploreDropdownOpen}
                aria-haspopup="true"
              >
                <span>Explore all</span>
                <ChevronDown
                  className={`w-3.5 h-3.5 transition-transform duration-200 ${
                    exploreDropdownOpen ? 'rotate-180' : ''
                  }`}
                />
              </button>

              {/* Flyout Menu */}
              {exploreDropdownOpen && (
                <div className="absolute right-0 mt-2 w-72 rounded-2xl bg-slate-900 border border-slate-800 p-2 shadow-2xl backdrop-blur-2xl animate-fadeIn z-50">
                  <div className="px-3 py-1.5 text-[10px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-800/80 mb-1">
                    Civic Intelligence Lab
                  </div>
                  {exploreNavItems.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname?.startsWith(item.href) ?? false;
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        onClick={() => setExploreDropdownOpen(false)}
                        className={`flex items-start gap-2.5 p-2 rounded-xl text-xs transition-colors group ${
                          isActive ? 'bg-blue-600/15 text-blue-400' : 'hover:bg-slate-800 text-slate-200'
                        }`}
                      >
                        <div className="p-1.5 rounded-lg bg-slate-800 group-hover:bg-slate-700 text-blue-400 mt-0.5">
                          <Icon className="w-3.5 h-3.5" />
                        </div>
                        <div>
                          <div className="font-semibold text-white group-hover:text-blue-400 transition-colors">
                            {item.name}
                          </div>
                          <div className="text-[11px] text-slate-400 leading-tight">
                            {item.desc}
                          </div>
                        </div>
                      </Link>
                    );
                  })}
                  <div className="pt-1 mt-1 border-t border-slate-800/80">
                    <Link
                      href="/explore"
                      onClick={() => setExploreDropdownOpen(false)}
                      className="block text-center py-1.5 text-[11px] font-bold text-blue-400 hover:text-blue-300 transition-colors"
                    >
                      View All Features Directory →
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </nav>

          {/* Right Header Controls */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Search Action */}
            <button
              type="button"
              onClick={() => setSearchModalOpen(true)}
              title="Search public records (Ctrl+K)"
              className="hidden sm:inline-flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 hover:text-white transition-all focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <Search className="w-3.5 h-3.5 text-slate-400" />
              <span>Search public records</span>
              <kbd className="hidden lg:inline-block font-mono text-[10px] bg-slate-800 px-1.5 py-0.5 rounded text-slate-400 border border-slate-700">
                Ctrl K
              </kbd>
            </button>

            {/* Mobile Search Icon */}
            <button
              type="button"
              onClick={() => setSearchModalOpen(true)}
              aria-label="Open public search"
              className="sm:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <Search className="w-4 h-4" />
            </button>

            {/* Backend Status Dot */}
            <div
              onClick={checkStatus}
              title={`Flask Backend: ${backendStatus.online ? 'Online' : 'Offline'}. Click to test.`}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] text-slate-400 cursor-pointer select-none hover:border-slate-700"
            >
              <span
                className={`w-2 h-2 rounded-full ${
                  backendStatus.online ? 'bg-emerald-400' : 'bg-amber-400'
                }`}
              />
              <span className="hidden md:inline font-mono">
                {backendStatus.online ? 'API Online' : 'API Offline'}
              </span>
              <RefreshCw className={`w-2.5 h-2.5 ${checking ? 'animate-spin' : 'opacity-40'}`} />
            </div>

            {/* Mobile Hamburger Toggle */}
            <button
              type="button"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="xl:hidden p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
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
        <div className="xl:hidden border-t border-slate-800 bg-slate-950/98 backdrop-blur-2xl px-4 py-4 space-y-4 max-h-[85vh] overflow-y-auto custom-scrollbar animate-fadeIn">
          {/* Mobile Search Bar Trigger */}
          <button
            type="button"
            onClick={() => {
              setMobileMenuOpen(false);
              setSearchModalOpen(true);
            }}
            className="w-full relative flex items-center bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-400 text-left focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <Search className="w-4 h-4 text-slate-400 mr-2 shrink-0" />
            <span>Search schemes, promises, claims...</span>
          </button>

          {/* Primary Citizen Services */}
          <div>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 pb-1.5">
              Citizen Services
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
                        ? 'bg-blue-600 text-white shadow-sm'
                        : 'text-slate-300 hover:text-white hover:bg-slate-900'
                    }`}
                  >
                    <span>{item.name}</span>
                    {isActive && <span className="w-1.5 h-1.5 rounded-full bg-white" />}
                  </Link>
                );
              })}
            </div>
          </div>

          {/* Explore All Features */}
          <div className="pt-2 border-t border-slate-800/80">
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider px-2 pb-1.5 flex items-center justify-between">
              <span>Civic Intelligence Lab</span>
              <Link
                href="/explore"
                onClick={() => setMobileMenuOpen(false)}
                className="text-blue-400 hover:underline"
              >
                All Features
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
                        ? 'bg-blue-600/15 text-blue-400 font-semibold'
                        : 'text-slate-300 hover:text-white hover:bg-slate-900'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5 text-blue-400 shrink-0" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Global Unified Search Modal (Ctrl+K) */}
      <SearchModal
        isOpen={searchModalOpen}
        onClose={() => setSearchModalOpen(false)}
      />
    </header>
  );
};
