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
  onChange?: (code: string) => void;
}

// Pyodide is loaded from the official jsDelivr distribution so the deployed
// Vercel build does not depend on an untracked /public/pyodide directory.
const PYODIDE_VERSION = "314.0.6";
const PYODIDE_BASE = `https://cdn.jsdelivr.net/pyodide/v${PYODIDE_VERSION}/full/`;

let pyodidePromise: Promise<any> | null = null;

function loadPyodide(): Promise<any> {
  if (pyodidePromise) return pyodidePromise;

  pyodidePromise = (async () => {
    if (typeof window === "undefined") return null;

    const existing = (window as any).loadPyodide;
    if (existing) {
      return existing({ indexURL: PYODIDE_BASE });
    }

    const script = document.createElement("script");
    script.src = `${PYODIDE_BASE}pyodide.js`;
    script.async = true;
    document.head.appendChild(script);

    await new Promise<void>((resolve, reject) => {
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Pyodide CDN could not be loaded."));
    });

    const loader = (window as any).loadPyodide;
    if (!loader) throw new Error("Pyodide loader is missing after download.");
    return loader({ indexURL: PYODIDE_BASE });
  })();

  return pyodidePromise;
}

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

function escapeScriptText(value: string): string {
  // Prevent learner code from terminating the generated <script> tag.
  return value.replace(/</g, "\\u003c");
}

