'use client';

import React, { useState } from 'react';
import {
  Search,
  Filter,
  X,
  ChevronDown,
  ChevronUp,
  RotateCcw,
  SlidersHorizontal,
  Check
} from 'lucide-react';

export interface FilterOption {
  label: string;
  value: string;
  count?: number;
}

export interface FilterGroup {
  id: string;
  label: string;
  options: FilterOption[];
  value: string;
  isAdvanced?: boolean;
}

export interface SimpleFilterBarProps {
  searchQuery: string;
  onSearchChange: (query: string) => void;
  searchPlaceholder?: string;
  filterGroups: FilterGroup[];
  onFilterChange: (groupId: string, value: string) => void;
  onClearAll: () => void;
  totalResults: number;
  filteredResults: number;
  resultNoun?: string;
  className?: string;
}

export const SimpleFilterBar: React.FC<SimpleFilterBarProps> = ({
  searchQuery,
  onSearchChange,
  searchPlaceholder = 'Search records by keyword, name, or description...',
  filterGroups,
  onFilterChange,
  onClearAll,
  totalResults,
  filteredResults,
  resultNoun = 'records',
  className = ''
}) => {
  const [showMoreFilters, setShowMoreFilters] = useState<boolean>(false);

  const primaryGroups = filterGroups.filter((g) => !g.isAdvanced);
  const advancedGroups = filterGroups.filter((g) => g.isAdvanced);

  // Active filters calculation
  const activeFilters = filterGroups.filter(
    (g) => g.value && g.value !== 'ALL' && g.value !== ''
  );
  const hasActiveFilters = activeFilters.length > 0 || searchQuery.trim().length > 0;
  const activeAdvancedCount = advancedGroups.filter(
    (g) => g.value && g.value !== 'ALL' && g.value !== ''
  ).length;

  return (
    <div className={`p-4 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3.5 shadow-md ${className}`}>
      {/* 1. Main Search & Primary Filters */}
      <div className="flex flex-col md:flex-row items-stretch md:items-center gap-3">
        {/* Search input */}
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder={searchPlaceholder}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-9 pr-9 py-2.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={() => onSearchChange('')}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white p-0.5 rounded transition-colors"
              title="Clear search text"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {/* Primary Dropdowns / Filters */}
        <div className="flex flex-wrap items-center gap-2">
          {primaryGroups.map((group) => (
            <div key={group.id} className="relative min-w-[130px]">
              <select
                aria-label={`Filter by ${group.label}`}
                value={group.value}
                onChange={(e) => onFilterChange(group.id, e.target.value)}
                className={`w-full bg-slate-950 border rounded-xl px-3 py-2 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-blue-500 transition-all cursor-pointer ${
                  group.value && group.value !== 'ALL'
                    ? 'border-blue-500/60 text-blue-300 bg-blue-950/20'
                    : 'border-slate-800 text-slate-300 hover:border-slate-700'
                }`}
              >
                <option value="ALL">All {group.label}s</option>
                {group.options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label} {opt.count !== undefined ? `(${opt.count})` : ''}
                  </option>
                ))}
              </select>
            </div>
          ))}

          {/* More Filters Toggle (Progressive Disclosure) */}
          {advancedGroups.length > 0 && (
            <button
              type="button"
              onClick={() => setShowMoreFilters(!showMoreFilters)}
              className={`px-3 py-2 rounded-xl text-xs font-semibold border flex items-center gap-1.5 transition-all ${
                showMoreFilters || activeAdvancedCount > 0
                  ? 'bg-slate-800 text-blue-300 border-blue-500/40'
                  : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-white hover:border-slate-700'
              }`}
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span>More filters</span>
              {activeAdvancedCount > 0 && (
                <span className="w-4 h-4 rounded-full bg-blue-600 text-white text-[10px] flex items-center justify-center font-bold">
                  {activeAdvancedCount}
                </span>
              )}
              {showMoreFilters ? (
                <ChevronUp className="w-3.5 h-3.5" />
              ) : (
                <ChevronDown className="w-3.5 h-3.5" />
              )}
            </button>
          )}
        </div>
      </div>

      {/* 2. Expandable "More filters" section */}
      {showMoreFilters && advancedGroups.length > 0 && (
        <div className="p-3.5 rounded-xl bg-slate-950/70 border border-slate-800/80 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3 pt-3">
          {advancedGroups.map((group) => (
            <div key={group.id} className="space-y-1">
              <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                {group.label}
              </label>
              <select
                value={group.value}
                onChange={(e) => onFilterChange(group.id, e.target.value)}
                className={`w-full bg-slate-900 border rounded-xl px-3 py-1.5 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500 ${
                  group.value && group.value !== 'ALL'
                    ? 'border-blue-500/50 text-blue-300'
                    : 'border-slate-800 text-slate-300'
                }`}
              >
                <option value="ALL">All {group.label}s</option>
                {group.options.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label} {opt.count !== undefined ? `(${opt.count})` : ''}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      )}

      {/* 3. Active Filters Chips & Clear All */}
      <div className="flex flex-wrap items-center justify-between gap-2 pt-1 border-t border-slate-800/80 text-xs">
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-slate-400 font-medium">
            Showing <strong className="text-white">{filteredResults}</strong>
            {filteredResults !== totalResults ? ` of ${totalResults}` : ''} {resultNoun}
          </span>

          {/* Active chips */}
          {searchQuery.trim() && (
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-300 border border-blue-500/20 text-[11px]">
              <span>Search: "{searchQuery}"</span>
              <button
                type="button"
                onClick={() => onSearchChange('')}
                className="hover:text-white"
              >
                <X className="w-3 h-3" />
              </button>
            </span>
          )}

          {activeFilters.map((group) => {
            const selectedOpt = group.options.find((o) => o.value === group.value);
            const labelText = selectedOpt ? selectedOpt.label : group.value;
            return (
              <span
                key={group.id}
                className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-slate-800 text-slate-200 border border-slate-700 text-[11px]"
              >
                <span className="text-slate-400">{group.label}:</span>
                <span className="font-semibold text-white">{labelText}</span>
                <button
                  type="button"
                  onClick={() => onFilterChange(group.id, 'ALL')}
                  className="text-slate-400 hover:text-white p-0.5"
                  title={`Remove ${group.label} filter`}
                >
                  <X className="w-3 h-3" />
                </button>
              </span>
            );
          })}
        </div>

        {/* Clear All action */}
        {hasActiveFilters && (
          <button
            type="button"
            onClick={onClearAll}
            className="inline-flex items-center gap-1 text-[11px] font-semibold text-rose-400 hover:text-rose-300 transition-colors ml-auto px-2 py-0.5 rounded hover:bg-rose-500/10"
          >
            <RotateCcw className="w-3 h-3" />
            <span>Clear filters</span>
          </button>
        )}
      </div>
    </div>
  );
};
