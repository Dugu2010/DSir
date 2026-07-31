'use client';

import { useState, useRef, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useQuery, useMutation } from '@tanstack/react-query';
import { AppShell } from '@/components/layout/AppShell';
import { Card, Badge, Button } from '@/components/ui';
import { api } from '@/lib/api';
import {
  Code2, ChevronLeft, ChevronRight, Play, CheckCircle, XCircle,
  Lightbulb, Clock, Zap, AlertTriangle, RefreshCw, RotateCcw,
} from 'lucide-react';
import { cn, exerciseTypeLabel } from '@/lib/utils';
import toast from 'react-hot-toast';

export default function ExercisePage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [code, setCode] = useState('');
  const [showHints, setShowHints] = useState<number[]>([]);

  const { data: exercise, isLoading } = useQuery({
    queryKey: ['exercise', params.id],
    queryFn: () => api.get<any>(`/practice/exercises/${params.id}`),
    enabled: !!params.id,
  });

  const submitMutation = useMutation({
    mutationFn: (code: string) => api.post<any>(`/practice/exercises/${params.id}/submit`, {
      code,
      language: 'python',
    }),
    onSuccess: (data) => {
      if (data.status === 'passed') {
        toast.success(`Passed! Score: ${data.score}% 🎉`);
      } else {
        toast.error(`Failed. Score: ${data.score}%. Try again!`);
      }
    },
    onError: () => toast.error('Submission failed. Please try again.'),
  });

  useEffect(() => {
    if (exercise?.starter_code) {
      setCode(exercise.starter_code);
    }
  }, [exercise]);

  const handleSubmit = () => {
    if (!code.trim()) return;
    submitMutation.mutate(code);
  };

  const handleReset = () => {
    setCode(exercise?.starter_code || '');
  };

  const handleTab = (e: React.KeyboardEvent) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const textarea = textareaRef.current;
      if (!textarea) return;
      const start = textarea.selectionStart;
      const end = textarea.selectionEnd;
      const newCode = code.substring(0, start) + '    ' + code.substring(end);
      setCode(newCode);
      setTimeout(() => {
        textarea.selectionStart = textarea.selectionEnd = start + 4;
      }, 0);
    }
  };

  if (isLoading || !exercise) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-[80vh]">
          <div className="h-8 w-8 border-2 border-brand-600 border-t-transparent rounded-full animate-spin" />
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Left panel: Instructions */}
        <div className="w-[42%] border-r border-border bg-surface dark:bg-[#0d0d14] overflow-y-auto scrollbar-thin">
          {/* Header */}
          <div className="sticky top-0 z-10 bg-surface/90 dark:bg-[#0d0d14]/90 backdrop-blur-xl border-b border-border px-4 h-14 flex items-center gap-3">
            <button onClick={() => router.back()} className="p-1.5 rounded-lg text-ink-tertiary hover:text-ink hover:bg-surface-secondary">
              <ChevronLeft className="h-4 w-4" />
            </button>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-ink truncate">{exercise.title}</p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={exercise.difficulty === 'easy' ? 'success' : exercise.difficulty === 'medium' ? 'warning' : 'danger'} size="sm">
                {exercise.difficulty}
              </Badge>
              <Badge variant="outline" size="sm">{exerciseTypeLabel(exercise.exercise_type)}</Badge>
            </div>
          </div>

          {/* Content */}
          <div className="p-6 space-y-6">
            <div>
              <h1 className="text-xl font-bold text-ink mb-2">{exercise.title}</h1>
              <p className="text-ink-secondary leading-relaxed">{exercise.description}</p>
            </div>

            <Card padding="md" className="bg-brand-50/50 dark:bg-brand-950/20 border-brand-100 dark:border-brand-900">
              <h3 className="text-sm font-semibold text-brand-700 dark:text-brand-400 mb-2">Instructions</h3>
              <p className="text-sm text-ink-secondary whitespace-pre-wrap">{exercise.instructions}</p>
            </Card>

            {/* Hints */}
            {exercise.hints && exercise.hints.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-ink mb-3 flex items-center gap-2">
                  <Lightbulb className="h-4 w-4 text-amber-400" /> Hints
                </h3>
                <div className="space-y-2">
                  {exercise.hints.map((hint: any, i: number) => (
                    <div key={i}>
                      {!showHints.includes(i) ? (
                        <button
                          onClick={() => setShowHints([...showHints, i])}
                          className="w-full text-left px-4 py-3 rounded-xl border border-border hover:border-amber-300 hover:bg-amber-50/50 dark:hover:bg-amber-950/20 transition-colors text-sm text-ink-secondary"
                        >
                          <div className="flex items-center justify-between">
                            <span>Hint {i + 1}</span>
                            {hint.cost_percentage > 0 && (
                              <span className="text-xs text-amber-600">-{hint.cost_percentage}% score</span>
                            )}
                          </div>
                        </button>
                      ) : (
                        <Card padding="md" className="bg-amber-50/50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800">
                          <p className="text-sm text-ink">{hint.content}</p>
                        </Card>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Info */}
            <div className="text-xs text-ink-tertiary space-y-1">
              {exercise.estimated_duration_minutes && (
                <p className="flex items-center gap-1"><Clock className="h-3 w-3" /> Estimated: {exercise.estimated_duration_minutes} min</p>
              )}
              {exercise.points && (
                <p className="flex items-center gap-1"><Zap className="h-3 w-3 text-amber-400" /> {exercise.points} XP awarded</p>
              )}
            </div>
          </div>
        </div>

        {/* Right panel: Code Editor */}
        <div className="flex-1 flex flex-col bg-[#0d1117]">
          {/* Toolbar */}
          <div className="h-14 border-b border-white/10 flex items-center px-4 gap-3">
            <div className="flex items-center gap-2">
              <Code2 className="h-4 w-4 text-slate-400" />
              <span className="text-sm font-medium text-slate-300">Python</span>
            </div>
            <div className="flex-1" />
            <div className="flex items-center gap-2">
              <button
                onClick={handleReset}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs text-slate-400 hover:text-slate-200 hover:bg-white/5 transition-colors"
              >
                <RotateCcw className="h-3.5 w-3.5" /> Reset
              </button>
              <Button
                size="sm"
                onClick={handleSubmit}
                isLoading={submitMutation.isPending}
                leftIcon={submitMutation.isPending ? undefined : <Play className="h-3.5 w-3.5" />}
              >
                Run Code
              </Button>
            </div>
          </div>

          {/* Editor */}
          <div className="flex-1 overflow-hidden">
            <textarea
              ref={textareaRef}
              value={code}
              onChange={(e) => setCode(e.target.value)}
              onKeyDown={handleTab}
              className="w-full h-full bg-transparent text-slate-300 font-mono text-sm p-6 resize-none outline-none scrollbar-thin"
              spellCheck={false}
              placeholder="# Write your code here..."
            />
          </div>

          {/* Results */}
          {submitMutation.data && (
            <div className={cn(
              'border-t px-4 py-3',
              submitMutation.data.status === 'passed'
                ? 'border-emerald-500/30 bg-emerald-500/10'
                : 'border-red-500/30 bg-red-500/10',
            )}>
              <div className="flex items-center gap-2 mb-2">
                {submitMutation.data.status === 'passed' ? (
                  <>
                    <CheckCircle className="h-5 w-5 text-emerald-400" />
                    <span className="text-sm font-semibold text-emerald-400">Passed! — {submitMutation.data.score}%</span>
                  </>
                ) : (
                  <>
                    <XCircle className="h-5 w-5 text-red-400" />
                    <span className="text-sm font-semibold text-red-400">Failed — {submitMutation.data.score}%</span>
                  </>
                )}
              </div>
              {submitMutation.data.error_message && (
                <p className="text-xs text-red-300 mb-2">{submitMutation.data.error_message}</p>
              )}
              {submitMutation.data.test_results?.details && (
                <div className="space-y-1 mt-2">
                  {submitMutation.data.test_results.details.map((test: any, i: number) => (
                    <div key={i} className="flex items-center gap-2 text-xs">
                      {test.passed
                        ? <CheckCircle className="h-3.5 w-3.5 text-emerald-400" />
                        : <XCircle className="h-3.5 w-3.5 text-red-400" />
                      }
                      <span className={test.passed ? 'text-emerald-300' : 'text-red-300'}>
                        {test.test}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}
