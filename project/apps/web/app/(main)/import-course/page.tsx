"use client";

import { useState, useRef } from "react";
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
} from "lucide-react";
import { importContent, importPdf, ImportContentResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";

const languages = ["Python", "JavaScript", "TypeScript", "HTML/CSS", "SQL", "Go", "Rust", "Java", "C++", "C#"];
const categories = ["Frontend", "Backend", "Full Stack", "DevOps", "AI", "Mobile"];
const difficulties = ["beginner", "intermediate", "advanced"];

export default function ImportCoursePage() {
  const [sourceText, setSourceText] = useState("");
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [inputMode, setInputMode] = useState<"text" | "pdf">("text");
  const [courseTitle, setCourseTitle] = useState("");
  const [language, setLanguage] = useState("Python");
  const [category, setCategory] = useState("Backend");
  const [difficulty, setDifficulty] = useState("beginner");
  const [apiKey, setApiKey] = useState("");
  const [apiUrl, setApiUrl] = useState("https://shulker.in/api/colide_api_gateway-v1.0/");
  const [result, setResult] = useState<ImportContentResponse | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const mutation = useMutation({
    mutationFn: async () => {
      if (inputMode === "pdf" && pdfFile) {
        return importPdf({
          file: pdfFile,
          course_title: courseTitle || undefined,
          programming_language: language,
          technology: language,
          category,
          difficulty,
          provider: "custom",
          api_key: apiKey,
          api_url: apiUrl,
        });
      }
      return importContent({
        source_text: sourceText,
        course_title: courseTitle || undefined,
        programming_language: language,
        technology: language,
        category,
        difficulty,
        provider: "custom",
        api_key: apiKey,
        api_url: apiUrl,
      });
    },
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setResult(null);
    mutation.mutate();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      if (file.size > 50 * 1024 * 1024) {
        alert("File is too large. Maximum size is 50 MB.");
        return;
      }
      setPdfFile(file);
      setInputMode("pdf");
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 50 * 1024 * 1024) {
        alert("File is too large. Maximum size is 50 MB.");
        return;
      }
      setPdfFile(file);
      setInputMode("pdf");
    }
  };

  const canSubmit = inputMode === "text"
    ? sourceText.trim().length > 0 && apiKey.trim().length > 0
    : pdfFile !== null && apiKey.trim().length > 0;

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
          <h1 className="text-2xl font-bold tracking-tight text-card-foreground">Import Course</h1>
          <p className="text-muted-foreground">
            Upload a PDF or paste source text to create a structured course
          </p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-5">
        {/* Form */}
        <div className="lg:col-span-3">
          <form onSubmit={handleSubmit} className="space-y-6">
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
                  placeholder="Paste your content here..."
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
                  Upload a PDF file (book, handbook, or article)
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
                        Supports .pdf files up to 50 MB
                      </p>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Course settings */}
            <div className="rounded-2xl border border-border bg-card p-6">
              <label className="flex items-center gap-2 text-lg font-semibold text-card-foreground">
                <BookOpen className="h-5 w-5 text-primary" />
                Course Settings
              </label>
              <div className="mt-4 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="mb-1 block text-sm font-medium text-card-foreground">Course Title</label>
                  <input
                    type="text"
                    value={courseTitle}
                    onChange={(e) => setCourseTitle(e.target.value)}
                    placeholder="AI will generate from content"
                    className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  />
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-card-foreground">Language</label>
                  <select
                    value={language}
                    onChange={(e) => setLanguage(e.target.value)}
                    className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  >
                    {languages.map((l) => (
                      <option key={l} value={l}>{l}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-card-foreground">Category</label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  >
                    {categories.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="mb-1 block text-sm font-medium text-card-foreground">Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full rounded-xl border border-border bg-background px-4 py-2.5 text-foreground focus:border-primary focus:ring-1 focus:ring-primary"
                  >
                    {difficulties.map((d) => (
                      <option key={d} value={d}>{d.charAt(0).toUpperCase() + d.slice(1)}</option>
                    ))}
                  </select>
                </div>
              </div>
            </div>

            {/* API Key */}
            <div className="rounded-2xl border border-border bg-card p-6">
              <label className="flex items-center gap-2 text-lg font-semibold text-card-foreground">
                <Key className="h-5 w-5 text-primary" />
                Your AI API Key
              </label>
              <p className="mb-3 mt-1 text-sm text-muted-foreground">
                Your API key is sent directly to the AI provider and is not stored on this server.
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
                placeholder="API endpoint URL"
                className="w-full rounded-xl border border-border bg-background px-4 py-2.5 font-mono text-sm text-foreground placeholder:text-muted-foreground focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </div>

            <Button
              type="submit"
              disabled={mutation.isPending || !canSubmit}
              className="w-full gap-2"
              size="lg"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  {inputMode === "pdf" ? "Extracting PDF & " : ""}Generating course...
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  {inputMode === "pdf" ? "Upload & Generate Course" : "Generate Course"}
                </>
              )}
            </Button>
          </form>
        </div>

        {/* Sidebar: Preview / Results */}
        <div className="lg:col-span-2">
          {mutation.isPending && (
            <div className="rounded-2xl border border-border bg-card p-6">
              <h3 className="flex items-center gap-2 text-lg font-semibold text-card-foreground">
                <Loader2 className="h-5 w-5 animate-spin text-primary" />
                Creating course...
              </h3>
              <div className="mt-4 space-y-3">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-4 w-2/3" />
                <Skeleton className="h-4 w-3/4" />
              </div>
              <p className="mt-4 text-sm text-muted-foreground">
                {inputMode === "pdf"
                  ? "Extracting text from PDF then generating course structure..."
                  : "AI is analyzing the source text and structuring it into modules and lessons..."}
              </p>
            </div>
          )}

          {mutation.isError && (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-6 dark:border-red-900 dark:bg-red-950">
              <div className="flex items-start gap-3">
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-600 dark:text-red-400" />
                <div>
                  <h3 className="font-semibold text-red-800 dark:text-red-200">Import failed</h3>
                  <p className="mt-1 text-sm text-red-700 dark:text-red-300">
                    {mutation.error instanceof Error ? mutation.error.message : "An unexpected error occurred"}
                  </p>
                </div>
              </div>
            </div>
          )}

          {result && !mutation.isPending && (
            <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-6 dark:border-emerald-900 dark:bg-emerald-950">
              <div className="flex items-start gap-3">
                <CheckCircle2 className="mt-0.5 h-6 w-6 shrink-0 text-emerald-600 dark:text-emerald-400" />
                <div>
                  <h3 className="text-lg font-bold text-emerald-800 dark:text-emerald-200">
                    Course created!
                  </h3>
                  <p className="mt-2 text-sm text-emerald-700 dark:text-emerald-300">
                    {result.message}
                  </p>
                  <div className="mt-4 space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <BookOpen className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
                      <span className="text-emerald-800 dark:text-emerald-200">
                        <strong>{result.course_title}</strong>
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-emerald-700 dark:text-emerald-300">
                      {result.modules_created} modules · {result.lessons_created} lessons
                    </div>
                  </div>
                  <div className="mt-6 flex gap-3">
                    <Link
                      href={`/courses/${result.course_id}`}
                      className="inline-flex items-center gap-2 rounded-xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
                    >
                      View Course
                    </Link>
                    <Button
                      onClick={() => {
                        setResult(null);
                        setSourceText("");
                        setCourseTitle("");
                        setPdfFile(null);
                      }}
                      variant="secondary"
                      className="gap-2"
                    >
                      Import Another
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {!mutation.isPending && !mutation.isError && !result && (
            <div className="rounded-2xl border border-dashed border-border bg-card/50 p-8 text-center">
              <Sparkles className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold text-card-foreground">
                Ready to import
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                {inputMode === "pdf"
                  ? "Upload a PDF file and enter your API key to generate a course."
                  : "Paste your source text and API key, then click Generate Course."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
