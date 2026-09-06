"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap, Mail, Lock, ArrowRight, AlertCircle, Sun, Moon, CheckCircle2 } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();
  const { resolvedTheme, toggleTheme } = useTheme();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
    } catch (err: unknown) {
      const apiErr = err as { detail?: string };
      setError(apiErr?.detail || "Login failed. Please check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600 transition-colors duration-300">
      <div className="grid lg:grid-cols-2 min-h-screen">
        {/* Left — Form */}
        <div className="flex items-center justify-center px-4 sm:px-8 py-12">
          <div className="w-full max-w-md">
            <Link href="/" className="inline-flex items-center gap-2.5 mb-10 sm:mb-14 group">
              <div className="h-8 w-8 rounded-lg bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center">
                <GraduationCap className="h-4 w-4 text-coral-500" />
              </div>
              <span className="font-display font-bold text-xl text-ink">
                DSir <span className="font-mono text-[10px] uppercase tracking-eyebrow text-coral-500 align-middle ml-0.5">Academy</span>
              </span>
            </Link>

            <p className="eyebrow mb-4">Sign in</p>
            <h1 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">Welcome back.</h1>
            <p className="mt-3 text-ink-secondary">Sign in to continue your learning journey.</p>

            {error && (
              <div className="mt-6 p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 flex items-start gap-3 animate-slide-down">
                <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-8 space-y-4">
              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                leftIcon={<Mail className="h-4 w-4" />}
                required
              />
              <Input
                label="Password"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                leftIcon={<Lock className="h-4 w-4" />}
                required
              />
              <Button type="submit" className="w-full" size="lg" loading={loading}>
                Sign In <ArrowRight className="h-4 w-4" />
              </Button>
            </form>

            <p className="mt-4 text-right text-sm">
              <Link href="/forgot-password" className="text-ink-tertiary hover:text-ink hover:underline">
                Forgot password?
              </Link>
            </p>

            <p className="mt-6 text-center text-sm text-ink-secondary">
              Don&apos;t have an account?{" "}
              <Link href="/signup" className="text-coral-600 dark:text-coral-400 hover:underline font-medium">
                Create one free
              </Link>
            </p>

            {/* Demo credentials */}
            <div className="mt-8 p-4 rounded-xl bg-surface dark:bg-night-500 border border-border dark:border-white/5">
              <p className="eyebrow mb-3 !text-[10px]">Demo credentials</p>
              <div className="space-y-1.5">
                <p className="text-xs text-ink-secondary">
                  Email: <code className="text-coral-600 dark:text-coral-400 font-mono">demo@dsir.dev</code>
                </p>
                <p className="text-xs text-ink-secondary">
                  Password: <code className="text-coral-600 dark:text-coral-400 font-mono">Demo@123!</code>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right — Visual */}
        <div className="hidden lg:flex relative border-l border-border dark:border-white/5 bg-ink dark:bg-night-500 items-center justify-center p-12 overflow-hidden">
          <button
            onClick={toggleTheme}
            className="absolute top-6 right-6 p-4 rounded-lg bg-white/5 hover:bg-white/10 text-paper-50/70 hover:text-paper-50 transition-colors"
            aria-label={resolvedTheme === "dark" ? "Switch to light mode" : "Switch to dark mode"}
          >
            {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
          <div className="max-w-md">
            <p className="eyebrow mb-4 !text-coral-400">Welcome to the Academy</p>
            <h2 className="font-display text-3xl font-semibold text-paper-50 dark:text-ink leading-snug tracking-tight">
              Master programming <em className="italic text-coral-400">with AI</em>.
            </h2>
            <p className="mt-4 text-paper-50/70 dark:text-ink-secondary leading-relaxed">
              Interactive lessons, smart practice, and 24/7 AI tutoring to accelerate your learning.
            </p>
            <ul className="mt-8 space-y-4">
              {[
                "Interactive lessons with real code execution",
                "AI tutor available 24/7 to help you learn",
                "Practice engine with 2,000+ exercises",
                "Smart revision to retain what you learn",
                "Job-ready curriculum designed by engineers",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3 text-paper-50/85 dark:text-ink-secondary">
                  <CheckCircle2 className="h-5 w-5 text-coral-500 mt-0.5 flex-shrink-0" aria-hidden="true" />
                  <span className="text-sm leading-relaxed">{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
