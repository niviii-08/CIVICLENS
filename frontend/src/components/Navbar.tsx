'use client';

import React, { useState, useEffect } from 'react';
import { Search, Activity, Database, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { checkBackendHealth } from '../lib/api';

export const Navbar: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<{ online: boolean; message: string }>({
    online: false,
    message: 'Checking API status...',
  });
  const [checking, setChecking] = useState(false);

  const checkStatus = async () => {
    setChecking(true);
    const status = await checkBackendHealth();
    setBackendStatus(status);
    setChecking(false);
  };

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <header className="h-16 border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Search Input */}
      <div className="relative w-96 max-w-full">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
        <input
          type="text"
          placeholder="Search promises, demands, MLAs, claims, or G.O. numbers..."
          className="w-full bg-slate-900/90 border border-slate-800 rounded-xl pl-9 pr-4 py-2 text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 transition-all"
        />
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Backend API Status Pill */}
        <div
          onClick={checkStatus}
          title="Click to re-check API connection"
          className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium border cursor-pointer select-none transition-all ${
            backendStatus.online
              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/20'
              : 'bg-amber-500/10 text-amber-400 border-amber-500/30 hover:bg-amber-500/20'
          }`}
        >
          <span className="relative flex h-2 w-2">
            {backendStatus.online && (
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            )}
            <span
              className={`relative inline-flex rounded-full h-2 w-2 ${
                backendStatus.online ? 'bg-emerald-500' : 'bg-amber-500'
              }`}
            ></span>
          </span>
          <span className="font-semibold">
            {backendStatus.online ? 'Flask API Online (Port 5000)' : 'Flask Offline (Resilient Fallback Mode)'}
          </span>
          <RefreshCw className={`w-3 h-3 ml-1 ${checking ? 'animate-spin' : 'opacity-60'}`} />
        </div>

        {/* Database Status */}
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
          <Database className="w-3.5 h-3.5 text-blue-400" />
          <span>SQLite 120 Tables</span>
        </div>

        {/* State Tag */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs text-slate-400 border-l border-slate-800 pl-4">
          <span className="w-2 h-2 rounded-full bg-red-500"></span>
          <span>Tamil Nadu Secretariat</span>
        </div>
      </div>
    </header>
  );
};
