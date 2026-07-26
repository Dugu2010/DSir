"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createProjectSubmission, fetchCourseProjects } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";
import { Skeleton } from "@/components/ui/skeleton";

export default function CourseProjectsPage() {
  const { courseId } = useParams<{ courseId: string }>();
  const queryClient = useQueryClient();
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [success, setSuccess] = useState(false);

  const { data: projects, isLoading } = useQuery({
    queryKey: ["course-projects", courseId],
    queryFn: () => fetchCourseProjects(courseId),
  });

  const submitMutation = useMutation({
    mutationFn: createProjectSubmission,
    onSuccess: () => {
      setSuccess(true);
      setRepositoryUrl("");
      setSelectedProject(null);
      queryClient.invalidateQueries({ queryKey: ["project-submissions"] });
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProject) return;
    submitMutation.mutate({ project_id: selectedProject, repository_url: repositoryUrl });
  };

  if (isLoading) {
    return <Skeleton className="h-40 rounded-2xl" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Project Submissions</h1>
        <p className="text-muted-foreground">Submit your work and get AI feedback.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Available Projects</h2>
          {projects?.items.length ? (
            <ul className="mt-4 space-y-3">
              {projects.items.map((project) => (
                <li
                  key={project.id}
                  onClick={() => setSelectedProject(project.id)}
                  className={`cursor-pointer rounded-xl border p-4 transition ${
                    selectedProject === project.id
                      ? "border-primary bg-primary/5"
                      : "border-border bg-background hover:bg-accent"
                  }`}
                >
                  <h3 className="font-semibold text-card-foreground">{project.title}</h3>
                  <p className="text-sm text-muted-foreground">{project.description}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-muted-foreground">No projects available for this course yet.</p>
          )}
        </section>

        <section className="rounded-2xl border border-border bg-card p-6">
          <h2 className="text-lg font-semibold text-card-foreground">Submit Project</h2>
          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            {success && (
              <div className="rounded-lg bg-emerald-50 p-3 text-sm text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300">
                Submission received! AI feedback will be available soon.
              </div>
            )}
            {submitMutation.isError && (
              <ErrorMessage>
                {submitMutation.error instanceof Error ? submitMutation.error.message : "Submission failed"}
              </ErrorMessage>
            )}
            <div>
              <label className="block text-sm font-medium text-card-foreground">
                Repository URL
              </label>
              <input
                type="url"
                value={repositoryUrl}
                onChange={(e) => setRepositoryUrl(e.target.value)}
                placeholder="https://github.com/username/project"
                className="mt-1 block w-full rounded-lg border border-border bg-card px-3 py-2 text-foreground focus:border-primary focus:ring-primary"
              />
            </div>
            <Button
              type="submit"
              loading={submitMutation.isPending}
              disabled={!selectedProject}
              className="w-full"
            >
              Submit for Review
            </Button>
          </form>
        </section>
      </div>
    </div>
  );
}
