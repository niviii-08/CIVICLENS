'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Phone,
  HelpCircle,
  Bookmark,
  Sparkles,
  Languages,
  X,
  MessageSquare,
  ChevronUp,
  ShieldCheck,
  ChevronDown
} from 'lucide-react';
import { useLanguage } from '../lib/LanguageContext';
import { useSavedCivicItems } from '../lib/useSavedCivicItems';
import { CitizenHelplinesModal } from './CitizenHelplinesModal';
import { CitizenGlossaryModal } from './CitizenGlossaryModal';

export const CitizenFloatingHelp: React.FC = () => {
  const { language, toggleLanguage, t } = useLanguage();
  const { savedItems } = useSavedCivicItems();
  const [helplinesOpen, setHelplinesOpen] = useState(false);
  const [glossaryOpen, setGlossaryOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      {/* Floating Action Button / Dock in bottom right */}
      <div className="fixed bottom-5 right-5 z-40 flex flex-col items-end gap-2 pointer-events-auto select-none print:hidden">
        {/* Expanded Quick Citizen Utilities */}
        {expanded && (
          <div className="flex flex-col gap-2 p-2 rounded-2xl bg-[#070d24]/95 border border-cyan-500/30 backdrop-blur-2xl shadow-2xl shadow-cyan-950/60 animate-fade-in-up w-60">
            <div className="px-3 py-1.5 border-b border-white/[0.08] flex items-center justify-between">
              <span className="text-[11px] font-bold text-cyan-300 uppercase tracking-wider flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                <span>{language === 'ta' ? 'குடிமக்கள் உதவி' : 'Citizen Help Desk'}</span>
              </span>
              <button
                type="button"
                onClick={() => setExpanded(false)}
                className="text-slate-400 hover:text-white p-0.5"
                aria-label="Close help desk"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>

            {/* Helpline 1100 Trigger */}
            <button
              type="button"
              onClick={() => {
                setHelplinesOpen(true);
                setExpanded(false);
              }}
              className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-white bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 transition-all text-left group"
            >
              <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-300">
                <Phone className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <div className="leading-tight">{language === 'ta' ? 'உதவி எண்கள் (1100 / 181)' : 'Emergency Helplines'}</div>
                <div className="text-[10px] text-rose-300/80 font-mono">1100 · 181 · 1912 · 1913</div>
              </div>
            </button>

            {/* Civic Jargon Explainer */}
            <button
              type="button"
              onClick={() => {
                setGlossaryOpen(true);
                setExpanded(false);
              }}
              className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-white bg-cyan-500/10 hover:bg-cyan-500/20 border border-cyan-500/25 transition-all text-left group"
            >
              <div className="p-1.5 rounded-lg bg-cyan-500/20 text-cyan-300">
                <HelpCircle className="w-4 h-4" />
              </div>
              <div className="flex-1">
                <div className="leading-tight">{language === 'ta' ? 'அரசு சொல் விளக்கம்' : 'Decode Civic Jargon'}</div>
                <div className="text-[10px] text-slate-400 font-mono">G.O. · DBT · SLA · CAG</div>
              </div>
            </button>

            {/* Saved Items */}
            <Link
              href="/saved"
              onClick={() => setExpanded(false)}
              className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/25 transition-all text-left group"
            >
              <div className="p-1.5 rounded-lg bg-indigo-500/20 text-indigo-300 relative">
                <Bookmark className="w-4 h-4" />
                {savedItems.length > 0 && (
                  <span className="absolute -top-1 -right-1 w-3.5 h-3.5 rounded-full bg-cyan-400 text-black text-[9px] font-black flex items-center justify-center">
                    {savedItems.length}
                  </span>
                )}
              </div>
              <div className="flex-1">
                <div className="leading-tight">{language === 'ta' ? 'சேமித்த திட்டங்கள்' : 'My Saved Items'}</div>
                <div className="text-[10px] text-indigo-300/80 font-mono">
                  {savedItems.length} {language === 'ta' ? 'பதிவுகள்' : 'records tracked'}
                </div>
              </div>
            </Link>

            {/* Language Toggle */}
            <button
              type="button"
              onClick={toggleLanguage}
              className="flex items-center justify-between px-3 py-2 rounded-xl text-xs font-semibold text-slate-200 bg-white/[0.04] hover:bg-white/[0.08] border border-white/[0.08] transition-all"
            >
              <div className="flex items-center gap-2">
                <Languages className="w-4 h-4 text-amber-400" />
                <span>{language === 'ta' ? 'Language: தமிழ்' : 'Language: English'}</span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                {language === 'ta' ? 'Switch to EN' : 'தமிழ் மாற்று'}
              </span>
            </button>
          </div>
        )}

        {/* Master Floating Pill */}
        <div className="flex items-center gap-1.5 p-1 rounded-full bg-[#070e28]/90 border border-cyan-500/30 backdrop-blur-xl shadow-xl shadow-cyan-950/40">
          {/* Quick Helplines Call Button */}
          <button
            type="button"
            onClick={() => setHelplinesOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-rose-500/20 hover:bg-rose-500/30 border border-rose-500/40 text-rose-300 text-xs font-bold transition-all shadow-sm group"
            title="Tamil Nadu Government Helplines (1100)"
          >
            <Phone className="w-3.5 h-3.5 animate-pulse" />
            <span>1100</span>
          </button>

          {/* Language Fast Switch */}
          <button
            type="button"
            onClick={toggleLanguage}
            className="px-2.5 py-1.5 rounded-full bg-white/[0.05] hover:bg-white/[0.1] border border-white/[0.1] text-xs font-bold text-amber-300 transition-all"
            title="Switch Language (English / தமிழ்)"
          >
            {language === 'ta' ? 'English' : 'தமிழ்'}
          </button>

          {/* Expand/Collapse Menu Button */}
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 px-3 py-1.5 rounded-full bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white text-xs font-bold transition-all shadow-md shadow-cyan-500/25"
            aria-label="Toggle citizen help desk"
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>{language === 'ta' ? 'உதவி' : 'Help'}</span>
            {expanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronUp className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {/* Reusable Modals */}
      <CitizenHelplinesModal
        isOpen={helplinesOpen}
        onClose={() => setHelplinesOpen(false)}
      />
      <CitizenGlossaryModal
        isOpen={glossaryOpen}
        onClose={() => setGlossaryOpen(false)}
      />
    </>
  );
};
