"use client";

import Link from "next/link";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { useTheme } from "@/lib/theme";
import {
  GraduationCap, ArrowRight, Sun, Moon, Menu, X,
  CheckCircle2, Star, Quote, CalendarDays, Plus,
  BookOpen, Code2, Brain, Briefcase, Target,
} from "lucide-react";

/* ─────────────────────────────────────────────────────────────────────────
   DSir Academy — editorial landing (dark-first).
   Structure echoes the reference landing: numbered sections, mono eyebrows,
   serif display headlines, generous whitespace, coral accent used sparingly.
   ───────────────────────────────────────────────────────────────────────── */

const stats = [
  { value: "15K+", label: "Active Learners" },
  { value: "4.8", label: "Average Course Rating" },
  { value: "50+", label: "Expert Programs" },
  { value: "2K+", label: "Practice Exercises" },
];

const programs = [
  {
    number: "01",
    title: "Python Foundations",
    desc: "From zero to confident. Syntax, data structures, and clean problem-solving habits.",
    meta: "24 lessons · 4 modules",
    icon: Code2,
  },
  {
    number: "02",
    title: "Web Development",
    desc: "HTML, CSS, JavaScript and React — build and ship real interfaces from day one.",
    meta: "40 lessons · 6 modules",
    icon: BookOpen,
  },
  {
    number: "03",
    title: "AI-Assisted Engineering",
    desc: "Pair with an AI tutor, reviewer and mentor. Learn to build with today's tools.",
    meta: "30 lessons · 5 modules",
    icon: Brain,
  },
  {
    number: "04",
    title: "Career Launch Track",
    desc: "Portfolio projects, system design fundamentals, and interview preparation.",
    meta: "18 lessons · 3 modules",
    icon: Briefcase,
  },
];

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
    desc: "Spaced-repetition revision and automatic knowledge graphs keep what you learn from leaking away.",
  },
  {
    title: "AI is a coach, not a shortcut",
    desc: "Your tutor, reviewer and debugger work alongside you — explaining the why, never just the answer.",
  },
];

const faculty = [
  {
    name: "Dr. Ananya Rao",
    role: "Curriculum Lead · Algorithms",
    quote: "Teach the pattern, not the answer. Students who can explain their reasoning can build anything.",
  },
  {
    name: "Marcus Bell",
    role: "Staff Engineer · Web Platform",
    quote: "The web is the most powerful canvas we have. I help students learn to paint with it.",
  },
  {
    name: "Yuki Tanaka",
    role: "AI Researcher · Learning Systems",
    quote: "Good feedback is a superpower. We design every exercise around feedback that teaches.",
  },
];

const testimonials = [
  {
    name: "Priya S.",
    role: "Now a backend engineer",
    text: "I came in knowing nothing. The step-by-step lessons and the 24/7 AI tutor carried me from my first print() to my first production API.",
    stars: 5,
  },
  {
    name: "Daniel O.",
    role: "Career switcher",
    text: "The practice engine is brutal in the best way. Every exercise explains exactly why your code misbehaved — that's how you actually learn.",
    stars: 5,
  },
  {
    name: "Mei L.",
    role: "CS undergraduate",
    text: "Revision with spaced repetition kept everything fresh. I stopped re-watching tutorials and started building.",
    stars: 5,
  },
];

const events = [
  { date: "Aug 18", title: "Live cohort orientation — Python for absolute beginners", tag: "Live" },
  { date: "Aug 26", title: "Ask me anything with the faculty", tag: "Q&A" },
  { date: "Sep 03", title: "Build-a-project weekend: portfolio-ready apps", tag: "Workshop" },
];

const faqs = [
  {
    q: "I've never written a line of code. Is DSir for me?",
    a: "Yes. Every program begins from zero and assumes no prior knowledge. Lessons are short, exercises are scaffolded, and the AI tutor is available around the clock when you get stuck.",
  },
  {
    q: "How does the AI tutor work?",
    a: "You get a tutor, code reviewer, debugger and career advisor. They answer in context with your lessons and exercises, and they're trained to teach — not to hand you answers.",
  },
  {
    q: "Do I need to pay to start?",
    a: "No. Signing up is free, free courses are available, and you can explore the full catalog before committing to a program.",
  },
  {
    q: "How much time do I need each week?",
    a: "Most learners make great progress with 4–6 hours per week. The daily goal and revision system adapt to whatever schedule you have.",
  },
];

