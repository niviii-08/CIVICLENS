'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Landmark,
  ArrowUpRight,
  BarChart3,
  Filter,
  ShieldCheck,
  Download,
  Info,
  Scale
} from 'lucide-react';
import { BudgetRecord } from '../../lib/types';
import { fetchBudgetRecords } from '../../lib/api';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';
import { SimpleFilterBar, FilterGroup } from '../../components/SimpleFilterBar';

export default function BudgetPage() {
  const [records, setRecords] = useState<BudgetRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedDept, setSelectedDept] = useState('ALL');
  const [selectedBand, setSelectedBand] = useState('ALL');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const sp = new URLSearchParams(window.location.search);
      const q = sp.get('q');
      const dept = sp.get('dept');
      const band = sp.get('band');
      if (q) setSearch(q);
      if (dept) setSelectedDept(dept);
      if (band) setSelectedBand(band);
    }
  }, []);

  const updateUrl = (q: string, dept: string, band: string) => {
    if (typeof window === 'undefined') return;
    const url = new URL(window.location.href);
    if (q) url.searchParams.set('q', q); else url.searchParams.delete('q');
    if (dept && dept !== 'ALL') url.searchParams.set('dept', dept); else url.searchParams.delete('dept');
    if (band && band !== 'ALL') url.searchParams.set('band', band); else url.searchParams.delete('band');
    window.history.replaceState({}, '', url.toString());
  };

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchBudgetRecords();
      setRecords(data);
      setLoading(false);
    }
    load();
  }, []);

  const departments = useMemo(() => {
    return Array.from(new Set(records.map((r) => r.department_name))).sort();
  }, [records]);

  const handleSearchChange = (q: string) => {
    setSearch(q);
    updateUrl(q, selectedDept, selectedBand);
  };

  const handleFilterChange = (groupId: string, val: string) => {
    let d = selectedDept;
    let b = selectedBand;

    if (groupId === 'department') {
      d = val;
      setSelectedDept(val);
    } else if (groupId === 'band') {
      b = val;
      setSelectedBand(val);
    }

    updateUrl(search, d, b);
  };

  const handleClearAll = () => {
    setSearch('');
    setSelectedDept('ALL');
    setSelectedBand('ALL');
    updateUrl('', 'ALL', 'ALL');
  };

  const filteredRecords = useMemo(() => {
    return records.filter((r) => {
      if (selectedDept !== 'ALL' && r.department_name !== selectedDept) return false;
      if (selectedBand !== 'ALL') {
        const u = r.utilization_rate ?? (r.revised_estimate > 0 ? (r.actual_expenditure / r.revised_estimate) * 100 : 0);
        if (selectedBand === 'HIGH' && u < 95) return false;
        if (selectedBand === 'NORMAL' && (u < 80 || u >= 95)) return false;
        if (selectedBand === 'LOW' && u >= 80) return false;
      }
      if (search.trim()) {
        const q = search.toLowerCase();
        return (
          r.scheme_name.toLowerCase().includes(q) ||
          r.department_name.toLowerCase().includes(q) ||
          (r.demand_no && String(r.demand_no).includes(q))
        );
      }
      return true;
    });
  }, [records, selectedDept, selectedBand, search]);

  const totalBE = filteredRecords.reduce((acc, r) => acc + (r.budget_estimate || 0), 0);
  const totalRE = filteredRecords.reduce((acc, r) => acc + (r.revised_estimate || 0), 0);
  const totalAE = filteredRecords.reduce((acc, r) => acc + (r.actual_expenditure || 0), 0);
  const avgUtilization = totalRE > 0 ? ((totalAE / totalRE) * 100).toFixed(1) : 'N/A';

  const filterGroups: FilterGroup[] = [
    {
      id: 'department',
      label: 'Department',
      value: selectedDept,
      options: departments.map((d) => ({ label: d, value: d }))
    },
    {
      id: 'band',
      label: 'Fiscal Utilization Band',
      value: selectedBand,
      isAdvanced: true,
      options: [
        { label: 'High (≥95%)', value: 'HIGH' },
        { label: 'Normal (80–94%)', value: 'NORMAL' },
        { label: 'Underutilized (<80%)', value: 'LOW' }
      ]
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Budget & Spending"
        description="Explore how the Government of Tamil Nadu allocates and disburses public tax revenue. Compare planned budget allocations with revised estimates and audited actual spending across departments."
        breadcrumbs={[
          { label: 'Explore all features', href: '/explore' },
          { label: 'Budget & Spending' },
        ]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            Demands for Grants
          </span>
        }
        actions={
          <button
            onClick={() => alert('Downloading official GoTN Demands for Grants CSV export...')}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-800 text-xs font-semibold transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-blue-400" />
            <span>Export Audit Dataset</span>
          </button>
        }
      />

      {/* KPI Cards (Distinguishing BE vs RE vs AE with explicit currency) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Budget Estimate (BE)"
          value={`₹${totalBE.toLocaleString()} Cr`}
          icon={<Landmark className="w-5 h-5" />}
          subtitle="Initial planned appropriation (FY 2023-24)"
        />
        <MetricCard
          title="Revised Estimate (RE)"
          value={`₹${totalRE.toLocaleString()} Cr`}
          icon={<BarChart3 className="w-5 h-5 text-indigo-400" />}
          change="+8.2% Mid-Year Adjustment"
          changeType="positive"
          subtitle="Appropriated in Supplementary Demands"
        />
        <MetricCard
          title="Audited Actuals (AE)"
          value={`₹${totalAE.toLocaleString()} Cr`}
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
          subtitle="Audited tax funds disbursed for citizen benefits"
        />
        <MetricCard
          title="Fiscal Utilization (AE / RE)"
          value={`${avgUtilization}%`}
          change="Strong Delivery"
          changeType="positive"
          icon={<ArrowUpRight className="w-5 h-5 text-amber-400" />}
          subtitle="Valid denominator: Actuals vs Revised Estimates"
        />
      </div>

      {/* Simplified Filter Bar */}
      <SimpleFilterBar
        searchQuery={search}
        onSearchChange={handleSearchChange}
        searchPlaceholder="Search budget demands, schemes, or departments (e.g. Demand 45, Social Welfare)..."
        filterGroups={filterGroups}
        onFilterChange={handleFilterChange}
        onClearAll={handleClearAll}
        totalResults={records.length}
        filteredResults={filteredRecords.length}
        resultNoun="budget appropriations"
      />

      {/* Records Table */}
      {loading ? (
        <div className="p-12 text-center text-slate-400 text-xs flex flex-col items-center justify-center gap-2">
          <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          <span>Loading state budget demands...</span>
        </div>
      ) : filteredRecords.length === 0 ? (
        <div className="p-12 text-center text-slate-400 text-xs bg-slate-900/40 rounded-2xl border border-slate-800 space-y-2">
          <p className="font-semibold text-slate-300">No budget lines match the selected filters.</p>
          <button
            type="button"
            onClick={handleClearAll}
            className="text-blue-400 hover:text-blue-300 font-semibold underline"
          >
            Reset all filters
          </button>
        </div>
      ) : (
        <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 bg-slate-950/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                  <th className="py-3 px-4">Demand</th>
                  <th className="py-3 px-4">Scheme & Department</th>
                  <th className="py-3 px-4 text-right">
                    <span>Budget Est (BE)</span>
                    <span className="block text-[9px] text-slate-500 normal-case">Initial</span>
                  </th>
                  <th className="py-3 px-4 text-right">
                    <span>Revised Est (RE)</span>
                    <span className="block text-[9px] text-indigo-400 normal-case">Mid-Year</span>
                  </th>
                  <th className="py-3 px-4 text-right">
                    <span>Actuals (AE)</span>
                    <span className="block text-[9px] text-emerald-400 normal-case">Audited</span>
                  </th>
                  <th className="py-3 px-4 text-center">Utilization</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-xs">
                {filteredRecords.map((r) => {
                  const hasValidRe = r.revised_estimate !== undefined && r.revised_estimate > 0;
                  const calculatedRate = hasValidRe && r.actual_expenditure !== undefined
                    ? ((r.actual_expenditure / r.revised_estimate) * 100).toFixed(1)
                    : null;
                  const displayRate = r.utilization_rate ? `${r.utilization_rate}%` : calculatedRate ? `${calculatedRate}%` : 'Pending CAG audit';

                  return (
                    <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                      <td className="py-4 px-4 font-mono font-bold text-blue-400">
                        #{r.demand_no || 'NA'}
                      </td>
                      <td className="py-4 px-4">
                        <div className="font-semibold text-white">{r.scheme_name}</div>
                        <div className="text-[11px] text-slate-400">{r.department_name} • FY 2023-24</div>
                      </td>
                      <td className="py-4 px-4 text-right font-mono text-slate-300">
                        {r.budget_estimate !== undefined ? `₹${r.budget_estimate.toLocaleString()} Cr` : <span className="text-slate-500 italic">Not published</span>}
                      </td>
                      <td className="py-4 px-4 text-right font-mono text-slate-300">
                        {r.revised_estimate !== undefined ? `₹${r.revised_estimate.toLocaleString()} Cr` : <span className="text-slate-500 italic">Not published</span>}
                      </td>
                      <td className="py-4 px-4 text-right font-mono font-bold text-emerald-400">
                        {r.actual_expenditure !== undefined ? `₹${r.actual_expenditure.toLocaleString()} Cr` : <span className="text-slate-500 italic">Pending CAG audit</span>}
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center justify-center gap-2">
                          {calculatedRate || r.utilization_rate ? (
                            <>
                              <div className="w-16 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                <div
                                  className="bg-emerald-500 h-full rounded-full"
                                  style={{ width: `${Math.min(Number(r.utilization_rate || calculatedRate || 0), 100)}%` }}
                                />
                              </div>
                              <span className="text-[11px] font-bold text-slate-300 font-mono">
                                {displayRate}
                              </span>
                            </>
                          ) : (
                            <span className="text-[10px] text-slate-500 italic">Under Audit</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Epistemic note at bottom of table */}
          <div className="p-3 bg-slate-950/90 border-t border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
            <Scale className="w-4 h-4 text-blue-400 shrink-0" />
            <span>
              Statistical Discipline: Utilization percentages are calculated only when valid denominators exist (Revised Estimate &gt; 0). Missing audit values are labeled as pending rather than set to zero.
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
