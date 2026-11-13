'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import {
  Sparkles,
  Users,
  GraduationCap,
  Sprout,
  Heart,
  Home,
  CheckCircle2,
  ArrowRight,
  Bookmark,
  BookmarkCheck,
  FileText,
  BadgePercent,
  Check,
  HelpCircle,
  ExternalLink
} from 'lucide-react';
import { useSavedCivicItems } from '../lib/useSavedCivicItems';

interface BenefitScheme {
  id: string;
  name: string;
  name_ta: string;
  targetGroup: 'women' | 'students' | 'farmers' | 'elders' | 'general';
  monthlyBenefit: string;
  annualBenefitTotal?: string;
  eligibility: string[];
  documentsNeeded: string[];
  howToApply: string;
  portalUrl: string;
  provenanceGO: string;
  detailUrl: string;
  badge: string;
}

const BENEFIT_SCHEMES: BenefitScheme[] = [
  {
    id: 'SCH-SW-KMUT',
    name: 'Kalaignar Magalir Urimai Thittam (KMUT)',
    name_ta: 'கலைஞர் மகளிர் உரிமைத் திட்டம்',
    targetGroup: 'women',
    monthlyBenefit: '₹1,000 / month (Direct Bank Deposit)',
    annualBenefitTotal: '₹12,000 / year',
    eligibility: [
      'Woman head of eligible family residing in Tamil Nadu',
      'Annual family income under ₹2.5 Lakhs',
      'Family electricity consumption under 3,600 units/year',
      'Family holds less than 5 acres of wetland or 10 acres of dryland'
    ],
    documentsNeeded: [
      'Aadhaar Card with mobile link',
      'Smart Family Ration Card',
      'Electricity Bill (Consumer Number)',
      'Bank Account Passbook (Aadhaar linked)'
    ],
    howToApply: 'Special registration camps in your ward/village or nearest e-Sevai Center.',
    portalUrl: 'https://kmut.tn.gov.in',
    provenanceGO: 'G.O. Ms No. 41 Social Welfare',
    detailUrl: '/schemes/SCH-SW-KMUT',
    badge: 'Direct Benefit Transfer (DBT)'
  },
  {
    id: 'SCH-TR-VIDIYAL',
    name: 'Vidiyal Payanam (Fare-Free Bus Travel for Women)',
    name_ta: 'விடியல் பயணம் (கட்டணமில்லாப் பேருந்து)',
    targetGroup: 'women',
    monthlyBenefit: '100% Free Travel on Standard Town/City Buses',
    annualBenefitTotal: 'Saves ₹800 - ₹1,200 per month on average',
    eligibility: [
      'All women citizens residing or working in Tamil Nadu',
      'Transgender women and visually impaired citizens with escort',
      'No income ceiling or ration card requirement'
    ],
    documentsNeeded: ['No pass or document needed — simply board any pink-board ordinary town bus'],
    howToApply: 'Walk-on boarding on all government town/city buses with pink boards.',
    portalUrl: 'https://www.tnstc.in',
    provenanceGO: 'G.O. Ms No. 12 Transport Dept',
    detailUrl: '/schemes/SCH-TR-VIDIYAL',
    badge: 'Universal Citizen Service'
  },
  {
    id: 'SCH-EDU-BREAKFAST',
    name: "Chief Minister's Morning Breakfast Scheme",
    name_ta: 'முதலமைச்சரின் காலை உணவுத் திட்டம்',
    targetGroup: 'students',
    monthlyBenefit: 'Nutritious Hot Cooked Breakfast Every School Morning',
    annualBenefitTotal: 'Over 200 school days of hot meals per year',
    eligibility: [
      'All children enrolled in Classes 1 through 5',
      'Studying in government primary schools across all 38 districts of Tamil Nadu'
    ],
    documentsNeeded: ['Automatic school enrollment — no separate application required'],
    howToApply: 'Provided directly at school to all enrolled government school primary students.',
    portalUrl: 'https://tnschools.gov.in',
    provenanceGO: 'G.O. Ms No. 19 Social Welfare',
    detailUrl: '/schemes/SCH-EDU-BREAKFAST',
    badge: '100% School Coverage'
  },
  {
    id: 'SCH-HE-PUDHUMAI',
    name: 'Pudhumai Penn Scheme (Higher Education Assistance)',
    name_ta: 'புதுமைப் பெண் திட்டம்',
    targetGroup: 'students',
    monthlyBenefit: '₹1,000 / month until College Graduation',
    annualBenefitTotal: '₹12,000 / year + Tuition waiver',
    eligibility: [
      'Girl students who studied Classes 6 to 12 in Tamil Nadu government schools',
      'Enrolled in recognized undergraduate degree, diploma, ITI, or engineering colleges'
    ],
    documentsNeeded: [
      'Class 6-12 Government School Study Certificate',
      'College Admission / Bonafide Certificate',
      'Student Aadhaar Card & Bank Account'
    ],
    howToApply: 'Apply through your college nodal officer or on the Penkalvi portal.',
    portalUrl: 'https://www.penkalvi.tn.gov.in',
    provenanceGO: 'Higher Education Guidelines G.O.',
    detailUrl: '/schemes/SCH-HE-PUDHUMAI',
    badge: 'Direct Bank Transfer'
  },
  {
    id: 'SCH-AG-KALAIGNAR',
    name: 'Kalaignarin All Village Integrated Agriculture Programme',
    name_ta: 'அனைத்து கிராம ஒருங்கிணைந்த வேளாண் வளர்ச்சித் திட்டம்',
    targetGroup: 'farmers',
    monthlyBenefit: 'Free Saplings, Seeds, Toolkits & 100% Micro-Irrigation Subsidy',
    annualBenefitTotal: 'Subsidies up to ₹45,000 per farming family',
    eligibility: [
      'Small and marginal farmers in selected revenue villages across 37 rural districts',
      'Farmers with patta/chitta land ownership records'
    ],
    documentsNeeded: ['Patta/Chitta copy', 'Aadhaar Card', 'Farmer Registration ID / Uzhavan App'],
    howToApply: 'Register via the Uzhavan Mobile App or visit local Assistant Director of Agriculture.',
    portalUrl: 'https://tnhorticulture.tn.gov.in',
    provenanceGO: 'Agriculture Demand No. 05 Policy Note',
    detailUrl: '/schemes/SCH-AG-KALAIGNAR',
    badge: 'Uzhavan App Integrated'
  },
  {
    id: 'SCH-HL-INNUYIR',
    name: 'Innuyir Kaappom — Nammai Kaakkum 48 (Road Safety & Emergency Care)',
    name_ta: 'இன்னுயிர் காப்போம் — நம்மை காக்கும் 48',
    targetGroup: 'general',
    monthlyBenefit: 'Cashless Emergency Treatment up to ₹1 Lakh in First 48 Hours',
    annualBenefitTotal: '100% Free at over 680 empanelled private and government hospitals',
    eligibility: [
      'Any road accident victim injured within Tamil Nadu geographical territory',
      'Available to residents, visitors, and travelers of any state/nationality'
    ],
    documentsNeeded: ['Zero documentation required at emergency admission — automatic coverage'],
    howToApply: 'Direct admission by emergency 108 ambulance or bystanders at nearest empanelled hospital.',
    portalUrl: 'https://nhm.tn.gov.in',
    provenanceGO: 'Health Department G.O. Ms No. 248',
    detailUrl: '/schemes',
    badge: 'Cashless Emergency Medical'
  }
];

