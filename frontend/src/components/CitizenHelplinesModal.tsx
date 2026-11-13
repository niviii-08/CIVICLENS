'use client';

import React from 'react';
import {
  Phone,
  X,
  ExternalLink,
  ShieldAlert,
  Building2,
  Zap,
  Droplets,
  HeartHandshake,
  GraduationCap,
  Ambulance,
  PhoneCall
} from 'lucide-react';

interface HelplinesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const HELPLINES = [
  {
    number: '1100',
    title: "Chief Minister's Helpline (CM Special Cell)",
    title_ta: 'முதலமைச்சரின் உதவி மையம்',
    desc: 'State-wide citizen grievance redressal for all government departments across Tamil Nadu.',
    department: 'Government of Tamil Nadu',
    icon: PhoneCall,
    color: 'text-cyan-400 bg-cyan-950/80 border-cyan-500/30',
    portalUrl: 'https://cmhelpline.tnega.org',
    badge: 'Toll Free · 24x7'
  },
  {
    number: '1913',
    title: 'Greater Chennai Corporation (GCC)',
    title_ta: 'பெருநகர சென்னை மாநகராட்சி',
    desc: 'Civic complaints on road repairs, streetlights, stormwater drains, garbage collection, and stray cattle.',
    department: 'Municipal Administration',
    icon: Building2,
    color: 'text-amber-400 bg-amber-950/80 border-amber-500/30',
    portalUrl: 'https://chennaicorporation.gov.in',
    badge: 'Greater Chennai'
  },
  {
    number: '1912',
    title: 'TANGEDCO Electricity Consumer Care',
    title_ta: 'மின்வாரிய புகார் மையம்',
    desc: 'Power outage reports, hazardous live wires, transformer repairs, low voltage, and new service connections.',
    department: 'Energy Department',
    icon: Zap,
    color: 'text-yellow-400 bg-yellow-950/80 border-yellow-500/30',
    portalUrl: 'https://www.tangedco.gov.in',
    badge: 'All Districts'
  },
  {
    number: '044-4567 4567',
    title: 'CMWSSB (Metro Water & Sewerage)',
    title_ta: 'சென்னை குடிநீர் வாரியம்',
    desc: 'Drinking water tanker booking, sewage line blocks, contaminated water supply, and pipeline leaks.',
    department: 'Municipal Water Supply',
    icon: Droplets,
    color: 'text-blue-400 bg-blue-950/80 border-blue-500/30',
    portalUrl: 'https://chennaimetrowater.tn.gov.in',
    badge: 'Chennai Metro'
  },
  {
    number: '181',
    title: "Women's Helpline",
    title_ta: 'மகளிர் உதவி எண்',
    desc: '24x7 toll-free support, counseling, emergency rescue, and legal aid for women in distress.',
    department: 'Social Welfare & Women Empowerment',
    icon: HeartHandshake,
    color: 'text-rose-400 bg-rose-950/80 border-rose-500/30',
    portalUrl: 'https://cms.tn.gov.in',
    badge: 'Confidential · 24x7'
  },
  {
    number: '14417',
    title: 'School Education Department Helpline',
    title_ta: 'பள்ளிக் கல்வி உதவி மையம்',
    desc: 'Guidance on government school admissions, textbooks, morning breakfast scheme, and student mental health.',
    department: 'School Education Department',
    icon: GraduationCap,
    color: 'text-emerald-400 bg-emerald-950/80 border-emerald-500/30',
    portalUrl: 'https://tnschools.gov.in',
    badge: 'Students & Parents'
  },
  {
    number: '108',
    title: 'Emergency Medical Ambulance',
    title_ta: 'அவசர மருத்துவ ஊர்தி',
    desc: 'Immediate emergency medical response and hospitalization across Tamil Nadu.',
    department: 'Health & Family Welfare',
    icon: Ambulance,
    color: 'text-red-400 bg-red-950/80 border-red-500/30',
    portalUrl: 'https://nhm.tn.gov.in',
    badge: 'Emergency 24x7'
  }
];

export const CitizenHelplinesModal: React.FC<HelplinesModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="relative w-full max-w-2xl rounded-3xl bg-[#090e24] border border-cyan-500/30 p-6 sm:p-8 shadow-2xl overflow-hidden max-h-[90vh] flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-labelledby="helplines-modal-title"
      >
        {/* Subtle top shine */}
        <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-400/40 to-transparent" />

        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-white/[0.08] pb-4 shrink-0">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/25">
                <Phone className="w-5 h-5" />
              </span>
              <div>
                <h2 id="helplines-modal-title" className="text-lg sm:text-xl font-black text-white">
                  Tamil Nadu Official Citizen Helplines
                </h2>
                <p className="text-xs text-amber-300 font-sans">
                  தமிழ்நாடு அரசு அவசர மற்றும் மக்கள் குறைதீர்ப்பு உதவி எண்கள்
                </p>
              </div>
            </div>
            <p className="text-xs text-slate-300 pt-1">
              Click any phone number to call directly from your device or access official government portals.
            </p>
          </div>

          <button
            onClick={onClose}
            aria-label="Close helplines dialog"
            className="p-2 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Helplines List */}
        <div className="space-y-3 overflow-y-auto custom-scrollbar my-4 pr-1 flex-1">
          {HELPLINES.map((h) => {
            const Icon = h.icon;
            return (
              <div
                key={h.number}
                className="p-4 rounded-2xl bg-white/[0.025] hover:bg-white/[0.05] border border-white/[0.06] hover:border-cyan-500/30 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-3 group"
              >
                <div className="flex items-start gap-3">
                  <div className={`p-2.5 rounded-xl border shrink-0 ${h.color}`}>
                    <Icon className="w-5 h-5" />
                  </div>
                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-bold text-sm text-white group-hover:text-cyan-300 transition-colors">
                        {h.title}
                      </h3>
                      <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-white/[0.05] text-slate-300 border border-white/[0.1]">
                        {h.badge}
                      </span>
                    </div>
                    <div className="text-xs text-amber-300/80 font-sans">
                      {h.title_ta}
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      {h.desc}
                    </p>
                  </div>
                </div>

                {/* Call Button & Portal Link */}
                <div className="flex items-center gap-2 shrink-0 self-end sm:self-center pl-11 sm:pl-0">
                  {h.portalUrl && (
                    <a
                      href={h.portalUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-2 rounded-xl bg-white/[0.04] hover:bg-white/[0.08] text-slate-400 hover:text-white transition-colors text-xs"
                      title="Open Official Portal"
                      aria-label={`Open ${h.title} portal`}
                    >
                      <ExternalLink className="w-4 h-4" />
                    </a>
                  )}
                  <a
                    href={`tel:${h.number.replace(/\s+/g, '')}`}
                    className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 font-bold text-sm transition-all group-hover:scale-105"
                  >
                    <Phone className="w-3.5 h-3.5 text-cyan-400" />
                    <span>{h.number}</span>
                  </a>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer Note */}
        <div className="pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] text-slate-400 shrink-0">
          <span>All helplines are maintained by statutory Tamil Nadu Government authorities.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-white/[0.08] hover:bg-white/[0.12] text-white font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
