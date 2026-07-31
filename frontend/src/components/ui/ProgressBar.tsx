'use client';

import { cn } from '@/lib/utils';
import { Star, StarHalf } from 'lucide-react';

interface ProgressBarProps {
  value: number;
  max?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'brand' | 'success' | 'warning';
  showLabel?: boolean;
  className?: string;
}

export function ProgressBar({ value, max = 100, size = 'md', variant = 'brand', showLabel = true, className }: ProgressBarProps) {
  const percentage = Math.min(Math.round((value / max) * 100), 100);
  const heights = { sm: 'h-1.5', md: 'h-2.5', lg: 'h-4' };
  const colors = {
    brand: 'bg-brand-600',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
  };

  return (
    <div className={cn('w-full', className)}>
      <div className={cn('w-full rounded-full bg-surface-secondary overflow-hidden', heights[size])}>
        <div
          className={cn('h-full rounded-full transition-all duration-500 ease-out', colors[variant])}
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between mt-1">
          <span className="text-xs text-ink-tertiary">{percentage}%</span>
          <span className="text-xs text-ink-tertiary">{value}/{max}</span>
        </div>
      )}
    </div>
  );
}

interface RatingProps {
  value: number;
  count?: number;
  size?: 'sm' | 'md';
}

export function Rating({ value, count, size = 'sm' }: RatingProps) {
  const stars = [];
  const fullStars = Math.floor(value);
  const hasHalf = value - fullStars >= 0.3;
  const starSize = size === 'sm' ? 'h-3.5 w-3.5' : 'h-4 w-4';

  for (let i = 0; i < fullStars; i++) {
    stars.push(<Star key={`full-${i}`} className={cn(starSize, 'fill-amber-400 text-amber-400')} />);
  }
  if (hasHalf) {
    stars.push(<StarHalf key="half" className={cn(starSize, 'fill-amber-400 text-amber-400')} />);
  }

  return (
    <div className="flex items-center gap-1">
      <div className="flex">{stars}</div>
      <span className="text-sm font-semibold text-ink">{value.toFixed(1)}</span>
      {count !== undefined && (
        <span className="text-xs text-ink-tertiary">({count.toLocaleString()})</span>
      )}
    </div>
  );
}
