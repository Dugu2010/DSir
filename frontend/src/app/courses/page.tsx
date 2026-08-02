"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState, useEffect, useCallback, useMemo } from "react";
import { courses as coursesApi, admin, auth } from "@/lib/api";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { CardSkeleton } from "@/components/ui/Skeleton";
import { formatDuration, formatNumber, difficultyColor } from "@/lib/utils";
import type { CourseListItem } from "@/lib/types";
import {
  Search, Star, BookOpen, Clock, Users,
  TrendingUp, AlertCircle, RefreshCw, X, Trash2,
  GraduationCap, BarChart3, Layers, Filter, SlidersHorizontal,
  CheckCircle2, Play,
} from "lucide-react";

// Gradient presets for course cards
const GRADIENTS = [
  "from-violet-600 to-indigo-700",
  "from-emerald-600 to-teal-700",
  "from-amber-500 to-orange-600",
  "from-rose-500 to-pink-600",
  "from-cyan-500 to-blue-600",
  "from-fuchsia-500 to-purple-600",
  "from-lime-500 to-green-600",
  "from-sky-500 to-indigo-600",
];

const ICONS = ["🐍", "⚛️", "🚀", "💡", "🔧", "📊", "🎨", "🤖", "📱", "🔐"];

function getGradient(index: number) {
  return GRADIENTS[index % GRADIENTS.length];
}

function getIcon(index: number) {
  return ICONS[index % ICONS.length];
}

