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
  const timeoutRef = useRef<NodeJS.Timeout>();

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    clearTimeout(timeoutRef.current);
    timeoutRef.current = setTimeout(() => setCopied(false), 2000);
  }, [code]);

  useEffect(() => () => clearTimeout(timeoutRef.current), []);

  const lines = code.split("\n");
  const lang = (language || "python").toLowerCase();
  const canRun = runnable && (lang === "python" || lang === "javascript" || lang === "html" || lang === "js");

  // Map language to sandbox language
  const sandboxLang = lang === "js" ? "javascript" : (lang as "python" | "javascript" | "html");

  return (
    <>
      <div className={cn(
        "group relative rounded-xl border border-border bg-[#0d1117] overflow-hidden",
        className
      )}>
        {/* Header bar */}
        <div className="flex items-center justify-between px-4 py-2 border-b border-white/10">
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
            {language}
          </span>
          <div className="flex items-center gap-1">
            {canRun && (
              <button
                onClick={() => setShowSandbox(true)}
                className="flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium text-emerald-400 hover:text-emerald-300 hover:bg-emerald-500/10 transition-colors"
                title="Run this code"
              >
                <Play className="h-3.5 w-3.5 fill-current" />
                Run
              </button>
            )}
            <button
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2 py-1 rounded-md text-xs text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
            >
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        </div>

        {/* Code display */}
        <div className="overflow-x-auto p-4">
          <pre className="text-sm leading-relaxed" style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}>
            <code>
              {lines.map((line, i) => (
                <div key={i} className="table-row">
                  {showLineNumbers && (
                    <span className="table-cell select-none pr-4 text-right text-slate-600 w-12">
                      {i + 1}
                    </span>
                  )}
                  <span className="table-cell text-slate-300">{line || " "}</span>
                </div>
              ))}
            </code>
          </pre>
        </div>
      </div>

      {/* Sandbox overlay */}
      {showSandbox && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
          <div className="w-full max-w-5xl h-[85vh] rounded-2xl overflow-hidden shadow-2xl border border-white/10">
            {/* Overlay header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#161b22] border-b border-white/10">
              <div className="flex items-center gap-2">
                <Play className="h-4 w-4 text-emerald-400 fill-current" />
                <span className="text-sm font-medium text-slate-200">Code Playground</span>
                <span className="text-xs text-slate-500">— experiment freely</span>
              </div>
              <button
                onClick={() => setShowSandbox(false)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition-colors"
              >
                <X className="h-5 w-5" />
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
