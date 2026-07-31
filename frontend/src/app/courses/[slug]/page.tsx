"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";
import Link from "next/link";
import { courses as coursesApi, users as usersApi } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { PageLoader } from "@/components/ui/States";
import { formatDuration, formatNumber, difficultyColor } from "@/lib/utils";
import {
  BookOpen, Clock, Users, Star, Award, Target, ChevronRight,
  Code2, Play, CheckCircle2, BarChart3, Globe, Layers,
} from "lucide-react";
import toast from "react-hot-toast";

export default function CoursePage() {
  const { slug } = useParams<{ slug: string }>();
  const { isAuthenticated } = useAuth();

  const { data: course, isLoading } = useQuery({
    queryKey: ["course", slug],
    queryFn: () => coursesApi.get(slug),
  });

  const { data: modules } = useQuery({
    queryKey: ["modules", slug],
    queryFn: () => coursesApi.getModules(slug),
  });

  const { data: lessons } = useQuery({
    queryKey: ["lessons", slug],
    queryFn: () => coursesApi.getLessons(slug),
  });

  const handleEnroll = async () => {
    if (!course) return;
    try {
      await usersApi.enroll(course.id);
      toast.success("Enrolled successfully!");
    } catch (err: unknown) {
      const apiErr = err as { detail?: string };
      if (apiErr.detail === "Already enrolled") {
        toast.error("You're already enrolled in this course");
      } else {
        toast.error("Failed to enroll. Please try again.");
      }
    }
  };

  if (isLoading) return <PageLoader />;
  if (!course) return <div className="text-center py-16">Course not found</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Hero */}
      <div className="rounded-3xl bg-gradient-to-br from-brand-600 to-brand-800 p-8 md:p-12 text-white">
        <div className="flex flex-wrap gap-2 mb-4">
          <Badge size="sm" className="bg-white/20 text-white border-0">
            {course.difficulty}
          </Badge>
          {course.skill_tags?.map((tag) => (
            <Badge key={tag} size="sm" className="bg-white/10 text-white/90 border-0">
              {tag}
            </Badge>
          ))}
        </div>
        <h1 className="text-3xl md:text-4xl font-bold">{course.title}</h1>
        <p className="mt-3 text-white/80 text-lg max-w-2xl">{course.description}</p>

        <div className="flex flex-wrap items-center gap-6 mt-6 text-sm text-white/70">
          <span className="flex items-center gap-1.5">
            <BookOpen className="h-4 w-4" /> {course.lesson_count} lessons
          </span>
          {course.estimated_duration_minutes && (
            <span className="flex items-center gap-1.5">
              <Clock className="h-4 w-4" /> {formatDuration(course.estimated_duration_minutes)}
            </span>
          )}
          <span className="flex items-center gap-1.5">
            <Users className="h-4 w-4" /> {formatNumber(course.enrollment_count)} enrolled
          </span>
          <span className="flex items-center gap-1.5">
            <Star className="h-4 w-4 text-amber-400 fill-amber-400" /> {course.rating_average} ({course.rating_count} reviews)
          </span>
        </div>

        <div className="mt-8">
          <Button
            size="lg"
            className="bg-white text-brand-700 hover:bg-white/90"
            onClick={handleEnroll}
          >
            {isAuthenticated ? "Enroll Now — Free" : "Start Learning Free"}
          </Button>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Main content */}
        <div className="lg:col-span-2 space-y-8">
          {/* What you'll learn */}
          {course.learning_objectives && (
            <section>
              <h2 className="text-xl font-bold text-ink mb-4">What You&apos;ll Learn</h2>
              <div className="grid sm:grid-cols-2 gap-3">
                {course.learning_objectives.map((obj, i) => (
                  <div key={i} className="flex items-start gap-2.5">
                    <CheckCircle2 className="h-5 w-5 text-emerald-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm text-ink-secondary">{obj}</span>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Prerequisites */}
          {course.prerequisites && course.prerequisites.length > 0 && (
            <section>
              <h2 className="text-xl font-bold text-ink mb-4">Prerequisites</h2>
              <div className="space-y-2">
                {course.prerequisites.map((pre, i) => (
                  <div key={i} className="flex items-center gap-2.5 text-sm text-ink-secondary">
                    <div className="h-1.5 w-1.5 rounded-full bg-ink-tertiary" />
                    {pre}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Course Content / Curriculum */}
          <section>
            <h2 className="text-xl font-bold text-ink mb-4">Course Curriculum</h2>
            {modules ? (
              <div className="space-y-3">
                {modules.map((mod, idx) => (
                  <div key={mod.id} className="rounded-xl border border-border overflow-hidden">
                    <div className="flex items-center justify-between p-4 bg-surface-secondary/50 cursor-pointer hover:bg-surface-secondary transition-colors">
                      <div className="flex items-center gap-3">
                        <span className="text-sm font-medium text-ink-tertiary">
                          {String(idx + 1).padStart(2, "0")}
                        </span>
                        <div>
                          <h3 className="font-medium text-ink">{mod.title}</h3>
                          <p className="text-xs text-ink-tertiary mt-0.5">
                            {mod.lesson_count} lessons
                            {mod.estimated_duration_minutes && ` • ${formatDuration(mod.estimated_duration_minutes)}`}
                          </p>
                        </div>
                      </div>
                      <ChevronRight className="h-4 w-4 text-ink-tertiary" />
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-sm text-ink-tertiary">Loading curriculum...</div>
            )}
          </section>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <Card padding="md">
            <h3 className="font-semibold text-ink mb-3">Course Info</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Level</span>
                <Badge size="sm" className={difficultyColor(course.difficulty)}>
                  {course.difficulty}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Language</span>
                <span className="text-ink font-medium">{course.language}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Lessons</span>
                <span className="text-ink font-medium">{course.lesson_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Duration</span>
                <span className="text-ink font-medium">{formatDuration(course.estimated_duration_minutes)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-ink-tertiary">Enrolled</span>
                <span className="text-ink font-medium">{formatNumber(course.enrollment_count)}</span>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-border">
              <Button className="w-full" size="lg" onClick={handleEnroll}>
                Enroll Free
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
