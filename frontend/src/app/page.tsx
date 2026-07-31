"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { useTheme } from "@/lib/theme";
import {
  GraduationCap, Code2, Brain, Sparkles, Trophy,
  BookOpen, ArrowRight, Star, Users, Zap, CheckCircle2,
  Globe, Shield, BarChart3, Sun, Moon, Menu, X,
} from "lucide-react";
import { useState } from "react";

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
  const { resolvedTheme, toggleTheme } = useTheme();
  const [mobileMenu, setMobileMenu] = useState(false);

  return (
    <div className="min-h-screen bg-[#fafbff] dark:bg-[#0a0a0f] transition-colors duration-200">
      {/* Nav */}
      <nav className="sticky top-0 z-50 bg-white/80 dark:bg-[#0a0a0f]/80 backdrop-blur-xl border-b border-[#e8ecf1] dark:border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-sm shadow-brand-500/20">
              <GraduationCap className="h-4.5 w-4.5 text-white" />
            </div>
            <span className="font-bold text-xl text-[#1a1d2e] dark:text-white">DSir</span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden sm:flex items-center gap-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3] transition-colors"
              title={resolvedTheme === "dark" ? "Light mode" : "Dark mode"}
            >
              {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <Link href="/login">
              <Button variant="ghost" size="sm">Sign In</Button>
            </Link>
            <Link href="/signup">
              <Button size="sm">Get Started Free</Button>
            </Link>
          </div>

          {/* Mobile menu button */}
          <div className="flex sm:hidden items-center gap-1">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5 text-[#6b7280] dark:text-[#8b8fa3]"
            >
              {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <button
              onClick={() => setMobileMenu(!mobileMenu)}
              className="p-2 rounded-lg hover:bg-[#f1f3f5] dark:hover:bg-white/5"
            >
              {mobileMenu ? <X className="h-5 w-5 text-[#1a1d2e] dark:text-white" /> : <Menu className="h-5 w-5 text-[#1a1d2e] dark:text-white" />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileMenu && (
          <div className="sm:hidden border-t border-[#e8ecf1] dark:border-white/5 bg-white dark:bg-[#0a0a0f] p-4 space-y-3 animate-slide-down">
            <Link href="/login" className="block w-full" onClick={() => setMobileMenu(false)}>
              <Button variant="ghost" size="sm" className="w-full justify-center">Sign In</Button>
            </Link>
            <Link href="/signup" className="block w-full" onClick={() => setMobileMenu(false)}>
              <Button size="sm" className="w-full justify-center">Get Started Free</Button>
            </Link>
          </div>
        )}
      </nav>

      {/* Hero */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 sm:pt-20 pb-20 sm:pb-24 text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-brand-50 dark:bg-brand-500/10 text-brand-700 dark:text-brand-400 text-sm font-medium mb-6 sm:mb-8 animate-fade-in">
          <Sparkles className="h-4 w-4" />
          AI-Powered Learning Platform
        </div>
        <h1 className="text-4xl sm:text-5xl lg:text-7xl font-bold text-[#1a1d2e] dark:text-white tracking-tight leading-tight">
          Learn to code.{" "}
          <span className="text-brand-600 dark:text-brand-400">Get job-ready.</span>
        </h1>
        <p className="mt-4 sm:mt-6 text-base sm:text-xl text-[#6b7280] dark:text-[#8b8fa3] max-w-3xl mx-auto leading-relaxed">
          The world&apos;s best AI-powered programming education platform. From absolute beginner to
          professional software engineer — with interactive lessons, smart revision, and 24/7 AI tutoring.
        </p>
        <div className="mt-8 sm:mt-10 flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4">
          <Link href="/signup" className="w-full sm:w-auto">
            <Button size="xl" rightIcon={<ArrowRight className="h-5 w-5" />} className="w-full sm:w-auto">
              Start Learning Free
            </Button>
          </Link>
          <Link href="/courses" className="w-full sm:w-auto">
            <Button variant="secondary" size="xl" className="w-full sm:w-auto">
              Browse Courses
            </Button>
          </Link>
        </div>
        <div className="mt-6 flex items-center justify-center gap-1 text-sm text-[#9ca3af] dark:text-[#6b7280]">
          <CheckCircle2 className="h-4 w-4 text-emerald-500" />
          No credit card required • Free courses available
        </div>
      </section>

      {/* Stats */}
      <section className="border-y border-[#e8ecf1] dark:border-white/5 bg-[#f8fafc] dark:bg-white/[0.02]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 sm:py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 sm:gap-8">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-2xl sm:text-3xl font-bold text-[#1a1d2e] dark:text-white">{stat.value}</div>
                <div className="text-xs sm:text-sm text-[#9ca3af] dark:text-[#6b7280] mt-1">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="text-center mb-12 sm:mb-16">
          <h2 className="text-2xl sm:text-4xl font-bold text-[#1a1d2e] dark:text-white">
            Everything you need to succeed
          </h2>
          <p className="mt-4 text-base sm:text-lg text-[#6b7280] dark:text-[#8b8fa3] max-w-2xl mx-auto">
            A complete learning ecosystem designed to take you from zero to professional.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {features.map((feature, i) => (
            <div
              key={feature.title}
              className="rounded-2xl border border-[#e8ecf1] dark:border-white/5 bg-white dark:bg-[#0d0d13] p-5 sm:p-6 hover:shadow-lg hover:shadow-brand-500/5 hover:border-brand-200 dark:hover:border-brand-500/20 transition-all duration-200 group"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <div className="h-10 w-10 sm:h-12 sm:w-12 rounded-xl bg-brand-50 dark:bg-brand-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <feature.icon className="h-5 w-5 sm:h-6 sm:w-6 text-brand-600 dark:text-brand-400" />
              </div>
              <h3 className="text-base sm:text-lg font-semibold text-[#1a1d2e] dark:text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-[#6b7280] dark:text-[#8b8fa3] leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Technologies */}
      <section className="border-t border-[#e8ecf1] dark:border-white/5 bg-[#f8fafc] dark:bg-white/[0.02] py-12 sm:py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-base sm:text-lg font-semibold text-[#1a1d2e] dark:text-white mb-6 sm:mb-8">
            Master in-demand technologies
          </h3>
          <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-3">
            {technologies.map((tech) => (
              <span
                key={tech}
                className="px-3 sm:px-4 py-2 rounded-xl bg-white dark:bg-[#0d0d13] border border-[#e8ecf1] dark:border-white/5 text-xs sm:text-sm font-medium text-[#6b7280] dark:text-[#8b8fa3] hover:text-[#1a1d2e] dark:hover:text-white hover:border-brand-200 dark:hover:border-brand-500/20 transition-all cursor-default"
              >
                {tech}
              </span>
            ))}
          </div>
          <p className="mt-6 text-xs sm:text-sm text-[#9ca3af] dark:text-[#6b7280]">...and 30+ more technologies with new courses added regularly</p>
        </div>
      </section>

      {/* CTA */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
        <div className="rounded-3xl bg-gradient-to-br from-brand-600 to-brand-800 p-8 sm:p-12 md:p-16 text-center relative overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,_var(--tw-gradient-stops))] from-white/10 via-transparent to-transparent" />
          <div className="relative">
            <h2 className="text-2xl sm:text-4xl font-bold text-white">
              Ready to start your journey?
            </h2>
            <p className="mt-4 text-base sm:text-lg text-white/80 max-w-2xl mx-auto">
              Join thousands of learners already building their future with DSir.
            </p>
            <div className="mt-8">
              <Link href="/signup">
                <Button
                  size="xl"
                  className="bg-white text-brand-700 hover:bg-white/90 shadow-lg shadow-brand-900/20"
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
      <footer className="border-t border-[#e8ecf1] dark:border-white/5 py-8 sm:py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <GraduationCap className="h-5 w-5 text-brand-600 dark:text-brand-400" />
              <span className="font-bold text-[#1a1d2e] dark:text-white">DSir</span>
            </div>
            <p className="text-sm text-[#9ca3af] dark:text-[#6b7280]">
              © 2024 DSir. Built for learners everywhere.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
