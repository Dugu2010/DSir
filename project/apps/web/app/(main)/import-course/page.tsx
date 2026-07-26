"use client";

import { useState, useRef, useCallback } from "react";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import {
  ArrowLeft,
  BookOpen,
  FileText,
  Key,
  Loader2,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Upload,
  File,
  X,
  ChevronDown,
  ChevronUp,
  Layers,
  Code,
  Brain,
  Edit3,
  Save,
  Trash2,
  Plus,
  GripVertical,
} from "lucide-react";
import {
  importPreview,
  importPreviewPdf,
  importApprove,
  ImportPreviewResponse,
  ImportContentResponse,
  ModuleProposal,
  LessonProposal,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

export default function ImportCoursePage() {
  // ── Step tracking ───────────────────────────────────────────────────
  const [step, setStep] = useState<"upload" | "preview" | "done">("upload");

  // ── Upload step ──────────────────────────────────────────────────────
  const [sourceText, setSourceText] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [inputMode, setInputMode] = useState<"text" | "pdf">("text");
  const [apiKey, setApiKey] = useState("");
  const [apiUrl, setApiUrl] = useState("https://shulker.in/api/colide_api_gateway-v1.0/");
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  // ── Preview / editing ────────────────────────────────────────────────
  const [preview, setPreview] = useState<ImportPreviewResponse | null>(null);
  const [editable, setEditable] = useState<ImportPreviewResponse | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [expandedModules, setExpandedModules] = useState<Set<number>>(new Set());
  const [result, setResult] = useState<ImportContentResponse | null>(null);

  // ── Mutations ────────────────────────────────────────────────────────
  const previewMutation = useMutation({
    mutationFn: async () => {
      if (inputMode === "pdf" && pdfFile) {
        return importPreviewPdf({
          file: pdfFile,
          provider: "custom",
          api_key: apiKey,
          api_url: apiUrl,
        });
      }
      return importPreview({
        source_text: sourceText,
        provider: "custom",
        api_key: apiKey,
        api_url: apiUrl,
      });
    },
    onSuccess: (data) => {
      setPreview(data);
      setEditable(JSON.parse(JSON.stringify(data))); // deep clone for editing
      setStep("preview");
      // Expand all modules by default
      setExpandedModules(new Set(data.modules.map((_, i) => i)));
    },
  });

  const approveMutation = useMutation({
    mutationFn: async () => {
      if (!editable) throw new Error("No proposal to approve");
      return importApprove(editable);
    },
    onSuccess: (data) => {
      setResult(data);
      setStep("done");
    },
  });

  const handleUpload = (e: React.FormEvent) => {
    e.preventDefault();
    previewMutation.mutate();
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      if (file.size > 100 * 1024 * 1024) {
        alert("File is too large. Maximum size is 100 MB.");
        return;
      }
      setPdfFile(file);
      setInputMode("pdf");
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 100 * 1024 * 1024) {
        alert("File is too large. Maximum size is 100 MB.");
        return;
      }
      setPdfFile(file);
      setInputMode("pdf");
    }
  }, []);

  const canUpload = inputMode === "text"
    ? sourceText.trim().length > 0 && apiKey.trim().length > 0
    : pdfFile !== null && apiKey.trim().length > 0;

  // ── Editing helpers ──────────────────────────────────────────────────
  const toggleModule = (idx: number) => {
    setExpandedModules((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  const updateField = useCallback(<K extends keyof ImportPreviewResponse>(
    key: K, value: ImportPreviewResponse[K]
  ) => {
    if (!editable) return;
    setEditable({ ...editable, [key]: value });
  }, [editable]);

  const updateModule = useCallback((idx: number, field: keyof ModuleProposal, value: string) => {
    if (!editable) return;
    const modules = [...editable.modules];
    modules[idx] = { ...modules[idx], [field]: value };
    setEditable({ ...editable, modules });
  }, [editable]);

  const updateLesson = useCallback(
    (modIdx: number, lesIdx: number, field: keyof LessonProposal, value: string | string[] | Record<string, string | string[]>) => {
      if (!editable) return;
      const modules = [...editable.modules];
      const lessons = [...modules[modIdx].lessons];
      lessons[lesIdx] = { ...lessons[lesIdx], [field]: value };
      modules[modIdx] = { ...modules[modIdx], lessons };
      setEditable({ ...editable, modules });
    },
    [editable]
  );

  // ── Difficulty colors ────────────────────────────────────────────────
  const difficultyBadge = (d: string) => {
    const styles: Record<string, string> = {
      beginner: "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
      intermediate: "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
      advanced: "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300",
    };
    return styles[d.toLowerCase()] || styles.intermediate;
  };

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <div className="mx-auto max-w-4xl space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link
          href="/courses"
          className="flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-card text-card-foreground transition hover:bg-accent"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-card-foreground">
            {step === "upload" && "Import Course"}
            {step === "preview" && "Review & Approve Course"}
            {step === "done" && "Course Created"}
          </h1>
          <p className="text-muted-foreground">
            {step === "upload" && "Upload a PDF or paste source text — AI will structure it into a complete course"}
            {step === "preview" && "Review the AI-generated course structure. Edit anything before approving."}
            {step === "done" && "Your course has been created and published"}
          </p>
        </div>
      </div>

      {/* Steps indicator */}
      <div className="flex items-center gap-3 text-sm">
        <div className={cn("flex items-center gap-2", step === "upload" ? "text-primary font-semibold" : step === "done" ? "text-emerald-600" : "text-muted-foreground")}>
          <div className={cn("flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold", 
            step === "upload" ? "bg-primary text-primary-foreground" :
            step === "done" ? "bg-emerald-500 text-white" : "bg-muted text-muted-foreground")}>
            {step === "done" ? <CheckCircle2 className="h-4 w-4" /> : "1"}
          </div>
          Upload
        </div>
        <div className="h-px flex-1 bg-border" />
        <div className={cn("flex items-center gap-2", step === "preview" ? "text-primary font-semibold" : step === "done" ? "text-emerald-600" : "text-muted-foreground")}>
          <div className={cn("flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold",
            step === "preview" ? "bg-primary text-primary-foreground" :
            step === "done" ? "bg-emerald-500 text-white" : "bg-muted text-muted-foreground")}>
            {step === "done" ? <CheckCircle2 className="h-4 w-4" /> : "2"}
          </div>
          Review
        </div>
        <div className="h-px flex-1 bg-border" />
        <div className={cn("flex items-center gap-2", step === "done" ? "text-primary font-semibold text-emerald-600" : "text-muted-foreground")}>
          <div className={cn("flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold",
            step === "done" ? "bg-emerald-500 text-white" : "bg-muted text-muted-foreground")}>
            {step === "done" ? <CheckCircle2 className="h-4 w-4" /> : "3"}
          </div>
          Done
        </div>
      </div>

      {/* ───────────────────── STEP 1: UPLOAD ──────────────────────────── */}
      {step === "upload" && (
        <form onSubmit={handleUpload} className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-5">
            {/* Main content */}
            <div className="lg:col-span-3 space-y-6">
              {/* Input mode toggle */}
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => setInputMode("text")}
                  className={cn(
                    "flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition",
                    inputMode === "text"
                      ? "bg-primary text-primary-foreground"
                      : "bg-card text-card-foreground hover:bg-accent"
                  )}
                >
                  <FileText className="h-4 w-4" />
                  Paste Text
                </button>
                <button
                  type="button"
                  onClick={() => setInputMode("pdf")}
                  className={cn(
                    "flex items-center gap-2 rounded-xl px-4 py-2 text-sm font-medium transition",
                    inputMode === "pdf"
                      ? "bg-primary text-primary-foreground"
                      : "bg-card text-card-foreground hover:bg-accent"
                  )}
                >
                  <Upload className="h-4 w-4" />
                  Upload PDF
                </button>
              </div>

              {/* Text input */}
              {inputMode === "text" && (
                <div className="rounded-2xl border border-border bg-card p-6">
                  <label className="flex items-center gap-2 text-lg font-semibold text-card-foreground">
                    <FileText className="h-5 w-5 text-primary" />
                    Source Text
                  </label>
                  <p className="mb-3 mt-1 text-sm text-muted-foreground">
                    Paste the content from your book, PDF, or notes here
                  </p>
                  <textarea
                    value={sourceText}
                    onChange={(e) => setSourceText(e.target.value)}
                    rows={12}
                    placeholder="Paste your course content here..."
                    className="w-full rounded-xl border border-border bg-background p-4 font-mono text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                    required
                  />
                </div>
              )}

              {/* PDF upload */}
              {inputMode === "pdf" && (
                <div className="rounded-2xl border border-border bg-card p-6">
                  <label className="flex items-center gap-2 text-lg font-semibold text-card-foreground">
                    <Upload className="h-5 w-5 text-primary" />
                    Upload PDF
                  </label>
                  <p className="mb-3 mt-1 text-sm text-muted-foreground">
                    Upload a PDF file — AI will extract, analyze, and structure it
                  </p>
                  <div
                    onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                    onDragLeave={() => setDragOver(false)}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={cn(
                      "flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition",
                      dragOver
                        ? "border-primary bg-primary/5"
                        : pdfFile
                          ? "border-emerald-300 bg-emerald-50 dark:border-emerald-700 dark:bg-emerald-950"
                          : "border-border bg-background hover:border-primary/50 hover:bg-accent/30"
                    )}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf,application/pdf"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    {pdfFile ? (
                      <div className="flex items-center gap-3">
                        <File className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
                        <div className="text-left">
                          <p className="font-medium text-card-foreground">{pdfFile.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {(pdfFile.size / 1024 / 1024).toFixed(1)} MB
                          </p>
                        </div>
                        <button
                          type="button"
                          onClick={(e) => { e.stopPropagation(); setPdfFile(null); }}
                          className="rounded-full p-1 text-muted-foreground hover:bg-background hover:text-card-foreground"
                        >
                          <X className="h-4 w-4" />
                        </button>
                      </div>
                    ) : (
                      <>
                        <Upload className="mb-3 h-10 w-10 text-muted-foreground" />
                        <p className="font-medium text-card-foreground">
                          Drop your PDF here or click to browse
                        </p>
                        <p className="mt-1 text-sm text-muted-foreground">
                          Supports .pdf files up to 100 MB
                        </p>
                      </>
                    )}
                  </div>
                </div>
              )}

              {/* API Key */}
              <div className="rounded-2xl border border-border bg-card p-6">
                <label className="flex items-center gap-2 text-lg font-semibold text-card-foreground">
                  <Key className="h-5 w-5 text-primary" />
                  Your AI API Key
                </label>
                <p className="mb-3 mt-1 text-sm text-muted-foreground">
                  Your API key is sent directly to the AI provider. It is never stored on this server.
                </p>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your API key"
                  className="mb-3 w-full rounded-xl border border-border bg-background px-4 py-2.5 text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  required
                />
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  placeholder="API endpoint URL (defaults to shulker.in)"
                  className="w-full rounded-xl border border-border bg-background px-4 py-2.5 font-mono text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                />
              </div>

              <Button
                type="submit"
                disabled={previewMutation.isPending || !canUpload}
                className="w-full gap-2"
                size="lg"
              >
                {previewMutation.isPending ? (
                  <>
                    <Loader2 className="h-5 w-5 animate-spin" />
                    AI is analyzing & structuring...
                  </>
                ) : (
                  <>
                    <Sparkles className="h-5 w-5" />
                    Analyze & Generate Course Preview
                  </>
                )}
              </Button>
            </div>

            {/* Sidebar info */}
            <div className="lg:col-span-2">
              <div className="rounded-2xl border border-border bg-card p-6">
                <h3 className="flex items-center gap-2 text-lg font-semibold text-card-foreground">
                  <Brain className="h-5 w-5 text-primary" />
                  How it works
                </h3>
                <ul className="mt-4 space-y-3 text-sm text-muted-foreground">
                  <li className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">1</span>
                    Upload your PDF or paste the source text from your book / handbook
                  </li>
                  <li className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">2</span>
                    AI analyzes the content and generates a structured course with modules and lessons
                  </li>
                  <li className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">3</span>
                    AI decides the course title, language, category, and assigns difficulty per module
                  </li>
                  <li className="flex gap-3">
                    <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary/10 text-xs font-bold text-primary">4</span>
                    Review the preview, edit anything you want, then approve to publish
                  </li>
                </ul>
              </div>
            </div>
          </div>

          {previewMutation.isError && (
            <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
              <div>
                <p className="font-medium text-red-800 dark:text-red-200">Generation failed</p>
                <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                  {(previewMutation.error as Error)?.message || "An unknown error occurred. Please try again."}
                </p>
              </div>
            </div>
          )}
        </form>
      )}

      {/* ───────────────────── STEP 2: PREVIEW ────────────────────────── */}
      {step === "preview" && editable && (
        <div className="space-y-6">
          {/* Action bar */}
          <div className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border border-border bg-card p-4">
            <div className="flex items-center gap-3">
              {isEditing ? (
                <span className="flex items-center gap-2 text-sm font-medium text-amber-600 dark:text-amber-400">
                  <Edit3 className="h-4 w-4" />
                  Editing mode — click any field to modify
                </span>
              ) : (
                <span className="text-sm text-muted-foreground">
                  {editable.modules.length} modules · {editable.modules.reduce((s, m) => s + m.lessons.length, 0)} lessons
                </span>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  if (isEditing) {
                    // Save edits: copy current editable back
                    setIsEditing(false);
                  } else {
                    setIsEditing(true);
                  }
                }}
              >
                {isEditing ? (
                  <><Save className="mr-1.5 h-4 w-4" /> Done Editing</>
                ) : (
                  <><Edit3 className="mr-1.5 h-4 w-4" /> Edit</>
                )}
              </Button>
            </div>
          </div>

          {/* Course metadata */}
          <div className="rounded-2xl border border-border bg-card p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-card-foreground">Course Details</h2>
              {isEditing && <span className="text-xs text-muted-foreground italic">Click to edit</span>}
            </div>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Title</label>
                {isEditing ? (
                  <input
                    value={editable.title}
                    onChange={(e) => updateField("title", e.target.value)}
                    className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                ) : (
                  <p className="text-sm font-medium text-card-foreground">{editable.title}</p>
                )}
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Language</label>
                {isEditing ? (
                  <input
                    value={editable.programming_language}
                    onChange={(e) => updateField("programming_language", e.target.value)}
                    className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                ) : (
                  <p className="text-sm font-medium text-card-foreground">{editable.programming_language}</p>
                )}
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Category</label>
                {isEditing ? (
                  <input
                    value={editable.category}
                    onChange={(e) => updateField("category", e.target.value)}
                    className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                ) : (
                  <p className="text-sm font-medium text-card-foreground">{editable.category}</p>
                )}
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Technology</label>
                {isEditing ? (
                  <input
                    value={editable.technology}
                    onChange={(e) => updateField("technology", e.target.value)}
                    className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                ) : (
                  <p className="text-sm font-medium text-card-foreground">{editable.technology}</p>
                )}
              </div>
            </div>
            <div className="mt-4">
              <label className="mb-1 block text-xs font-medium text-muted-foreground">Description</label>
              {isEditing ? (
                <textarea
                  value={editable.description}
                  onChange={(e) => updateField("description", e.target.value)}
                  rows={2}
                  className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                />
              ) : (
                <p className="text-sm text-muted-foreground">{editable.description || "No description"}</p>
              )}
            </div>
            <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Skills</label>
                {isEditing ? (
                  <input
                    value={editable.skills.join(", ")}
                    onChange={(e) => updateField("skills", e.target.value.split(",").map(s => s.trim()).filter(Boolean))}
                    className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                    placeholder="Comma-separated skills"
                  />
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {editable.skills.map((s, i) => (
                      <span key={i} className="rounded-md bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                        {s}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              <div>
                <label className="mb-1 block text-xs font-medium text-muted-foreground">Learning Objectives</label>
                {isEditing ? (
                  <input
                    value={editable.learning_objectives.join(", ")}
                    onChange={(e) => updateField("learning_objectives", e.target.value.split(",").map(s => s.trim()).filter(Boolean))}
                    className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                    placeholder="Comma-separated objectives"
                  />
                ) : (
                  <div className="flex flex-wrap gap-1.5">
                    {editable.learning_objectives.map((o, i) => (
                      <span key={i} className="rounded-md bg-indigo-100 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300">
                        {o}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Modules & Lessons */}
          <div className="space-y-4">
            {editable.modules.map((mod, modIdx) => (
              <div key={modIdx} className="rounded-2xl border border-border bg-card overflow-hidden">
                {/* Module header */}
                <button
                  type="button"
                  onClick={() => toggleModule(modIdx)}
                  className="flex w-full items-center justify-between gap-3 p-4 text-left hover:bg-accent/40 transition"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <Layers className="h-5 w-5 shrink-0 text-primary" />
                    <div className="min-w-0">
                      {isEditing ? (
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground shrink-0">#{modIdx + 1}</span>
                          <input
                            value={mod.title}
                            onChange={(e) => updateModule(modIdx, "title", e.target.value)}
                            className="rounded-lg border border-border bg-background px-2 py-1 text-sm font-medium text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                            onClick={(e) => e.stopPropagation()}
                          />
                        </div>
                      ) : (
                        <p className="font-medium text-card-foreground">
                          {modIdx + 1}. {mod.title}
                        </p>
                      )}
                      <p className="mt-0.5 text-xs text-muted-foreground">
                        {mod.lessons.length} lessons · {mod.difficulty}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {!isEditing && (
                      <span className={cn("rounded-full px-2.5 py-0.5 text-xs font-medium", difficultyBadge(mod.difficulty))}>
                        {mod.difficulty}
                      </span>
                    )}
                    {expandedModules.has(modIdx) ? (
                      <ChevronUp className="h-5 w-5 text-muted-foreground" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-muted-foreground" />
                    )}
                  </div>
                </button>

                {/* Expanded content */}
                {expandedModules.has(modIdx) && (
                  <div className="border-t border-border p-4 space-y-4">
                    {/* Module description */}
                    {isEditing ? (
                      <textarea
                        value={mod.description}
                        onChange={(e) => updateModule(modIdx, "description", e.target.value)}
                        rows={2}
                        className="w-full rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                        placeholder="Module description"
                        onClick={(e) => e.stopPropagation()}
                      />
                    ) : (
                      mod.description && (
                        <p className="text-sm text-muted-foreground">{mod.description}</p>
                      )
                    )}

                    {/* Difficulty editing */}
                    {isEditing && (
                      <div>
                        <label className="mb-1 block text-xs font-medium text-muted-foreground">Difficulty</label>
                        <select
                          value={mod.difficulty}
                          onChange={(e) => updateModule(modIdx, "difficulty", e.target.value)}
                          className="rounded-lg border border-border bg-background px-3 py-1.5 text-sm text-foreground"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <option value="beginner">Beginner</option>
                          <option value="intermediate">Intermediate</option>
                          <option value="advanced">Advanced</option>
                        </select>
                      </div>
                    )}

                    {/* Lessons */}
                    <div className="space-y-3">
                      <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                        Lessons ({mod.lessons.length})
                      </p>
                      {mod.lessons.map((lsn, lesIdx) => (
                        <div
                          key={lesIdx}
                          className="rounded-xl border border-border bg-background p-3"
                        >
                          <div className="flex items-start justify-between gap-2">
                            <div className="flex-1 min-w-0">
                              {isEditing ? (
                                <input
                                  value={lsn.title}
                                  onChange={(e) => updateLesson(modIdx, lesIdx, "title", e.target.value)}
                                  className="w-full rounded-lg border border-border bg-card px-2 py-1 text-sm font-medium text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                                />
                              ) : (
                                <p className="text-sm font-medium text-card-foreground">
                                  {lesIdx + 1}. {lsn.title}
                                </p>
                              )}
                            </div>
                            <span className="shrink-0 rounded-md bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                              {lsn.code_language}
                            </span>
                          </div>

                          {/* Expandable lesson detail in editing mode */}
                          {isEditing && (
                            <div className="mt-3 space-y-2">
                              <textarea
                                value={lsn.body}
                                onChange={(e) => updateLesson(modIdx, lesIdx, "body", e.target.value)}
                                rows={3}
                                className="w-full rounded-lg border border-border bg-card px-2 py-1 text-xs text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                                placeholder="Lesson body (markdown)"
                              />
                              <textarea
                                value={lsn.code_example}
                                onChange={(e) => updateLesson(modIdx, lesIdx, "code_example", e.target.value)}
                                rows={2}
                                className="w-full rounded-lg border border-border bg-card px-2 py-1 font-mono text-xs text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                                placeholder="Code example"
                              />
                              <div className="grid grid-cols-2 gap-2">
                                <div>
                                  <label className="mb-0.5 block text-xs text-muted-foreground">Best practices</label>
                                  <input
                                    value={lsn.best_practices.join(", ")}
                                    onChange={(e) => updateLesson(modIdx, lesIdx, "best_practices", e.target.value.split(",").map(s => s.trim()).filter(Boolean))}
                                    className="w-full rounded-lg border border-border bg-card px-2 py-1 text-xs text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                                  />
                                </div>
                                <div>
                                  <label className="mb-0.5 block text-xs text-muted-foreground">Common mistakes</label>
                                  <input
                                    value={lsn.common_mistakes.join(", ")}
                                    onChange={(e) => updateLesson(modIdx, lesIdx, "common_mistakes", e.target.value.split(",").map(s => s.trim()).filter(Boolean))}
                                    className="w-full rounded-lg border border-border bg-card px-2 py-1 text-xs text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                                  />
                                </div>
                              </div>
                              <div>
                                <label className="mb-0.5 block text-xs text-muted-foreground">Quiz question</label>
                                <input
                                  value={typeof lsn.quiz?.question === "string" ? lsn.quiz.question : ""}
                                  onChange={(e) => updateLesson(modIdx, lesIdx, "quiz", { ...lsn.quiz, question: e.target.value })}
                                  className="w-full rounded-lg border border-border bg-card px-2 py-1 text-xs text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                                />
                              </div>
                              <input
                                value={lsn.try_it}
                                onChange={(e) => updateLesson(modIdx, lesIdx, "try_it", e.target.value)}
                                placeholder="Try it yourself exercise"
                                className="w-full rounded-lg border border-border bg-card px-2 py-1 text-xs text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                              />
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Approve button */}
          <Button
            onClick={() => {
              if (!isEditing) {
                // Save edits before approving
                setIsEditing(false);
              }
              approveMutation.mutate();
            }}
            disabled={approveMutation.isPending}
            className="w-full gap-2"
            size="lg"
          >
            {approveMutation.isPending ? (
              <>
                <Loader2 className="h-5 w-5 animate-spin" />
                Creating course...
              </>
            ) : (
              <>
                <CheckCircle2 className="h-5 w-5" />
                Approve & Create Course
              </>
            )}
          </Button>

          {approveMutation.isError && (
            <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 dark:border-red-800 dark:bg-red-950">
              <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />
              <div>
                <p className="font-medium text-red-800 dark:text-red-200">Failed to create course</p>
                <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                  {(approveMutation.error as Error)?.message || "An unknown error occurred."}
                </p>
              </div>
            </div>
          )}

          {/* Loading skeleton for preview */}
          {previewMutation.isPending && (
            <div className="rounded-2xl border border-border bg-card p-6">
              <div className="flex items-center gap-2 text-lg font-semibold text-card-foreground mb-4">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                AI is generating course structure...
              </div>
              <div className="space-y-3">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-32 w-full" />
              </div>
            </div>
          )}
        </div>
      )}

      {/* ───────────────────── STEP 3: DONE ────────────────────────────── */}
      {step === "done" && result && (
        <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-8 text-center dark:border-emerald-800 dark:bg-emerald-950">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100 dark:bg-emerald-900">
            <CheckCircle2 className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h2 className="text-xl font-bold text-card-foreground">{result.course_title}</h2>
          <p className="mt-2 text-muted-foreground">{result.message}</p>
          <div className="mt-4 flex items-center justify-center gap-6 text-sm text-muted-foreground">
            <span>{result.modules_created} modules</span>
            <span className="text-muted-foreground">·</span>
            <span>{result.lessons_created} lessons</span>
          </div>
          <div className="mt-6 flex items-center justify-center gap-3">
            <Link href={`/courses/${result.course_id}`}>
              <Button>
                <BookOpen className="mr-2 h-4 w-4" />
                View Course
              </Button>
            </Link>
            <Button
              variant="ghost"
              onClick={() => {
                setStep("upload");
                setPreview(null);
                setEditable(null);
                setResult(null);
                setSourceText("");
                setPdfFile(null);
              }}
            >
              Import Another
            </Button>
          </div>
        </div>
      )}

      {/* Loading state for upload step */}
      {step === "upload" && previewMutation.isPending && (
        <div className="rounded-2xl border border-border bg-card p-6">
          <div className="flex items-center gap-2 text-lg font-semibold text-card-foreground mb-4">
            <Loader2 className="h-5 w-5 animate-spin text-primary" />
            AI is analyzing your content...
          </div>
          <div className="space-y-3">
            <Skeleton className="h-5 w-3/4" />
            <Skeleton className="h-4 w-1/2" />
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-4 w-3/4" />
            <Skeleton className="h-32 w-full" />
          </div>
          <p className="mt-4 text-sm text-muted-foreground">
            Extracting key concepts, structuring modules, and generating lessons...
          </p>
        </div>
      )}
    </div>
  );
}
