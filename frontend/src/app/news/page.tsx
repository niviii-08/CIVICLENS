'use client';

import React, { useState } from 'react';
import { Newspaper, Globe, Sparkles, TrendingUp, BarChart2 } from 'lucide-react';
import { MetricCard } from '../../components/MetricCard';
import { PageHeader } from '../../components/PageHeader';

export default function NewsPage() {
  const articles = [
    {
      id: "ART-TN-101",
      outlet: "Dina Thanthi (தினத்தந்தி)",
      language: "Tamil",
      title: "மகளிர் உரிமைத் தொகை: குடும்பத் தலைவிகள் மகிழ்ச்சி",
      topic: "KMUT Welfare Disbursement",
      framing: "Positive Policy Delivery",
      polarity_score: "+0.78",
      entity_focus: "Women Beneficiaries, Social Welfare Dept"
    },
    {
      id: "ART-TN-102",
      outlet: "The Hindu (Tamil Nadu)",
      language: "English",
      title: "Tamil Nadu expands morning breakfast scheme to state-aided schools in urban blocks",
      topic: "Elementary Education Nutrition",
      framing: "Objective / Informative",
      polarity_score: "+0.45",
      entity_focus: "Chief Minister, School Education Dept"
    },
    {
      id: "ART-TN-103",
      outlet: "Dinamalar (தினமலர்)",
      language: "Tamil",
      title: "மழைக்கால வெள்ள வடிகால் பணிகள் தாமதம்: பொதுமக்கள் அவதி",
      topic: "Urban Infrastructure & Floods",
      framing: "Civic Scrutiny / Critical",
      polarity_score: "-0.62",
      entity_focus: "GCC, Singara Chennai 2.0"
    },
    {
      id: "ART-TN-104",
      outlet: "The New Indian Express",
      language: "English",
      title: "Zero-fare bus scheme transforms women's workforce mobility in suburban corridors, study finds",
      topic: "Vidiyal Payanam Transport",
      framing: "Socio-Economic Impact",
      polarity_score: "+0.82",
      entity_focus: "Transport Dept, Planning Commission"
    }
  ];

  return (
    <div className="space-y-6">
      <PageHeader
        title="News Coverage"
        description="Bilingual analysis of how Tamil and English news media report on Tamil Nadu government programs and civic developments, tracking topic focus and neutral coverage balance."
        breadcrumbs={[
          { label: 'Explore all features', href: '/explore' },
          { label: 'News Coverage' },
        ]}
        badge={
          <span className="text-xs font-bold px-2.5 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            Media Analysis
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <MetricCard
          title="Monitored News Publications"
          value="18 Outlets"
          icon={<Globe className="w-5 h-5 text-cyan-400" />}
          subtitle="9 Tamil & 9 English Dailies"
        />
        <MetricCard
          title="Bilingual Articles Processed"
          value="14,820"
          change="Indic-NLP & SpaCy"
          changeType="positive"
          icon={<Sparkles className="w-5 h-5 text-indigo-400" />}
          subtitle="Entity normalization active"
        />
        <MetricCard
          title="Neutrality Balance Index"
          value="0.94 / 1.0"
          change="High Balance"
          changeType="positive"
          icon={<BarChart2 className="w-5 h-5 text-emerald-400" />}
          subtitle="Non-partisan epistemic score"
        />
      </div>

      <div className="space-y-3">
        {articles.map((art) => (
          <div
            key={art.id}
            className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 hover:border-slate-700 transition-all shadow-md space-y-2"
          >
            <div className="flex items-center justify-between text-xs">
              <div className="flex items-center gap-2">
                <span className="font-bold text-white">{art.outlet}</span>
                <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                  {art.language}
                </span>
              </div>
              <span className={`font-mono font-bold text-xs ${art.polarity_score.startsWith('+') ? 'text-emerald-400' : 'text-rose-400'}`}>
                Polarity {art.polarity_score}
              </span>
            </div>
            <h3 className="text-sm font-bold text-white leading-snug">{art.title}</h3>
            <div className="flex flex-wrap items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800/80">
              <span>Topic: <strong className="text-slate-300">{art.topic}</strong></span>
              <span>Framing: <strong className="text-blue-400">{art.framing}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