export default function CoursesPage() {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [sort, setSort] = useState("popular");
  const [selectedTag, setSelectedTag] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<{ id: string; title: string } | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(timer);
  }, [search]);

  // Check admin
  useEffect(() => {
    auth.me().then(u => setIsAdmin(u?.role === "admin" || u?.role === "superadmin")).catch(() => {});
  }, []);

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["courses", debouncedSearch, difficulty, sort],
    queryFn: () => coursesApi.list({
      ...(debouncedSearch && { search: debouncedSearch }),
      ...(difficulty && { difficulty }),
      sort,
    }),
  });

  const items: CourseListItem[] = (data as any)?.items ?? [];
  const total = (data as any)?.total ?? 0;

  // Extract unique tags from courses
  const allTags = useMemo(() => {
    const tags = new Set<string>();
    items.forEach(c => c.skill_tags?.forEach(t => tags.add(t)));
    return Array.from(tags).sort();
  }, [items]);

  // Filter by tag client-side
  const filteredItems = useMemo(() => {
    if (!selectedTag) return items;
    return items.filter(c => c.skill_tags?.includes(selectedTag));
  }, [items, selectedTag]);

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: (courseId: string) => admin.deleteCourse(courseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
      setDeleteTarget(null);
    },
  });

  const clearFilters = useCallback(() => {
    setSearch("");
    setDebouncedSearch("");
    setDifficulty("");
    setSort("popular");
    setSelectedTag("");
  }, []);

  const hasActiveFilters = debouncedSearch || difficulty || selectedTag || sort !== "popular";

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Hero */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-600 via-brand-700 to-indigo-800 p-8 md:p-12">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.08)_0%,transparent_60%)]" />
        <div className="absolute top-0 right-0 w-96 h-96 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/4 blur-3xl" />
        <div className="relative z-10">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-3">
            Explore Courses
          </h1>
          <p className="text-white/70 text-lg max-w-xl">
            Master new skills with expert-crafted courses. From Python to AI, find your next challenge.
          </p>
          <div className="flex flex-wrap gap-6 mt-6">
            <div className="flex items-center gap-2 text-white/80">
              <div className="h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center">
                <BookOpen className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="text-xl font-bold text-white">{formatNumber(total)}</div>
                <div className="text-xs text-white/50">Courses</div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-white/80">
              <div className="h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center">
                <GraduationCap className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="text-xl font-bold text-white">
                  {items.length > 0 ? formatNumber(items.reduce((s, c) => s + c.enrollment_count, 0)) : "—"}
                </div>
                <div className="text-xs text-white/50">Enrollments</div>
              </div>
            </div>
            <div className="flex items-center gap-2 text-white/80">
              <div className="h-10 w-10 rounded-xl bg-white/10 flex items-center justify-center">
                <Layers className="h-5 w-5 text-white" />
              </div>
              <div>
                <div className="text-xl font-bold text-white">{allTags.length}</div>
                <div className="text-xs text-white/50">Topics</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Input
              placeholder="Search courses by title, description, or topic..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              leftIcon={<Search className="h-4 w-4" />}
              rightIcon={
                search ? (
                  <button onClick={() => { setSearch(""); setDebouncedSearch(""); }} className="hover:text-brand-600">
                    <X className="h-4 w-4" />
                  </button>
                ) : undefined
              }
            />
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFilters(!showFilters)}
              leftIcon={<SlidersHorizontal className="h-4 w-4" />}
              className={showFilters ? "border-brand-500 text-brand-600 dark:text-brand-400" : ""}
            >
              Filters
              {hasActiveFilters && (
                <span className="ml-1.5 h-2 w-2 rounded-full bg-brand-500" />
              )}
            </Button>
          </div>
        </div>

        {/* Tag pills */}
        {allTags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedTag("")}
              className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                !selectedTag
                  ? "bg-brand-600 text-white shadow-sm"
                  : "bg-[#f0f2f7] dark:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3] hover:bg-brand-100 dark:hover:bg-brand-500/10"
              }`}
            >
              All
            </button>
            {allTags.slice(0, 12).map(tag => (
              <button
                key={tag}
                onClick={() => setSelectedTag(selectedTag === tag ? "" : tag)}
                className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all ${
                  selectedTag === tag
                    ? "bg-brand-600 text-white shadow-sm"
                    : "bg-[#f0f2f7] dark:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3] hover:bg-brand-100 dark:hover:bg-brand-500/10"
                }`}
              >
                {tag}
              </button>
            ))}
          </div>
        )}

        {/* Extended filters */}
        {showFilters && (
          <div className="flex flex-wrap items-center gap-3 p-4 rounded-2xl bg-[#f8f9fc] dark:bg-white/[0.03] border border-[#e8ecf1] dark:border-white/5">
            <div className="flex items-center gap-2">
              <Filter className="h-4 w-4 text-[#9ca3af]" />
              <span className="text-sm text-[#6b7280] dark:text-[#8b8fa3]">Level:</span>
              <select
                value={difficulty}
                onChange={(e) => setDifficulty(e.target.value)}
                className="h-9 px-3 rounded-lg border border-[#e8ecf1] dark:border-white/10 bg-white dark:bg-[#0d0d13] text-sm text-[#1a1d2e] dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="">All Levels</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-4 w-4 text-[#9ca3af]" />
              <span className="text-sm text-[#6b7280] dark:text-[#8b8fa3]">Sort:</span>
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value)}
                className="h-9 px-3 rounded-lg border border-[#e8ecf1] dark:border-white/10 bg-white dark:bg-[#0d0d13] text-sm text-[#1a1d2e] dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              >
                <option value="popular">Most Popular</option>
                <option value="newest">Newest First</option>
                <option value="rating">Highest Rated</option>
              </select>
            </div>
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters} leftIcon={<X className="h-3.5 w-3.5" />}>
                Clear all
              </Button>
            )}
          </div>
        )}

        {/* Active filters summary */}
        {hasActiveFilters && !showFilters && (
          <div className="flex items-center gap-2 text-sm text-[#6b7280] dark:text-[#8b8fa3]">
            <span>{filteredItems.length} of {items.length} courses</span>
            <button onClick={clearFilters} className="text-brand-600 dark:text-brand-400 hover:underline ml-1">
              Clear filters
            </button>
          </div>
        )}
      </div>

      {/* Error state */}
      {error && (
        <div className="rounded-2xl border border-red-200 dark:border-red-500/20 bg-red-50 dark:bg-red-500/5 p-6 flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center flex-shrink-0">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-red-700 dark:text-red-400">Failed to load courses</p>
            <p className="text-sm text-red-600/80 dark:text-red-400/80">Could not connect to the server.</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()} leftIcon={<RefreshCw className="h-4 w-4" />}>
            Retry
          </Button>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      )}

      {/* Course Grid */}
      {!isLoading && !error && (
        <>
          {filteredItems.length > 0 ? (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredItems.map((course, i) => (
                <CourseCard
                  key={course.id}
                  course={course}
                  gradient={getGradient(i)}
                  icon={getIcon(i)}
                  isAdmin={isAdmin}
                  onDelete={(id, title) => setDeleteTarget({ id, title })}
                />
              ))}
            </div>
          ) : (
            <EmptyState
              search={debouncedSearch}
              difficulty={difficulty}
              selectedTag={selectedTag}
              onClear={clearFilters}
            />
          )}
        </>
      )}

      {/* Delete confirmation modal */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm" onClick={() => setDeleteTarget(null)}>
          <div
            className="bg-white dark:bg-[#14141a] rounded-2xl p-6 max-w-md w-full shadow-2xl border border-[#e8ecf1] dark:border-white/10"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 rounded-xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center">
                <Trash2 className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-[#1a1d2e] dark:text-white">Delete Course</h3>
                <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3]">
                  This will permanently delete the course and all its content.
                </p>
              </div>
            </div>
            <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3] mb-6">
              Are you sure you want to delete <strong className="text-[#1a1d2e] dark:text-white">"{deleteTarget.title}"</strong>?
              This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button variant="outline" onClick={() => setDeleteTarget(null)} disabled={deleteMutation.isPending}>
                Cancel
              </Button>
              <Button
                variant="danger"
                onClick={() => deleteMutation.mutate(deleteTarget.id)}
                isLoading={deleteMutation.isPending}
                leftIcon={!deleteMutation.isPending ? <Trash2 className="h-4 w-4" /> : undefined}
              >
                Delete Course
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// Course Card Component
function CourseCard({
  course,
  gradient,
  icon,
  isAdmin,
  onDelete,
}: {
  course: CourseListItem;
  gradient: string;
  icon: string;
  isAdmin: boolean;
  onDelete: (id: string, title: string) => void;
}) {
  return (
    <div className="group relative">
      <Link href={`/courses/${course.slug}`}>
        <Card hover padding="none" className="overflow-hidden h-full transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
          {/* Gradient cover */}
          <div className={`h-36 bg-gradient-to-br ${gradient} flex items-center justify-center relative overflow-hidden`}>
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_70%_30%,rgba(255,255,255,0.1)_0%,transparent_50%)]" />
            <div className="absolute inset-0 opacity-10" style={{
              backgroundImage: "radial-gradient(circle, rgba(255,255,255,0.3) 1px, transparent 1px)",
              backgroundSize: "20px 20px",
            }} />
            <span className="text-4xl relative z-10">{icon}</span>
            {course.is_featured && (
              <span className="absolute top-3 right-3 px-2 py-0.5 rounded-full bg-amber-400/90 text-amber-900 text-[10px] font-bold uppercase tracking-wider">
                Featured
              </span>
            )}
          </div>

          <div className="p-5">
            {/* Tags + Rating */}
            <div className="flex items-start justify-between mb-2">
              <Badge size="sm" className={difficultyColor(course.difficulty)}>
                {course.difficulty}
              </Badge>
              {course.rating_count > 0 && (
                <div className="flex items-center gap-1">
                  <Star className="h-3.5 w-3.5 text-amber-500 fill-amber-500" />
                  <span className="text-xs font-semibold text-[#1a1d2e] dark:text-white">{course.rating_average}</span>
                  <span className="text-xs text-[#9ca3af] dark:text-[#6b7280]">
                    ({formatNumber(course.rating_count)})
                  </span>
                </div>
              )}
            </div>

            {/* Title */}
            <h3 className="font-semibold text-[#1a1d2e] dark:text-white mb-1.5 line-clamp-2 group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">
              {course.title}
            </h3>

            {/* Description */}
            <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3] line-clamp-2 mb-4">
              {course.description}
            </p>

            {/* Meta */}
            <div className="flex items-center gap-3 text-xs text-[#9ca3af] dark:text-[#6b7280] mb-3">
              <span className="flex items-center gap-1">
                <BookOpen className="h-3 w-3" /> {course.lesson_count} lessons
              </span>
              {course.estimated_duration_minutes && (
                <span className="flex items-center gap-1">
                  <Clock className="h-3 w-3" /> {formatDuration(course.estimated_duration_minutes)}
                </span>
              )}
              <span className="flex items-center gap-1">
                <Users className="h-3 w-3" /> {formatNumber(course.enrollment_count)}
              </span>
            </div>

            {/* Tags */}
            {course.skill_tags && course.skill_tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {course.skill_tags.slice(0, 4).map((tag) => (
                  <Badge key={tag} size="sm" variant="outline">{tag}</Badge>
                ))}
                {course.skill_tags.length > 4 && (
                  <Badge size="sm" variant="outline">+{course.skill_tags.length - 4}</Badge>
                )}
              </div>
            )}
          </div>
        </Card>
      </Link>

      {/* Admin delete button (outside link) */}
      {isAdmin && (
        <button
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            onDelete(course.id, course.title);
          }}
          className="absolute top-3 left-3 z-20 p-1.5 rounded-lg bg-red-500/90 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
          title="Delete course"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}

