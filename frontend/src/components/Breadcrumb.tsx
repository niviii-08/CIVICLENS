'use client';

import React from 'react';
import Link from 'next/link';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items, className = '' }) => {
  return (
    <nav aria-label="Breadcrumb" className={`flex items-center space-x-1.5 text-xs text-slate-400 ${className}`}>
      <Link
        href="/"
        className="inline-flex items-center gap-1 text-slate-400 hover:text-slate-200 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-1 py-0.5"
      >
        <Home className="w-3.5 h-3.5" />
        <span className="sr-only sm:not-sr-only sm:inline">Home</span>
      </Link>

      {items.map((item, idx) => {
        const isLast = idx === items.length - 1;
        return (
          <React.Fragment key={idx}>
            <ChevronRight className="w-3 h-3 text-slate-600 shrink-0" aria-hidden="true" />
            {isLast || !item.href ? (
              <span className="font-semibold text-slate-200 truncate max-w-[200px] sm:max-w-none" aria-current="page">
                {item.label}
              </span>
            ) : (
              <Link
                href={item.href}
                className="text-slate-400 hover:text-slate-200 transition-colors focus:outline-none focus:ring-1 focus:ring-blue-500 rounded px-1 py-0.5 truncate max-w-[150px] sm:max-w-none"
              >
                {item.label}
              </Link>
            )}
          </React.Fragment>
        );
      })}
    </nav>
  );
};
