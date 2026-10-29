"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { practice } from "@/lib/api";
import type { SavedSnippet } from "@/lib/types";
import Sandbox from "@/components/Sandbox";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import {
  ArrowLeft, Code2, Plus, Save, Trash2, TerminalSquare, FileCode2,
} from "lucide-react";
import toast from "react-hot-toast";

const TEMPLATES = [
  {
    name: "Hello, world",
    code: '# Your first program\nprint("Hello, DSir!")\n\nname = "Learner"\nprint(f"Welcome, {name}.")\n',
    stdin: "",
  },
  {
    name: "Read input",
    code: '# Type values in the Standard input box below\nname = input("Your name: ")\nage = int(input("Your age: "))\nprint(f"Hi {name}, next year you will be {age + 1}.")\n',
    stdin: "Ada\n36\n",
  },
  {
    name: "Loop and total",
    code: "numbers = [4, 8, 15, 16, 23, 42]\ntotal = 0\nfor number in numbers:\n    total += number\n    print(f\"added {number}, total {total}\")\n\nprint(\"average:\", round(total / len(numbers), 2))\n",
    stdin: "",
  },
  {
    name: "Functions and tests",
    code: 'def is_even(number):\n    return number % 2 == 0\n\n\nfor value in range(1, 7):\n    print(value, "even" if is_even(value) else "odd")\n\nassert is_even(10) is True\nassert is_even(7) is False\nprint("checks passed")\n',
    stdin: "",
  },
];

const EMPTY_CODE = '# Start a new snippet\n\nprint("Hello, DSir!")\n';

