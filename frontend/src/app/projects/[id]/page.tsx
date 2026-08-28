"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { useQuery, useMutation } from "@tanstack/react-query";
import { projects } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { ChevronLeft, FolderKanban, Send, CheckCircle, Clock, Star } from "lucide-react";
import { cn, difficultyColor } from "@/lib/utils";
import toast from "react-hot-toast";
import type { ProjectDetail } from "@/lib/types";

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const [files, setFiles] = useState<Record<string, string>>({});
  const [activeFile, setActiveFile] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const { data: project, isLoading, error, refetch } = useQuery({
    queryKey: ["project", params.id],
    queryFn: () => projects.get(params.id),
    enabled: !!params.id,
    retry: 1,
  });

  useEffect(() => {
    if (project?.starter_files) {
      setFiles(project.starter_files as Record<string, string>);
      setActiveFile(Object.keys(project.starter_files as object)[0] || null);
    }
  }, [project]);

  const submitMutation = useMutation({
    mutationFn: (code_files: Record<string, string>) => projects.submit(params.id, { code_files }),
    onSuccess: () => {
      setSubmitted(true);
      toast.success("Project submitted for review! 🎉");
    },
    onError: () => toast.error("Submission failed. Please try again."),
  });

  if (isLoading || !project) {
    if (error) return <ErrorState title="Couldn't load this project" description="Check your connection and try again." onRetry={() => refetch()} />;
    return <PageLoader label="Loading project..." />;
  }

  const fileNames = Object.keys(files);
  const p = project as ProjectDetail;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <button
          onClick={() => router.back()}
          className="p-2 rounded-lg text-ink-tertiary hover:text-ink hover:bg-surface-tertiary dark:hover:bg-white/5"
          aria-label="Go back"
        >
          <ChevronLeft className="h-5 w-5" />
        </button>
        <div className="flex-1">
          <p className="eyebrow mb-1">Project</p>
          <h1 className="font-display text-2xl font-semibold text-ink flex items-center gap-2">
            <FolderKanban className="h-6 w-6 text-coral-500" />
            {p.title}
          </h1>
        </div>
        <Badge size="sm" className={difficultyColor(p.difficulty)}>{p.difficulty}</Badge>
      </div>

      {p.is_capstone && (
        <div className="flex items-center gap-2 text-amber-500 text-sm font-medium">
          <Star className="h-4 w-4 fill-current" /> Capstone project
          {p.estimated_duration_hours && (
            <span className="flex items-center gap-1 text-ink-tertiary font-normal ml-2">
              <Clock className="h-3.5 w-3.5" /> ~{p.estimated_duration_hours}h
            </span>
          )}
        </div>
      )}

      <Card padding="md">
        <h2 className="font-display font-semibold text-ink mb-2">Description</h2>
        <p className="text-sm text-ink-secondary leading-relaxed">{p.description}</p>
        <h2 className="font-display font-semibold text-ink mt-6 mb-2">Requirements</h2>
        <pre className="text-sm text-ink-secondary whitespace-pre-wrap font-sans leading-relaxed">{p.requirements}</pre>
      </Card>

      {/* Code editor */}
      <Card padding="none" className="overflow-hidden">
        <div className="flex items-center border-b border-border dark:border-white/10 px-3">
          {fileNames.map((name) => (
            <button
              key={name}
              onClick={() => setActiveFile(name)}
              className={cn(
                "px-3 py-2.5 text-sm font-mono border-b-2 transition-colors",
                activeFile === name
                  ? "border-coral-500 text-ink"
                  : "border-transparent text-ink-tertiary hover:text-ink",
              )}
            >
              {name}
            </button>
          ))}
        </div>
        {activeFile && (
          <textarea
            value={files[activeFile] || ""}
            onChange={(e) => setFiles((prev) => ({ ...prev, [activeFile!]: e.target.value }))}
            spellCheck={false}
            className="w-full h-[420px] bg-night-600 text-paper-50 dark:text-ink font-mono text-sm p-4 resize-none outline-none"
            style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace", lineHeight: 1.7 }}
          />
        )}
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-xs text-ink-tertiary">Your submission will be reviewed and scored.</p>
        {submitted ? (
          <div className="flex items-center gap-2 text-emerald-500 text-sm font-medium">
            <CheckCircle className="h-5 w-5" /> Submitted for review
          </div>
        ) : (
          <Button
            onClick={() => submitMutation.mutate(files)}
            loading={submitMutation.isPending}
            leftIcon={<Send className="h-4 w-4" />}
          >
            Submit Project
          </Button>
        )}
      </div>
    </div>
  );
}
