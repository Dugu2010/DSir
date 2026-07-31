"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";
import { Play, RotateCcw, Terminal, Loader2, Maximize2, Minimize2, Copy, Check } from "lucide-react";

type Language = "python" | "javascript" | "html";

interface SandboxProps {
  language?: Language;
  initialCode?: string;
  readOnly?: boolean;
  height?: string;
  className?: string;
  onRun?: (code: string, output: string) => void;
}

// ── Pyodide singleton loader ──────────────────────────
let pyodidePromise: Promise<any> | null = null;
function loadPyodide(): Promise<any> {
  if (pyodidePromise) return pyodidePromise;
  pyodidePromise = (async () => {
    if (typeof window === "undefined") return null;
    // Load pyodide via script tag to avoid webpack build-time resolution
    const script = document.createElement("script");
    script.src = "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/pyodide.js";
    document.head.appendChild(script);
    await new Promise((resolve, reject) => {
      script.onload = resolve;
      script.onerror = reject;
    });
    // @ts-ignore
    const pyodide = await (window as any).loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/",
    });
    return pyodide;
  })();
  return pyodidePromise;
}

// ── HTML template wrapper ────────────────────────────
function wrapHTML(code: string): string {
  return `<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: system-ui, sans-serif; padding: 16px; line-height: 1.5; }
</style>
</head>
<body>${code}</body>
</html>`;
}

