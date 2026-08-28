"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";
import { Copy, Check, Play, X } from "lucide-react";
import Sandbox from "@/components/Sandbox";

interface CodeBlockProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
  className?: string;
  runnable?: boolean;
}

export function CodeBlock({
  code,
  language = "python",
  showLineNumbers = true,
  className,
  runnable = true,
}: CodeBlockProps) {
  const [copied, setCopied] = useState(false);
  const [showSandbox, setShowSandbox] = useState(false);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);
  const closeButtonRef = useRef<HTMLButtonElement | null>(null);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(code);
      setCopied(true);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard unavailable (permissions, insecure context) — fail quietly
      // rather than throwing in the UI.
    }
  }, [code]);

  useEffect(() => () => { if (timeoutRef.current) clearTimeout(timeoutRef.current); }, []);

  // Close the sandbox overlay with Escape and restore focus to the Run button.
  useEffect(() => {
    if (!showSandbox) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setShowSandbox(false);
        closeButtonRef.current?.focus();
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [showSandbox]);

  const lines = code.split("\n");
  const lang = (language || "python").toLowerCase();
  const canRun = runnable && (lang === "python" || lang === "javascript" || lang === "html" || lang === "js");

  // Map language to sandbox language
  const sandboxLang = lang === "js" ? "javascript" : (lang as "python" | "javascript" | "html");

  return (
    <>
      <div className={cn(
        "group relative rounded-xl border border-border dark:border-white/10 bg-night-600 dark:bg-night-600 overflow-hidden",
        className
      )}>
        {/* Header bar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-paper-50/10 dark:border-white/10 bg-paper-50/5 dark:bg-white/[0.03]">
          <span className="flex items-center gap-2">
            <span className="flex gap-1.5" aria-hidden="true">
              <span className="h-2.5 w-2.5 rounded-full bg-paper-50/20 dark:bg-white/15" />
              <span className="h-2.5 w-2.5 rounded-full bg-paper-50/20 dark:bg-white/15" />
              <span className="h-2.5 w-2.5 rounded-full bg-paper-50/20 dark:bg-white/15" />
            </span>
            <span className="text-xs font-mono uppercase tracking-eyebrow text-paper-50/50 dark:text-ink-tertiary">
              {language}
            </span>
          </span>
          <div className="flex items-center gap-1">
            {canRun && (
              <button
                onClick={() => setShowSandbox(true)}
                ref={closeButtonRef}
                className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium text-coral-400 hover:text-coral-300 hover:bg-coral-500/10 transition-colors focus-visible:outline-2 focus-visible:outline-coral-400"
                aria-haspopup="dialog"
              >
                <Play className="h-3.5 w-3.5 fill-current" aria-hidden="true" />
                Run
              </button>
            )}
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs text-paper-50/50 dark:text-ink-tertiary hover:text-paper-50 dark:hover:text-ink hover:bg-white/10 transition-colors focus-visible:outline-2 focus-visible:outline-white/60"
              aria-label={copied ? "Copied to clipboard" : "Copy code to clipboard"}
            >
              {copied ? <Check className="h-3.5 w-3.5 text-coral-400" aria-hidden="true" /> : <Copy className="h-3.5 w-3.5" aria-hidden="true" />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        </div>

        {/* Code display */}
        <div className="overflow-x-auto max-h-[480px] overflow-y-auto">
          <pre className="text-sm leading-relaxed font-mono p-4" style={{ fontFamily: "var(--font-mono), 'JetBrains Mono', 'Fira Code', monospace" }}>
            <code>
              {lines.map((line, i) => (
                <div key={i} className="table-row">
                  {showLineNumbers && (
                    <span className="table-cell select-none pr-4 text-right text-paper-50/25 dark:text-ink-tertiary/60 w-12">
                      {i + 1}
                    </span>
                  )}
                  <span className="table-cell text-paper-50/90 dark:text-ink">{line || " "}</span>
                </div>
              ))}
            </code>
          </pre>
        </div>
      </div>

      {/* Sandbox overlay */}
      {showSandbox && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4"
          role="dialog"
          aria-modal="true"
          aria-label="Code playground"
          onClick={() => setShowSandbox(false)}
        >
          <div
            className="w-full max-w-5xl h-[85vh] rounded-2xl overflow-hidden shadow-2xl border border-paper-50/15 dark:border-white/10"
            onClick={e => e.stopPropagation()}
          >
            {/* Overlay header */}
            <div className="flex items-center justify-between px-4 py-3 bg-night-600 border-b border-paper-50/10 dark:border-white/10">
              <div className="flex items-center gap-2">
                <Play className="h-4 w-4 text-coral-400 fill-current" aria-hidden="true" />
                <span className="text-sm font-medium text-paper-50 dark:text-ink">Code Playground</span>
                <span className="text-xs text-paper-50/50 dark:text-ink-tertiary">— experiment freely</span>
              </div>
              <button
                onClick={() => setShowSandbox(false)}
                className="p-1.5 rounded-lg text-paper-50/50 dark:text-ink-tertiary hover:text-paper-50 dark:hover:text-ink hover:bg-white/10 transition-colors"
                aria-label="Close code playground"
              >
                <X className="h-5 w-5" aria-hidden="true" />
              </button>
            </div>
            <Sandbox
              language={sandboxLang}
              initialCode={code}
              height="calc(85vh - 44px)"
            />
          </div>
        </div>
      )}
    </>
  );
}
