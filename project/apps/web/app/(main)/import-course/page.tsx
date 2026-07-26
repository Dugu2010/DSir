"use client";

import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import Link from "next/link";
import { ArrowLeft, BookOpen, FileText, Key, Loader2, Sparkles, CheckCircle2, AlertCircle } from "lucide-react";
import { importContent, ImportContentResponse } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ErrorMessage } from "@/components/ui/error-message";

const languages = ["Python", "JavaScript", "TypeScript", "HTML/CSS", "SQL", "Go", "Rust", "Java", "C++", "C#"];
const categories = ["Frontend", "Backend", "Full Stack", "DevOps", "AI", "Mobile"];
const difficulties = ["beginner", "intermediate", "advanced"];

export default function ImportCoursePage() {
  const [sourceText, setSourceText] = useState("");
  const [courseTitle, setCourseTitle] = useState("");
  const [language, setLanguage] = useState("Python");
  const [category, setCategory] = useState("Backend");
  const [difficulty, setDifficulty] = useState("beginner");
  const [apiKey, setApiKey] = useState("");
  const [apiUrl, setApiUrl] = useState("https://shulker.in/api/colide_api_gateway-v1.0/");
  const [result, setResult] = useState<ImportContentResponse | null>(null);

  const mutation = useMutation({
    mutationFn: () =>
      importContent({
        source_text: sourceText,
        course_title: courseTitle || undefined,
        programming_language: language,
        technology: language,
        category,
        difficulty,
        provider: "custom",
        api_key: apiKey,
        api_url: apiUrl,
      }),
    onSuccess: (data) => {
      setResult(data);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setResult(null);
    mutation.mutate();
  };

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
            Paste source text (book, article, or notes) and let AI turn it into a structured course
          </p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-5">
        {/* Form */}
        <div className="lg:col-span-3">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Source text */}
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
                Paste your API key. It is sent only to process this request and is not stored on the server.
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
              disabled={mutation.isPending || !sourceText.trim() || !apiKey.trim()}
              className="w-full gap-2"
              size="lg"
            >
              {mutation.isPending ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin" />
                  Generating course... This may take a minute
                </>
              ) : (
                <>
                  <Sparkles className="h-5 w-5" />
                  Generate Course
                </>
              )}
            </Button>
          </form>
        </div>

        {/* Sidebar: Preview / Results */}
        <div className="lg:col-span-2">
          {/* Loading state */}
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
                AI is analyzing the source text and structuring it into modules and lessons...
              </p>
            </div>
          )}

          {/* Error state */}
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

          {/* Success state */}
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
                    <div className="flex items-center gap-2">
                      <span className="text-emerald-700 dark:text-emerald-300">
                        {result.modules_created} modules · {result.lessons_created} lessons
                      </span>
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

          {/* Empty state */}
          {!mutation.isPending && !mutation.isError && !result && (
            <div className="rounded-2xl border border-dashed border-border bg-card/50 p-8 text-center">
              <Sparkles className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold text-card-foreground">
                Ready to import
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Paste your source text and API key, then click &quot;Generate Course&quot;.
                The AI will analyze the content and create a structured course
                with modules, lessons, quizzes, and exercises.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
