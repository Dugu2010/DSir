"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Card, Badge, Button } from "@/components/ui";
import { PageLoader, ErrorState } from "@/components/ui/States";
import Sandbox from "@/components/Sandbox";
import { api } from "@/lib/api";
import { runPythonTests } from "@/lib/browserPython";
import { Code2, ChevronLeft, CheckCircle, XCircle, Lightbulb, Clock, Zap, Send, Sparkles } from "lucide-react";
import { cn, exerciseTypeLabel } from "@/lib/utils";
import toast from "react-hot-toast";

export default function ExercisePage() {
  const params = useParams<{ id: string }>(); const router = useRouter();
  const [code, setCode] = useState(""); const [showHints, setShowHints] = useState<number[]>([]); const [result, setResult] = useState<any>(null); const [freePractice, setFreePractice] = useState(false);
  const { data: exercise, isLoading, error, refetch } = useQuery({ queryKey: ["exercise", params.id], queryFn: () => api.get<any>(`/practice/exercises/${params.id}`), enabled: !!params.id, retry: 1 });
  const submitMutation = useMutation({
    mutationFn: async () => {
      const browserResult = await runPythonTests(code, exercise.test_code || "");
      return api.post<any>(`/practice/exercises/${params.id}/submit`, { code, language: "python", client_result: browserResult });
    },
    onSuccess: (data) => { setResult(data); data.status === "passed" ? toast.success(`Passed! ${data.score}% 🎉`) : toast.error(`Failed — ${data.score}%. Check the explanation below.`); },
    onError: (e: any) => toast.error(e?.message || "Could not submit. Please try again.")
  });
  useEffect(() => { if (exercise?.starter_code) setCode(exercise.starter_code); }, [exercise]);
  if (isLoading) return <PageLoader label="Loading exercise..." />;
  if (error || !exercise) return <ErrorState title="Couldn't load this exercise" description="Check your connection and try again." onRetry={() => refetch()} className="min-h-[60vh]" />;

  return <div className="flex flex-col lg:flex-row h-[calc(100vh-4rem)]">
    <div className="w-full lg:w-[42%] lg:border-r border-border bg-surface dark:bg-night-500 overflow-y-auto max-h-[45vh] lg:max-h-none">
      <div className="sticky top-0 z-10 bg-surface/90 dark:bg-night-500/90 backdrop-blur-xl border-b border-border dark:border-white/10 px-4 h-14 flex items-center gap-3">
        <button onClick={() => router.back()} className="p-1.5 rounded-lg text-ink-tertiary hover:text-ink" aria-label="Go back"><ChevronLeft className="h-4 w-4" /></button>
        <p className="text-sm font-medium text-ink truncate flex-1">{exercise.title}</p>
        <Badge variant={exercise.difficulty === "easy" ? "success" : exercise.difficulty === "medium" ? "warning" : "danger"} size="sm">{exercise.difficulty}</Badge>
      </div>
      <div className="p-6 space-y-6">
        <div><p className="eyebrow mb-2">Exercise</p><h1 className="font-display text-xl font-semibold text-ink mb-2">{exercise.title}</h1><p className="text-ink-secondary leading-relaxed">{exercise.description}</p></div>
        <Card padding="md" className="bg-coral-50/50 dark:bg-coral-500/5 border-coral-200 dark:border-coral-500/10"><h3 className="text-sm font-semibold font-mono uppercase tracking-eyebrow text-coral-700 dark:text-coral-400 mb-2">Instructions</h3><p className="text-sm text-ink-secondary whitespace-pre-wrap">{exercise.instructions}</p></Card>
        {exercise.hints?.length > 0 && <div><h3 className="text-sm font-semibold text-ink mb-3 flex items-center gap-2"><Lightbulb className="h-4 w-4 text-amber-500" /> Hints</h3><div className="space-y-2">{exercise.hints.map((hint: any, i: number) => !showHints.includes(i) ? <button key={i} onClick={() => setShowHints([...showHints, i])} className="w-full text-left px-4 py-3 rounded-xl border border-border hover:border-amber-400/60 text-sm text-ink-secondary">💡 Hint {i + 1}{hint.cost_percentage > 0 && <span className="float-right text-xs text-amber-600">-{hint.cost_percentage}% score</span>}</button> : <Card key={i} padding="md" className="bg-amber-50/50 dark:bg-amber-500/5"><p className="text-sm text-ink">{hint.content}</p></Card>)}</div></div>}
        <div className="text-xs text-ink-tertiary space-y-1">{exercise.estimated_duration_minutes && <p className="flex items-center gap-1"><Clock className="h-3 w-3" /> ~{exercise.estimated_duration_minutes} min</p>}{exercise.points && <p className="flex items-center gap-1"><Zap className="h-3 w-3 text-amber-400" /> {exercise.points} XP</p>}</div>
      </div>
    </div>
    <div className="flex-1 flex flex-col bg-night-600">
      <div className="h-14 border-b border-paper-50/10 flex items-center px-4 gap-3 shrink-0"><Code2 className="h-4 w-4 text-coral-500" /><span className="text-sm font-medium text-paper-50/80 dark:text-ink">{freePractice ? "Free Python Practice" : "Python Editor"}</span><div className="flex-1" /><Button size="sm" variant={freePractice ? "secondary" : "outline"} onClick={() => { setFreePractice(!freePractice); setResult(null); }} leftIcon={<Sparkles className="h-3.5 w-3.5" />}>{freePractice ? "Back to Exercise" : "Free Practice"}</Button>{!freePractice && <Button size="sm" onClick={() => submitMutation.mutate()} loading={submitMutation.isPending} leftIcon={!submitMutation.isPending ? <Send className="h-3.5 w-3.5" /> : undefined}>Submit Solution</Button>}</div>
      <div className="flex-1 min-h-0"><Sandbox key={freePractice ? "free" : "exercise"} language="python" initialCode={freePractice ? "# Try anything here!\nprint(\"Hello, DSir! 🚀\")\n" : (exercise.starter_code || "# Write your solution here\n")} height="100%" onChange={setCode} /></div>
      {result && !freePractice && <div role="status" aria-live="polite" className={cn("shrink-0 border-t px-4 py-3 overflow-y-auto max-h-56", result.status === "passed" ? "border-emerald-500/30 bg-emerald-500/10" : "border-red-500/30 bg-red-500/10")}><div className="flex items-center gap-2 mb-2">{result.status === "passed" ? <CheckCircle className="h-5 w-5 text-emerald-400" /> : <XCircle className="h-5 w-5 text-red-400" />}<span className="text-sm font-semibold text-paper-50">{result.status === "passed" ? `Passed — ${result.score}%` : `Failed — ${result.score}%`}</span></div>{result.error_message && <pre className="text-xs text-red-300 whitespace-pre-wrap mb-2">{result.error_message}</pre>}{result.test_results?.details?.map((test: any, i: number) => <div key={i} className="mb-2 text-xs"><div className={test.passed ? "text-emerald-300" : "text-red-300"}>{test.passed ? "✅" : "❌"} {test.test}</div>{!test.passed && test.error && <pre className="mt-1 text-red-300/80 whitespace-pre-wrap pl-5">{test.error}</pre>}</div>)}</div>}
    </div>
  </div>;
}
