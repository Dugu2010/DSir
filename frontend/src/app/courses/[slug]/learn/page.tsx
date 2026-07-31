"use client";

import { useQuery, useMutation } from "@tanstack/react-query";
import { useParams, useRouter } from "next/navigation";
import { useState, useCallback, useEffect } from "react";
import { courses as coursesApi, learning, users } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PageLoader } from "@/components/ui/States";
import { formatDuration, difficultyColor } from "@/lib/utils";
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

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeLesson, setActiveLesson] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

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

  if (structLoading) return <PageLoader />;

  return (
    <div className="flex h-[calc(100vh-8rem)] -m-4 lg:-m-8">
      {/* Sidebar - Curriculum */}
      <div className={`${sidebarOpen ? "w-80" : "w-0"} transition-all duration-200 border-r border-border bg-surface overflow-hidden flex-shrink-0`}>
        <div className="w-80 h-full flex flex-col">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <h2 className="font-semibold text-ink text-sm">Course Content</h2>
            <button
              onClick={() => setSidebarOpen(false)}
              className="p-1 rounded-lg hover:bg-surface-secondary"
            >
              <X className="h-4 w-4 text-ink-tertiary" />
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-1">
            {courseStructure?.map((mod: { id: string; slug: string; title: string; lessons: Array<{ slug: string; title: string; duration: number; is_free_preview: boolean }> }, modIdx: number) => (
              <div key={mod.id}>
                <div className="flex items-center gap-2 px-3 py-2 text-xs font-medium text-ink-tertiary uppercase tracking-wider">
                  <span className="h-5 w-5 rounded bg-surface-secondary flex items-center justify-center text-2xs">
                    {String(modIdx + 1).padStart(2, "0")}
                  </span>
                  {mod.title}
                </div>
                {mod.lessons?.map((l: { slug: string; title: string; duration: number; is_free_preview: boolean }) => (
                  <button
                    key={l.slug}
                    onClick={() => setActiveLesson(l.slug)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-left transition-all ${
                      activeLesson === l.slug
                        ? "bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-400 font-medium"
                        : "text-ink-secondary hover:bg-surface-secondary hover:text-ink"
                    }`}
                  >
                    <div className={`h-6 w-6 rounded-full flex-shrink-0 flex items-center justify-center text-xs ${
                      activeLesson === l.slug
                        ? "bg-brand-600 text-white"
                        : "bg-surface-secondary text-ink-tertiary"
                    }`}>
                      {activeLesson === l.slug ? <Play className="h-3 w-3 fill-current" /> : l.slug[0]?.toUpperCase()}
                    </div>
                    <span className="flex-1 truncate">{l.title}</span>
                    {l.is_free_preview && (
                      <Badge size="sm" variant="success" className="flex-shrink-0">Free</Badge>
                    )}
                  </button>
                ))}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Lesson top bar */}
        <div className="flex items-center gap-3 px-6 py-3 border-b border-border bg-surface">
          {!sidebarOpen && (
            <button
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 rounded-lg hover:bg-surface-secondary"
            >
              <List className="h-5 w-5 text-ink-secondary" />
            </button>
          )}
          <div className="flex-1" />
          <Button
            variant="outline"
            size="sm"
            leftIcon={<BookMarked className="h-4 w-4" />}
            onClick={() => users.createBookmark({ lesson_id: lesson?.id })}
          >
            Bookmark
          </Button>
          <Button
            variant="outline"
            size="sm"
            leftIcon={<PenLine className="h-4 w-4" />}
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
                <h1 className="text-3xl font-bold text-ink">{lesson.title}</h1>
                {lesson.description && (
                  <p className="mt-2 text-ink-secondary">{lesson.description}</p>
                )}
              </div>

              {/* Content */}
              <div
                className="prose-lesson"
                dangerouslySetInnerHTML={{ __html: renderMarkdown(lesson.content) }}
              />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <BookOpen className="h-12 w-12 text-ink-tertiary mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-ink">Select a lesson</h3>
                <p className="text-sm text-ink-secondary mt-1">Choose a lesson from the sidebar to start learning.</p>
              </div>
            </div>
          )}
        </div>

        {/* Bottom navigation */}
        {lesson && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-surface">
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
    </div>
  );
}

// Simple markdown renderer
function renderMarkdown(md: string): string {
  let html = md;

  // Code blocks
  html = html.replace(/```(\w+)?\n([\s\S]*?)```/g, (_match, lang, code) => {
    const escaped = code
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;");
    return `<pre><code class="language-${lang || ''}">${escaped}</code></pre>`;
  });

  // Inline code
  html = html.replace(/`([^`]+)`/g, "<code>$1</code>");

  // Headers
  html = html.replace(/^#### (.+)$/gm, "<h4>$1</h4>");
  html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");

  // Bold and italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>");
  html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");

  // Blockquotes
  html = html.replace(/^> (.+)$/gm, "<blockquote>$1</blockquote>");

  // Horizontal rules
  html = html.replace(/^---$/gm, "<hr>");

  // Unordered lists
  html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
  html = html.replace(/(<li>.*<\/li>\n?)+/g, "<ul>$&</ul>");

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");

  // Paragraphs
  html = html.replace(/^(?!<[a-z]).+(?!<\/[a-z]>)$/gm, "<p>$&</p>");

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>');

  return html;
}
