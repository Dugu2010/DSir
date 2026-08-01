"use client";

import { useState, useRef, useCallback } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import {
  Upload, Sparkles, FileText, BookOpen, CheckCircle2,
  Loader2, AlertCircle, ArrowRight, Code2, Zap,
  GraduationCap, List, X, Download, Play,
  Eye, FileType, Hash, Globe,
} from "lucide-react";
import toast from "react-hot-toast";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

export default function AdminAIPage() {
  const { user } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [topic, setTopic] = useState("");
  const [status, setStatus] = useState<"idle" | "uploading" | "extracting" | "structuring" | "ready" | "importing" | "done" | "error">("idle");
  const [statusMsg, setStatusMsg] = useState("");
  const [result, setResult] = useState<any>(null);
  const [importResult, setImportResult] = useState<any>(null);
  const [extractedText, setExtractedText] = useState("");

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

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0];
    if (f) {
      setFile(f);
      setStatus("idle");
      setResult(null);
      setImportResult(null);
      setExtractedText("");
    }
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) {
      setFile(f);
      setStatus("idle");
      setResult(null);
      setImportResult(null);
      setExtractedText("");
    }
  }, []);

  const processFile = async () => {
    if (!file) return;
    try {
      setStatus("uploading");
      setStatusMsg("Uploading file...");

      const formData = new FormData();
      formData.append("file", file);

      const token = localStorage.getItem("access_token");
      const params = topic ? `?topic=${encodeURIComponent(topic)}` : "";

      setStatus("extracting");
      setStatusMsg("Extracting text with AI...");

      const res = await fetch(`${API_BASE}/api/v1/admin/ai/extract${params}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Failed" }));
        throw new Error(err.detail || "Processing failed");
      }

      setStatus("structuring");
      setStatusMsg("AI is analyzing and structuring content...");

      const data = await res.json();
      setResult(data.course_data);
      setExtractedText(data.extracted_preview || "");
      setStatus("ready");
      setStatusMsg("Content structured successfully!");
      toast.success("AI analysis complete!");
    } catch (err: any) {
      setStatus("error");
      setStatusMsg(err.message || "Something went wrong");
      toast.error(err.message || "Processing failed");
    }
  };

  const importCourse = async () => {
    if (!result) return;
    try {
      setStatus("importing");
      setStatusMsg("Importing into database...");

      const token = localStorage.getItem("access_token");
      const res = await fetch(`${API_BASE}/api/v1/admin/ai/import`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ course_data: result }),
      });

      if (!res.ok) throw new Error("Import failed");

      const data = await res.json();
      setImportResult(data);
      setStatus("done");
      setStatusMsg("Course imported successfully!");
      toast.success(`Created: ${data.lesson_count} lessons, ${data.exercise_count} exercises`);
    } catch (err: any) {
      setStatus("error");
      setStatusMsg(err.message || "Import failed");
      toast.error("Import failed");
    }
  };

  const resetAll = () => {
    setFile(null);
    setTopic("");
    setStatus("idle");
    setStatusMsg("");
    setResult(null);
    setImportResult(null);
    setExtractedText("");
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-ink flex items-center gap-3">
          <Sparkles className="h-6 w-6 text-brand-600" />
          AI Course Generator
        </h1>
        <p className="text-ink-secondary mt-1">
          Upload a handbook, textbook, or notes — AI extracts and structures everything into a complete course.
        </p>
      </div>

      {/* Upload Area */}
      {status !== "ready" && status !== "importing" && status !== "done" && (
        <Card padding="lg">
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className="border-2 border-dashed border-[#e8ecf1] dark:border-white/10 rounded-2xl p-10 text-center cursor-pointer hover:border-brand-300 dark:hover:border-brand-500/30 transition-colors"
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.png,.jpg,.jpeg,.webp,.txt,.md,.py,.json,.csv,.docx"
              onChange={handleFileChange}
              className="hidden"
            />
            {file ? (
              <div className="space-y-2">
                <div className="h-14 w-14 rounded-2xl bg-brand-50 dark:bg-brand-500/10 flex items-center justify-center mx-auto">
                  <FileText className="h-7 w-7 text-brand-600 dark:text-brand-400" />
                </div>
                <p className="font-semibold text-ink text-lg">{file.name}</p>
                <p className="text-sm text-ink-tertiary">{(file.size / 1024).toFixed(1)} KB</p>
                <Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); setFile(null); }}>
                  <X className="h-4 w-4 mr-1" /> Change file
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="h-14 w-14 rounded-2xl bg-[#f1f3f5] dark:bg-white/5 flex items-center justify-center mx-auto">
                  <Upload className="h-7 w-7 text-ink-tertiary" />
                </div>
                <p className="font-semibold text-ink">Drop your handbook here</p>
                <p className="text-sm text-ink-tertiary">PDF, image, text — even handwritten notes</p>
                <Badge variant="outline" size="sm">PDF • PNG • JPG • TXT • MD • DOCX</Badge>
              </div>
            )}
          </div>

          {/* Topic hint */}
          {file && (
            <div className="mt-4">
              <input
                type="text"
                placeholder="Optional: what's this about? (e.g. 'Python Programming')"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full h-10 px-4 rounded-xl border border-[#e8ecf1] dark:border-white/10 bg-white dark:bg-[#0d0d13] text-sm text-ink placeholder:text-ink-tertiary focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
          )}

          {/* Process button */}
          {file && status !== "extracting" && status !== "structuring" && (
            <Button
              onClick={processFile}
              size="lg"
              className="w-full mt-4"
              leftIcon={<Sparkles className="h-5 w-5" />}
            >
              Analyze with AI
            </Button>
          )}
        </Card>
      )}

      {/* Processing State */}
      {(status === "extracting" || status === "structuring" || status === "importing") && (
        <Card padding="lg" className="text-center space-y-4">
          <div className="h-16 w-16 rounded-2xl bg-brand-50 dark:bg-brand-500/10 flex items-center justify-center mx-auto">
            {status === "importing" ? (
              <Download className="h-8 w-8 text-brand-600 animate-bounce" />
            ) : (
              <Sparkles className="h-8 w-8 text-brand-600 animate-pulse" />
            )}
          </div>
          <div>
            <p className="font-semibold text-ink text-lg">
              {status === "extracting" && "Extracting text..."}
              {status === "structuring" && "AI is structuring content..."}
              {status === "importing" && "Importing into database..."}
            </p>
            <p className="text-ink-secondary text-sm mt-1">{statusMsg}</p>
          </div>
          <div className="flex justify-center">
            <div className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="h-2 w-2 rounded-full bg-brand-500 animate-bounce"
                  style={{ animationDelay: `${i * 150}ms` }}
                />
              ))}
            </div>
          </div>
        </Card>
      )}

      {/* Error */}
      {status === "error" && (
        <Card padding="lg">
          <div className="text-center space-y-4">
            <div className="h-14 w-14 rounded-2xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center mx-auto">
              <AlertCircle className="h-7 w-7 text-red-500" />
            </div>
            <p className="font-semibold text-red-600 dark:text-red-400">{statusMsg}</p>
            <Button variant="outline" onClick={resetAll}>Try Again</Button>
          </div>
        </Card>
      )}

      {/* Ready - Preview */}
      {status === "ready" && result && (
        <div className="space-y-4">
          <Card padding="lg">
            <div className="flex items-start justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-ink flex items-center gap-2">
                  <CheckCircle2 className="h-5 w-5 text-emerald-500" /> Ready to Import
                </h2>
                <p className="text-ink-secondary mt-1">Review the course structure below, then import it.</p>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" onClick={resetAll}>Cancel</Button>
                <Button size="md" onClick={importCourse} leftIcon={<Download className="h-4 w-4" />}>
                  Import Course
                </Button>
              </div>
            </div>

            {/* Course Info */}
            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-bold text-ink">{result.course?.title}</h3>
                <div className="flex flex-wrap gap-2 mt-2">
                  <Badge variant="outline">{result.course?.difficulty}</Badge>
                  <Badge variant="outline">{result.course?.estimated_duration_minutes} min</Badge>
                  <Badge variant="outline">{result.modules?.length || 0} modules</Badge>
                </div>
                <p className="text-sm text-ink-secondary mt-2">{result.course?.description}</p>
              </div>

              {/* Modules & Lessons */}
              <div className="space-y-2">
                {result.modules?.map((mod: any, mi: number) => (
                  <details key={mi} className="group">
                    <summary className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#f8fafc] dark:bg-white/[0.03] border border-[#e8ecf1] dark:border-white/5 cursor-pointer hover:border-brand-200 dark:hover:border-brand-500/20 transition-colors">
                      <span className="h-6 w-6 rounded-md bg-brand-100 dark:bg-brand-500/10 flex items-center justify-center text-xs font-bold text-brand-600 dark:text-brand-400">
                        {String(mi + 1).padStart(2, "0")}
                      </span>
                      <span className="font-medium text-ink text-sm flex-1">{mod.title}</span>
                      <Badge size="sm" variant="outline">{mod.lessons?.length || 0} lessons</Badge>
                    </summary>
                    <div className="ml-9 mt-1 space-y-1 pb-2">
                      {mod.lessons?.map((l: any, li: number) => (
                        <div key={li} className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm">
                          <Play className="h-3 w-3 text-ink-tertiary flex-shrink-0" />
                          <span className="text-ink-secondary flex-1">{l.title}</span>
                          <span className="text-xs text-ink-tertiary">{l.difficulty}</span>
                          <span className="text-xs text-ink-tertiary">{l.exercises?.length || 0} ex</span>
                        </div>
                      ))}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Done */}
      {status === "done" && importResult && (
        <Card padding="lg" className="text-center space-y-6">
          <div className="h-16 w-16 rounded-2xl bg-emerald-100 dark:bg-emerald-500/10 flex items-center justify-center mx-auto">
            <CheckCircle2 className="h-8 w-8 text-emerald-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-ink">Course Imported!</h2>
            <p className="text-ink-secondary mt-2">
              {importResult.lesson_count} lessons across {importResult.module_count} modules with {importResult.exercise_count} exercises
            </p>
          </div>
          <div className="flex justify-center gap-3">
            <Link href={`/courses/${importResult.course_slug}`}>
              <Button leftIcon={<BookOpen className="h-4 w-4" />}>View Course</Button>
            </Link>
            <Button variant="outline" onClick={resetAll}>
              Create Another
            </Button>
          </div>
        </Card>
      )}

      {/* Extracted Text Preview (collapsed) */}
      {extractedText && status === "ready" && (
        <details className="group">
          <summary className="flex items-center gap-2 px-4 py-2 text-xs text-ink-tertiary cursor-pointer hover:text-ink-secondary">
            <Eye className="h-3 w-3" /> View extracted text
          </summary>
          <Card padding="md" className="mt-2">
            <pre className="text-xs text-ink-secondary whitespace-pre-wrap font-mono max-h-48 overflow-y-auto">
              {extractedText}
            </pre>
          </Card>
        </details>
      )}
    </div>
  );
}
