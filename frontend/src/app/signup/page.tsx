"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap, Mail, Lock, User, ArrowRight, AlertCircle, CheckCircle2 } from "lucide-react";

export default function SignupPage() {
  const { signup } = useAuth();
  const [form, setForm] = useState({ display_name: "", username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const update = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm({ ...form, [field]: e.target.value });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signup(form);
    } catch (err: unknown) {
      const apiErr = err as { detail?: string };
      setError(apiErr?.detail || "Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600 transition-colors duration-300">
      <div className="grid lg:grid-cols-2 min-h-screen">
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

            <p className="eyebrow mb-4">No. 01 — Begin</p>
            <h1 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">Create your account.</h1>
            <p className="mt-3 text-ink-secondary">Start your journey to becoming a software engineer.</p>

            {error && (
              <div className="mt-6 p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="mt-8 space-y-4">
              <Input
                label="Full Name"
                placeholder="Alex Chen"
                value={form.display_name}
                onChange={update("display_name")}
                leftIcon={<User className="h-4 w-4" />}
                required
              />
              <Input
                label="Username"
                placeholder="alexchen"
                value={form.username}
                onChange={update("username")}
                hint="Letters, numbers, underscores, and hyphens"
                required
              />
              <Input
                label="Email"
                type="email"
                placeholder="you@example.com"
                value={form.email}
                onChange={update("email")}
                leftIcon={<Mail className="h-4 w-4" />}
                required
              />
              <Input
                label="Password"
                type="password"
                placeholder="Min. 8 characters"
                value={form.password}
                onChange={update("password")}
                leftIcon={<Lock className="h-4 w-4" />}
                hint="At least 8 characters"
                required
              />
              <Button type="submit" className="w-full" size="lg" loading={loading}>
                Create Account <ArrowRight className="h-4 w-4" />
              </Button>
            </form>

            <p className="mt-6 text-center text-sm text-ink-secondary">
              Already have an account?{" "}
              <Link href="/login" className="text-coral-600 dark:text-coral-400 hover:underline font-medium">
                Sign in
              </Link>
            </p>
          </div>
        </div>

        <div className="hidden lg:flex relative border-l border-border dark:border-white/5 bg-ink dark:bg-night-500 items-center justify-center p-12">
          <div className="max-w-md">
            <p className="eyebrow mb-4 !text-coral-400">Why DSir?</p>
            <h2 className="font-display text-3xl font-semibold text-paper-50 dark:text-ink tracking-tight mb-8">
              A complete learning <em className="italic text-coral-400">ecosystem</em>.
            </h2>
            <div className="space-y-4">
              {[
                "Interactive lessons with real code execution",
                "AI tutor available 24/7 to help you learn",
                "Practice engine with 2,000+ exercises",
                "Smart revision to retain what you learn",
                "Job-ready curriculum designed by engineers",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-coral-500 mt-0.5 flex-shrink-0" aria-hidden="true" />
                  <span className="text-paper-50/85 dark:text-ink-secondary leading-relaxed">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
