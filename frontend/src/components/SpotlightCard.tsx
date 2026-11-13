'use client';

import React, { useState, useRef } from 'react';
import Link from 'next/link';

interface SpotlightCardProps {
  children: React.ReactNode;
  className?: string;
  href?: string;
  spotlightColor?: string;
  borderColor?: string;
  showCrosshairs?: boolean;
  'aria-label'?: string;
  onClick?: () => void;
}

export const SpotlightCard: React.FC<SpotlightCardProps> = ({
  children,
  className = '',
  href,
  spotlightColor = 'rgba(6, 182, 212, 0.14)',
  borderColor = 'rgba(6, 182, 212, 0.35)',
  showCrosshairs = true,
  'aria-label': ariaLabel,
  onClick,
}) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setMousePos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
    });
  };

  const handleMouseEnter = () => setIsHovered(true);
  const handleMouseLeave = () => setIsHovered(false);

  const content = (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      style={{
        borderColor: isHovered ? borderColor : undefined,
      }}
      className={`relative rounded-3xl border border-white/[0.08] bg-gradient-to-b from-[#0a1024]/90 to-[#040714]/95 p-6 backdrop-blur-2xl transition-all duration-300 shadow-2xl overflow-hidden group ${
        isHovered ? '-translate-y-1 shadow-cyan-950/20 shadow-2xl' : ''
      } ${className}`}
      aria-label={ariaLabel}
    >
      {/* Dynamic Cursor Spotlight Radial Overlay */}
      <div
        className="pointer-events-none absolute inset-0 z-0 transition-opacity duration-500 ease-out"
        style={{
          opacity: isHovered ? 1 : 0,
          background: `radial-gradient(450px circle at ${mousePos.x}px ${mousePos.y}px, ${spotlightColor}, transparent 75%)`,
        }}
      />

      {/* Top 1px hairline inner shine */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/20 to-transparent z-10" />

      {/* Corner crosshair markers (Godly technical precision design) */}
      {showCrosshairs && (
        <>
          <span className="pointer-events-none absolute top-2 left-2 font-mono text-[10px] text-white/20 select-none z-10 leading-none">
            +
          </span>
          <span className="pointer-events-none absolute top-2 right-2 font-mono text-[10px] text-white/20 select-none z-10 leading-none">
            +
          </span>
          <span className="pointer-events-none absolute bottom-2 left-2 font-mono text-[10px] text-white/20 select-none z-10 leading-none">
            +
          </span>
          <span className="pointer-events-none absolute bottom-2 right-2 font-mono text-[10px] text-white/20 select-none z-10 leading-none">
            +
          </span>
        </>
      )}

      {/* Relative wrapper for card children so they render above the spotlight */}
      <div className="relative z-10 flex flex-col h-full justify-between">
        {children}
      </div>
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="block h-full cursor-pointer focus:outline-none" aria-label={ariaLabel}>
        {content}
      </Link>
    );
  }

  return content;
};
