'use client';

import React, { useState, useEffect } from 'react';
import { Landmark, ArrowUpRight, BarChart3, Filter, ShieldCheck, Download } from 'lucide-react';
import { BudgetRecord } from '../../lib/types';
import { fetchBudgetRecords } from '../../lib/api';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';

export default function BudgetPage() {
  const [records, setRecords] = useState<BudgetRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedDept, setSelectedDept] = useState('ALL');

  useEffect(() => {
    async function load() {
      setLoading(true);
      const data = await fetchBudgetRecords();
      setRecords(data);
      setLoading(false);
    }
    load();
  }, []);

  const departments = Array.from(new Set(records.map((r) => r.department_name)));

  const filteredRecords = selectedDept === 'ALL'
    ? records
    : records.filter((r) => r.department_name === selectedDept);

  const totalBE = records.reduce((acc, r) => acc + (r.budget_estimate || 0), 0);
  const totalRE = records.reduce((acc, r) => acc + (r.revised_estimate || 0), 0);
  const totalAE = records.reduce((acc, r) => acc + (r.actual_expenditure || 0), 0);
  const avgUtilization = (totalAE / totalRE * 100).toFixed(1);

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

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Sample Budget Estimate (BE)"
          value={`₹${totalBE.toLocaleString()} Cr`}
          icon={<Landmark className="w-5 h-5" />}
          subtitle="Initial budget outlay"
        />
        <MetricCard
          title="Revised Estimate (RE)"
          value={`₹${totalRE.toLocaleString()} Cr`}
          icon={<BarChart3 className="w-5 h-5 text-indigo-400" />}
          change="+8.2% Adjustment"
          changeType="positive"
          subtitle="Mid-year appropriation"
        />
        <MetricCard
          title="Audited Actuals (AE)"
          value={`₹${totalAE.toLocaleString()} Cr`}
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
          subtitle="Disbursed & verified funds"
        />
        <MetricCard
          title="Overall Fiscal Utilization"
          value={`${avgUtilization}%`}
          change="Strong Delivery"
          changeType="positive"
          icon={<ArrowUpRight className="w-5 h-5 text-amber-400" />}
          subtitle="Actuals vs Revised Estimates"
        />
      </div>

      {/* Filter Row */}
      <div className="p-4 rounded-2xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <span className="text-xs font-semibold text-slate-300">Filter Department:</span>
        </div>
        <select
          value={selectedDept}
          onChange={(e) => setSelectedDept(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-blue-500"
        >
          <option value="ALL">All Departments ({departments.length})</option>
          {departments.map((dept) => (
            <option key={dept} value={dept}>
              {dept}
            </option>
          ))}
        </select>
      </div>

      {/* Records Table */}
      <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <th className="py-3 px-4">Demand</th>
                <th className="py-3 px-4">Scheme & Department</th>
                <th className="py-3 px-4 text-right">Budget Est (BE)</th>
                <th className="py-3 px-4 text-right">Revised Est (RE)</th>
                <th className="py-3 px-4 text-right">Actuals (AE)</th>
                <th className="py-3 px-4 text-center">Utilization</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {filteredRecords.map((r) => (
                <tr key={r.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-4 px-4 font-mono font-bold text-blue-400">
                    #{r.demand_no || 'NA'}
                  </td>
                  <td className="py-4 px-4">
                    <div className="font-semibold text-white">{r.scheme_name}</div>
                    <div className="text-[11px] text-slate-400">{r.department_name}</div>
                  </td>
                  <td className="py-4 px-4 text-right font-mono text-slate-300">
                    ₹{r.budget_estimate.toLocaleString()} Cr
                  </td>
                  <td className="py-4 px-4 text-right font-mono text-slate-300">
                    ₹{r.revised_estimate.toLocaleString()} Cr
                  </td>
                  <td className="py-4 px-4 text-right font-mono font-bold text-emerald-400">
                    ₹{r.actual_expenditure.toLocaleString()} Cr
                  </td>
                  <td className="py-4 px-4">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-20 bg-slate-800 h-1.5 rounded-full overflow-hidden">
                        <div
                          className="bg-emerald-500 h-full rounded-full"
                          style={{ width: `${Math.min(r.utilization_rate || 95, 100)}%` }}
                        />
                      </div>
                      <span className="text-[11px] font-bold text-slate-300 font-mono">
                        {r.utilization_rate || 95}%
                      </span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