export default function Sandbox({
  language = "python",
  initialCode = "",
  readOnly = false,
  height = "300px",
  className,
  onRun,
}: SandboxProps) {
  const [code, setCode] = useState(initialCode);
  const [output, setOutput] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [isFullscreen, setFullscreen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [pyodide, setPyodide] = useState<any>(null);
  const [pyLoading, setPyLoading] = useState(language === "python");
  const outputRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  // Load Pyodide on mount for Python
  useEffect(() => {
    if (language !== "python") return;
    setPyLoading(true);
    loadPyodide()
      .then((p) => setPyodide(p))
      .catch(() => setOutput("Error: Failed to load Python runtime. Check your internet connection."))
      .finally(() => setPyLoading(false));
  }, [language]);

  // Run code
  const runCode = useCallback(async () => {
    if (!code.trim()) return;
    setIsRunning(true);
    setOutput("");

    try {
      if (language === "python") {
        // ── Python via Pyodide ──
        if (!pyodide) {
          setOutput("Python runtime not loaded yet. Please wait...");
          setIsRunning(false);
          return;
        }
        let result = "";
        pyodide.setStdout({
          batched: (text: string) => { result += text + "\n"; },
        });
        pyodide.setStderr({
          batched: (text: string) => { result += "[stderr] " + text + "\n"; },
        });
        try {
          await pyodide.runPythonAsync(code);
        } catch (e: any) {
          result += `Error: ${e.message || e}`;
        }
        setOutput(result || "(no output)");
        onRun?.(code, result);
      } else if (language === "javascript") {
        // ── JavaScript via sandboxed iframe ──
        const wrapped = wrapHTML(`<script>${code}<\/script>`);
        if (iframeRef.current) {
          iframeRef.current.srcdoc = wrapped;
          // Capture console.log from iframe
          setTimeout(() => {
            try {
              const iframe = iframeRef.current;
              if (!iframe?.contentWindow) return;
              // Override console in the iframe
              const script = iframe.contentDocument?.createElement("script");
              if (!script) return;
              script.textContent = `
                window.__output__ = [];
                const _log = console.log;
                const _err = console.error;
                console.log = (...args) => {
                  _log(...args);
                  window.__output__.push(args.map(String).join(' '));
                };
                console.error = (...args) => {
                  _err(...args);
                  window.__output__.push('[Error] ' + args.map(String).join(' '));
                };
              `;
              iframe.contentDocument?.head.appendChild(script);
            } catch {}
          }, 100);
          setTimeout(() => {
            try {
              const out = (iframeRef.current?.contentWindow as any)?.__output__;
              setOutput(out?.length ? out.join("\n") : "(no output)");
            } catch {
              setOutput("(no output)");
            }
          }, 500);
        }
      } else if (language === "html") {
        // ── HTML/CSS via sandboxed iframe ──
        if (iframeRef.current) {
          iframeRef.current.srcdoc = wrapHTML(code);
          setOutput("Rendered in preview below.");
        }
      }
    } catch (e: any) {
      setOutput(`Error: ${e.message || e}`);
    } finally {
      setIsRunning(false);
    }
  }, [code, language, pyodide, onRun]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const ta = textareaRef.current;
      if (!ta) return;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      setCode(code.substring(0, start) + "    " + code.substring(end));
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + 4;
      });
    }
    // Ctrl/Cmd + Enter to run
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runCode();
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Determine language-specific label and placeholder
  const langLabel = { python: "🐍 Python", javascript: "📜 JavaScript", html: "🌐 HTML" };
  const placeholder = {
    python: '# Write Python code here...\nprint("Hello, DSir! 🚀")\n\nname = "Learner"\nprint(f"Welcome, {name}!")\n',
    javascript: '// Write JavaScript here...\nconsole.log("Hello, DSir! 🚀");\n\nconst name = "Learner";\nconsole.log(`Welcome, ${name}!`);\n',
    html: '<!-- Write HTML here -->\n<h1>Hello, DSir! 🚀</h1>\n<p>Welcome to the sandbox!</p>\n',
  };

  return (
    <div
      className={cn(
        "rounded-2xl border border-border overflow-hidden bg-[#0d1117]",
        isFullscreen && "fixed inset-0 z-50 rounded-none",
        className
      )}
      style={{ height: isFullscreen ? "100vh" : height }}
    >
      {/* Toolbar */}
      <div className="flex items-center h-11 px-3 border-b border-white/10 bg-[#161b22] gap-2">
        <Terminal className="h-3.5 w-3.5 text-slate-400" />
        <span className="text-xs font-medium text-slate-300">{langLabel[language]}</span>
        {pyLoading && (
          <span className="flex items-center gap-1 text-xs text-amber-400 ml-2">
            <Loader2 className="h-3 w-3 animate-spin" /> Loading Python...
          </span>
        )}
        <div className="flex-1" />
        <button
          onClick={handleCopy}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors"
          title="Copy code"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
        <button
          onClick={() => setCode(initialCode)}
          className="flex items-center gap-1 px-2 py-1 rounded-md text-xs text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors"
          title="Reset"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={() => setFullscreen(!isFullscreen)}
          className="p-1.5 rounded-md text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors"
          title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
        >
          {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
        </button>
        <button
          onClick={runCode}
          disabled={isRunning || (language === "python" && pyLoading)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-600 text-white hover:bg-emerald-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isRunning ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <Play className="h-3.5 w-3.5 fill-current" />
          )}
          Run {language === "python" ? "(Ctrl+Enter)" : ""}
        </button>
      </div>

      {/* Editor + Output split */}
      <div className="flex flex-col" style={{ height: "calc(100% - 44px)" }}>
        {/* Code Editor */}
        <textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => !readOnly && setCode(e.target.value)}
          onKeyDown={handleKeyDown}
          readOnly={readOnly}
          className="flex-1 w-full bg-transparent text-slate-300 font-mono text-sm p-4 resize-none outline-none scrollbar-thin"
          style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace", lineHeight: 1.7 }}
          spellCheck={false}
          placeholder={placeholder[language]}
        />

        {/* Resize handle */}
        <div className="h-1 bg-white/5 cursor-row-resize hover:bg-brand-500/50 transition-colors" />

        {/* Output */}
        <div
          ref={outputRef}
          className="h-[120px] overflow-y-auto bg-[#0d1017] border-t border-white/5 p-3 font-mono text-xs text-slate-300"
        >
          {output ? (
            <pre className="whitespace-pre-wrap break-words">{output}</pre>
          ) : (
            <span className="text-slate-600 italic">Run code to see output here...</span>
          )}
        </div>

        {/* Hidden iframe for JS/HTML execution */}
        {(language === "javascript" || language === "html") && (
          <iframe
            ref={iframeRef}
            sandbox="allow-scripts"
            className="hidden"
            title="sandbox"
          />
        )}
      </div>
    </div>
  );
}