export const CitizenBenefitFinder: React.FC = () => {
  const [selectedGroup, setSelectedGroup] = useState<'women' | 'students' | 'farmers' | 'general'>('women');
  const { isSaved, saveRecord, removeRecord } = useSavedCivicItems();

  const matchingSchemes = BENEFIT_SCHEMES.filter(
    (s) => s.targetGroup === selectedGroup || (selectedGroup === 'general' && s.targetGroup === 'general')
  );

  const personaTabs = [
    { key: 'women', label: 'Women & Homemakers', label_ta: 'மகளிர்', icon: Users, color: 'text-rose-400' },
    { key: 'students', label: 'Students & Youth', label_ta: 'மாணவர்கள்', icon: GraduationCap, color: 'text-cyan-400' },
    { key: 'farmers', label: 'Farmers & Rural', label_ta: 'விவசாயிகள்', icon: Sprout, color: 'text-emerald-400' },
    { key: 'general', label: 'All Citizens & Families', label_ta: 'பொது மக்கள்', icon: Home, color: 'text-indigo-400' }
  ];

  return (
    <section className="rounded-3xl bg-gradient-to-b from-[#0b122e]/95 to-[#060a1d]/95 border border-cyan-500/25 p-6 sm:p-8 backdrop-blur-2xl shadow-2xl relative overflow-hidden my-8">
      {/* Background radial glow */}
      <div className="absolute top-0 right-0 w-80 h-80 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

      {/* Header */}
      <div className="relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-white/[0.08] pb-6 mb-6">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono font-bold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            Citizen Benefit Finder · உடனடி நலத்திட்ட தேடல்
          </div>
          <h2 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
            Find Government Benefits For You &amp; Your Family
          </h2>
          <p className="text-xs sm:text-sm text-slate-300 mt-1 max-w-2xl leading-relaxed">
            Select your category to see verified monthly payments, free services, eligibility criteria, and step-by-step application instructions.
          </p>
        </div>

        <Link
          href="/schemes"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-cyan-400 hover:text-cyan-300 transition-colors shrink-0"
        >
          <span>View All Cataloged Schemes ({BENEFIT_SCHEMES.length})</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Step 1: Persona Tabs */}
      <div className="relative z-10 mb-6">
        <label className="block text-xs font-mono uppercase tracking-wider text-slate-400 mb-2.5">
          Step 1: Who are you looking benefits for? (தேர்ந்தெடுக்கவும்):
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
          {personaTabs.map((tab) => {
            const Icon = tab.icon;
            const isSelected = selectedGroup === tab.key;
            return (
              <button
                key={tab.key}
                type="button"
                onClick={() => setSelectedGroup(tab.key as any)}
                className={`flex flex-col sm:flex-row items-center sm:items-start gap-2.5 p-3.5 rounded-2xl border text-left transition-all duration-200 ${
                  isSelected
                    ? 'bg-cyan-500/15 border-cyan-400 text-white shadow-lg shadow-cyan-500/20 scale-[1.02]'
                    : 'bg-white/[0.03] border-white/[0.08] hover:bg-white/[0.06] text-slate-300 hover:text-white'
                }`}
              >
                <div className={`p-2 rounded-xl bg-black/40 border border-white/[0.08] shrink-0 ${tab.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-bold text-xs sm:text-sm leading-tight">
                    {tab.label}
                  </div>
                  <div className="text-[11px] text-amber-300 font-sans mt-0.5">
                    {tab.label_ta}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Step 2: Matching Schemes Cards */}
      <div className="relative z-10 space-y-4">
        <div className="flex items-center justify-between text-xs font-mono text-slate-400 px-1">
          <span>MATCHING CITIZEN WELFARE SCHEMES ({matchingSchemes.length})</span>
          <span className="text-emerald-400 font-bold">100% Primary G.O. Audited</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {matchingSchemes.map((scheme) => {
            const saved = isSaved('scheme', scheme.id);

            const handleBookmarkToggle = () => {
              if (saved) {
                removeRecord('scheme', scheme.id);
              } else {
                saveRecord({
                  record_type: 'scheme',
                  record_id: scheme.id,
                  title: scheme.name,
                  detail_url: scheme.detailUrl,
                  current_status: 'ACTIVE_BENEFIT',
                });
              }
            };

            return (
              <div
                key={scheme.id}
                className="rounded-3xl bg-[#090f26]/90 border border-white/[0.08] hover:border-cyan-500/40 p-6 flex flex-col justify-between space-y-4 transition-all duration-300 shadow-xl group hover:-translate-y-1"
              >
                {/* Header */}
                <div className="space-y-2">
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-[10px] font-mono font-bold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-300 border border-emerald-500/20">
                      {scheme.badge}
                    </span>
                    <button
                      onClick={handleBookmarkToggle}
                      className={`p-1.5 rounded-xl border transition-all text-xs flex items-center gap-1 ${
                        saved
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-400'
                          : 'bg-white/[0.04] text-slate-400 hover:text-white border-white/[0.08]'
                      }`}
                      title={saved ? 'Remove from My Saved Benefits' : 'Save to My List'}
                      aria-label={`Bookmark ${scheme.name}`}
                    >
                      {saved ? <BookmarkCheck className="w-4 h-4 text-cyan-400" /> : <Bookmark className="w-4 h-4" />}
                      <span className="hidden sm:inline text-[10px] font-mono">{saved ? 'Saved' : 'Save'}</span>
                    </button>
                  </div>

                  <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors leading-snug">
                    {scheme.name}
                  </h3>
                  <div className="text-xs font-medium text-amber-300 font-sans">
                    {scheme.name_ta}
                  </div>
                </div>

                {/* Big Benefit Box */}
                <div className="p-4 rounded-2xl bg-emerald-950/40 border border-emerald-500/30 space-y-1">
                  <span className="text-[10px] font-mono font-bold text-emerald-400 uppercase tracking-wider block">
                    Direct Financial &amp; Service Benefit:
                  </span>
                  <p className="text-base font-black text-white leading-tight">
                    {scheme.monthlyBenefit}
                  </p>
                  {scheme.annualBenefitTotal && (
                    <p className="text-xs text-emerald-300 font-mono">
                      Total Value: {scheme.annualBenefitTotal}
                    </p>
                  )}
                </div>

                {/* Eligibility checklist */}
                <div className="space-y-1.5 text-xs">
                  <span className="font-bold text-slate-200 block text-[11px] font-mono uppercase tracking-wide">
                    Who Qualifies (தகுதி):
                  </span>
                  <ul className="space-y-1">
                    {scheme.eligibility.map((item, idx) => (
                      <li key={idx} className="flex items-start gap-2 text-slate-300 leading-relaxed">
                        <Check className="w-3.5 h-3.5 text-cyan-400 shrink-0 mt-0.5" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Documents needed */}
                <div className="p-3 rounded-2xl bg-black/40 border border-white/[0.05] space-y-1 text-xs">
                  <span className="font-bold text-slate-300 text-[11px] font-mono block">
                    Documents Needed (தேவையான ஆவணங்கள்):
                  </span>
                  <div className="flex flex-wrap gap-1.5 pt-0.5">
                    {scheme.documentsNeeded.map((doc, idx) => (
                      <span key={idx} className="text-[11px] px-2 py-0.5 rounded-lg bg-white/[0.04] text-slate-300 border border-white/[0.08]">
                        {doc}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Where to apply & CTA */}
                <div className="pt-3 border-t border-white/[0.08] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
                  <div className="text-[11px] text-slate-400">
                    <strong className="text-slate-300">How to apply: </strong>
                    {scheme.howToApply}
                  </div>

                  <div className="flex items-center gap-2 shrink-0">
                    {scheme.portalUrl && (
                      <a
                        href={scheme.portalUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-3 py-1.5 rounded-xl bg-white/[0.05] hover:bg-white/[0.1] text-slate-300 hover:text-white transition-colors text-xs font-semibold inline-flex items-center gap-1"
                        aria-label={`Official portal for ${scheme.name}`}
                      >
                        <span>Portal</span>
                        <ExternalLink className="w-3 h-3 text-cyan-400" />
                      </a>
                    )}
                    <Link
                      href={scheme.detailUrl}
                      className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 text-cyan-300 border border-cyan-500/30 text-xs font-bold transition-all group-hover:scale-105"
                    >
                      <span>Full Details</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