export default function LandingPage() {
  const { resolvedTheme, toggleTheme } = useTheme();
  const [mobileMenu, setMobileMenu] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(0);

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
              className="p-2 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5 text-ink-secondary transition-colors"
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
              className="p-2 rounded-lg hover:bg-surface-tertiary dark:hover:bg-white/5"
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
        <div className="max-w-3xl">
          <p className="eyebrow mb-6 animate-fade-in">No. 01 — The new standard in programming education</p>
          <h1 className="font-display text-4xl sm:text-6xl lg:text-7xl font-semibold text-ink leading-[1.05] tracking-tight">
            Learn to code, <br className="hidden sm:block" />
            <em className="font-medium italic">get</em>{" "}
            <span className="highlight-coral">job-ready</span>.
          </h1>
          <p className="mt-6 sm:mt-8 text-base sm:text-lg text-ink-secondary leading-relaxed max-w-2xl">
            DSir Academy takes you from absolute beginner to working software engineer —
            with interactive lessons, a practice engine, smart revision, and a 24/7 AI tutor.
            No infinite library. A finite, focused path with a real end date.
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
          <div className="mt-6 flex items-center gap-2 text-sm text-ink-tertiary">
            <CheckCircle2 className="h-4 w-4 text-coral-500" />
            Join thousands of learners · Free courses available
          </div>
        </div>
      </section>

      {/* ── Stats ───────────────────────────────────────────────── */}
      <section className="border-y border-border dark:border-white/5">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-14">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 sm:gap-10">
            {stats.map((stat) => (
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

      {/* ── Programs ────────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div className="grid lg:grid-cols-[1fr_2fr] gap-10 lg:gap-16">
          <div className="lg:sticky lg:top-24 lg:self-start">
            <p className="eyebrow mb-4">No. 02 — Our popular programs</p>
            <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
              A focused path, <em className="italic text-coral-600 dark:text-coral-400">not</em> an infinite library.
            </h2>
            <p className="mt-4 text-ink-secondary leading-relaxed">
              Every program is a finite sequence of modules, lessons and exercises designed
              by engineers — with a clear start, middle, and end.
            </p>
            <Link href="/courses" className="inline-block mt-6">
              <Button variant="outline" rightIcon={<ArrowRight className="h-4 w-4" />}>
                Explore the full catalog
              </Button>
            </Link>
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            {programs.map((p) => (
              <div
                key={p.number}
                className="rounded-2xl border border-border bg-surface dark:bg-night-500 p-6 hover:border-coral-400/60 dark:hover:border-coral-500/40 transition-colors"
              >
                <div className="flex items-center justify-between mb-5">
                  <p.icon className="h-6 w-6 text-coral-500" aria-hidden="true" />
                  <span className="font-mono text-xs tracking-eyebrow text-ink-tertiary">No. {p.number}</span>
                </div>
                <h3 className="font-display text-xl font-semibold text-ink">{p.title}</h3>
                <p className="mt-2 text-sm text-ink-secondary leading-relaxed">{p.desc}</p>
                <p className="mt-4 font-mono text-xs uppercase tracking-eyebrow text-ink-tertiary">{p.meta}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── What we believe ─────────────────────────────────────── */}
      <section className="border-y border-border dark:border-white/5 bg-surface dark:bg-night-500/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="max-w-2xl mb-12 sm:mb-16">
            <p className="eyebrow mb-4">No. 03 — What we believe</p>
            <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
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

      {/* ── Faculty ─────────────────────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div className="max-w-2xl mb-12 sm:mb-16">
          <p className="eyebrow mb-4">No. 04 — Faculty</p>
          <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
            Built by people who <em className="italic text-coral-600 dark:text-coral-400">build</em>.
          </h2>
        </div>
        <div className="grid md:grid-cols-3 gap-4 sm:gap-6">
          {faculty.map((f) => (
            <figure key={f.name} className="rounded-2xl border border-border bg-surface dark:bg-night-500 p-6 sm:p-8">
              <Quote className="h-6 w-6 text-coral-500 mb-5" aria-hidden="true" />
              <blockquote className="text-sm sm:text-base text-ink-secondary leading-relaxed">
                “{f.quote}”
              </blockquote>
              <figcaption className="mt-6 pt-5 border-t border-border dark:border-white/5">
                <p className="font-display font-semibold text-ink">{f.name}</p>
                <p className="mt-0.5 font-mono text-xs uppercase tracking-eyebrow text-ink-tertiary">{f.role}</p>
              </figcaption>
            </figure>
          ))}
        </div>
      </section>

      {/* ── Testimonials ────────────────────────────────────────── */}
      <section className="border-y border-border dark:border-white/5 bg-surface dark:bg-night-500/40">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <div className="max-w-2xl mb-12 sm:mb-16">
            <p className="eyebrow mb-4">No. 05 — What our students say</p>
            <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
              Outcomes, <span className="highlight-coral">in their words</span>.
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-4 sm:gap-6">
            {testimonials.map((t) => (
              <figure key={t.name} className="rounded-2xl border border-border bg-surface dark:bg-night-500 p-6 sm:p-8 flex flex-col">
                <div className="flex gap-0.5 mb-4" aria-label={`${t.stars} out of 5 stars`}>
                  {Array.from({ length: t.stars }).map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-amber-400 text-amber-400" aria-hidden="true" />
                  ))}
                </div>
                <blockquote className="text-sm text-ink-secondary leading-relaxed flex-1">
                  “{t.text}”
                </blockquote>
                <figcaption className="mt-6 pt-5 border-t border-border dark:border-white/5">
                  <p className="font-display font-semibold text-ink">{t.name}</p>
                  <p className="mt-0.5 font-mono text-xs uppercase tracking-eyebrow text-ink-tertiary">{t.role}</p>
                </figcaption>
              </figure>
            ))}
          </div>
        </div>
      </section>

      {/* ── Events / On the calendar ────────────────────────────── */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div className="grid lg:grid-cols-[1fr_2fr] gap-10 lg:gap-16">
          <div>
            <p className="eyebrow mb-4">No. 06 — On the calendar</p>
            <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
              Live cohorts &amp; <em className="italic text-coral-600 dark:text-coral-400">events</em>.
            </h2>
            <p className="mt-4 text-ink-secondary leading-relaxed">
              Small, capped cohorts with fixed start dates — the same calibre of teaching
              and accountability as a great classroom, online.
            </p>
          </div>
          <div className="divide-y divide-border dark:divide-white/5 border-y border-border dark:border-white/5">
            {events.map((ev) => (
              <div key={ev.title} className="flex items-center gap-5 py-5">
                <span className="font-mono text-xs sm:text-sm tracking-eyebrow text-coral-500 w-16 flex-shrink-0">
                  {ev.date}
                </span>
                <span className="flex-1 text-sm sm:text-base font-medium text-ink">{ev.title}</span>
                <span className="font-mono text-2xs uppercase tracking-eyebrow text-ink-tertiary border border-border dark:border-white/10 rounded-full px-3 py-1 flex-shrink-0">
                  {ev.tag}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ─────────────────────────────────────────────────── */}
      <section className="border-t border-border dark:border-white/5 bg-surface dark:bg-night-500/40">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
          <p className="eyebrow mb-4 text-center">No. 07 — Frequently asked</p>
          <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight text-center mb-12 sm:mb-16">
            Questions, answered.
          </h2>
          <div className="space-y-3">
            {faqs.map((faq, i) => {
              const isOpen = openFaq === i;
              return (
                <div key={faq.q} className="rounded-2xl border border-border bg-surface dark:bg-night-500">
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
        <div className="rounded-3xl border border-border bg-ink dark:bg-night-500 dark:border-white/5 px-6 py-14 sm:py-20 text-center relative overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-coral-500/60 to-transparent" aria-hidden="true" />
          <p className="eyebrow mb-5 justify-center text-coral-400">No. 08 — Begin</p>
          <h2 className="font-display text-3xl sm:text-5xl font-semibold tracking-tight text-paper-50 dark:text-ink">
            Your first lesson is <em className="italic text-coral-400">free</em>.
          </h2>
          <p className="mt-4 text-base sm:text-lg text-paper-50/70 dark:text-ink-secondary max-w-xl mx-auto">
            Join thousands of learners already building their future with DSir Academy.
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
              <Link href="/courses" className="hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Courses</Link>
              <Link href="/practice" className="hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Practice</Link>
              <Link href="/login" className="hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Sign In</Link>
              <Link href="/signup" className="hover:text-coral-600 dark:hover:text-coral-400 transition-colors">Sign Up</Link>
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
