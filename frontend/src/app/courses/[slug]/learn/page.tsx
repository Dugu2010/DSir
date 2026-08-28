"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useState, useCallback, useEffect, useRef } from "react";
import { courses as coursesApi, learning, users } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader } from "@/components/ui/States";
import { CodeBlock } from "@/components/ui/CodeBlock";
import Sandbox from "@/components/Sandbox";
import { formatDuration, difficultyColor, extractStarterCode } from "@/lib/utils";
import type { Lesson } from "@/lib/types";
import {
  ChevronLeft, ChevronRight, CheckCircle2, Clock, BookOpen,
  BookMarked, MessageSquare, MessageCircle, PenLine, Play,
  List, X, Copy, Check, Code2, Lightbulb, ThumbsUp,
} from "lucide-react";
import toast from "react-hot-toast";

export default function LearnPage() {
  const { slug } = useParams<{ slug: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [drawer, setDrawer] = useState<"closed" | "mobile" | "desktop">("closed");
  const [activeLesson, setActiveLesson] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [notesOpen, setNotesOpen] = useState(false);
  const [noteText, setNoteText] = useState("");
  const sandboxRef = useRef<HTMLDivElement>(null);

  const { data: courseStructure, isLoading: structLoading } = useQuery({
    queryKey: ["course-lessons", slug],
    queryFn: () => coursesApi.getLessons(slug),
  });

  // Auto-select first lesson
  useEffect(() => {
    if (courseStructure && courseStructure.length > 0 && !activeLesson) {
      const firstModule = courseStructure[0];
      if (firstModule.lessons && firstModule.lessons.length > 0) {
        setActiveLesson(firstModule.lessons[0].slug);
      }
    }
  }, [courseStructure, activeLesson]);

  // Open the curriculum sidebar by default on desktop
  useEffect(() => {
    if (window.matchMedia("(min-width: 1024px)").matches) {
      setDrawer("desktop");
    }
  }, []);

  const toggleDrawer = useCallback(() => {
    setDrawer((current) => {
      if (current !== "closed") return "closed";
      return window.matchMedia("(min-width: 1024px)").matches ? "desktop" : "mobile";
    });
  }, []);

  const scrollToSandbox = useCallback(() => {
    sandboxRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, []);

  // Find current lesson info
  let currentModuleSlug = "";
  if (activeLesson && courseStructure) {
    for (const mod of courseStructure) {
      const found = mod.lessons?.find((l: { slug: string }) => l.slug === activeLesson);
      if (found) {
        currentModuleSlug = mod.slug;
        break;
      }
    }
  }

  const { data: lesson, isLoading: lessonLoading } = useQuery({
    queryKey: ["lesson", slug, currentModuleSlug, activeLesson],
    queryFn: () => learning.getLesson(slug, currentModuleSlug, activeLesson!),
    enabled: !!activeLesson && !!currentModuleSlug,
  });

  const { data: progressData } = useQuery({
    queryKey: ["lesson-progress", slug, currentModuleSlug, activeLesson],
    queryFn: () => learning.getProgress(slug, currentModuleSlug, activeLesson!),
    enabled: !!activeLesson && !!currentModuleSlug,
  });

  const progressMutation = useMutation({
    mutationFn: (data: { is_completed: boolean }) =>
      learning.updateProgress(slug, currentModuleSlug, activeLesson!, data),
  });

  const { data: notes } = useQuery({
    queryKey: ["lesson-notes", lesson?.id],
    queryFn: () => users.getNotes(lesson!.id),
    enabled: !!lesson?.id && notesOpen,
  });

  const noteMutation = useMutation({
    mutationFn: (content: string) => users.createNote({ lesson_id: lesson!.id, content }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["lesson-notes", lesson?.id] });
      setNoteText("");
      toast.success("Note saved");
    },
    onError: () => toast.error("Failed to save note"),
  });

  // Find prev/next lesson
  const getLessonNav = () => {
    if (!courseStructure || !activeLesson) return { prev: null, next: null };
    let allLessons: Array<{ slug: string; moduleSlug: string; moduleIdx: number }> = [];
    courseStructure.forEach((mod: { slug: string; lessons: Array<{ slug: string }> }, midx: number) => {
      mod.lessons?.forEach((l: { slug: string }) => {
        allLessons.push({ slug: l.slug, moduleSlug: mod.slug, moduleIdx: midx });
      });
    });
    const idx = allLessons.findIndex((l) => l.slug === activeLesson);
    return {
      prev: idx > 0 ? allLessons[idx - 1] : null,
      next: idx < allLessons.length - 1 ? allLessons[idx + 1] : null,
    };
  };

  const nav = getLessonNav();

  const markComplete = () => {
    progressMutation.mutate({ is_completed: true });
    toast.success("Lesson completed! 🎉");
  };

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Prefill the sandbox with the lesson's first runnable code example
  const starter = lesson ? extractStarterCode(lesson.content) : null;

  if (structLoading) return <PageLoader />;

  return (
    <div className="flex h-[calc(100vh-8rem)] -m-4 lg:-m-8">
      {/* Sidebar - Curriculum (drawer on mobile, inline on desktop) */}
      {(drawer === "desktop" || drawer === "mobile") && (
        <>
          {drawer === "mobile" && (
            <div
              className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
              onClick={() => setDrawer("closed")}
              aria-hidden="true"
            />
          )}
          <div
            className={`${
              drawer === "mobile"
                ? "fixed inset-y-0 left-0 w-80 shadow-2xl z-50"
                : "hidden lg:flex w-80 flex-shrink-0 h-full"
            } flex-col border-r border-border dark:border-white/10 bg-surface`}
            role="complementary"
            aria-label="Course curriculum"
          >
            <div className="flex items-center justify-between p-4 border-b border-border dark:border-white/10">
              <div>
                <p className="eyebrow mb-0.5">Curriculum</p>
                <h2 className="font-display font-semibold text-ink dark:text-ink text-sm">Course Content</h2>
              </div>
              <button
                onClick={() => setDrawer("closed")}
                className="p-1 rounded-lg hover:bg-surface-secondary dark:hover:bg-white/5 text-ink-tertiary"
                aria-label="Close course content sidebar"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {courseStructure?.map((mod: { id: string; slug: string; title: string; lessons: Array<{ slug: string; title: string; is_free_preview: boolean }> }, modIdx: number) => (
              <div key={mod.id}>
                <div className="flex items-center gap-2 px-3 py-2 text-xs font-mono uppercase tracking-eyebrow text-ink-tertiary">
                  <span className="h-5 w-5 rounded bg-surface-tertiary dark:bg-white/10 flex items-center justify-center text-coral-600 dark:text-coral-400">
                    {String(modIdx + 1).padStart(2, "0")}
                  </span>
                  {mod.title}
                </div>
                {mod.lessons?.map((l: { slug: string; title: string; is_free_preview: boolean }) => (
                  <button
                    key={l.slug}
                    onClick={() => {
                      setActiveLesson(l.slug);
                      if (drawer === "mobile") setDrawer("closed");
                    }}
                    aria-current={activeLesson === l.slug ? "page" : undefined}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-left transition-all ${
                      activeLesson === l.slug
                        ? "bg-coral-50 dark:bg-coral-500/10 text-coral-700 dark:text-coral-400 font-medium border border-coral-200 dark:border-coral-500/30"
                        : "text-ink-secondary hover:bg-surface-secondary dark:hover:bg-white/5 hover:text-ink dark:hover:text-ink"
                    }`}
                  >
                    <div className={`h-6 w-6 rounded-full flex-shrink-0 flex items-center justify-center text-xs ${
                      activeLesson === l.slug
                        ? "bg-coral-500 text-night-600"
                        : "bg-surface-tertiary dark:bg-white/10 text-ink-tertiary"
                    }`}>
                      {activeLesson === l.slug ? <Play className="h-3 w-3 fill-current" /> : l.slug[0]?.toUpperCase()}
                    </div>
                    <span className="flex-1 truncate">{l.title}</span>
                    {l.is_free_preview && (
                      <Badge size="sm" className="flex-shrink-0 bg-coral-500/10 text-coral-700 dark:text-coral-400 border border-coral-500/30">Free</Badge>
                    )}
                  </button>
                ))}
              </div>
            ))}
            </div>
          </div>
        </>
      )}

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Lesson top bar */}
        <div className="flex items-center gap-2 px-4 lg:px-6 py-3 border-b border-border dark:border-white/10 bg-surface">
          {drawer === "closed" && (
            <button
              onClick={toggleDrawer}
              className="p-1.5 rounded-lg hover:bg-surface-secondary dark:hover:bg-white/5 text-ink-secondary"
              aria-label="Open course content sidebar"
            >
              <List className="h-5 w-5" />
            </button>
          )}
          <div className="flex-1" />
          {lesson && (
            <button
              onClick={scrollToSandbox}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold bg-gradient-to-r from-coral-500 to-coral-400 text-night-600 hover:from-coral-400 hover:to-coral-300 transition-all shadow-md shadow-coral-500/30 ring-2 ring-coral-500/30 hover:ring-coral-400/50"
              title="Jump to the code playground"
            >
              <Play className="h-3.5 w-3.5 fill-current" /> Try it Out
            </button>
          )}
          <Button
            variant="outline"
            size="sm"
            leftIcon={<BookMarked className="h-4 w-4" />}
            onClick={() => {
              if (!lesson?.id) return;
              users.createBookmark({ lesson_id: lesson.id })
                .then(() => toast.success("Bookmark saved"))
                .catch(() => toast.error("Failed to save bookmark"));
            }}
          >
            Bookmark
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<PenLine className="h-4 w-4" />}
            onClick={() => setNotesOpen(true)}
          >
            Notes
          </Button>
        </div>

        {/* Lesson content */}
        <div className="flex-1 overflow-y-auto">
          {lessonLoading ? (
            <PageLoader />
          ) : lesson ? (
            <div className="max-w-3xl mx-auto px-6 py-8">
              {/* Header */}
              <div className="mb-8">
                <div className="flex items-center gap-3 mb-3">
                  <Badge size="sm" className={difficultyColor(lesson.difficulty)}>
                    {lesson.difficulty}
                  </Badge>
                  {lesson.estimated_duration_minutes && (
                    <span className="flex items-center gap-1 text-xs text-ink-tertiary">
                      <Clock className="h-3.5 w-3.5" /> {formatDuration(lesson.estimated_duration_minutes)}
                    </span>
                  )}
                  {lesson.skill_tags?.map((tag: string) => (
                    <Badge key={tag} size="sm" variant="outline">{tag}</Badge>
                  ))}
                </div>
                <h1 className="font-display text-3xl font-semibold tracking-tight text-ink">{lesson.title}</h1>
                {lesson.description && (
                  <p className="mt-2 text-ink-secondary">{lesson.description}</p>
                )}
              </div>

              {/* Learning Objectives */}
              {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
                <div className="mb-8 p-5 rounded-2xl bg-coral-50/60 dark:bg-coral-500/5 border border-coral-200 dark:border-coral-500/10">
                  <h3 className="text-sm font-semibold text-coral-700 dark:text-coral-400 mb-3 flex items-center gap-2 font-mono uppercase tracking-eyebrow">
                    <Lightbulb className="h-4 w-4" /> Learning Objectives
                  </h3>
                  <ul className="space-y-2 list-none pl-0">
                    {lesson.learning_objectives.map((obj: string, i: number) => (
                      <li key={i} className="flex items-start gap-2.5 text-sm text-ink-secondary">
                        <CheckCircle2 className="h-4 w-4 text-coral-500 flex-shrink-0 mt-0.5" />
                        {obj}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Content */}
              {renderContent(lesson.content)}

              {/* Try it Yourself */}
              <div ref={sandboxRef} className="mt-8 pt-8 border-t border-border dark:border-white/10">
                <div className="flex items-center gap-3 mb-4">
                  <div className="h-10 w-10 rounded-xl bg-coral-500/10 flex items-center justify-center">
                    <Play className="h-5 w-5 text-coral-600 dark:text-coral-400" />
                  </div>
                  <div>
                    <h2 className="font-display text-lg font-semibold text-ink">Try it Yourself</h2>
                    <p className="text-sm text-ink-secondary">
                      Experiment with code — runs entirely in your browser. No server needed.
                    </p>
                  </div>
                </div>
                <Sandbox
                  language={starter?.language ?? "python"}
                  initialCode={starter?.code ?? `# Experiment with what you just learned!
print("Hello, DSir!")`}
                  height="280px"
                />
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <BookOpen className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
                <h3 className="font-display text-lg font-semibold text-ink">Select a lesson</h3>
                <p className="text-sm text-ink-secondary mt-1">Choose a lesson from the sidebar to start learning.</p>
              </div>
            </div>
          )}
        </div>

        {/* Bottom navigation */}
        {lesson && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-border dark:border-white/10 bg-surface">
            <div>
              {nav.prev ? (
                <Button
                  variant="ghost"
                  size="sm"
                  leftIcon={<ChevronLeft className="h-4 w-4" />}
                  onClick={() => setActiveLesson(nav.prev!.slug)}
                >
                  Previous
                </Button>
              ) : (
                <div />
              )}
            </div>
            <Button
              variant={progressData?.is_completed ? "success" : "primary"}
              size="sm"
              leftIcon={progressData?.is_completed ? <CheckCircle2 className="h-4 w-4" /> : undefined}
              onClick={markComplete}
              loading={progressMutation.isPending}
              disabled={progressData?.is_completed}
            >
              {progressData?.is_completed ? "Completed" : "Mark Complete"}
            </Button>
            <div>
              {nav.next ? (
                <Button
                  variant="ghost"
                  size="sm"
                  rightIcon={<ChevronRight className="h-4 w-4" />}
                  onClick={() => setActiveLesson(nav.next!.slug)}
                >
                  Next
                </Button>
              ) : (
                <div />
              )}
            </div>
          </div>
        )}
      </div>

      {/* Notes modal */}
      {notesOpen && lesson && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={() => setNotesOpen(false)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-label="Lesson notes"
            className="bg-surface dark:bg-night-500 rounded-2xl p-6 max-w-lg w-full max-h-[80vh] flex flex-col shadow-xl border border-border dark:border-white/10"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-display text-lg font-semibold text-ink truncate">Notes — {lesson.title}</h3>
              <button
                onClick={() => setNotesOpen(false)}
                className="p-1.5 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-tertiary"
                aria-label="Close notes"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2 mb-4">
              {notes && notes.length > 0 ? (
                notes.map((n) => (
                  <div key={n.id} className="rounded-xl border border-border dark:border-white/10 bg-surface-secondary dark:bg-white/5 p-3">
                    <p className="text-sm text-ink whitespace-pre-wrap">{n.content}</p>
                    <p className="text-xs text-ink-tertiary mt-1.5">{new Date(n.created_at).toLocaleString()}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-ink-tertiary text-center py-6">No notes yet. Add your first note below.</p>
              )}
            </div>

            <div className="space-y-2">
              <textarea
                value={noteText}
                onChange={(e) => setNoteText(e.target.value)}
                placeholder="Write a note about this lesson..."
                rows={3}
                className="w-full p-3 rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-600 text-sm text-ink placeholder:text-ink-tertiary focus:outline-none focus:ring-2 focus:ring-coral-500 resize-none"
              />
              <Button
                onClick={() => noteMutation.mutate(noteText)}
                loading={noteMutation.isPending}
                disabled={!noteText.trim()}
              >
                Add Note
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Render lesson content: code fences become runnable CodeBlocks, the rest is
// rendered as escaped markdown.
function renderContent(content: string) {
  const parts = content.split(/(```[\s\S]*?```)/g);
  return parts.map((part, i) => {
    if (part.startsWith("```")) {
      const lines = part.split("\n");
      const lang = lines[0].replace("```", "").trim() || "python";
      const code = lines.slice(1, -1).join("\n");
      return <CodeBlock key={i} code={code} language={lang} className="my-6" />;
    }
    return (
      <div key={i} className="prose-lesson" dangerouslySetInnerHTML={{ __html: renderMarkdown(part) }} />
    );
  });
}

// Simple markdown renderer. Content is HTML-escaped first so lesson text can
// never inject markup; code fences are emitted as escaped <pre><code> blocks.
function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function inline(text: string): string {
  let out = escapeHtml(text);
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  out = out.replace(/\*(.+?)\*/g, "<em>$1</em>");
  out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/[^\s)]*)\)/g, '<a href="$2" rel="noopener noreferrer" target="_blank">$1</a>');
  return out;
}

function block(line: string): string {
  const trimmed = line.trimStart();
  if (trimmed.startsWith("#### ")) return `<h4>${inline(trimmed.slice(5))}</h4>`;
  if (trimmed.startsWith("### ")) return `<h3>${inline(trimmed.slice(4))}</h3>`;
  if (trimmed.startsWith("## ")) return `<h2>${inline(trimmed.slice(3))}</h2>`;
  if (trimmed.startsWith("# ")) return `<h1>${inline(trimmed.slice(2))}</h1>`;
  if (trimmed.startsWith("> ")) return `<blockquote>${inline(trimmed.slice(2))}</blockquote>`;
  if (trimmed === "---") return "<hr>";
  return `<p>${inline(trimmed)}</p>`;
}

function renderMarkdown(md: string): string {
  const out: string[] = [];
  const lines = md.split("\n");
  let i = 0;
  let listType: "ul" | "ol" | null = null;

  const closeList = () => {
    if (listType) { out.push(`</${listType}>`); listType = null; }
  };

  while (i < lines.length) {
    const raw = lines[i];
    const line = raw.trimEnd();

    // Code fences
    if (line.trim().startsWith("```")) {
      closeList();
      const lang = line.trim().replace(/```/g, "").trim();
      const code: string[] = [];
      i += 1;
      while (i < lines.length && !lines[i].trim().startsWith("```")) {
        code.push(lines[i]);
        i += 1;
      }
      i += 1; // skip closing fence
      out.push(`<pre><code${lang ? ` class="language-${escapeHtml(lang)}"` : ""}>${escapeHtml(code.join("\n"))}</code></pre>`);
      continue;
    }

    if (line.startsWith("- ")) {
      if (listType !== "ul") { closeList(); out.push("<ul>"); listType = "ul"; }
      out.push(`<li>${inline(line.slice(2))}</li>`);
    } else if (/^\d+\.\s+/.test(line)) {
      if (listType !== "ol") { closeList(); out.push("<ol>"); listType = "ol"; }
      out.push(`<li>${inline(line.replace(/^\d+\.\s+/, ""))}</li>`);
    } else if (line.trim() === "") {
      closeList();
    } else {
      closeList();
      out.push(block(line));
    }
    i += 1;
  }
  closeList();
  return out.join("\n");
}
