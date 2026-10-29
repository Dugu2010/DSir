"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@/components/ui/Button";
import { useTheme } from "@/lib/theme";
import { courses as coursesApi } from "@/lib/api";
import { formatNumber } from "@/lib/utils";
import type { CourseListItem } from "@/lib/types";
import {
  GraduationCap, ArrowRight, Sun, Moon, Menu, X,
  CheckCircle2, Plus, BookOpen, Code2, Braces, Brain,
} from "lucide-react";

/* ─────────────────────────────────────────────────────────────────────────
   DSir Academy — editorial landing (dark-first).
   Catalog numbers and course cards come from the public courses API;
   nothing on this page is fabricated.
   ───────────────────────────────────────────────────────────────────────── */

const beliefs = [
  {
    title: "Begin with the fundamentals",
    desc: "Every path assumes nothing. Concepts are built slowly, one idea at a time, with instant feedback at every step.",
  },
  {
    title: "Practice beats passive watching",
    desc: "Lessons end where exercises begin. You learn by writing, debugging and refactoring real code.",
  },
  {
    title: "Memory is engineered, not wished",
    desc: "Spaced-repetition revision brings back exactly what's due, so what you learn today is still there next month.",
  },
  {
    title: "AI is a coach, not a shortcut",
    desc: "Your tutor, reviewer and debugger work alongside you — explaining the why, never just the answer.",
  },
];

const faqs = [
  {
    q: "I've never written a line of code. Is DSir for me?",
    a: "Yes. Every course begins from zero and assumes no prior knowledge. Lessons are short, exercises are scaffolded, and the AI tutor is available around the clock when you get stuck.",
  },
  {
    q: "How does the AI tutor work?",
    a: "You get a tutor, code reviewer, debugger, career advisor and mentor. They answer in context with your lessons and exercises, and they're designed to teach — not to hand you answers.",
  },
  {
    q: "Do I need to pay to start?",
    a: "No. Creating an account is free, and every course in the catalog is free to start.",
  },
  {
    q: "How much time do I need each week?",
    a: "As much as you can spare. Set a daily goal, keep a streak, and let the revision system schedule reviews around your timetable.",
  },
];

function courseIcon(course: CourseListItem) {
  const tags = course.skill_tags ?? [];
  if (tags.includes("JavaScript")) return Braces;
  if (tags.includes("Python")) return Code2;
  return BookOpen;
}

