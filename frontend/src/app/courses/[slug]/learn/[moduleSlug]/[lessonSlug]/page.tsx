'use client';

import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useState, useEffect, useRef } from 'react';
import { api } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { Card, Badge, Button } from '@/components/ui';
import { CodeBlock } from '@/components/ui/CodeBlock';
import Sandbox from '@/components/Sandbox';
import {
  BookOpen, Clock, ChevronLeft, ChevronRight, CheckCircle,
  Circle, BookMarked, Sparkles, Play, Menu, X, List,
  Lock, Unlock, Maximize2, Copy, ArrowUp, PanelLeft,
  GraduationCap, Code2, Lightbulb, ThumbsUp,
} from 'lucide-react';
import { cn } from '@/lib/utils';
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

  const scrollToSandbox = () => {
    sandboxRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

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

  const { data: lesson, isLoading } = useQuery({
    queryKey: ['lesson', slug, moduleSlug, lessonSlug],
    queryFn: () => api.get<any>(`/learn/${slug}/${moduleSlug}/${lessonSlug}`),
    enabled: !!slug && !!moduleSlug && !!lessonSlug,
  });

  const { data: structure } = useQuery({
    queryKey: ['course-structure', slug],
    queryFn: () => api.get<any[]>(`/courses/${slug}/lessons`),
    enabled: !!slug,
  });

  const { data: progress } = useQuery({
    queryKey: ['lesson-progress', slug, moduleSlug, lessonSlug],
    queryFn: () => api.get<any>(`/learn/${slug}/${moduleSlug}/${lessonSlug}/progress`),
    enabled: !!slug && !!moduleSlug && !!lessonSlug && isAuthenticated,
  });

  // Find prev/next lesson
  let prevLesson: LessonNav | null = null, nextLesson: LessonNav | null = null;
  let currentModuleTitle = '';
  if (structure && moduleSlug && lessonSlug) {
    const allLessons: LessonNav[] = [];
    structure.forEach((m: any) => {
      m.lessons?.forEach((l: any) => allLessons.push({ module: m, lesson: l }));
      if (m.slug === moduleSlug) currentModuleTitle = m.title;
    });
    const idx = allLessons.findIndex((l) => l.lesson.slug === lessonSlug && l.module.slug === moduleSlug);
    if (idx > 0) prevLesson = allLessons[idx - 1];
    if (idx < allLessons.length - 1) nextLesson = allLessons[idx + 1];
  }

  const markComplete = async () => {
    try {
      await api.put(`/learn/${slug}/${moduleSlug}/${lessonSlug}/progress`, {
        is_completed: true,
        completion_percentage: 100,
      });
      queryClient.invalidateQueries({ queryKey: ['lesson-progress'] });
      toast.success('Lesson completed! 🎉');
    } catch {
      toast.error('Failed to mark as complete');
    }
  };

  // Loading state
  if (isLoading || !lesson) {
    return (
      <div className="flex items-center justify-center min-h-[80vh]">
        <div className="text-center">
          <div className="relative mx-auto mb-6">
            <div className="h-16 w-16 rounded-2xl bg-brand-100 dark:bg-brand-500/10 flex items-center justify-center">
              <GraduationCap className="h-8 w-8 text-brand-600 dark:text-brand-400" />
            </div>
            <div className="absolute -bottom-1 -right-1 h-6 w-6 rounded-full bg-white dark:bg-[#0a0a0f] flex items-center justify-center">
              <div className="h-4 w-4 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
            </div>
          </div>
          <p className="text-ink-secondary text-sm">Loading lesson...</p>
        </div>
      </div>
    );
  }

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
      {/* Lesson Content Drawer - Hidden by default, toggle via button */}
      {(drawer === 'desktop' || drawer === 'mobile') && (
        <>
          {/* Overlay for mobile */}
          <div
            className="lg:hidden fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={() => setDrawer('closed')}
          />
          {/* Drawer */}
          <div className={cn(
            "border-r border-[#e8ecf1] dark:border-white/5 bg-white dark:bg-[#0d0d13]",
            "flex-shrink-0 flex flex-col z-50",
            drawer === 'mobile'
              ? "fixed inset-y-0 left-0 w-80 shadow-2xl"
              : "hidden lg:flex w-72"
          )}>
            <div className="flex items-center justify-between p-4 border-b border-[#e8ecf1] dark:border-white/5">
              <h2 className="font-semibold text-sm text-[#1a1d2e] dark:text-white">Course Content</h2>
              <button
                onClick={() => setDrawer('closed')}
                className="p-1.5 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280]"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-1">
              {structure?.map((mod: any, modIdx: number) => (
                <div key={mod.id || modIdx}>
                  <div className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-[#9ca3af] dark:text-[#6b7280] uppercase tracking-wider">
                    <span className="h-5 w-5 rounded-md bg-[#f1f3f5] dark:bg-white/5 flex items-center justify-center text-2xs font-bold text-[#6b7280]">
                      {String(modIdx + 1).padStart(2, '0')}
                    </span>
                    {mod.title}
                  </div>
                  {mod.lessons?.map((l: any) => {
                    const isCurrent = l.slug === lessonSlug && mod.slug === moduleSlug;
                    return (
                      <Link
                        key={l.slug}
                        href={`/courses/${slug}/learn/${mod.slug}/${l.slug}`}
                        onClick={() => setDrawer(drawer === 'mobile' ? 'closed' : drawer)}
                        className={cn(
                          "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm text-left transition-all duration-150 w-full",
                          isCurrent
                            ? "bg-brand-50 dark:bg-brand-500/10 text-brand-700 dark:text-brand-400 font-medium shadow-sm"
                            : "text-[#6b7280] dark:text-[#8b8fa3] hover:text-[#1a1d2e] dark:hover:text-white hover:bg-[#f1f3f5] dark:hover:bg-white/5"
                        )}
                      >
                        <div className={cn(
                          "h-6 w-6 rounded-full flex-shrink-0 flex items-center justify-center text-xs font-medium",
                          isCurrent
                            ? "bg-brand-600 text-white"
                            : "bg-[#f1f3f5] dark:bg-white/5 text-[#9ca3af]"
                        )}>
                          {isCurrent ? <Play className="h-3 w-3 fill-current" /> : l.slug[0]?.toUpperCase()}
                        </div>
                        <span className="flex-1 truncate text-xs">{l.title}</span>
                        {l.is_free_preview && (
                          <Badge size="sm" className="bg-emerald-100 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400 border-0 flex-shrink-0">Free</Badge>
                        )}
                      </Link>
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top navigation bar */}
        <div className="flex items-center gap-2 px-4 lg:px-6 h-14 border-b border-[#e8ecf1] dark:border-white/5 bg-white/50 dark:bg-[#0d0d13]/50 backdrop-blur-sm flex-shrink-0">
          {/* Drawer toggle */}
          <button
            onClick={() => {
              if (drawer === 'closed') setDrawer('desktop');
              else if (drawer === 'desktop') setDrawer('mobile');
              else setDrawer('closed');
            }}
            className={cn(
              "p-2 rounded-lg transition-colors",
              drawer !== 'closed'
                ? "bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400"
                : "hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3]"
            )}
            title="Toggle lesson menu"
          >
            <List className="h-4.5 w-4.5" />
          </button>

          <Link
            href={`/courses/${slug}`}
            className="p-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3] transition-colors"
          >
            <ChevronLeft className="h-4.5 w-4.5" />
          </Link>

          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-[#1a1d2e] dark:text-white truncate">{lesson.title}</p>
            {currentModuleTitle && (
              <p className="text-xs text-[#9ca3af] dark:text-[#6b7280] truncate">{currentModuleTitle}</p>
            )}
          </div>

          <div className="hidden sm:flex items-center gap-1.5">
            <button
              onClick={scrollToSandbox}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-emerald-50 dark:bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-100 dark:hover:bg-emerald-500/20 transition-colors"
            >
              <Play className="h-3.5 w-3.5 fill-current" /> Try it Out
            </button>
            {lesson.estimated_duration_minutes && (
              <span className="flex items-center gap-1 text-xs text-[#6b7280] dark:text-[#8b8fa3] px-2 py-1 rounded-lg bg-[#f1f3f5] dark:bg-white/5">
                <Clock className="h-3.5 w-3.5" /> {lesson.estimated_duration_minutes} min
              </span>
            )}
            {lesson.difficulty && (
              <Badge variant={lesson.difficulty === 'beginner' ? 'success' : 'warning'} size="sm">
                {lesson.difficulty}
              </Badge>
            )}
          </div>
        </div>

        {/* Scrollable content */}
        <div ref={contentRef} className="flex-1 overflow-y-auto scrollbar-thin">
          <div className="max-w-3xl mx-auto px-4 lg:px-8 py-6 lg:py-10">
            {/* Title area */}
            <div className="mb-8">
              <h1 className="text-2xl lg:text-3xl font-bold text-[#1a1d2e] dark:text-white tracking-tight">{lesson.title}</h1>
              {lesson.description && (
                <p className="mt-2 text-[#6b7280] dark:text-[#8b8fa3] leading-relaxed">{lesson.description}</p>
              )}
            </div>

            {/* Learning Objectives */}
            {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
              <div className="mb-8 p-5 rounded-2xl bg-brand-50/50 dark:bg-brand-500/5 border border-brand-100 dark:border-brand-500/10">
                <h3 className="text-sm font-semibold text-brand-700 dark:text-brand-400 mb-3 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4" /> Learning Objectives
                </h3>
                <ul className="space-y-2">
                  {lesson.learning_objectives.map((obj: string, i: number) => (
                    <li key={i} className="flex items-start gap-2.5 text-sm text-[#4b5563] dark:text-[#a0a5b8]">
                      <CheckCircle className="h-4 w-4 text-brand-500 flex-shrink-0 mt-0.5" />
                      {obj}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Main lesson content */}
            <div className="pb-8">
              {renderContent(lesson.content)}
            </div>

            {/* Try it Yourself */}
            <div ref={sandboxRef} className="mt-8 pt-8 border-t border-[#e8ecf1] dark:border-white/5">
              <div className="flex items-center gap-3 mb-4">
                <div className="h-10 w-10 rounded-xl bg-emerald-100 dark:bg-emerald-500/10 flex items-center justify-center">
                  <Play className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-[#1a1d2e] dark:text-white">Try it Yourself</h2>
                  <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3]">
                    Experiment with code — runs entirely in your browser. No server needed.
                  </p>
                </div>
              </div>
              <Sandbox
                language="python"
                initialCode={lesson.starter_code || '# Experiment with what you just learned!\nprint("Hello, DSir!")\n'}
                height="280px"
              />
            </div>

            {/* Bottom actions */}
            <div className="mt-10 pt-8 border-t border-[#e8ecf1] dark:border-white/5">
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
            className="fixed bottom-6 right-6 z-30 h-10 w-10 rounded-full bg-white dark:bg-[#1a1a24] border border-[#e8ecf1] dark:border-white/10 shadow-lg flex items-center justify-center text-[#6b7280] hover:text-[#1a1d2e] dark:hover:text-white transition-all hover:shadow-xl"
          >
            <ArrowUp className="h-4.5 w-4.5" />
          </button>
        )}
      </div>
    </div>
  );
}

// Simple markdown renderer
function renderMarkdown(md: string): string {
  let html = md;

  // Code blocks (handled separately above)
  // headers
  html = html.replace(/^#### (.+)$/gm, '<h4 class="text-base font-semibold mt-6 mb-2 text-[#1a1d2e] dark:text-white">$1</h4>');
  html = html.replace(/^### (.+)$/gm, '<h3 class="text-lg font-semibold mt-8 mb-3 text-[#1a1d2e] dark:text-white">$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2 class="text-xl font-bold mt-10 mb-4 text-[#1a1d2e] dark:text-white">$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1 class="text-2xl font-bold mt-12 mb-6 text-[#1a1d2e] dark:text-white">$1</h1>');

  // Bold & italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong class="font-semibold"><em>$1</em></strong>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-[#1a1d2e] dark:text-white">$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded-md bg-[#f1f3f5] dark:bg-white/5 text-sm font-mono text-brand-600 dark:text-brand-400">$1</code>');

  // Blockquotes
  html = html.replace(/^> (.+)$/gm, '<blockquote class="border-l-4 border-brand-400 dark:border-brand-600 pl-4 py-1.5 my-4 text-[#6b7280] dark:text-[#8b8fa3] italic bg-brand-50/50 dark:bg-brand-500/5 rounded-r-lg">$1</blockquote>');

  // Unordered lists
  html = html.replace(/^- (.+)$/gm, '<li class="ml-4 text-[#4b5563] dark:text-[#a0a5b8] mb-1 flex items-start gap-2"><span class="text-brand-500 mt-0.5 flex-shrink-0">•</span> $1</li>');

  // Ordered lists
  html = html.replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 text-[#4b5563] dark:text-[#a0a5b8] mb-1">$1. $2</li>');

  // Horizontal rules
  html = html.replace(/^---$/gm, '<hr class="my-8 border-[#e8ecf1] dark:border-white/5">');

  // Paragraphs (wrap remaining text)
  html = html.replace(/^(?!<[a-z/])[A-Za-z].+$/gm, '<p class="mb-4 leading-7 text-[#4b5563] dark:text-[#a0a5b8]">$&</p>');

  return html;
}
