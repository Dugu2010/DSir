'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/layout/AppShell';
import { Card, Badge, Button, CodeBlock } from '@/components/ui';
import Sandbox from '@/components/Sandbox';
import { api } from '@/lib/api';
import {
  BookOpen, Clock, ChevronLeft, ChevronRight, CheckCircle,
  Circle, BookMarked, Sparkles, ThumbsUp, MessageSquare,
  Play, PanelRight, Maximize2, Copy,
} from 'lucide-react';
import { cn } from '@/lib/utils';

export default function LessonPage() {
  const params = useParams<{ slug: string; moduleSlug: string; lessonSlug: string }>();
  const { slug, moduleSlug, lessonSlug } = params;

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
    enabled: !!slug && !!moduleSlug && !!lessonSlug,
  });

  // Find prev/next lesson
  let prevLesson = null, nextLesson = null;
  if (structure) {
    const allLessons: { module: any; lesson: any }[] = [];
    structure.forEach((m: any) => m.lessons.forEach((l: any) => allLessons.push({ module: m, lesson: l })));
    const currentIdx = allLessons.findIndex((l: any) => l.lesson.slug === lessonSlug && l.module.slug === moduleSlug);
    if (currentIdx > 0) prevLesson = allLessons[currentIdx - 1];
    if (currentIdx < allLessons.length - 1) nextLesson = allLessons[currentIdx + 1];
  }

  const markComplete = async () => {
    try {
      await api.put(`/learn/${slug}/${moduleSlug}/${lessonSlug}/progress`, {
        is_completed: true,
        completion_percentage: 100,
      });
    } catch {}
  };

  if (isLoading || !lesson) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="h-8 w-8 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
        </div>
      </AppShell>
    );
  }

  // Extract code blocks from markdown for rendering
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
        <div key={i} className="prose dark:prose-invert max-w-none" dangerouslySetInnerHTML={{
          __html: part
            .replace(/^### (.+)$/gm, '<h3 class="text-xl font-semibold text-ink mt-8 mb-3">$1</h3>')
            .replace(/^## (.+)$/gm, '<h2 class="text-2xl font-bold text-ink mt-10 mb-4">$1</h2>')
            .replace(/^# (.+)$/gm, '<h1 class="text-3xl font-bold text-ink mt-12 mb-6">$1</h1>')
            .replace(/\*\*(.+?)\*\*/g, '<strong class="font-semibold text-ink">$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/`(.+?)`/g, '<code class="px-1.5 py-0.5 rounded-md bg-surface-secondary text-sm font-mono text-brand-600">$1</code>')
            .replace(/^> (.+)$/gm, '<blockquote class="border-l-4 border-brand-400 pl-4 py-1 my-4 text-ink-secondary italic">$1</blockquote>')
            .replace(/^- (.+)$/gm, '<li class="ml-4 text-ink-secondary">• $1</li>')
            .replace(/^(\d+)\. (.+)$/gm, '<li class="ml-4 text-ink-secondary">$1. $2</li>')
            .replace(/\n\n/g, '<br/><br/>')
        }} />
      );
    });
  };

  return (
    <AppShell>
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Lesson content */}
        <div className="flex-1 overflow-y-auto">
          {/* Navigation bar */}
          <div className="sticky top-0 z-20 bg-surface/90 dark:bg-[#0d0d14]/90 backdrop-blur-xl border-b border-border px-4 h-14 flex items-center gap-3">
            <Link href={`/courses/${slug}/learn`} className="p-1.5 rounded-lg text-ink-tertiary hover:text-ink hover:bg-surface-secondary">
              <ChevronLeft className="h-4 w-4" />
            </Link>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-ink truncate">{lesson.title}</p>
            </div>
            <div className="flex items-center gap-2">
              {lesson.estimated_duration_minutes && (
                <Badge variant="outline" size="sm" className="flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {lesson.estimated_duration_minutes} min
                </Badge>
              )}
              {lesson.difficulty && (
                <Badge variant={lesson.difficulty === 'beginner' ? 'success' : 'warning'} size="sm">
                  {lesson.difficulty}
                </Badge>
              )}
            </div>
          </div>

          {/* Content */}
          <div className="max-w-3xl mx-auto px-6 py-8">
            <h1 className="text-2xl sm:text-3xl font-bold text-ink tracking-tight mb-2">{lesson.title}</h1>
            {lesson.description && (
              <p className="text-lg text-ink-secondary mb-8">{lesson.description}</p>
            )}

            {/* Learning Objectives */}
            {lesson.learning_objectives && lesson.learning_objectives.length > 0 && (
              <Card padding="md" className="mb-8 bg-brand-50/50 dark:bg-brand-950/20 border-brand-100 dark:border-brand-900">
                <h3 className="text-sm font-semibold text-brand-700 dark:text-brand-400 mb-3">Learning Objectives</h3>
                <ul className="space-y-1.5">
                  {lesson.learning_objectives.map((obj: string, i: number) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-ink-secondary">
                      <CheckCircle className="h-4 w-4 text-brand-500 flex-shrink-0 mt-0.5" />
                      {obj}
                    </li>
                  ))}
                </ul>
              </Card>
            )}

            {/* Main content */}
            {renderContent(lesson.content)}

            {/* Code Playground */}
            <div className="mt-12 pt-8 border-t border-border">
              <div className="flex items-center gap-2 mb-4">
                <Play className="h-5 w-5 text-emerald-500" />
                <h2 className="text-lg font-bold text-ink">Try it Yourself</h2>
              </div>
              <p className="text-sm text-ink-secondary mb-4">
                Experiment with what you learned. The code runs in your browser — no server needed.
              </p>
              <Sandbox language="python" initialCode="# Try what you just learned!\nprint('Hello, DSir!')\n" height="250px" />
            </div>

            {/* Complete button */}
            <div className="mt-12 pt-8 border-t border-border">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex gap-2">
                  <Button
                    variant={progress?.is_completed ? 'primary' : 'outline'}
                    size="lg"
                    onClick={markComplete}
                    leftIcon={progress?.is_completed ? <CheckCircle className="h-5 w-5" /> : <Circle className="h-5 w-5" />}
                  >
                    {progress?.is_completed ? 'Completed' : 'Mark as Complete'}
                  </Button>
                  <Button variant="ghost" size="lg" leftIcon={<BookMarked className="h-5 w-5" />}>
                    Bookmark
                  </Button>
                </div>
                <div className="flex gap-2">
                  {prevLesson && (
                    <Link href={`/courses/${slug}/learn/${prevLesson.module.slug}/${prevLesson.lesson.slug}`}>
                      <Button variant="ghost" size="md" leftIcon={<ChevronLeft className="h-4 w-4" />}>
                        Previous
                      </Button>
                    </Link>
                  )}
                  {nextLesson && (
                    <Link href={`/courses/${slug}/learn/${nextLesson.module.slug}/${nextLesson.lesson.slug}`}>
                      <Button size="md" rightIcon={<ChevronRight className="h-4 w-4" />}>
                        Next Lesson
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right sidebar */}
        <aside className="hidden xl:block w-72 border-l border-border bg-surface dark:bg-[#0d0d14] overflow-y-auto scrollbar-thin p-4">
          <h3 className="text-sm font-semibold text-ink mb-3">Lesson Info</h3>
          <div className="space-y-2 text-sm text-ink-secondary">
            {lesson.estimated_duration_minutes && (
              <div className="flex items-center gap-2"><Clock className="h-4 w-4" /> {lesson.estimated_duration_minutes} min</div>
            )}
            {lesson.skill_tags && lesson.skill_tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 pt-2">
                {lesson.skill_tags.map((tag: string) => (
                  <Badge key={tag} variant="outline" size="sm">{tag}</Badge>
                ))}
              </div>
            )}
          </div>

          <div className="mt-6">
            <h3 className="text-sm font-semibold text-ink mb-3">Actions</h3>
            <div className="space-y-2">
              <Button variant="ghost" size="sm" className="w-full justify-start" leftIcon={<Sparkles className="h-4 w-4" />}>
                Ask AI about this
              </Button>
              <Button variant="ghost" size="sm" className="w-full justify-start" leftIcon={<MessageSquare className="h-4 w-4" />}>
                Discussion
              </Button>
              <Button variant="ghost" size="sm" className="w-full justify-start" leftIcon={<Copy className="h-4 w-4" />}>
                Copy lesson link
              </Button>
            </div>
          </div>
        </aside>
      </div>
    </AppShell>
  );
}
