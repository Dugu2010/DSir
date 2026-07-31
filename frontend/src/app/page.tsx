"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";
import {
  GraduationCap, Code2, Brain, Sparkles, Trophy,
  BookOpen, ArrowRight, Star, Users, Zap, CheckCircle2,
  Globe, Shield, BarChart3,
} from "lucide-react";

const features = [
  {
    icon: Code2,
    title: "Interactive Practice Engine",
    description: "Hundreds of exercises with instant feedback. Debug, refactor, and optimize real code.",
  },
  {
    icon: Brain,
    title: "Smart Revision System",
    description: "Spaced repetition ensures you remember everything. Auto-generated flashcards and knowledge graphs.",
  },
  {
    icon: Sparkles,
    title: "AI-Powered Learning",
    description: "24/7 AI tutor, code reviewer, and career advisor. Get unstuck instantly.",
  },
  {
    icon: Trophy,
    title: "Gamified Experience",
    description: "Earn XP, unlock achievements, and compete on leaderboards while you learn.",
  },
  {
    icon: Globe,
    title: "Real-World Projects",
    description: "Build portfolio-ready projects with industry-standard tools and practices.",
  },
  {
    icon: Shield,
    title: "Job-Ready Curriculum",
    description: "From zero to employed. Paths designed with industry experts for real career outcomes.",
  },
];

const stats = [
  { value: "15K+", label: "Active Learners" },
  { value: "4.8", label: "Average Rating" },
  { value: "50+", label: "Courses" },
  { value: "2K+", label: "Exercises" },
];

const technologies = [
  "Python", "JavaScript", "HTML", "CSS", "React", "TypeScript",
  "Node.js", "FastAPI", "SQL", "Docker", "Git", "AWS",
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-surface">
      {/* Nav */}
      <nav className="sticky top-0 z-50 bg-surface/80 backdrop-blur-xl border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-brand-600 flex items-center justify-center">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl text-ink">DSir</span>
          </Link>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Get Started Free</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-50 dark:bg-brand-950 text-brand-700 dark:text-brand-400 text-sm font-medium mb-8">
          <Sparkles className="h-4 w-4" />
          AI-Powered Learning Platform
        </div>
        <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-ink tracking-tight leading-tight">
          Learn to code.{" "}
          <span className="text-brand-600">Get job-ready.</span>
        </h1>
        <p className="mt-6 text-xl text-ink-secondary max-w-3xl mx-auto leading-relaxed">
          The world&apos;s best AI-powered programming education platform. From absolute beginner to
          professional software engineer — with interactive lessons, smart revision, and 24/7 AI tutoring.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/signup">
            <Button size="xl" rightIcon={<ArrowRight className="h-5 w-5" />}>
              Start Learning Free
            </Button>
          </Link>
          <Link href="/courses">
            <Button variant="secondary" size="xl">
              Browse Courses
            </Button>
          </Link>
        </div>
        <div className="mt-8 flex items-center justify-center gap-1 text-sm text-ink-tertiary">
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          No credit card required • Free courses available
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-border bg-surface-secondary/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-3xl font-bold text-ink">{stat.value}</div>
                <div className="text-sm text-ink-tertiary mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-ink">
            Everything you need to succeed
          </h2>
          <p className="mt-4 text-lg text-ink-secondary max-w-2xl mx-auto">
            A complete learning ecosystem designed to take you from zero to professional.
          </p>
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border border-border p-6 hover:shadow-lg hover:border-ink-tertiary transition-all duration-200"
            >
              <div className="h-12 w-12 rounded-xl bg-brand-50 dark:bg-brand-950 flex items-center justify-center mb-4">
                <feature.icon className="h-6 w-6 text-brand-600 dark:text-brand-400" />
              </div>
              <h3 className="text-lg font-semibold text-ink mb-2">{feature.title}</h3>
              <p className="text-sm text-ink-secondary leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Technologies */}
      <section className="border-t border-border bg-surface-secondary/30 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-lg font-semibold text-ink mb-8">
            Master in-demand technologies
          </h3>
          <div className="flex flex-wrap items-center justify-center gap-3">
            {technologies.map((tech) => (
              <span
                key={tech}
                className="px-4 py-2 rounded-xl bg-surface border border-border text-sm font-medium text-ink-secondary hover:text-ink hover:border-ink-tertiary transition-all"
              >
                {tech}
              </span>
            ))}
          </div>
          <p className="mt-6 text-sm text-ink-tertiary">...and 30+ more technologies with new courses added regularly</p>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="rounded-3xl bg-brand-600 p-12 md:p-16 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-brand-500 to-brand-700 opacity-50" />
          <div className="relative">
            <h2 className="text-3xl sm:text-4xl font-bold text-white">
              Ready to start your journey?
            </h2>
            <p className="mt-4 text-lg text-white/80 max-w-2xl mx-auto">
              Join thousands of learners already building their future with DSir.
            </p>
            <div className="mt-8">
              <Link href="/signup">
                <Button
                  size="xl"
                  className="bg-white text-brand-700 hover:bg-white/90"
                  rightIcon={<ArrowRight className="h-5 w-5" />}
                >
                  Get Started Free
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-brand-600" />
              <span className="font-bold text-ink">DSir</span>
            </div>
            <p className="text-sm text-ink-tertiary">
              © 2024 DSir. Built for learners everywhere.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