// Empty State
function EmptyState({
  search,
  difficulty,
  selectedTag,
  onClear,
}: {
  search: string;
  difficulty: string;
  selectedTag: string;
  onClear: () => void;
}) {
  const hasFilters = search || difficulty || selectedTag;

  return (
    <div className="text-center py-20">
      <div className="h-20 w-20 rounded-2xl bg-[#f0f2f7] dark:bg-white/5 flex items-center justify-center mx-auto mb-5">
        {hasFilters ? (
          <Search className="h-8 w-8 text-[#9ca3af] dark:text-[#6b7280]" />
        ) : (
          <BookOpen className="h-8 w-8 text-[#9ca3af] dark:text-[#6b7280]" />
        )}
      </div>
      <h3 className="text-lg font-semibold text-[#1a1d2e] dark:text-white mb-2">
        {hasFilters ? "No matching courses" : "No courses yet"}
      </h3>
      <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3] max-w-sm mx-auto mb-6">
        {hasFilters
          ? "Try adjusting your search or filters to find what you're looking for."
          : "Courses will appear here once they're published. Check back soon!"}
      </p>
      {hasFilters && (
        <Button variant="outline" onClick={onClear} leftIcon={<X className="h-4 w-4" />}>
          Clear all filters
        </Button>
      )}
    </div>
  );
}