export default function WorkspacePage() {
  const queryClient = useQueryClient();
  const [code, setCode] = useState(TEMPLATES[0].code);
  const [stdin, setStdin] = useState("");
  const [title, setTitle] = useState("Untitled snippet");
  const [activeId, setActiveId] = useState<string | null>(null);
  const [editorRevision, setEditorRevision] = useState(0);

  const { data: snippets, isLoading, error } = useQuery({
    queryKey: ["saved-snippets"],
    queryFn: () => practice.listSnippets(),
  });

  const saveMutation = useMutation({
    mutationFn: async () => {
      const cleanTitle = title.trim() || "Untitled snippet";
      if (activeId) {
        return practice.updateSnippet(activeId, { title: cleanTitle, code, stdin });
      }
      return practice.createSnippet({ title: cleanTitle, code, stdin });
    },
    onSuccess: (snippet: SavedSnippet) => {
      setActiveId(snippet.id);
      setTitle(snippet.title);
      queryClient.invalidateQueries({ queryKey: ["saved-snippets"] });
      toast.success("Snippet saved");
    },
    onError: () => toast.error("Could not save this snippet."),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => practice.deleteSnippet(id),
    onSuccess: (_data, id) => {
      queryClient.invalidateQueries({ queryKey: ["saved-snippets"] });
      if (activeId === id) startNew();
      toast.success("Snippet deleted");
    },
    onError: () => toast.error("Could not delete this snippet."),
  });

  const snippetList = useMemo(() => snippets ?? [], [snippets]);

  function loadSnippet(snippet: SavedSnippet) {
    setActiveId(snippet.id);
    setTitle(snippet.title);
    setCode(snippet.code);
    setStdin(snippet.stdin ?? "");
    setEditorRevision((value) => value + 1);
  }

  function startNew() {
    setActiveId(null);
    setTitle("Untitled snippet");
    setCode(EMPTY_CODE);
    setStdin("");
    setEditorRevision((value) => value + 1);
  }

  function loadTemplate(template: (typeof TEMPLATES)[number]) {
    setActiveId(null);
    setTitle(template.name);
    setCode(template.code);
    setStdin(template.stdin);
    setEditorRevision((value) => value + 1);
  }

  return (
    <div className="max-w-7xl mx-auto space-y-5">
      <div className="flex flex-wrap items-center gap-3">
        <Link
          href="/practice"
          className="p-2 rounded-lg text-ink-tertiary hover:text-ink hover:bg-surface-tertiary dark:hover:bg-white/5"
          aria-label="Back to practice"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div className="min-w-0 flex-1">
          <p className="font-mono text-[11px] uppercase tracking-[0.18em] text-coral-600 dark:text-coral-400 mb-1">{"// "}Independent workspace</p>
          <h1 className="font-display text-xl sm:text-3xl font-medium tracking-tight text-ink flex items-center gap-2">
            <TerminalSquare className="h-6 w-6 sm:h-7 sm:w-7 text-coral-500 shrink-0" />
            <span className="break-words">Python Playground</span>
          </h1>
        </div>
        <Badge variant="outline" size="sm" className="hidden sm:inline-flex shrink-0">Runs in your browser</Badge>
      </div>

      <div className="grid gap-5 lg:grid-cols-[260px_minmax(0,1fr)]">
        <aside className="order-2 lg:order-1 space-y-4 min-w-0">
          <div className="rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-4 space-y-3">
            <div className="flex items-center justify-between gap-2">
              <h2 className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-tertiary flex items-center gap-2">
                <FileCode2 className="h-3.5 w-3.5 text-coral-500" /> Saved snippets
              </h2>
              <button
                onClick={startNew}
                className="flex items-center gap-1 text-xs font-medium text-coral-600 dark:text-coral-400 hover:underline"
              >
                <Plus className="h-3.5 w-3.5" /> New
              </button>
            </div>

            {isLoading ? (
              <p className="text-xs text-ink-tertiary">Loading your snippets...</p>
            ) : error ? (
              <p className="text-xs text-red-600 dark:text-red-400">
                Could not load snippets. Your current code is still safe.
              </p>
            ) : snippetList.length === 0 ? (
              <p className="text-xs text-ink-tertiary leading-relaxed">
                Nothing saved yet. Write something, give it a title, and save it here.
              </p>
            ) : (
              <ul className="space-y-1.5 max-h-52 lg:max-h-[320px] overflow-y-auto pr-1">
                {snippetList.map((snippet) => (
                  <li key={snippet.id} className="flex items-center gap-1">
                    <button
                      onClick={() => loadSnippet(snippet)}
                      className={`flex-1 min-w-0 text-left px-2.5 py-2 rounded-lg text-sm transition-colors ${
                        activeId === snippet.id
                          ? "bg-surface-tertiary dark:bg-night-400 text-ink font-semibold"
                          : "text-ink-secondary hover:bg-surface-secondary dark:hover:bg-white/5"
                      }`}
                    >
                      <span className="block truncate">{snippet.title}</span>
                      <span className="block text-[10px] text-ink-tertiary mt-0.5">
                        {new Date(snippet.updated_at).toLocaleDateString()}
                      </span>
                    </button>
                    <button
                      onClick={() => deleteMutation.mutate(snippet.id)}
                      disabled={deleteMutation.isPending}
                      className="p-1.5 rounded-md text-ink-tertiary hover:text-red-500 hover:bg-red-500/10 shrink-0"
                      aria-label={`Delete ${snippet.title}`}
                      title="Delete snippet"
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div className="rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 p-4 space-y-2">
            <h2 className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-tertiary flex items-center gap-2">
              <Code2 className="h-3.5 w-3.5 text-coral-500" /> Templates
            </h2>
            <div className="flex flex-wrap gap-1.5">
              {TEMPLATES.map((template) => (
                <button
                  key={template.name}
                  onClick={() => loadTemplate(template)}
                  className="px-2.5 py-1.5 rounded-lg border border-border dark:border-white/10 text-xs text-ink-secondary hover:border-coral-400 hover:text-ink transition-colors"
                >
                  {template.name}
                </button>
              ))}
            </div>
            <p className="text-[11px] text-ink-tertiary leading-relaxed pt-1">
              Snippets are private to your account. Python runs in WebAssembly in this
              tab with no network or filesystem access.
            </p>
          </div>
        </aside>

        <section className="order-1 lg:order-2 min-w-0 space-y-3">
          <div className="flex flex-col sm:flex-row gap-2 sm:items-center">
            <label htmlFor="snippet-title" className="sr-only">Snippet title</label>
            <input
              id="snippet-title"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              maxLength={120}
              className="flex-1 min-w-0 px-3 py-2.5 rounded-lg border border-border dark:border-white/10 bg-surface dark:bg-night-500 text-sm text-ink outline-none focus:ring-2 focus:ring-coral-500"
              placeholder="Snippet title"
            />
            <div className="flex gap-2">
              <Button
                onClick={() => saveMutation.mutate()}
                loading={saveMutation.isPending}
                leftIcon={<Save className="h-4 w-4" />}
                className="flex-1 sm:flex-none"
              >
                {activeId ? "Save changes" : "Save snippet"}
              </Button>
              {activeId && (
                <Button variant="outline" onClick={startNew} className="flex-1 sm:flex-none">
                  New
                </Button>
              )}
            </div>
          </div>

          <Sandbox
            key={editorRevision}
            language="python"
            initialCode={code}
            stdin={stdin}
            onStdinChange={setStdin}
            onChange={setCode}
            height="clamp(460px, 62vh, 700px)"
            className="shadow-sm"
          />
          <p className="text-xs text-ink-tertiary">
            Use <kbd className="font-mono">Ctrl/⌘ + Enter</kbd> to run. The editor keeps
            long lines scrollable; the output panel never pushes the page sideways.
          </p>
        </section>
      </div>
    </div>
  );
}
