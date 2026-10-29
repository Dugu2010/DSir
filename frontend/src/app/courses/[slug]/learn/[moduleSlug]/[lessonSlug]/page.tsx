'use client';

import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useRef, useCallback } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { Badge, Button } from '@/components/ui';
import { PageLoader } from '@/components/ui/States';
import { CodeBlock } from '@/components/ui/CodeBlock';
import Sandbox from '@/components/Sandbox';
import {
  Clock, ChevronLeft, ChevronRight, CheckCircle,
  Circle, Play, X, List, ArrowUp,
  Lightbulb,
} from 'lucide-react';
import { cn, extractStarterCode } from '@/lib/utils';
import toast from 'react-hot-toast';

interface LessonNav {
  module: any; lesson: any;
}

type DrawerState = 'closed' | 'mobile' | 'desktop';

export default function LessonPage() {
  const params = useParams<{ slug: string; moduleSlug: string; lessonSlug: string }>();
  const { slug, moduleSlug, lessonSlug } = params;
  const router = useRouter();
  const queryClient = useQueryClient();
  const { isAuthenticated } = useAuth();
  const contentRef = useRef<HTMLDivElement>(null);
  const sandboxRef = useRef<HTMLDivElement>(null);

  const [drawer, setDrawer] = useState<DrawerState>('closed');
  const [showBackToTop, setShowBackToTop] = useState(false);

  const scrollToSandbox = useCallback(() => {
    sandboxRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, []);

  // Scroll to top watcher
  useEffect(() => {
    const el = contentRef.current;
    if (!el) return;
    const handler = () => setShowBackToTop(el.scrollTop > 500);
    el.addEventListener('scroll', handler, { passive: true });
    return () => el.removeEventListener('scroll', handler);
  }, []);

  // Scroll to top on lesson change
  useEffect(() => {
    contentRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  }, [lessonSlug]);

  const { data: lesson, isLoading, error } = useQuery({
    queryKey: ['lesson', slug, moduleSlug, lessonSlug],
    queryFn: () => api.get<any>(`/learn/${slug}/${moduleSlug}/${lessonSlug}`),
    enabled: !!slug && !!moduleSlug && !!lessonSlug,
    retry: 1,
  });

  const { data: structure } = useQuery({
    queryKey: ['course-structure', slug],
    queryFn: () => api.get<any[]>(`/courses/${slug}/modules`),
    enabled: !!slug,
    retry: 1,
  });

  const { data: progress } = useQuery({
    queryKey: ['lesson-progress', slug, moduleSlug, lessonSlug],
    queryFn: () => api.get<any>(`/learn/${slug}/${moduleSlug}/${lessonSlug}/progress`),
    enabled: !!slug && !!moduleSlug && !!lessonSlug && isAuthenticated,
  });

  // Find prev/next lesson
  let prevLesson: LessonNav | null = null, nextLesson: LessonNav | null = null;
  let currentModuleTitle = '';
  let currentModuleIndex = 0;
  if (structure && moduleSlug && lessonSlug) {
    const allLessons: LessonNav[] = [];
    structure.forEach((m: any, mIdx: number) => {
      m.lessons?.forEach((l: any) => allLessons.push({ module: m, lesson: l }));
      if (m.slug === moduleSlug) {
        currentModuleTitle = m.title;
        currentModuleIndex = mIdx;
      }
    });
    const idx = allLessons.findIndex((l) => l.lesson.slug === lessonSlug && l.module.slug === moduleSlug);
    if (idx > 0) prevLesson = allLessons[idx - 1];
    if (idx < allLessons.length - 1) nextLesson = allLessons[idx + 1];
  }

  const toggleDrawer = useCallback(() => {
    setDrawer((current) => {
      if (current !== 'closed') return 'closed';
      const isDesktop = window.matchMedia('(min-width: 1024px)').matches;
      return isDesktop ? 'desktop' : 'mobile';
    });
  }, []);

  const markComplete = useCallback(async () => {
    try {
      await api.put(`/learn/${slug}/${moduleSlug}/${lessonSlug}/progress`, {
        is_completed: true,
        completion_percentage: 100,
      });
      queryClient.invalidateQueries({ queryKey: ['lesson-progress'] });
      toast.success('Lesson completed!');
    } catch {
      toast.error('Failed to mark as complete');
    }
  }, [slug, moduleSlug, lessonSlug, queryClient]);

  // Loading state
  if (isLoading || !lesson) {
    if (error) {
      return (
        <div className="flex items-center justify-center min-h-[70vh]">
          <div className="text-center max-w-sm">
            <p className="font-display text-lg font-semibold text-ink mb-2">Couldn&apos;t load this lesson</p>
            <p className="text-sm text-ink-secondary mb-6">Check your connection and try again.</p>
            <Button variant="outline" size="sm" onClick={() => router.refresh()} leftIcon={<ArrowUp className="h-3.5 w-3.5 rotate-90" />}>
              Reload
            </Button>
          </div>
        </div>
      );
    }
    return <PageLoader label="Loading lesson..." />;
  }

  // Prefill the sandbox with the lesson's first runnable code example
  const starter = extractStarterCode(lesson.content);

  // Editorial headline accent: italicise the final word of the title.
  const titleWords = lesson.title.trim().split(/\s+/);
  const titleLast = titleWords.length > 1 ? titleWords[titleWords.length - 1] : '';
  const titleHead = titleWords.length > 1 ? titleWords.slice(0, -1).join(' ') : lesson.title;

  // Markdown renderer with syntax highlighting
  const renderContent = (content: string) => {
    const parts = content.split(/(```[\s\S]*?```)/g);
    return parts.map((part, i) => {
      if (part.startsWith('```')) {
        const lines = part.split('\n');
        const lang = lines[0].replace('```', '').trim() || 'python';
        const code = lines.slice(1, -1).join('\n');
        return <CodeBlock key={i} code={code} language={lang} className="my-6" />;
      }
      return (
        <div key={i} className="prose-lesson" dangerouslySetInnerHTML={{ __html: renderMarkdown(part) }} />
      );
    });
  };

  return (
    <div className="flex h-[calc(100vh-8rem)] -m-4 lg:-m-8">
      {/* Lesson Content Drawer */}
      {(drawer === 'desktop' || drawer === 'mobile') && (
        <>
          {/* Overlay for mobile */}
          <div
            className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={() => setDrawer('closed')}
            aria-hidden="true"
          />
          {/* Drawer */}
          <div
            className={cn(
              "border-r border-border dark:border-white/5 bg-surface dark:bg-night-500",
              "flex-shrink-0 flex flex-col z-50",
              drawer === 'mobile'
                ? "fixed inset-y-0 left-0 w-80 shadow-2xl"
                : "hidden lg:flex w-72"
            )}
            role="complementary"
            aria-label="Course lessons"
          >
            <div className="flex items-center justify-between h-14 px-4 border-b border-border bg-surface-secondary">
              <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-tertiary">
                Syllabus Index <span className="text-coral-500">/ Track {String(currentModuleIndex + 1).padStart(2, '0')}</span>
              </p>
              <button
                onClick={() => setDrawer('closed')}
                className="p-1.5 rounded-lg hover:bg-surface-tertiary text-ink-secondary transition-colors"
                aria-label="Close course content menu"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto p-2 space-y-3 scrollbar-thin" aria-label="Lessons">
              {structure?.map((mod: any, modIdx: number) => (
                <div key={mod.id || modIdx}>
                  <div className="flex items-center gap-2 px-2 pt-2 pb-1.5">
                    <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-coral-500 flex-shrink-0">
                      Mod {String(modIdx + 1).padStart(2, '0')}
                    </span>
                    <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary truncate">{mod.title}</span>
                  </div>
                  {mod.lessons?.map((l: any) => {
                    const isCurrent = l.slug === lessonSlug && mod.slug === moduleSlug;
                    return (
                      <Link
                        key={l.slug}
                        href={`/courses/${slug}/learn/${mod.slug}/${l.slug}`}
                        onClick={() => setDrawer((d) => (d === 'mobile' ? 'closed' : d))}
                        aria-current={isCurrent ? 'page' : undefined}
                        className={cn(
                          "flex items-center gap-2.5 px-2.5 py-2 rounded-lg text-sm text-left transition-colors duration-150 w-full",
                          isCurrent
                            ? "bg-surface-tertiary dark:bg-night-400 text-ink font-semibold"
                            : "text-ink-secondary dark:text-ink-tertiary hover:text-ink hover:bg-surface-secondary dark:hover:bg-white/5"
                        )}
                      >
                        <span className={cn(
                          "h-1.5 w-1.5 rounded-full flex-shrink-0",
                          isCurrent ? "bg-coral-500" : "bg-ink-tertiary/40"
                        )} aria-hidden="true" />
                        <span className="flex-1 truncate text-[13px]">{l.title}</span>
                        {isCurrent && (
                          <span className="font-mono text-[9px] uppercase tracking-wider bg-coral-500 text-white px-1.5 py-0.5 rounded-sm flex-shrink-0">Now</span>
                        )}
                        {!isCurrent && l.is_free_preview && (
                          <span className="font-mono text-[9px] uppercase tracking-wider text-coral-500 flex-shrink-0">Preview</span>
                        )}
                      </Link>
                    );
                  })}
                </div>
              ))}
            </nav>
          </div>
        </>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top navigation bar */}
        <div className="flex items-center gap-2 px-4 lg:px-6 h-14 border-b border-border bg-surface-secondary/80 dark:bg-night-600/80 backdrop-blur-sm flex-shrink-0">
          {/* Drawer toggle */}
          <button
            onClick={toggleDrawer}
            aria-expanded={drawer !== 'closed'}
            aria-controls="lesson-drawer"
            className={cn(
              "p-2 rounded-lg transition-colors",
              drawer !== 'closed'
                ? "bg-surface-tertiary text-coral-500"
                : "hover:bg-surface-tertiary text-ink-secondary dark:text-ink-tertiary"
            )}
            aria-label="Toggle course content menu"
          >
            <List className="h-5 w-5" />
          </button>

          <Link
            href={`/courses/${slug}`}
            className="p-2 rounded-lg hover:bg-surface-tertiary text-ink-secondary dark:text-ink-tertiary transition-colors"
            aria-label="Back to course page"
          >
            <ChevronLeft className="h-5 w-5" />
          </Link>

          <div className="flex-1 min-w-0">
            <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary truncate">
              {currentModuleTitle || 'Lesson'}
            </p>
            <p className="text-sm font-medium text-ink truncate leading-tight">{lesson.title}</p>
          </div>

          <div className="flex items-center gap-1.5 flex-shrink-0">
            <button
              onClick={scrollToSandbox}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-[11px] font-mono font-semibold uppercase tracking-wide bg-coral-500 text-white hover:bg-coral-600 transition-colors"
              title="Jump to the code playground"
            >
              <Play className="h-3 w-3 fill-current" /> Run Code
            </button>
            {lesson.estimated_duration_minutes && (
              <span className="hidden md:flex items-center gap-1 font-mono text-[11px] text-ink-tertiary px-2 py-1 rounded-md bg-surface-tertiary dark:bg-white/5">
                <Clock className="h-3 w-3" /> {lesson.estimated_duration_minutes}m
              </span>
            )}
            {lesson.difficulty && (
              <span className="hidden md:inline-flex">
                <Badge variant={lesson.difficulty === 'beginner' ? 'success' : 'warning'} size="sm">
                  {lesson.difficulty}
                </Badge>
              </span>
            )}
          </div>
        </div>

        {/* Scrollable content */}
        <div ref={contentRef} className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="max-w-3xl mx-auto px-4 lg:px-8 py-8 lg:py-12">
            {/* Title area */}
            <div className="mb-8">
              <div className="flex flex-wrap items-center gap-2 mb-4">
                <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-coral-500">
                  — No. {String(currentModuleIndex + 1).padStart(2, '0')} — {currentModuleTitle || 'Lesson'}
                </span>
                {lesson.estimated_duration_minutes && (
                  <>
                    <span className="text-ink-tertiary text-[10px]">/</span>
                    <span className="font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">
                      {lesson.estimated_duration_minutes} min
                    </span>
                  </>
                )}
              </div>
              <h1 className="font-display text-3xl lg:text-4xl font-medium tracking-tight text-ink leading-[1.12]">
                {titleHead}{' '}
                {titleLast && <em className="italic font-normal text-coral-500">{titleLast}</em>}
              </h1>
              {lesson.description && (
                <p className="mt-4 text-base lg:text-lg text-ink-secondary leading-relaxed max-w-2xl">
                  {lesson.description}
                </p>
              )}
            </div>

            {/* Learning Objectives */}
            {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
              <div className="mb-8 rounded-xl border border-border bg-surface p-5">
                <div className="flex items-center gap-2 mb-4">
                  <Lightbulb className="h-4 w-4 text-coral-500" />
                  <h3 className="font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-ink">
                    Key Architectural Competencies
                  </h3>
                </div>
                <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-2">
                  {lesson.learning_objectives.map((obj: string, i: number) => (
                    <div key={i} className="flex items-start gap-2 rounded-lg bg-surface-secondary dark:bg-night-600/60 p-3">
                      <CheckCircle className="h-4 w-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                      <span className="text-xs leading-relaxed text-ink-secondary">{obj}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Main lesson content */}
            <div className="pb-8">
              {renderContent(lesson.content)}
            </div>

            {/* Try it Yourself */}
            <div ref={sandboxRef} className="mt-10 pt-8 border-t border-border">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="h-6 w-6 rounded-md bg-coral-500/10 flex items-center justify-center">
                    <Play className="h-3.5 w-3.5 text-coral-500 fill-current" />
                  </span>
                  <h2 className="font-mono text-[11px] font-semibold uppercase tracking-[0.14em] text-ink">Live Sandbox</h2>
                </div>
                <span className="hidden sm:inline font-mono text-[10px] uppercase tracking-[0.14em] text-ink-tertiary">
                  Runs in your browser
                </span>
              </div>
              <Sandbox
                language={starter?.language ?? "python"}
                initialCode={starter?.code || '# Experiment with what you just learned!\nprint("Hello, DSir!")\n'}
                height="280px"
              />
            </div>

            {/* Bottom actions */}
            <div className="mt-10 pt-8 border-t border-border">
              <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
                <Button
                  variant={progress?.is_completed ? 'primary' : 'outline'}
                  size="md"
                  onClick={markComplete}
                  leftIcon={progress?.is_completed ? <CheckCircle className="h-5 w-5" /> : <Circle className="h-5 w-5" />}
                  className={cn(progress?.is_completed && "pointer-events-none opacity-70")}
                >
                  {progress?.is_completed ? 'Completed ✓' : 'Mark as Complete'}
                </Button>

                <div className="flex gap-2">
                  {prevLesson && (
                    <Link
                      href={`/courses/${slug}/learn/${prevLesson.module.slug}/${prevLesson.lesson.slug}`}
                      className="flex-1 sm:flex-initial"
                    >
                      <Button variant="ghost" size="md" leftIcon={<ChevronLeft className="h-4 w-4" />} className="w-full">
                        <span className="hidden sm:inline">Previous</span>
                      </Button>
                    </Link>
                  )}
                  {nextLesson && (
                    <Link
                      href={`/courses/${slug}/learn/${nextLesson.module.slug}/${nextLesson.lesson.slug}`}
                      className="flex-1 sm:flex-initial"
                    >
                      <Button size="md" rightIcon={<ChevronRight className="h-4 w-4" />} className="w-full">
                        <span className="hidden sm:inline">Next Lesson</span>
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Back to top FAB */}
        {showBackToTop && (
          <button
            onClick={() => contentRef.current?.scrollTo({ top: 0, behavior: 'smooth' })}
            className="fixed bottom-6 right-6 z-30 h-10 w-10 rounded-full bg-surface dark:bg-night-500 border border-border dark:border-white/10 shadow-lg flex items-center justify-center text-ink-secondary hover:text-ink dark:hover:text-ink transition-all hover:shadow-xl"
            aria-label="Back to top"
          >
            <ArrowUp className="h-4 w-4" />
          </button>
        )}
      </div>
    </div>
  );
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

/** Inline formatting — applied after HTML escaping so raw HTML in lesson
 *  content is never injected as markup. */
function inline(text: string): string {
  let out = escapeHtml(text);
  out = out.replace(/`([^`]+)`/g, '<code>$1</code>');
  out = out.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  out = out.replace(/\*(.+?)\*/g, '<em>$1</em>');
  out = out.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+|\/[^\s)]*)\)/g, '<a href="$2" rel="noopener noreferrer" target="_blank">$1</a>');
  return out;
}

/** Simple markdown renderer. Code fences are extracted before this runs. */
function renderMarkdown(md: string): string {
  const lines = md.split('\n');
  const out: string[] = [];
  let listType: 'ul' | 'ol' | null = null;

  const closeList = () => {
    if (listType) { out.push(`</${listType}>`); listType = null; }
  };

  for (const raw of lines) {
    const line = raw.trimEnd();
    if (line.startsWith('- ')) {
      if (listType !== 'ul') { closeList(); out.push('<ul>'); listType = 'ul'; }
      out.push(`<li>${inline(line.slice(2))}</li>`);
    } else if (/^\d+\.\s+/.test(line)) {
      if (listType !== 'ol') { closeList(); out.push('<ol>'); listType = 'ol'; }
      out.push(`<li>${inline(line.replace(/^\d+\.\s+/, ''))}</li>`);
    } else if (line.trim() === '') {
      closeList();
    } else {
      closeList();
      out.push(block(line));
    }
  }
  closeList();
  return out.join('\n');
}

function block(line: string): string {
  const trimmed = line.trimStart();
  if (trimmed.startsWith('#### ')) return `<h4>${inline(trimmed.slice(5))}</h4>`;
  if (trimmed.startsWith('### ')) return `<h3>${inline(trimmed.slice(4))}</h3>`;
  if (trimmed.startsWith('## ')) return `<h2>${inline(trimmed.slice(3))}</h2>`;
  if (trimmed.startsWith('# ')) return `<h1>${inline(trimmed.slice(2))}</h1>`;
  if (trimmed.startsWith('> ')) return `<blockquote>${inline(trimmed.slice(2))}</blockquote>`;
  if (trimmed === '---') return '<hr>';
  return `<p>${inline(trimmed)}</p>`;
}
