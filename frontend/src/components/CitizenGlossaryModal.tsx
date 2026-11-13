'use client';

import React from 'react';
import {
  HelpCircle,
  X,
  BookOpen,
  FileText,
  CreditCard,
  Scale,
  Clock,
  Landmark,
  ShieldCheck,
  Building
} from 'lucide-react';

interface GlossaryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const GLOSSARY_TERMS = [
  {
    term: 'Government Order (G.O.)',
    term_ta: 'அரசாணை (G.O. Ms)',
    meaning: 'An official executive decree issued and signed by a state department secretary. It legally directs officials to spend treasury funds, launch welfare schemes, or implement policies.',
    example: 'Example: G.O. Ms No. 41 authorized the monthly ₹1,000 disbursement for Kalaignar Magalir Urimai Thittam.',
    icon: FileText,
    color: 'text-cyan-400 bg-cyan-950/80 border-cyan-500/30'
  },
  {
    term: 'Direct Benefit Transfer (DBT)',
    term_ta: 'நேரடி பணப் பரிமாற்றம் (DBT)',
    meaning: 'Welfare money sent straight from the government treasury into your Aadhaar-seeded bank account via the National Payments Corporation of India (NPCI) — completely cutting out middlemen or bribes.',
    example: 'Example: Vidiyal Payanam bus subsidies and KMUT ₹1,000 monthly credits use DBT rails.',
    icon: CreditCard,
    color: 'text-emerald-400 bg-emerald-950/80 border-emerald-500/30'
  },
  {
    term: 'Service Level Agreement (SLA)',
    term_ta: 'சேவை கால வரம்பு (SLA)',
    meaning: "Under the Tamil Nadu Citizen's Charter, every municipal department has a strict legal deadline (e.g. 7 days for streetlights, 14 days for road pothole repairs) to resolve your filed complaint.",
    example: 'Example: If GCC takes 25 days to fix a street drainage issue with a 14-day SLA, it is flagged as an SLA Breach.',
    icon: Clock,
    color: 'text-amber-400 bg-amber-950/80 border-amber-500/30'
  },
  {
    term: 'CAG (Comptroller & Auditor General)',
    term_ta: 'இந்தியக் கணக்காய்வு மற்றும் தணிக்கைத் துறை தலைவர்',
    meaning: "India's independent constitutional watchdog. The CAG audits all government spending to verify that public funds were actually spent on intended items according to statutory accounts.",
    example: 'Example: CIVICLENS TN uses CAG audit reports to check whether budget promises matched actual government accounts.',
    icon: Scale,
    color: 'text-indigo-400 bg-indigo-950/80 border-indigo-500/30'
  },
  {
    term: 'MLACDS (MLA Local Area Development Scheme)',
    term_ta: 'சட்டமன்ற உறுப்பினர் தொகுதி மேம்பாட்டு நிதி',
    meaning: 'Annual funds (currently ₹3 Crore per year) allocated to each of the 234 elected MLAs in Tamil Nadu to carry out essential local works like bus shelters, streetlights, drinking water borewells, and school repairs.',
    example: 'Example: You can inspect work orders approved by your local MLA in the Representatives tab.',
    icon: Building,
    color: 'text-blue-400 bg-blue-950/80 border-blue-500/30'
  },
  {
    term: 'Demands for Grants',
    term_ta: 'மானியக் கோரிக்கைகள்',
    meaning: 'The official annual budget requests submitted by each state minister to the Tamil Nadu Legislative Assembly. When passed, it grants the department permission to withdraw money from the Consolidated Fund.',
    example: 'Example: Demand No. 43 covers School Education budget and school breakfast allocations.',
    icon: Landmark,
    color: 'text-purple-400 bg-purple-950/80 border-purple-500/30'
  }
];

export const CitizenGlossaryModal: React.FC<GlossaryModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="relative w-full max-w-2xl rounded-3xl bg-[#090e24] border border-indigo-500/30 p-6 sm:p-8 shadow-2xl overflow-hidden max-h-[90vh] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-labelledby="glossary-modal-title"
      >
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-indigo-400/40 to-transparent" />

        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-white/[0.08] pb-4 shrink-0">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-indigo-500/10 text-indigo-400 border border-indigo-500/25">
                <BookOpen className="w-5 h-5" />
              </span>
              <div>
                <h2 id="glossary-modal-title" className="text-lg sm:text-xl font-black text-white">
                  Civic Jargon Decoded: Plain Citizen Explanations
                </h2>
                <p className="text-xs text-amber-300 font-sans">
                  அரசு சொற்களஞ்சியம் — எளிய மக்கள் விளக்கம்
                </p>
              </div>
            </div>
            <p className="text-xs text-slate-300 pt-1">
              Everyday explanations of government terminology, budget codes, and audit standards.
            </p>
          </div>

          <button
            onClick={onClose}
            aria-label="Close glossary dialog"
            className="p-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Terms List */}
        <div className="space-y-3.5 overflow-y-auto custom-scrollbar my-4 pr-1 flex-1">
          {GLOSSARY_TERMS.map((t) => {
            const Icon = t.icon;
            return (
              <div
                key={t.term}
                className="p-4 rounded-2xl bg-white/[0.025] border border-white/[0.06] hover:border-indigo-500/30 transition-all space-y-2 group"
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-xl border shrink-0 ${t.color}`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="font-bold text-sm text-white group-hover:text-cyan-300 transition-colors">
                      {t.term}
                    </h3>
                    <span className="text-xs text-amber-300/80 font-sans">{t.term_ta}</span>
                  </div>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed pl-10">
                  {t.meaning}
                </p>

                <div className="ml-10 p-2.5 rounded-xl bg-black/40 border border-white/[0.04] text-[11px] text-slate-400 font-mono">
                  {t.example}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] text-slate-400 shrink-0">
          <span>Need more help? Check individual record detail pages for full G.O. references.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.12] text-white font-semibold transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
};
