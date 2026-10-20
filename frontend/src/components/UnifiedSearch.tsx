'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Search,
  X,
  Loader2,
  ArrowRight,
  AlertCircle,
  ShieldCheck,
  Filter,
  CheckCircle2,
  ExternalLink
} from 'lucide-react';
import { fetchUnifiedSearch } from '../lib/api';
import { UnifiedSearchResult, UnifiedSearchResponse } from '../lib/types';
import { CivicStateNotice } from './CivicStateNotice';

export interface UnifiedSearchProps {
  initialQuery?: string;
  initialCategory?: string;
  placeholder?: string;
  variant?: 'hero' | 'compact' | 'modal';
  onNavigate?: () => void;
  className?: string;
}

const CATEGORY_TABS = [
  { key: 'all', label: 'All Records' },
  { key: 'scheme', label: 'Schemes' },
  { key: 'promise', label: 'Promises' },
  { key: 'representative', label: 'MLAs' },
  { key: 'civic', label: 'Civic Issues' },
  { key: 'claim', label: 'Claims' },
  { key: 'policy', label: 'Policy Results' },
  { key: 'budget', label: 'Budget' },
  { key: 'funding', label: 'Funding' },
  { key: 'news', label: 'News' }
];

export const UnifiedSearch: React.FC<UnifiedSearchProps> = ({
  initialQuery = '',
  initialCategory = 'all',
  placeholder = 'Search a scheme, department, representative or issue...',
  variant = 'hero',
  onNavigate,
  className = ''
}) => {
  const [query, setQuery] = useState(initialQuery);
  const [activeQuery, setActiveQuery] = useState(initialQuery);
  const [category, setCategory] = useState(initialCategory);
  const [results, setResults] = useState<UnifiedSearchResult[]>([]);
  const [categoryCounts, setCategoryCounts] = useState<Record<string, number>>({});
  const [totalCount, setTotalCount] = useState(0);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  const searchSeqRef = useRef(0);

  const executeSearch = async (searchTerm: string, selectedCat: string = category) => {
    const trimmed = searchTerm.trim();
    if (!trimmed) {
      setResults([]);
      setTotalCount(0);
      setHasSearched(false);
      setSearchError(null);
      return;
    }

    const currentSeq = ++searchSeqRef.current;
    setIsSearching(true);
    setSearchError(null);
    setActiveQuery(trimmed);

    try {
      const data: UnifiedSearchResponse = await fetchUnifiedSearch(trimmed, selectedCat, 1, 30);
      // Ensure stale out-of-order response does not overwrite latest search
      if (currentSeq === searchSeqRef.current) {
        setResults(data.items || []);
        setCategoryCounts(data.categories || {});
        setTotalCount(data.total || 0);
        setHasSearched(true);
      }
    } catch (err) {
      if (currentSeq === searchSeqRef.current) {
        setSearchError('Unable to search public records right now. Please check your connection to the server.');
        setResults([]);
        setTotalCount(0);
        setHasSearched(true);
      }
    } finally {
      if (currentSeq === searchSeqRef.current) {
        setIsSearching(false);
      }
    }
  };

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    executeSearch(query, category);
  };

  const handleClear = () => {
    setQuery('');
    setActiveQuery('');
    setResults([]);
    setTotalCount(0);
    setHasSearched(false);
    setSearchError(null);
    setCategory('all');
  };

  const handleCategoryChange = (newCat: string) => {
    setCategory(newCat);
    if (activeQuery) {
      executeSearch(activeQuery, newCat);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Escape') {
      handleClear();
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Search Input Bar */}
      <form onSubmit={handleSubmit} className="relative w-full" role="search">
        <label htmlFor="unified-search-input" className="sr-only">
          Search public records across Tamil Nadu
        </label>
        <div className="relative flex items-center">
          <Search className="w-5 h-5 text-slate-400 absolute left-4 pointer-events-none" />
          <input
            id="unified-search-input"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            aria-label={placeholder}
            className={`w-full bg-slate-900/90 border border-slate-700/80 rounded-2xl pl-12 pr-28 text-white placeholder-slate-400 shadow-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all ${
              variant === 'hero' ? 'py-3.5 text-sm sm:text-base' : 'py-2.5 text-xs sm:text-sm'
            }`}
          />
          {query && (
            <button
              type="button"
              onClick={handleClear}
              aria-label="Clear search input"
              className="absolute right-24 p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            type="submit"
            disabled={!query.trim() || isSearching}
            className={`absolute right-2 px-4 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:hover:bg-blue-600 text-white font-semibold shadow-md transition-all flex items-center gap-1.5 ${
              variant === 'hero' ? 'py-2 text-xs sm:text-sm' : 'py-1.5 text-xs'
            }`}
          >
            {isSearching ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Searching</span>
              </>
            ) : (
              <span>Search</span>
            )}
          </button>
        </div>
      </form>

      {/* Category Filter Pills (rendered once a search is active) */}
      {hasSearched && !searchError && (
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 custom-scrollbar">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0 mr-1" />
          {CATEGORY_TABS.map((tab) => {
            const count = categoryCounts[tab.key] ?? (tab.key === 'all' ? totalCount : 0);
            if (tab.key !== 'all' && count === 0) return null; // Hide empty categories
            const isSelected = category === tab.key;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => handleCategoryChange(tab.key)}
                className={`px-3 py-1 rounded-xl text-xs font-semibold whitespace-nowrap transition-colors flex items-center gap-1.5 ${
                  isSelected
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                    : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                <span>{tab.label}</span>
                <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isSelected ? 'bg-blue-500 text-white' : 'bg-slate-800 text-slate-400'}`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* Results / Error / Empty States */}
      {hasSearched && (
        <div aria-live="polite" className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h2 className="text-base sm:text-lg font-bold text-white">
                Results for &ldquo;{activeQuery}&rdquo;
              </h2>
              <span className="text-xs text-slate-400">
                Found {totalCount} {totalCount === 1 ? 'record' : 'records'} across public categories
              </span>
            </div>
            <button
              onClick={handleClear}
              className="text-xs font-semibold text-slate-400 hover:text-white px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-900 hover:bg-slate-800 transition-colors"
            >
              Clear search
            </button>
          </div>

          {searchError ? (
            <CivicStateNotice
              state="failed_api_request"
              title="Search Service Interrupted"
              description={searchError}
              onRetry={() => executeSearch(activeQuery, category)}
            />
          ) : results.length === 0 ? (
            <CivicStateNotice
              state="no_matching_results"
              title="No Matching Public Records Found"
              description={`No public records matched "${activeQuery}" ${category !== 'all' ? `in category "${category}"` : 'across public categories'}. Try broader terms like "breakfast", "magalir", or "water".`}
              queryOrFilter={activeQuery}
              onClearFilters={category !== 'all' ? () => handleCategoryChange('all') : undefined}
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {results.map((item) => (
                <div
                  key={`${item.type}-${item.id}`}
                  className="rounded-2xl bg-slate-900/80 border border-slate-800 p-5 space-y-3 hover:border-slate-700 transition-all flex flex-col justify-between group"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between gap-2">
                      <span
                        className={`text-[11px] font-bold px-2.5 py-0.5 rounded-full border ${
                          item.badge || 'bg-slate-800 text-slate-300 border-slate-700'
                        }`}
                      >
                        {item.type_label}
                      </span>
                      {item.date_or_period && (
                        <span className="text-xs text-slate-400 truncate max-w-[180px]">
                          {item.date_or_period}
                        </span>
                      )}
                    </div>

                    <h3 className="text-sm sm:text-base font-bold text-white leading-snug group-hover:text-blue-400 transition-colors">
                      {item.title}
                    </h3>

                    <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                      {item.description}
                    </p>

                    {item.department_or_entity && (
                      <p className="text-[11px] text-slate-400 truncate">
                        Department / Entity: <span className="text-slate-300">{item.department_or_entity}</span>
                      </p>
                    )}
                  </div>

                  <div className="pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    {item.evidence_available ? (
                      <span className="inline-flex items-center gap-1 text-[11px] text-emerald-400 font-medium">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span>Documented Evidence</span>
                      </span>
                    ) : (
                      <span className="text-[11px] text-slate-400">Public Record</span>
                    )}

                    <Link
                      href={item.route}
                      onClick={() => onNavigate && onNavigate()}
                      aria-label={`Open record details for ${item.title}`}
                      className="inline-flex items-center gap-1 font-semibold text-blue-400 hover:text-blue-300 transition-colors focus-visible:ring-2 focus-visible:ring-blue-500 rounded-lg px-2 py-1"
                    >
                      <span>Open record</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