export default function LandingPage() {
  const { resolvedTheme, toggleTheme } = useTheme();
  const [mobileMenu, setMobileMenu] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(0);

  const { data: catalog } = useQuery({
    queryKey: ["public-courses"],
    queryFn: () => coursesApi.list({ size: "100", sort: "popular" }),
  });

  const catalogItems = catalog?.items ?? [];
  const catalogTotal = catalog?.total ?? 0;
  const catalogComplete = catalogItems.length >= catalogTotal;
  const freeCourses = catalogItems.filter((course) => course.is_free).length;
  const totalModules = catalogItems.reduce((sum, course) => sum + course.module_count, 0);
  const totalLessons = catalogItems.reduce((sum, course) => sum + course.lesson_count, 0);
  const programCards = catalogItems.slice(0, 4);
  const suffix = catalogComplete ? "" : "+";
  const catalogStats = [
    { value: formatNumber(catalogTotal), label: "Courses" },
    { value: `${formatNumber(totalModules)}${suffix}`, label: "Modules" },
    { value: `${formatNumber(totalLessons)}${suffix}`, label: "Lessons" },
    { value: `${formatNumber(freeCourses)}${suffix}`, label: "Free courses" },
  ];
  const freeLine = !catalog || catalogTotal === 0
    ? null
    : !catalogComplete
      ? `${formatNumber(catalogTotal)} courses in the catalog`
      : freeCourses === catalogTotal
        ? `All ${formatNumber(catalogTotal)} courses are free to start`
        : freeCourses > 0
          ? `${formatNumber(freeCourses)} of ${formatNumber(catalogTotal)} courses are free to start`
          : `${formatNumber(catalogTotal)} courses in the catalog`;

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600 text-ink transition-colors duration-300">
      {/* ── Nav ─────────────────────────────────────────────────── */}
      <nav className="sticky top-0 z-50 bg-surface-secondary/85 dark:bg-night-600/85 backdrop-blur-xl border-b border-border dark:border-white/5">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="h-8 w-8 rounded-lg bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center">
              <GraduationCap className="h-4 w-4 text-coral-500" />
            </div>
            <span className="font-display font-bold text-xl tracking-tight text-ink">
              DSir <span className="font-mono text-[10px] uppercase tracking-eyebrow text-coral-500 align-middle ml-1">Academy</span>
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden sm:flex items-center gap-1">
            <button
              onClick={toggleTheme}
              className="p-4 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-secondary transition-colors"
              title={resolvedTheme === "dark" ? "Light mode" : "Dark mode"}
              aria-label={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <Link href="/courses" className="hidden md:block">
              <Button variant="ghost" size="sm">Courses</Button>
            </Link>
            <Link href="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Sign Up</Button>
            </Link>
          </div>

          {/* Mobile controls */}
          <div className="flex sm:hidden items-center gap-1">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-secondary"
              title={resolvedTheme === "dark" ? "Light mode" : "Dark mode"}
              aria-label={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
            >
              {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <button
              onClick={() => setMobileMenu(!mobileMenu)}
              className="p-4 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5"
              aria-expanded={mobileMenu}
              aria-controls="mobile-menu"
              aria-label="Toggle navigation menu"
            >
              {mobileMenu ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenu && (
          <div id="mobile-menu" className="sm:hidden border-t border-border dark:border-white/5 bg-surface dark:bg-night-500 p-4 space-y-3 animate-slide-down">
            <Link href="/courses" className="block w-full" onClick={() => setMobileMenu(false)}>
              <Button variant="ghost" size="sm" className="w-full justify-center">Browse Courses</Button>
            </Link>
            <Link href="/login" className="block w-full" onClick={() => setMobileMenu(false)}>
              <Button variant="ghost" size="sm" className="w-full justify-center">Sign In</Button>
            </Link>
            <Link href="/signup" className="block w-full" onClick={() => setMobileMenu(false)}>
              <Button size="sm" className="w-full justify-center">Sign Up</Button>
            </Link>
          </div>
        )}
      </nav>

      {/* ── Hero ────────────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-24 pb-16 sm:pb-24">
        <div className="grid lg:grid-cols-[1.05fr_0.95fr] gap-12 lg:gap-16 items-center">
          <div>
            <p className="eyebrow mb-6 animate-fade-in">No. 01 — The new standard in programming education</p>
            <h1 className="font-display text-4xl sm:text-6xl font-medium text-ink leading-[1.05] tracking-tight">
              Learn to code, <br className="hidden sm:block" />
              <em className="font-medium italic">get</em>{" "}
              <span className="highlight-coral">job-ready</span>.
            </h1>
            <p className="mt-6 sm:mt-8 text-base sm:text-lg text-ink-secondary leading-relaxed max-w-xl">
              DSir Academy takes you from absolute beginner to working software engineer —
              with interactive lessons, a practice engine, smart revision, and a 24/7 AI tutor.
              No infinite library — a finite, focused path from your first line of code to real projects.
            </p>
            <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-start sm:items-center gap-3 sm:gap-4">
              <Link href="/signup" className="w-full sm:w-auto">
                <Button size="xl" rightIcon={<ArrowRight className="h-5 w-5" />} className="w-full sm:w-auto">
                  Start Learning
                </Button>
              </Link>
              <Link href="/courses" className="w-full sm:w-auto">
                <Button variant="secondary" size="xl" className="w-full sm:w-auto">
                  Browse Courses
                </Button>
              </Link>
            </div>
            {freeLine && (
              <div className="mt-6 flex items-center gap-2 text-sm text-ink-tertiary">
                <CheckCircle2 className="h-4 w-4 text-coral-500" />
                {freeLine}
              </div>
            )}
          </div>

          {/* Kernel preview panel */}
          <div className="relative">
            <div className="rounded-xl border border-border dark:border-white/10 bg-surface dark:bg-night-500 overflow-hidden">
              <div className="flex items-center justify-between px-4 py-2.5 border-b border-border dark:border-white/10 bg-surface-secondary dark:bg-night-600/60">
                <div className="flex items-center gap-2.5 min-w-0">
                  <span className="flex gap-1.5 flex-shrink-0" aria-hidden="true">
                    <span className="h-2 w-2 rounded-full bg-ink-tertiary/40" />
                    <span className="h-2 w-2 rounded-full bg-ink-tertiary/40" />
                    <span className="h-2 w-2 rounded-full bg-ink-tertiary/40" />
                  </span>
                  <span className="font-mono text-[10px] text-ink-tertiary truncate">python-basics / hello-world.py</span>
                </div>
                <span className="flex items-center gap-1.5 font-mono text-[9px] uppercase tracking-wide text-emerald-600 dark:text-emerald-400 flex-shrink-0">
                  <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" aria-hidden="true" /> Lesson preview
                </span>
              </div>
              <pre className="p-4 text-[11px] sm:text-xs leading-relaxed font-mono overflow-x-auto text-ink-secondary">
                <code>
                  <span className="text-ink-tertiary select-none">01  </span><span className="text-ink-tertiary"># Lesson 1 — Your first Python program</span>{"\n"}
                  <span className="text-ink-tertiary select-none">02  </span>name = <span className="text-emerald-600 dark:text-emerald-400">&quot;world&quot;</span>{"\n"}
                  <span className="text-ink-tertiary select-none">03  </span>greeting = <span className="text-emerald-600 dark:text-emerald-400">&quot;Hello, &quot;</span> + name{"\n"}
                  <span className="text-ink-tertiary select-none">04  </span>{"\n"}
                  <span className="text-ink-tertiary select-none">05  </span><span className="text-sky-600 dark:text-sky-400">print</span>(greeting){"\n"}
                  <span className="text-ink-tertiary select-none">06  </span>{"\n"}
                  <span className="text-ink-tertiary select-none">07  </span><span className="text-violet-600 dark:text-violet-400">for</span> step <span className="text-violet-600 dark:text-violet-400">in</span> [<span className="text-emerald-600 dark:text-emerald-400">&quot;learn&quot;</span>, <span className="text-emerald-600 dark:text-emerald-400">&quot;practice&quot;</span>, <span className="text-emerald-600 dark:text-emerald-400">&quot;revise&quot;</span>]:{"\n"}
                  <span className="text-ink-tertiary select-none">08  </span>{"    "}<span className="text-sky-600 dark:text-sky-400">print</span>(step)
                </code>
              </pre>
              <div className="flex items-center justify-between px-4 py-2.5 border-t border-border dark:border-white/10 bg-surface-secondary dark:bg-night-600/60 font-mono text-[9px] uppercase tracking-wide">
                <span className="text-emerald-600 dark:text-emerald-400">Python · Lesson 01</span>
                <span className="text-ink-tertiary">Beginner friendly</span>
              </div>
            </div>
            <div className="mt-3 rounded-lg border border-border dark:border-white/10 bg-surface dark:bg-night-500 px-4 py-3 flex items-center gap-3">
              <span className="h-7 w-7 rounded-md bg-coral-500/10 border border-coral-500/30 flex items-center justify-center flex-shrink-0">
                <Brain className="h-3.5 w-3.5 text-coral-600 dark:text-coral-400" aria-hidden="true" />
              </span>
              <div className="min-w-0">
                <p className="font-mono text-[9px] uppercase tracking-wide text-ink-tertiary">AI tutor · included with every course</p>
                <p className="text-xs text-ink-secondary truncate">Ask questions, review code, and debug in context.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Catalog stats ───────────────────────────────────────── */}
      {catalog && catalogTotal > 0 && (
        <section className="border-y border-border dark:border-white/5">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 sm:gap-10">
              {catalogStats.map((stat) => (
                <div key={stat.label}>
                  <div className="font-display text-3xl sm:text-4xl font-semibold text-ink">{stat.value}</div>
                  <div className="mt-1.5 text-xs sm:text-sm font-mono uppercase tracking-eyebrow text-ink-tertiary">
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── Catalog ─────────────────────────────────────────────── */}
      {catalog && programCards.length > 0 && (
        <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="grid lg:grid-cols-[1fr_2fr] gap-10 lg:gap-16">
            <div className="lg:sticky lg:top-24 lg:self-start">
              <p className="eyebrow mb-4">No. 02 — The course catalog</p>
              <h2 className="font-display text-3xl sm:text-4xl font-medium text-ink tracking-tight">
                A focused path, <em className="italic text-coral-600 dark:text-coral-400">not</em> an infinite library.
              </h2>
              <p className="mt-4 text-ink-secondary leading-relaxed">
                Every course is a finite sequence of modules, lessons and exercises —
                with a clear start, middle, and end.
              </p>
              <Link href="/courses" className="inline-block mt-6">
                <Button variant="outline" rightIcon={<ArrowRight className="h-4 w-4" />}>
                  Explore the full catalog
                </Button>
              </Link>
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              {programCards.map((course, index) => {
                const Icon = courseIcon(course);
                return (
                  <Link
                    key={course.id}
                    href={`/courses/${course.slug}`}
                    className="group rounded-xl border border-border bg-surface dark:bg-night-500 p-6 hover:border-coral-500/40 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-5">
                      <span className="h-9 w-9 rounded-lg bg-coral-500/10 border border-coral-500/20 flex items-center justify-center">
                        <Icon className="h-4 w-4 text-coral-600 dark:text-coral-400" aria-hidden="true" />
                      </span>
                      <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-ink-tertiary">
                        No. {String(index + 1).padStart(2, "0")}
                      </span>
                    </div>
                    <h3 className="font-display text-xl font-medium text-ink">{course.title}</h3>
                    <p className="mt-2 text-sm text-ink-secondary leading-relaxed">{course.description}</p>
                    <div className="mt-4 pt-4 border-t border-border dark:border-white/10 flex items-center justify-between">
                      <p className="font-mono text-[10px] uppercase tracking-wide text-ink-tertiary">
                        {course.lesson_count} lessons · {course.module_count} modules
                      </p>
                      <ArrowRight className="h-3.5 w-3.5 text-coral-600 dark:text-coral-400 group-hover:translate-x-0.5 transition-transform" aria-hidden="true" />
                    </div>
                  </Link>
                );
              })}
            </div>
          </div>
        </section>
      )}

      {/* ── What we believe ─────────────────────────────────────── */}
      <section className="border-y border-border dark:border-white/5 bg-surface dark:bg-night-500/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="max-w-2xl mb-12 sm:mb-16">
            <p className="eyebrow mb-4">No. 03 — What we believe</p>
            <h2 className="font-display text-3xl sm:text-4xl font-medium text-ink tracking-tight">
              Four principles behind <span className="highlight-coral">every lesson</span>.
            </h2>
          </div>
          <div className="grid sm:grid-cols-2 gap-x-10 gap-y-10">
            {beliefs.map((b, i) => (
              <div key={b.title} className="flex gap-5">
                <span className="font-mono text-sm text-coral-500 pt-1">
                  {String(i + 1).padStart(2, "0")}
                </span>
                <div>
                  <h3 className="font-display text-lg font-semibold text-ink">{b.title}</h3>
                  <p className="mt-1.5 text-sm text-ink-secondary leading-relaxed">{b.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ─────────────────────────────────────────────────── */}
      <section className="border-t border-border dark:border-white/5 bg-surface dark:bg-night-500/40">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <p className="eyebrow mb-4 text-center">No. 04 — Frequently asked</p>
          <h2 className="font-display text-3xl sm:text-4xl font-medium text-ink tracking-tight text-center mb-12 sm:mb-16">
            Questions, answered.
          </h2>
          <div className="space-y-3">
            {faqs.map((faq, i) => {
              const isOpen = openFaq === i;
              return (
                <div key={faq.q} className="rounded-xl border border-border bg-surface dark:bg-night-500">
                  <button
                    onClick={() => setOpenFaq(isOpen ? null : i)}
                    aria-expanded={isOpen}
                    aria-controls={`faq-answer-${i}`}
                    className="w-full flex items-center justify-between gap-4 px-5 sm:px-6 py-4 sm:py-5 text-left"
                  >
                    <span className="font-display text-base sm:text-lg font-semibold text-ink">{faq.q}</span>
                    <Plus className={`h-5 w-5 text-coral-500 flex-shrink-0 transition-transform duration-200 ${isOpen ? "rotate-45" : ""}`} aria-hidden="true" />
                  </button>
                  {isOpen && (
                    <div id={`faq-answer-${i}`} className="px-5 sm:px-6 pb-5 -mt-1 animate-fade-in">
                      <p className="text-sm text-ink-secondary leading-relaxed">{faq.a}</p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── CTA ─────────────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div className="rounded-xl border border-border bg-ink dark:bg-night-500 dark:border-white/10 px-6 py-14 sm:py-20 text-center relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
          <p className="eyebrow mb-5 justify-center text-coral-400">No. 05 — Begin</p>
          <h2 className="font-display text-3xl sm:text-5xl font-semibold tracking-tight text-paper-50 dark:text-ink">
            Start learning <em className="italic text-coral-400">today</em>.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-paper-50/70 dark:text-ink-secondary max-w-xl mx-auto">
            Create a free account and open your first lesson in minutes. No setup, no credit card.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
            <Link href="/signup" className="w-full sm:w-auto">
              <Button size="xl" className="w-full sm:w-auto" rightIcon={<ArrowRight className="h-5 w-5" />}>
                Start Learning
              </Button>
            </Link>
            <Link href="/courses" className="w-full sm:w-auto">
              <Button variant="secondary" size="xl" className="w-full sm:w-auto bg-white/5 text-paper-50 dark:text-ink hover:bg-white/10 border-white/10 dark:border-border">
                Browse Courses
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <footer className="border-t border-border dark:border-white/5 py-10 sm:py-14">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
            <div className="flex items-center gap-2.5">
              <GraduationCap className="h-5 w-5 text-coral-500" aria-hidden="true" />
              <span className="font-display font-bold text-lg text-ink">DSir Academy</span>
            </div>
            <div className="flex flex-wrap gap-x-8 gap-y-2 text-sm text-ink-tertiary">
              <Link href="/courses" className="px-3 py-4 rounded text-base hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Courses</Link>
              <Link href="/practice" className="px-3 py-4 rounded text-base hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Practice</Link>
              <Link href="/login" className="px-3 py-4 rounded text-base hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Sign In</Link>
              <Link href="/signup" className="px-3 py-4 rounded text-base hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Sign Up</Link>
            </div>
          </div>
          <div className="mt-8 pt-6 border-t border-border dark:border-white/5 flex flex-col sm:flex-row items-center justify-between gap-3">
            <p className="text-sm text-ink-tertiary">
              © {new Date().getFullYear()} DSir. Built for learners everywhere.
            </p>
            <p className="font-mono text-2xs uppercase tracking-eyebrow text-ink-tertiary">
              Begun · Not finished
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
