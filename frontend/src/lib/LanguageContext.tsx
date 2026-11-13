'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'en' | 'ta';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const DICTIONARY: Record<string, { en: string; ta: string }> = {
  // Navigation
  'nav.home': { en: 'Home', ta: 'முதற்பக்கம்' },
  'nav.schemes': { en: 'Welfare Schemes', ta: 'அரசுத் திட்டங்கள்' },
  'nav.promises': { en: 'Promises Tracker', ta: 'வாக்குறுதிகள்' },
  'nav.representatives': { en: 'MLAs & Leaders', ta: 'சட்டமன்ற உறுப்பினர்கள்' },
  'nav.civic': { en: 'Civic Grievances', ta: 'மக்கள் குறைகள்' },
  'nav.claims': { en: 'Fact Check', ta: 'உண்மை சரிபார்ப்பு' },
  'nav.policy': { en: 'Policy Results', ta: 'கொள்கை முடிவுகள்' },
  'nav.budget': { en: 'Budget & Spending', ta: 'நிதிநிலை அறிக்கை' },
  'nav.explore': { en: 'All Features', ta: 'அனைத்து பிரிவுகள்' },
  'nav.saved': { en: 'Saved Items', ta: 'சேமிக்கப்பட்டவை' },

  // Header CTAs
  'header.search': { en: 'Search public records...', ta: 'அரசுப் பதிவுகளைத் தேடுக...' },
  'header.helplines': { en: 'Helplines 1100', ta: 'உதவி எண்கள் 1100' },
  'header.glossary': { en: 'Civic Jargon Decoded', ta: 'அரசு சொல் விளக்கம்' },
  'header.apiOnline': { en: 'Live Records', ta: 'நேரலைப் பதிவுகள்' },
  'header.apiOffline': { en: 'Cached Records', ta: 'சேமிக்கப்பட்ட பதிவுகள்' },

  // Hero
  'hero.badge': {
    en: 'TAMIL NADU CITIZEN PORTAL · 100% OFFICIAL RECORDS',
    ta: 'தமிழ்நாடு மக்கள் நலன் & உண்மைத் தகவல் தளம்',
  },
  'hero.title1': { en: "Tamil Nadu's", ta: 'தமிழ்நாட்டின்' },
  'hero.title2': { en: 'Citizen Welfare &', ta: 'மக்கள் நலன் &' },
  'hero.title3': { en: 'Public Accountability.', ta: 'உண்மைத் தகவல்கள்.' },
  'hero.subtitle': {
    en: 'Check welfare scheme eligibility in 30 seconds, track election promises delivered, find your local MLA, and verify public facts against official Government Orders.',
    ta: '30 வினாடிகளில் உங்களுக்கான அரசுத் திட்டங்களைத் தெரிந்து கொள்ளுங்கள்; தேர்தல் வாக்குறுதிகள், உங்கள் தொகுதி எம்.எல்.ஏ பணிகள் மற்றும் உண்மைத் தகவல்களைச் சரிபாருங்கள்.',
  },
  'hero.cta.schemes': { en: 'Check My Eligibility', ta: 'எனக்கான திட்டங்கள்' },
  'hero.cta.promises': { en: 'Track 2021 Promises', ta: 'வாக்குறுதிகள் நிலை' },
  'hero.cta.reps': { en: 'Find My MLA', ta: 'என் தொகுதி எம்.எல்.ஏ' },
  'hero.cta.helplines': { en: 'Citizen Helplines', ta: 'அவசர உதவி எண்கள்' },

  // Quick Action Launchpad
  'launchpad.eligibility.title': { en: 'Welfare Benefit Finder', ta: 'உடனடி நலத்திட்ட தேடல்' },
  'launchpad.eligibility.desc': {
    en: 'Find cash assistance, student aid, and free services you qualify for.',
    ta: 'மகளிர் உரிமைத் தொகை, புதுமைப் பெண் மற்றும் இலவச சேவைகளை அறியுங்கள்.',
  },
  'launchpad.promises.title': { en: '2021 Manifesto Tracker', ta: 'தேர்தல் வாக்குறுதிகள்' },
  'launchpad.promises.desc': {
    en: '234 commitments tracked with official Government Orders.',
    ta: '234 தேர்தல் வாக்குறுதிகளின் உண்மை நிலை மற்றும் அரசாணைகள்.',
  },
  'launchpad.reps.title': { en: '234 MLAs Mapped', ta: '234 எம்.எல்.ஏ-க்கள்' },
  'launchpad.reps.desc': {
    en: 'Local constituency development funds (MLACDS) and attendance.',
    ta: 'தொகுதி மேம்பாட்டு நிதி செலவு மற்றும் சட்டசபை வருகைப் பதிவுகள்.',
  },
  'launchpad.claims.title': { en: 'Fact Check & Verification', ta: 'உண்மை சரிபார்ப்பு' },
  'launchpad.claims.desc': {
    en: 'Political claims verified with CAG audit reports & gazettes.',
    ta: 'அரசியல் கூற்றுகள் தணிக்கை அறிக்கைகள் மூலம் சரிபார்க்கப்பட்டது.',
  },

  // Common
  'common.search': { en: 'Search', ta: 'தேடு' },
  'common.filter': { en: 'Filter', ta: 'வடிகட்டு' },
  'common.all': { en: 'All', ta: 'அனைத்தும்' },
  'common.reset': { en: 'Reset', ta: 'மீட்டமை' },
  'common.viewDetails': { en: 'View Details', ta: 'முழு விவரம்' },
  'common.save': { en: 'Save', ta: 'சேமி' },
  'common.saved': { en: 'Saved', ta: 'சேமிக்கப்பட்டது' },
  'common.call': { en: 'Call Now', ta: 'அழைக்க' },
};

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  toggleLanguage: () => {},
  t: (key: string) => key,
});

const STORAGE_KEY = 'civiclens_lang_pref';

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>('en');

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY) as Language | null;
      if (stored === 'en' || stored === 'ta') {
        setLanguageState(stored);
      }
    }
  }, []);

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, lang);
    }
  };

  const toggleLanguage = () => {
    const next = language === 'en' ? 'ta' : 'en';
    setLanguage(next);
  };

  const t = (key: string): string => {
    const item = DICTIONARY[key];
    if (!item) return key;
    return item[language] || item.en || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export function useLanguage() {
  return useContext(LanguageContext);
}
