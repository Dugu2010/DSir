'use client';

import { cn } from '@/lib/utils';
import { CheckCircle, AlertCircle, XCircle, Info, X } from 'lucide-react';
import { useEffect, useState } from 'react';

const icons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertCircle,
  info: Info,
};

const styles = {
  success: 'border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950/50',
  error: 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-950/50',
  warning: 'border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950/50',
  info: 'border-sky-200 bg-sky-50 dark:border-sky-800 dark:bg-sky-950/50',
};

const iconColors = {
  success: 'text-emerald-500',
  error: 'text-red-500',
  warning: 'text-amber-500',
  info: 'text-sky-500',
};

interface AlertProps {
  type?: keyof typeof styles;
  title?: string;
  children: React.ReactNode;
  onDismiss?: () => void;
  className?: string;
}

export function Alert({ type = 'info', title, children, onDismiss, className }: AlertProps) {
  const [visible, setVisible] = useState(true);
  const Icon = icons[type];

  useEffect(() => {
    if (type === 'success') {
      const timer = setTimeout(() => setVisible(false), 5000);
      return () => clearTimeout(timer);
    }
  }, [type]);

  if (!visible) return null;

  return (
    <div className={cn('flex items-start gap-3 rounded-xl border p-4', styles[type], className)}>
      <Icon className={cn('h-5 w-5 mt-0.5 flex-shrink-0', iconColors[type])} />
      <div className="flex-1 min-w-0">
        {title && <p className="text-sm font-semibold text-ink">{title}</p>}
        <div className="text-sm text-ink-secondary">{children}</div>
      </div>
      {(onDismiss || type === 'success') && (
        <button onClick={() => { setVisible(false); onDismiss?.(); }} className="flex-shrink-0 text-ink-tertiary hover:text-ink p-0.5">
          <X className="h-4 w-4" />
        </button>
      )}
    </div>
  );
}
