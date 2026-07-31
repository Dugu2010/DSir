"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap, Mail, Lock, ArrowRight, AlertCircle } from "lucide-react";

export default function LoginPage() {
  const { login } = useAuth();
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
    <div className="min-h-screen flex">
      {/* Left - Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Link href="/" className="inline-flex items-center gap-2 mb-12">
            <div className="h-8 w-8 rounded-xl bg-brand-600 flex items-center justify-center">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl text-ink">DSir</span>
          </Link>

          <h1 className="text-3xl font-bold text-ink">Welcome back</h1>
          <p className="mt-2 text-ink-secondary">Sign in to continue your learning journey.</p>

          {error && (
            <div className="mt-6 p-4 rounded-xl bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900 flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-red-600 mt-0.5 flex-shrink-0" />
              <p className="text-sm text-red-700 dark:text-red-400">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
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
              Sign In
            </Button>
          </form>

          <p className="mt-6 text-center text-sm text-ink-secondary">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-brand-600 hover:underline font-medium">
              Create one free
            </Link>
          </p>

          {/* Demo credentials */}
          <div className="mt-8 p-4 rounded-xl bg-surface-secondary border border-border">
            <p className="text-xs font-medium text-ink-tertiary mb-2">DEMO CREDENTIALS</p>
            <p className="text-xs text-ink-secondary">Email: <code className="text-brand-600">demo@dsir.dev</code></p>
            <p className="text-xs text-ink-secondary">Password: <code className="text-brand-600">Demo@123!</code></p>
          </div>
        </div>
      </div>

      {/* Right - Visual */}
      <div className="hidden lg:flex flex-1 bg-brand-600 items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-brand-500 to-brand-700" />
        <div className="relative text-center">
          <div className="text-7xl mb-6">🚀</div>
          <h2 className="text-3xl font-bold text-white mb-4">
            Master programming with AI
          </h2>
          <p className="text-lg text-white/80 max-w-md">
            Interactive lessons, smart practice, and 24/7 AI tutoring to accelerate your learning.
          </p>
        </div>
      </div>
    </div>
  );
}
