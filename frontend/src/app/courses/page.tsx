"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { useState, useEffect, useCallback, useMemo, useId } from "react";
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
  AlertCircle, RefreshCw, X, Trash2,
  GraduationCap, Layers, Filter, SlidersHorizontal, ArrowRight,
} from "lucide-react";

// Calm editorial palette for course-card headers (no gradients).
const CARD_TINTS = [
  "bg-coral-50 text-coral-600 dark:bg-coral-500/10 dark:text-coral-400",
  "bg-amber-50 text-amber-700 dark:bg-amber-500/10 dark:text-amber-400",
  "bg-emerald-50 text-emerald-700 dark:bg-emerald-500/10 dark:text-emerald-400",
  "bg-sky-50 text-sky-700 dark:bg-sky-500/10 dark:text-sky-400",
  "bg-violet-50 text-violet-700 dark:bg-violet-500/10 dark:text-violet-400",
  "bg-rose-50 text-rose-700 dark:bg-rose-500/10 dark:text-rose-400",
];

const ICONS = ["🐍", "⚛️", "🚀", "💡", "🔧", "📊", "🎨", "🤖", "📱", "🔐"];

function getTint(i: number) { return CARD_TINTS[i % CARD_TINTS.length]; }
function getIcon(i: number) { return ICONS[i % ICONS.length]; }

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

  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(search), 300);
    return () => clearTimeout(t);
  }, [search]);

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

  const items: CourseListItem[] = useMemo(() => (data as any)?.items ?? [], [data]);
  const total = useMemo(() => (data as any)?.total ?? 0, [data]);

  const allTags = useMemo(() => {
    const tags = new Set<string>();
    items.forEach(c => c.skill_tags?.forEach(t => tags.add(t)));
    return Array.from(tags).sort();
  }, [items]);

  const filteredItems = useMemo(() => {
    if (!selectedTag) return items;
    return items.filter(c => c.skill_tags?.includes(selectedTag));
  }, [items, selectedTag]);

  const deleteMutation = useMutation({
    mutationFn: (courseId: string) => admin.deleteCourse(courseId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courses"] });
      setDeleteTarget(null);
    },
  });

  const clearFilters = useCallback(() => {
    setSearch(""); setDebouncedSearch(""); setDifficulty(""); setSort("popular"); setSelectedTag("");
  }, []);

  const hasActiveFilters = debouncedSearch || difficulty || selectedTag || sort !== "popular";

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-3xl bg-ink dark:bg-night-500 border border-border dark:border-white/5 p-8 md:p-12 text-paper-50 dark:text-ink">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
        <p className="eyebrow mb-4 !text-coral-400">No. 02 — The catalog</p>
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mb-3">Explore Courses</h1>
        <p className="text-paper-50/70 dark:text-ink-secondary text-lg max-w-xl">
          Master new skills with expert-crafted courses. From Python to AI, find your next challenge.
        </p>
        <div className="flex flex-wrap gap-8 mt-8">
          <Stat icon={<BookOpen className="h-5 w-5" />} value={formatNumber(total)} label="Courses" />
          <Stat icon={<GraduationCap className="h-5 w-5" />} value={items.length > 0 ? formatNumber(items.reduce((s, c) => s + c.enrollment_count, 0)) : "—"} label="Enrollments" />
          <Stat icon={<Layers className="h-5 w-5" />} value={String(allTags.length)} label="Topics" />
        </div>
      </div>

      {/* Search + Filters */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="flex-1 relative">
            <Input
              placeholder="Search courses by title or topic..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              leftIcon={<Search className="h-4 w-4" />}
            />
            {search && (
              <button
                onClick={() => { setSearch(""); setDebouncedSearch(""); }}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-ink-tertiary hover:text-ink-secondary dark:hover:text-ink transition-colors"
                aria-label="Clear search"
              >
                <X className="h-4 w-4" />
              </button>
            )}
          </div>
          <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)} aria-expanded={showFilters} aria-controls="course-filters" leftIcon={<SlidersHorizontal className="h-4 w-4" />}>
            Filters{hasActiveFilters && <span className="ml-1.5 h-2 w-2 rounded-full bg-coral-500" />}
          </Button>
        </div>

        {/* Tag pills */}
        {allTags.length > 0 && (
          <div className="flex flex-wrap gap-2">
            <TagPill active={!selectedTag} onClick={() => setSelectedTag("")}>All</TagPill>
            {allTags.slice(0, 12).map(tag => (
              <TagPill key={tag} active={selectedTag === tag} onClick={() => setSelectedTag(selectedTag === tag ? "" : tag)}>
                {tag}
              </TagPill>
            ))}
          </div>
        )}

        {showFilters && (
          <div id="course-filters" className="flex flex-wrap items-center gap-3 p-4 rounded-2xl bg-surface-tertiary dark:bg-white/[0.03] border border-border dark:border-white/5">
            <FilterSelect label="Level" value={difficulty} onChange={setDifficulty} options={[
              { value: "", label: "All Levels" },
              { value: "beginner", label: "Beginner" },
              { value: "intermediate", label: "Intermediate" },
              { value: "advanced", label: "Advanced" },
            ]} />
            <FilterSelect label="Sort" value={sort} onChange={setSort} options={[
              { value: "popular", label: "Most Popular" },
              { value: "newest", label: "Newest First" },
              { value: "rating", label: "Highest Rated" },
            ]} />
            {hasActiveFilters && (
              <Button variant="ghost" size="sm" onClick={clearFilters} leftIcon={<X className="h-3.5 w-3.5" />}>Clear all</Button>
            )}
          </div>
        )}

        {hasActiveFilters && !showFilters && (
          <p className="text-sm text-ink-secondary dark:text-ink-tertiary">
            {filteredItems.length} of {items.length} courses · <button onClick={clearFilters} className="text-coral-600 dark:text-coral-400 hover:underline">Clear filters</button>
          </p>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-2xl border border-red-200 dark:border-red-500/20 bg-red-50 dark:bg-red-500/5 p-6 flex items-center gap-4">
          <div className="h-10 w-10 rounded-xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center flex-shrink-0">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-red-700 dark:text-red-400">Failed to load courses</p>
            <p className="text-sm text-red-600/80 dark:text-red-400/80">Could not connect to the server.</p>
          </div>
          <Button variant="outline" size="sm" onClick={() => refetch()} leftIcon={<RefreshCw className="h-4 w-4" />}>Retry</Button>
        </div>
      )}

      {/* Loading */}
      {isLoading && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => <CardSkeleton key={i} />)}
        </div>
      )}

      {/* Grid */}
      {!isLoading && !error && (
        filteredItems.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredItems.map((course, i) => (
              <CourseCard
                key={course.id}
                course={course}
                tint={getTint(i)}
                icon={getIcon(i)}
                isAdmin={isAdmin}
                onDelete={(id, title) => setDeleteTarget({ id, title })}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-20">
            <div className="h-20 w-20 rounded-2xl bg-surface-tertiary dark:bg-white/5 flex items-center justify-center mx-auto mb-5">
              <Search className="h-8 w-8 text-ink-tertiary" />
            </div>
            <h3 className="font-display text-lg font-semibold text-ink dark:text-ink mb-2">No courses found</h3>
            <p className="text-sm text-ink-secondary dark:text-ink-tertiary max-w-sm mx-auto mb-6">
              Try adjusting your search or filters.
            </p>
            <Button variant="outline" onClick={clearFilters} leftIcon={<X className="h-4 w-4" />}>Clear filters</Button>
          </div>
        )
      )}

      {/* Delete modal */}
      {deleteTarget && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
          onClick={() => setDeleteTarget(null)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-course-title"
            className="bg-surface dark:bg-night-500 rounded-2xl p-6 max-w-md w-full shadow-xl border border-border dark:border-white/10"
            onClick={e => e.stopPropagation()}
          >
            <div className="flex items-center gap-3 mb-4">
              <div className="h-12 w-12 rounded-xl bg-red-100 dark:bg-red-500/10 flex items-center justify-center">
                <Trash2 className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <div>
                <h3 id="delete-course-title" className="font-display text-lg font-semibold text-ink dark:text-ink">Delete Course</h3>
                <p className="text-sm text-ink-secondary">This will permanently delete the course and all its content.</p>
              </div>
            </div>
            <p className="text-sm text-ink-secondary mb-6">
              Are you sure you want to delete <strong className="text-ink dark:text-ink">&ldquo;{deleteTarget.title}&rdquo;</strong>? This cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <Button variant="outline" onClick={() => setDeleteTarget(null)} disabled={deleteMutation.isPending}>Cancel</Button>
              <Button variant="danger" onClick={() => deleteMutation.mutate(deleteTarget.id)} loading={deleteMutation.isPending}>Delete Course</Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function Stat({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <div className="flex items-center gap-3">
      <div className="h-10 w-10 rounded-xl bg-coral-500/10 flex items-center justify-center text-coral-400">{icon}</div>
      <div>
        <div className="font-display text-xl font-bold text-paper-50 dark:text-ink">{value}</div>
        <div className="text-xs font-mono uppercase tracking-eyebrow text-paper-50/50 dark:text-ink-tertiary">{label}</div>
      </div>
    </div>
  );
}

function TagPill({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      aria-pressed={active}
      className={`px-3 py-1.5 rounded-full text-xs font-medium font-mono transition-all ${
        active ? "bg-coral-500 text-night-600 shadow-none" : "bg-surface-tertiary dark:bg-white/5 text-ink-secondary dark:text-ink-tertiary hover:bg-coral-50 dark:hover:bg-coral-500/10 hover:text-coral-700 dark:hover:text-coral-400"
      }`}
    >
      {children}
    </button>
  );
}

function FilterSelect({ label, value, onChange, options }: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
}) {
  const id = useId();
  return (
    <div className="flex items-center gap-2">
      <Filter className="h-4 w-4 text-ink-tertiary" aria-hidden="true" />
      <label htmlFor={id} className="text-sm text-ink-secondary dark:text-ink-tertiary">{label}:</label>
      <select
        id={id}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="h-9 px-3 rounded-lg border border-border dark:border-white/10 bg-surface dark:bg-night-500 text-sm text-ink dark:text-ink focus:outline-none focus:ring-2 focus:ring-coral-500"
      >
        {options.map(o => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  );
}

function CourseCard({ course, tint, icon, isAdmin, onDelete }: {
  course: CourseListItem;
  tint: string;
  icon: string;
  isAdmin: boolean;
  onDelete: (id: string, title: string) => void;
}) {
  return (
    <div className="group relative">
      <Link href={`/courses/${course.slug}`}>
        <Card hover padding="none" className="overflow-hidden h-full transition-all duration-300 hover:-translate-y-0.5">
          <div className={`h-32 ${tint} flex items-center justify-center relative overflow-hidden border-b border-border dark:border-white/5`}>
            <span className="text-4xl relative z-10" aria-hidden="true">{icon}</span>
            {course.is_featured && (
              <span className="absolute top-3 right-3 px-2.5 py-0.5 rounded-full bg-coral-500 text-night-600 text-[10px] font-mono font-bold uppercase tracking-eyebrow">Featured</span>
            )}
            <span className="absolute bottom-2 left-3 font-mono text-[10px] uppercase tracking-eyebrow opacity-60" aria-hidden="true">
              No. {String(course.id.slice(-2).replace(/\D/g, "") || "—").padStart(2, "0")}
            </span>
          </div>
          <div className="p-5">
            <div className="flex items-start justify-between mb-2">
              <Badge size="sm" className={difficultyColor(course.difficulty)}>{course.difficulty}</Badge>
              {course.rating_count > 0 && (
                <div className="flex items-center gap-1">
                  <Star className="h-3.5 w-3.5 text-amber-500 fill-amber-500" />
                  <span className="text-xs font-semibold text-ink dark:text-ink">{course.rating_average}</span>
                  <span className="text-xs text-ink-tertiary">({formatNumber(course.rating_count)})</span>
                </div>
              )}
            </div>
            <h3 className="font-display font-semibold text-ink dark:text-ink mb-1.5 line-clamp-2 group-hover:text-coral-700 dark:group-hover:text-coral-400 transition-colors">{course.title}</h3>
            <p className="text-sm text-ink-secondary line-clamp-2 mb-4">{course.description}</p>
            <div className="flex items-center gap-3 text-xs text-ink-tertiary mb-3">
              <span className="flex items-center gap-1"><BookOpen className="h-3 w-3" /> {course.lesson_count} lessons</span>
              {course.estimated_duration_minutes && <span className="flex items-center gap-1"><Clock className="h-3 w-3" /> {formatDuration(course.estimated_duration_minutes)}</span>}
              <span className="flex items-center gap-1"><Users className="h-3 w-3" /> {formatNumber(course.enrollment_count)}</span>
            </div>
            {course.skill_tags && course.skill_tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {course.skill_tags.slice(0, 4).map(tag => <Badge key={tag} size="sm" variant="outline">{tag}</Badge>)}
                {course.skill_tags.length > 4 && <Badge size="sm" variant="outline">+{course.skill_tags.length - 4}</Badge>}
              </div>
            )}
          </div>
        </Card>
      </Link>
      {isAdmin && (
        <button
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); onDelete(course.id, course.title); }}
          className="absolute top-3 left-3 z-20 p-1.5 rounded-lg bg-red-500/90 text-white opacity-0 group-hover:opacity-100 focus:opacity-100 focus-visible:opacity-100 transition-opacity hover:bg-red-600"
          aria-label={`Delete course "${course.title}"`}
          title="Delete course"
        >
          <Trash2 className="h-3.5 w-3.5" />
        </button>
      )}
    </div>
  );
}
