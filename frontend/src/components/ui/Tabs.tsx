'use client';

import { cn } from '@/lib/utils';

interface TabsProps {
  tabs: { id: string; label: string; count?: number }[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
}

export function Tabs({ tabs, activeTab, onChange, className }: TabsProps) {
  return (
    <div className={cn('flex border-b border-border gap-0', className)}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={cn(
            'relative px-4 py-3 text-sm font-medium transition-colors',
            activeTab === tab.id
              ? 'text-brand-600'
              : 'text-ink-secondary hover:text-ink',
          )}
        >
          {tab.label}
          {tab.count !== undefined && (
            <span className={cn(
              'ml-1.5 rounded-full px-1.5 py-0.5 text-xs',
              activeTab === tab.id
                ? 'bg-brand-100 text-brand-700 dark:bg-brand-900/30 dark:text-brand-400'
                : 'bg-surface-secondary text-ink-tertiary',
            )}>
              {tab.count}
            </span>
          )}
          {activeTab === tab.id && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand-600 rounded-full" />
          )}
        </button>
      ))}
    </div>
  );
}