export default function Sandbox({
  language = "python",
  initialCode = "",
  readOnly = false,
  height = "300px",
  className,
  onRun,
  onChange,
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
  const runIdRef = useRef(0);

  useEffect(() => {
    if (language !== "python") {
      setPyLoading(false);
      return;
    }

    let cancelled = false;
    setPyLoading(true);
    setOutput("");

    loadPyodide()
      .then((p) => {
        if (!cancelled) setPyodide(p);
      })
      .catch((error: any) => {
        if (!cancelled) {
          setOutput(`Error: Python runtime could not load. ${error?.message || "Please refresh and try again."}`);
        }
      })
      .finally(() => {
        if (!cancelled) setPyLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [language]);

  // Capture messages from the opaque-origin JS/HTML sandbox. We never access
  // iframe.contentDocument, which is intentionally unavailable for a secure
  // sandbox="allow-scripts" iframe.
  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      if (event.source !== iframeRef.current?.contentWindow) return;
      const data = event.data;
      if (!data || data.type !== "dsir-sandbox-result") return;
      if (data.runId !== runIdRef.current) return;

      setOutput(typeof data.output === "string" ? data.output : "(no output)");
      setIsRunning(false);
      onRun?.(code, typeof data.output === "string" ? data.output : "");
    };

    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [code, onRun]);

  const runCode = useCallback(async () => {
    if (!code.trim() || isRunning) return;

    const runId = ++runIdRef.current;
    setIsRunning(true);
    setOutput("");

    try {
      if (language === "python") {
        if (!pyodide) {
          setOutput("Python runtime is still loading. Please wait a moment and run again.");
          setIsRunning(false);
          return;
        }

        let result = "";
        pyodide.setStdout({
          batched: (text: string) => {
            result += text + "\n";
          },
        });
        pyodide.setStderr({
          batched: (text: string) => {
            result += `[stderr] ${text}\n`;
          },
        });

        try {
          await pyodide.runPythonAsync(code);
        } catch (error: any) {
          result += `Error: ${error?.message || error}`;
        }

        if (runId === runIdRef.current) {
          const finalOutput = result.trimEnd() || "(no output)";
          setOutput(finalOutput);
          onRun?.(code, finalOutput);
        }
        setIsRunning(false);
        return;
      }

      if (!iframeRef.current) {
        throw new Error("Sandbox frame is unavailable.");
      }

      if (language === "javascript") {
        const safeCode = escapeScriptText(code);
        iframeRef.current.srcdoc = `<!doctype html>
<html><head><meta charset="UTF-8"></head><body>
<script>
(() => {
  const runId = ${JSON.stringify(runId)};
  const lines = [];
  const format = (args) => args.map((value) => {
    try {
      if (typeof value === "string") return value;
      return JSON.stringify(value);
    } catch (_) {
      return String(value);
    }
  }).join(" ");
  console.log = (...args) => lines.push(format(args));
  console.info = (...args) => lines.push(format(args));
  console.warn = (...args) => lines.push("[Warning] " + format(args));
  console.error = (...args) => lines.push("[Error] " + format(args));
  window.onerror = (message, source, line, column) => {
    lines.push("Error: " + message + " (line " + line + ")");
    window.parent.postMessage({ type: "dsir-sandbox-result", runId, output: lines.join("\\n") }, "*");
    return true;
  };
  try {
    ${safeCode}
  } catch (error) {
    lines.push("Error: " + (error?.message || error));
  }
  window.parent.postMessage({
    type: "dsir-sandbox-result",
    runId,
    output: lines.join("\\n") || "(no output)"
  }, "*");
})();
</script></body></html>`;
        return;
      }

      iframeRef.current.srcdoc = wrapHTML(code);
      setOutput("Rendered in preview below.");
      setIsRunning(false);
      onRun?.(code, "Rendered in preview below.");
    } catch (error: any) {
      setOutput(`Error: ${error?.message || error}`);
      setIsRunning(false);
    }
  }, [code, isRunning, language, onRun, pyodide]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Tab") {
      e.preventDefault();
      const ta = textareaRef.current;
      if (!ta) return;
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const next = code.substring(0, start) + "    " + code.substring(end);
      setCode(next);
      onChange?.(next);
      requestAnimationFrame(() => {
        ta.selectionStart = ta.selectionEnd = start + 4;
      });
    }

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

  const langLabel = { python: "🐍 Python", javascript: "📜 JavaScript", html: "🌐 HTML" };
  const placeholder = {
    python: '# Write Python code here...\nprint("Hello, DSir! 🚀")\n\nname = "Learner"\nprint(f"Welcome, {name}!")\n',
    javascript: '// Write JavaScript here...\nconsole.log("Hello, DSir! 🚀");\n\nconst name = "Learner";\nconsole.log(`Welcome, ${name}!`);\n',
    html: '<!-- Write HTML here -->\n<h1>Hello, DSir! 🚀</h1>\n<p>Welcome to the sandbox!</p>\n',
  };

  return (
    <div
      className={cn(
        "rounded-2xl border border-border overflow-hidden bg-night-600",
        isFullscreen && "fixed inset-0 z-50 rounded-none",
        className
      )}
      style={{ height: isFullscreen ? "100vh" : height }}
    >
      <div className="flex items-center h-11 px-3 border-b border-paper-50/10 dark:border-white/10 bg-paper-50/5 dark:bg-white/[0.03] gap-2">
        <Terminal className="h-3.5 w-3.5 text-coral-500 dark:text-coral-400" />
        <span className="text-xs font-medium font-mono text-paper-50/80 dark:text-ink">{langLabel[language]}</span>
        {pyLoading && (
          <span className="flex items-center gap-1 text-xs text-amber-500 dark:text-amber-400 ml-2">
            <Loader2 className="h-3 w-3 animate-spin" /> Loading Python...
          </span>
        )}
        <div className="flex-1" />
        <button
          onClick={handleCopy}
          className="p-1.5 rounded-md text-paper-50/50 dark:text-ink-tertiary hover:text-paper-50 dark:hover:text-ink hover:bg-white/5 transition-colors"
          title="Copy code"
        >
          {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
        </button>
        <button
          onClick={() => { setCode(initialCode); onChange?.(initialCode); }}
          className="flex items-center gap-1 px-2 py-1 rounded-md text-xs text-paper-50/50 dark:text-ink-tertiary hover:text-paper-50 dark:hover:text-ink hover:bg-white/5 transition-colors"
          title="Reset"
        >
          <RotateCcw className="h-3.5 w-3.5" />
        </button>
        <button
          onClick={() => setFullscreen(!isFullscreen)}
          className="p-1.5 rounded-md text-paper-50/50 dark:text-ink-tertiary hover:text-paper-50 dark:hover:text-ink hover:bg-white/5 transition-colors"
          title={isFullscreen ? "Exit fullscreen" : "Fullscreen"}
        >
          {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
        </button>
        <button
          onClick={runCode}
          disabled={isRunning || (language === "python" && pyLoading)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-coral-500 text-night-600 hover:bg-coral-400 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isRunning ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5 fill-current" />}
          Run {language === "python" ? "(Ctrl+Enter)" : ""}
        </button>
      </div>

      <div className="flex flex-col" style={{ height: "calc(100% - 44px)" }}>
        <textarea
          ref={textareaRef}
          value={code}
          onChange={(e) => {
            if (readOnly) return;
            const value = e.target.value;
            setCode(value);
            onChange?.(value);
          }}
          onKeyDown={handleKeyDown}
          readOnly={readOnly}
          className="flex-1 w-full bg-transparent text-paper-50/90 dark:text-ink font-mono text-sm p-4 resize-none outline-none scrollbar-thin"
          style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace", lineHeight: 1.7 }}
          spellCheck={false}
          placeholder={placeholder[language]}
        />

        <div className="h-1 bg-paper-50/10 dark:bg-white/5 cursor-row-resize hover:bg-coral-500/60 transition-colors" />

        <div
          ref={outputRef}
          className="h-[120px] overflow-y-auto bg-night-600 border-t border-paper-50/10 dark:border-white/5 p-3 font-mono text-xs text-paper-50/80 dark:text-ink-secondary"
        >
          {output ? (
            <pre className="whitespace-pre-wrap break-words">{output}</pre>
          ) : (
            <span className="text-paper-50/40 dark:text-ink-tertiary italic">Run code to see output here...</span>
          )}
        </div>

        {(language === "javascript" || language === "html") && (
          <iframe
            ref={iframeRef}
            sandbox="allow-scripts"
            className={language === "html" ? "w-full h-32 border-t border-paper-50/10" : "hidden"}
            title="DSir code sandbox"
          />
        )}
      </div>
    </div>
  );
}
