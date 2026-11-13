'use client';

import React from 'react';
import { Breadcrumb, BreadcrumbItem } from './Breadcrumb';

interface PageHeaderProps {
  title: string;
  description: string;
  breadcrumbs?: BreadcrumbItem[];
  badge?: React.ReactNode;
  actions?: React.ReactNode;
  className?: string;
}

export const PageHeader: React.FC<PageHeaderProps> = ({
  title,
  description,
  breadcrumbs,
  badge,
  actions,
  className = '',
}) => {
  return (
    <div className={`space-y-3 pb-6 border-b border-white/10 mb-8 relative ${className}`}>
      {/* Subtle ambient light line underneath */}
      <div className="absolute -bottom-[1px] left-0 w-32 h-[1px] bg-gradient-to-r from-cyan-500 to-transparent" />

      {breadcrumbs && breadcrumbs.length > 0 && (
        <div className="pb-1">
          <Breadcrumb items={breadcrumbs} />
        </div>
      )}

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1.5 max-w-3xl">
          <div className="flex items-center gap-2.5 flex-wrap">
            <h1 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight">
              {title}
            </h1>
            {badge && <div className="transition-transform hover:scale-105 duration-200">{badge}</div>}
          </div>
          <p className="text-xs md:text-sm text-slate-400 leading-relaxed max-w-2xl">
            {description}
          </p>
        </div>

        {actions && (
          <div className="flex items-center gap-2 shrink-0 flex-wrap">
            {actions}
          </div>
        )}
      </div>
    </div>
  );
};
