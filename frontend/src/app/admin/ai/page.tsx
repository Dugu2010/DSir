"use client";

import { useState, useRef } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  Upload, Sparkles, FileText, BookOpen, CheckCircle2,
  AlertCircle, ArrowRight, Code2,
  Eye, FileType, Play, ChevronDown, ChevronRight,
  Loader2,
} from "lucide-react";
import toast from "react-hot-toast";

const API = process.env.NEXT_PUBLIC_API_URL || "";

type Step = "upload" | "previewing" | "preview" | "importing" | "done" | "error";

export default function AdminAIPage() {
  const { user } = useAuth();
  const fileRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [topic, setTopic] = useState("");
  const [step, setStep] = useState<Step>("upload");
  const [error, setError] = useState("");
  const [structure, setStructure] = useState<any>(null);
  const [summary, setSummary] = useState<any>(null);
  const [textPreview, setTextPreview] = useState("");
  const [textLen, setTextLen] = useState(0);
  const [importResult, setImportResult] = useState<any>(null);
  const [expandedMods, setExpandedMods] = useState<Set<number>>(new Set());

  const isAdmin = user?.role === "superadmin" || user?.role === "admin";
  if (!isAdmin) {
    return (
      <div className="max-w-xl mx-auto mt-20 text-center">
        <div className="h-16 w-16 rounded-2xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="h-8 w-8 text-red-500" />
        </div>
        <h2 className="text-xl font-bold text-ink">Admin Access Only</h2>
        <p className="text-ink-secondary mt-2">This page requires admin privileges.</p>
      </div>
    );
  }

  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : "";
  const headers = { Authorization: `Bearer ${token}` };

  const uploadAndPreview = async () => {
    if (!file) return;
    setStep("previewing");
    setError("");
    try {
      const fd = new FormData();
      fd.append("file", file);
      const qs = topic ? `?topic=${encodeURIComponent(topic)}` : "";
      const res = await fetch(`${API}/api/v1/admin/ai/preview${qs}`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` }, body: fd,
      });
      if (!res.ok) {
        const e = await res.json().catch(() => ({ detail: "Failed" }));
        throw new Error(e.detail || "Preview failed");
      }
      const data = await res.json();
      setStructure(data.structure);
      setSummary(data.summary);
      setTextPreview(data.text_preview || "");
      setTextLen(data.text_length || 0);
      setExpandedMods(new Set());
      setStep("preview");
      toast.success(`Extracted ${data.summary?.modules || 0} modules, ${data.summary?.lessons || 0} lessons`);
    } catch (e: any) {
      setError(e.message);
      setStep("error");
      toast.error(e.message);
    }
  };

  const importCourse = async () => {
    if (!structure) return;
    setStep("importing");
    setError("");
    try {
      const res = await fetch(`${API}/api/v1/admin/ai/import`, {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify(structure),
      });
      if (!res.ok) {
        const e = await res.json().catch(() => ({ detail: "Import failed" }));
        throw new Error(e.detail || "Import failed");
      }
      const data = await res.json();
      setImportResult(data);
      setStep("done");
      toast.success(`${data.lesson_count} lessons, ${data.exercise_count} exercises imported!`);
    } catch (e: any) {
      setError(e.message);
      setStep("error");
      toast.error(e.message);
    }
  };

  const reset = () => {
    setFile(null); setTopic(""); setStep("upload"); setError("");
    setStructure(null); setSummary(null); setImportResult(null);
    setTextPreview(""); setTextLen(0);
  };

  const toggleModule = (idx: number) => {
    const next = new Set(expandedMods);
    next.has(idx) ? next.delete(idx) : next.add(idx);
    setExpandedMods(next);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) { setFile(f); setStep("upload"); setError(""); }
  };

  // ── UPLOAD ──
  if (step === "upload" || step === "previewing") {
    return (
      <div className="max-w-3xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-ink flex items-center gap-3">
            <Sparkles className="h-6 w-6 text-brand-600" />
            AI Course Generator
          </h1>
          <p className="text-ink-secondary mt-1">
            Upload any handbook, textbook, or notes — AI extracts and structures it into a course.
          </p>
        </div>

        <Card padding="lg">
          <div
            onDragOver={e => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileRef.current?.click()}
            className="border-2 border-dashed border-[#e8ecf1] dark:border-white/10 rounded-2xl p-10 text-center cursor-pointer hover:border-brand-300 dark:hover:border-brand-500/30 transition-colors"
          >
            <input ref={fileRef} type="file" accept=".pdf,.png,.jpg,.jpeg,.webp,.txt,.md,.py" onChange={e => { const f = e.target.files?.[0]; if (f) { setFile(f); setStep("upload"); setError(""); } }} className="hidden" />
            {file ? (
              <div className="space-y-2">
                <div className="h-14 w-14 rounded-2xl bg-brand-50 dark:bg-brand-500/10 flex items-center justify-center mx-auto">
                  <FileText className="h-7 w-7 text-brand-600" />
                </div>
                <p className="font-semibold text-ink text-lg">{file.name}</p>
                <p className="text-sm text-ink-tertiary">{(file.size / 1024).toFixed(0)} KB</p>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="h-14 w-14 rounded-2xl bg-[#f1f3f5] dark:bg-white/5 flex items-center justify-center mx-auto">
                  <Upload className="h-7 w-7 text-ink-tertiary" />
                </div>
                <p className="font-semibold text-ink">Drop your file here</p>
                <p className="text-sm text-ink-tertiary">PDF · Image · Text · Code — even handwritten notes</p>
              </div>
            )}
          </div>

          {file && (
            <div className="mt-4 space-y-3">
              <input
                type="text" value={topic}
                onChange={e => setTopic(e.target.value)}
                placeholder="What's this about? (e.g. Python Programming)"
                className="w-full h-10 px-4 rounded-xl border border-[#e8ecf1] dark:border-white/10 bg-white dark:bg-[#0d0d13] text-sm text-ink placeholder:text-ink-tertiary focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
              <Button
                onClick={uploadAndPreview}
                disabled={step === "previewing"}
                size="lg" className="w-full"
                leftIcon={step === "previewing" ? <Loader2 className="h-5 w-5 animate-spin" /> : <Sparkles className="h-5 w-5" />}
              >
                {step === "previewing" ? "AI is analyzing..." : "Analyze with AI"}
              </Button>
            </div>
          )}
        </Card>
      </div>
    );
  }

  // ── ERROR ──
  if (step === "error") {
    return (
      <div className="max-w-2xl mx-auto">
        <Card padding="lg" className="text-center space-y-4">
          <div className="h-14 w-14 rounded-2xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center mx-auto">
            <AlertCircle className="h-7 w-7 text-red-500" />
          </div>
          <p className="font-semibold text-red-600 dark:text-red-400">{error}</p>
          <Button variant="outline" onClick={reset}>Try Again</Button>
        </Card>
      </div>
    );
  }

  // ── PREVIEW ──
  if (step === "preview") {
    const mods = structure?.modules || [];
    const course = structure?.course || {};

    return (
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-ink flex items-center gap-3">
              <Sparkles className="h-6 w-6 text-brand-600" />
              Course Preview
            </h1>
            <p className="text-ink-secondary mt-1">Review the structure before importing</p>
          </div>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={reset}>Cancel</Button>
            <Button onClick={importCourse} leftIcon={<CheckCircle2 className="h-4 w-4" />}>
              Approve & Import
            </Button>
          </div>
        </div>

        {/* Course header */}
        <Card padding="lg">
          <h2 className="text-xl font-bold text-ink">{course.title}</h2>
          <div className="flex flex-wrap gap-2 mt-3">
            <Badge variant="outline">{course.difficulty}</Badge>
            <Badge variant="outline">{summary?.modules} modules</Badge>
            <Badge variant="outline">{summary?.lessons} lessons</Badge>
          </div>
          <p className="text-sm text-ink-secondary mt-3">{course.description}</p>
          {course.skill_tags?.length > 0 && (
            <div className="flex gap-1.5 mt-2">
              {course.skill_tags.map((t: string) => <Badge key={t} size="sm">{t}</Badge>)}
            </div>
          )}
        </Card>

        {/* Module/lesson tree */}
        <div className="space-y-2">
          {mods.map((mod: any, mi: number) => (
            <Card key={mi} padding="none" className="overflow-hidden">
              <button
                onClick={() => toggleModule(mi)}
                className="w-full flex items-center gap-3 px-5 py-4 text-left hover:bg-[#f8fafc] dark:hover:bg-white/[0.03] transition-colors"
              >
                <span className="h-7 w-7 rounded-lg bg-brand-100 dark:bg-brand-500/10 flex items-center justify-center text-xs font-bold text-brand-600 dark:text-brand-400 flex-shrink-0">
                  {String(mi + 1).padStart(2, "0")}
                </span>
                <span className="font-semibold text-ink text-sm flex-1">{mod.title}</span>
                <Badge size="sm" variant="outline">{mod.lessons?.length || 0} lessons</Badge>
                {expandedMods.has(mi) ? <ChevronDown className="h-4 w-4 text-ink-tertiary" /> : <ChevronRight className="h-4 w-4 text-ink-tertiary" />}
              </button>
              {expandedMods.has(mi) && (
                <div className="border-t border-[#e8ecf1] dark:border-white/5 px-5 py-2 space-y-1 bg-[#fafbfc] dark:bg-white/[0.02]">
                  {mod.lessons?.map((l: any, li: number) => (
                    <div key={li} className="flex items-center gap-3 px-2 py-2 rounded-lg text-sm">
                      <Play className="h-3 w-3 text-ink-tertiary flex-shrink-0" />
                      <span className="text-ink-secondary flex-1">{l.title}</span>
                      <span className="text-xs text-ink-tertiary">{l.difficulty}</span>
                    </div>
                  ))}
                </div>
              )}
            </Card>
          ))}
        </div>

        {/* Text preview */}
        {textPreview && (
          <details className="group">
            <summary className="flex items-center gap-2 px-4 py-2 text-xs text-ink-tertiary cursor-pointer hover:text-ink-secondary">
              <Eye className="h-3 w-3" /> Extracted text ({textLen.toLocaleString()} chars)
            </summary>
            <Card padding="md" className="mt-2">
              <pre className="text-xs text-ink-secondary whitespace-pre-wrap font-mono max-h-48 overflow-y-auto">{textPreview}</pre>
            </Card>
          </details>
        )}
      </div>
    );
  }

  // ── IMPORTING ──
  if (step === "importing") {
    return (
      <div className="max-w-xl mx-auto">
        <Card padding="lg" className="text-center space-y-4">
          <div className="h-16 w-16 rounded-2xl bg-brand-50 dark:bg-brand-500/10 flex items-center justify-center mx-auto">
            <Loader2 className="h-8 w-8 text-brand-600 animate-spin" />
          </div>
          <p className="font-semibold text-ink text-lg">Importing course...</p>
          <p className="text-ink-secondary text-sm">Generating lesson content with AI — this may take a minute</p>
        </Card>
      </div>
    );
  }

  // ── DONE ──
  if (step === "done" && importResult) {
    return (
      <div className="max-w-xl mx-auto">
        <Card padding="lg" className="text-center space-y-6">
          <div className="h-16 w-16 rounded-2xl bg-emerald-100 dark:bg-emerald-500/10 flex items-center justify-center mx-auto">
            <CheckCircle2 className="h-8 w-8 text-emerald-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-ink">Course Imported!</h2>
            <div className="flex justify-center gap-3 mt-3">
              <Badge variant="outline">{importResult.module_count} modules</Badge>
              <Badge variant="outline">{importResult.lesson_count} lessons</Badge>
              <Badge variant="outline">{importResult.exercise_count} exercises</Badge>
            </div>
          </div>
          <div className="flex justify-center gap-3">
            <Link href={`/courses/${importResult.course_slug}`}>
              <Button leftIcon={<BookOpen className="h-4 w-4" />}>View Course</Button>
            </Link>
            <Button variant="outline" onClick={reset}>Create Another</Button>
          </div>
        </Card>
      </div>
    );
  }

  return null;
}
