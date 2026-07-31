"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap, Mail, Lock, User, ArrowRight, AlertCircle } from "lucide-react";

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
    <div className="min-h-screen flex">
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Link href="/" className="inline-flex items-center gap-2 mb-10">
            <div className="h-8 w-8 rounded-xl bg-brand-600 flex items-center justify-center">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl text-ink">DSir</span>
          </Link>

          <h1 className="text-3xl font-bold text-ink">Create your account</h1>
          <p className="mt-2 text-ink-secondary">Start your journey to becoming a software engineer.</p>

          {error && (
            <div className="mt-6 p-4 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
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
              Create Account
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-secondary">
            Already have an account?{" "}
            <Link href="/login" className="text-brand-600 hover:underline font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>

      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-brand-600 to-brand-800 items-center justify-center p-12">
        <div className="text-center text-white">
          <h2 className="text-3xl font-bold mb-4">Why DSir?</h2>
          <div className="space-y-4 text-left mt-8">
            {[
              "Interactive lessons with real code execution",
              "AI tutor available 24/7 to help you learn",
              "Practice engine with 2000+ exercises",
              "Smart revision to retain what you learn",
              "Job-ready curriculum designed by experts",
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-3">
                <div className="h-2 w-2 rounded-full bg-white/60 mt-0.5 flex-shrink-0" />
                <span className="text-white/90">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
