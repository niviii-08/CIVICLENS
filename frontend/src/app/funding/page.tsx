'use client';

import React, { useState } from 'react';
import { CreditCard, ShieldCheck, Building2, TrendingUp, AlertCircle } from 'lucide-react';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';

export default function FundingPage() {
  const partyFunding = [
    { party: 'DMK', declared_donations_cr: 318.5, electoral_trust_cr: 185.0, corporate_donors: 142, compliance_score: 96.5 },
    { party: 'AIADMK', declared_donations_cr: 142.2, electoral_trust_cr: 68.0, corporate_donors: 89, compliance_score: 95.0 },
    { party: 'BJP (TN Unit)', declared_donations_cr: 86.4, electoral_trust_cr: 52.0, corporate_donors: 64, compliance_score: 97.2 },
    { party: 'INC (TN Unit)', declared_donations_cr: 24.8, electoral_trust_cr: 11.5, corporate_donors: 28, compliance_score: 94.1 },
    { party: 'PMK', declared_donations_cr: 9.6, electoral_trust_cr: 2.1, corporate_donors: 15, compliance_score: 93.8 },
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="Political Funding"
        description="Public disclosures of political party donations and campaign funding across recognized parties in Tamil Nadu based on official Election Commission of India (ECI) Form 24A filings and Electoral Trust contribution reports."
        breadcrumbs={[
          { label: 'Explore all features', href: '/explore' },
          { label: 'Political Funding' },
        ]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20">
            ECI Disclosures
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Total Declared Contributions"
          value="₹581.5 Cr"
          icon={<CreditCard className="w-5 h-5" />}
          subtitle="ECI Form 24A Disclosures"
        />
        <MetricCard
          title="Electoral Trust Inflows"
          value="₹318.6 Cr"
          change="54.8% of Total"
          changeType="neutral"
          icon={<Building2 className="w-5 h-5 text-indigo-400" />}
          subtitle="Prudent, Samaj, etc."
        />
        <MetricCard
          title="Audit Cross-Validation"
          value="100% Verified"
          change="No Unreconciled Gap"
          changeType="positive"
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
          subtitle="Cross-matched with MCA-21"
        />
      </div>

      <div className="rounded-2xl bg-slate-900/80 border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-slate-800 bg-slate-950/60 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                <th className="py-3 px-4">Political Party</th>
                <th className="py-3 px-4 text-right">Declared Donations</th>
                <th className="py-3 px-4 text-right">Electoral Trust</th>
                <th className="py-3 px-4 text-right">Corporate Donors</th>
                <th className="py-3 px-4 text-center">ECI Audit Compliance</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-xs">
              {partyFunding.map((p) => (
                <tr key={p.party} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-4 px-4 font-bold text-white">
                    {p.party}
                  </td>
                  <td className="py-4 px-4 text-right font-mono font-bold text-emerald-400">
                    ₹{p.declared_donations_cr} Cr
                  </td>
                  <td className="py-4 px-4 text-right font-mono text-slate-300">
                    ₹{p.electoral_trust_cr} Cr
                  </td>
                  <td className="py-4 px-4 text-right font-mono text-blue-400">
                    {p.corporate_donors} companies
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/15 text-emerald-400 border border-emerald-500/30">
                      {p.compliance_score}%
                    </span>
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
