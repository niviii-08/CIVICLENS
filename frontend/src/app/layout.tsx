import type { Metadata } from 'next';
import './globals.css';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';
import { CitizenFloatingHelp } from '../components/CitizenFloatingHelp';
import { LanguageProvider } from '../lib/LanguageContext';

export const metadata: Metadata = {
  title: 'CivicLens TN — Tamil Nadu Citizen Information & Public Welfare Portal',
  description: 'Evidence-grounded civic intelligence, welfare scheme benefits, manifesto tracking, and public accountability platform for the citizens of Tamil Nadu.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#030611] text-slate-100 flex flex-col antialiased selection:bg-cyan-500 selection:text-black relative font-sans">
        <LanguageProvider>
          {/* Ambient Animated Aurora Glows */}
          <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
            {/* Top Left Sapphire Orb */}
            <div className="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/15 rounded-full blur-[120px] animate-pulse-slow" />
            {/* Top Right Cyan Orb */}
            <div className="absolute -top-20 -right-20 w-[500px] h-[500px] bg-cyan-500/10 rounded-full blur-[140px] animate-pulse-slow" style={{ animationDelay: '2s' }} />
            {/* Center Violet Accent */}
            <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-indigo-600/10 rounded-full blur-[150px] animate-pulse-slow" style={{ animationDelay: '4s' }} />
            {/* Subtle Grid Dot Pattern */}
            <div className="absolute inset-0 bg-[radial-gradient(#ffffff0a_1px,transparent_1px)] [background-size:28px_28px] opacity-40" />
          </div>

          {/* Unified Top Header with Citizen Navigation & Mobile Drawer */}
          <div className="relative z-50">
            <Header />
          </div>

          {/* Central Content Container with Readable Max-Width */}
          <main className="relative z-10 flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-10 animate-fade-in">
            {children}
          </main>

          {/* Persistent Floating Citizen Dock (Helplines, Glossary, Fast Language Switch) */}
          <CitizenFloatingHelp />

          {/* Consistent Civic Footer */}
          <div className="relative z-10">
            <Footer />
          </div>
        </LanguageProvider>
      </body>
    </html>
  );
}
