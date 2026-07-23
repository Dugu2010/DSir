"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createProjectSubmission, fetchCourseProjects } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ErrorMessage } from "@/components/ui/error-message";

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
    return <div className="h-40 animate-pulse rounded-2xl bg-slate-200 dark:bg-slate-800" />;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Project Submissions</h1>
        <p className="text-slate-600 dark:text-slate-400">Submit your work and get AI feedback.</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Available Projects</h2>
          {projects?.items.length ? (
            <ul className="mt-4 space-y-3">
              {projects.items.map((project) => (
                <li
                  key={project.id}
                  onClick={() => setSelectedProject(project.id)}
                  className={`cursor-pointer rounded-xl border p-4 transition ${
                    selectedProject === project.id
                      ? "border-blue-500 bg-blue-50 dark:bg-blue-900/20"
                      : "border-slate-200 bg-slate-50 dark:border-slate-700 dark:bg-slate-800"
                  }`}
                >
                  <h3 className="font-semibold text-slate-900 dark:text-white">{project.title}</h3>
                  <p className="text-sm text-slate-600 dark:text-slate-400">{project.description}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-slate-600 dark:text-slate-400">No projects available for this course yet.</p>
          )}
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Submit Project</h2>
          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            {success && (
              <div className="rounded-lg bg-green-50 p-3 text-sm text-green-700 dark:bg-green-950 dark:text-green-200">
                Submission received! AI feedback will be available soon.
              </div>
            )}
            {submitMutation.isError && (
              <ErrorMessage>
                {submitMutation.error instanceof Error ? submitMutation.error.message : "Submission failed"}
              </ErrorMessage>
            )}
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">
                Repository URL
              </label>
              <input
                type="url"
                value={repositoryUrl}
                onChange={(e) => setRepositoryUrl(e.target.value)}
                placeholder="https://github.com/username/project"
                className="mt-1 block w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-slate-900 focus:border-blue-500 focus:ring-blue-500 dark:border-slate-700 dark:bg-slate-800 dark:text-white"
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
