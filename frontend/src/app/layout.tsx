import type { Metadata } from 'next';
import './globals.css';
import { Header } from '../components/Header';
import { Footer } from '../components/Footer';

export const metadata: Metadata = {
  title: 'CivicLens TN — Public Information for Tamil Nadu',
  description: 'Evidence-grounded civic intelligence, welfare scheme benefits, manifesto tracking, and public accountability platform for the state of Tamil Nadu.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#06070a] text-slate-100 flex flex-col antialiased selection:bg-blue-600 selection:text-white">
        {/* Unified Top Header with Citizen Navigation & Mobile Drawer */}
        <Header />

        {/* Central Content Container with Readable Max-Width */}
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">
          {children}
        </main>

        {/* Consistent Civic Footer */}
        <Footer />
      </body>
    </html>
  );
}
