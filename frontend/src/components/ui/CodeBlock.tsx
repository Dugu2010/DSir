'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { Copy, Check } from 'lucide-react';

interface CodeBlockProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
  className?: string;
}

export function CodeBlock({ code, language = 'python', showLineNumbers = true, className }: CodeBlockProps) {
  const [copied, setCopied] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout>();

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => setCopied(false), 2000);
  }, [code]);

  useEffect(() => () => clearTimeout(timeoutRef.current), []);

  const lines = code.split('\n');

  return (
    <div className={cn('group relative rounded-xl border border-border bg-[#0d1117] dark:bg-[#0d1117] overflow-hidden', className)}>
      <div className="flex items-center justify-between px-4 py-2 border-b border-white/10">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">{language}</span>
        <button
          onClick={handleCopy}
          className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
        >
          {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          {copied ? 'Copied' : 'Copy'}
        </button>
      </div>
      <div className="overflow-x-auto p-4">
        <pre className="text-sm leading-relaxed">
          <code className={`language-${language}`}>
            {lines.map((line, i) => (
              <div key={i} className="table-row">
                {showLineNumbers && (
                  <span className="table-cell select-none pr-4 text-right text-slate-600 w-12">{i + 1}</span>
                )}
                <span className="table-cell text-slate-300">{line || ' '}</span>
              </div>
            ))}
          </code>
        </pre>
      </div>
    </div>
  );
}
