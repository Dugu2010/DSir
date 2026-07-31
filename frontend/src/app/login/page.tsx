"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth } from "@/lib/auth";
import { useTheme } from "@/lib/theme";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap, Mail, Lock, ArrowRight, AlertCircle, Sun, Moon } from "lucide-react";

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
    <div className="min-h-screen flex bg-[#fafbff] dark:bg-[#0a0a0f] transition-colors duration-200">
      {/* Left - Form */}
      <div className="flex-1 flex items-center justify-center px-4 sm:px-6 lg:px-8">
        <div className="w-full max-w-md">
          <Link href="/" className="inline-flex items-center gap-2 mb-10 sm:mb-12">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-sm">
              <GraduationCap className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-xl text-[#1a1d2e] dark:text-white">DSir</span>
          </Link>

          <h1 className="text-2xl sm:text-3xl font-bold text-[#1a1d2e] dark:text-white">Welcome back</h1>
          <p className="mt-2 text-[#6b7280] dark:text-[#8b8fa3]">Sign in to continue your learning journey.</p>

          {error && (
            <div className="mt-6 p-4 rounded-xl bg-red-50 dark:bg-red-500/10 border border-red-200 dark:border-red-500/20 flex items-start gap-3 animate-slide-down">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 mt-0.5 flex-shrink-0" />
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

          <p className="mt-6 text-center text-sm text-[#6b7280] dark:text-[#8b8fa3]">
            Don&apos;t have an account?{" "}
            <Link href="/signup" className="text-brand-600 dark:text-brand-400 hover:underline font-medium">
              Create one free
            </Link>
          </p>

          {/* Demo credentials */}
          <div className="mt-6 p-4 rounded-xl bg-[#f8fafc] dark:bg-white/[0.03] border border-[#e8ecf1] dark:border-white/5">
            <p className="text-xs font-semibold text-[#9ca3af] dark:text-[#6b7280] uppercase tracking-wider mb-2">Demo Credentials</p>
            <div className="space-y-1">
              <p className="text-xs text-[#6b7280] dark:text-[#8b8fa3]">
                Email: <code className="text-brand-600 dark:text-brand-400 font-mono">demo@dsir.dev</code>
              </p>
              <p className="text-xs text-[#6b7280] dark:text-[#8b8fa3]">
                Password: <code className="text-brand-600 dark:text-brand-400 font-mono">Demo@123!</code>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Right - Visual */}
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-brand-600 to-brand-800 items-center justify-center p-12 relative overflow-hidden">
        <div className="absolute top-8 right-8">
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg bg-white/10 hover:bg-white/20 text-white/80 hover:text-white transition-colors"
          >
            {resolvedTheme === "dark" ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
          </button>
        </div>
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,_rgba(255,255,255,0.1)_0%,_transparent_50%)]" />
        <div className="relative text-center">
          <div className="text-6xl sm:text-7xl mb-6">🚀</div>
          <h2 className="text-2xl sm:text-3xl font-bold text-white mb-4">
            Master programming with AI
          </h2>
          <p className="text-base sm:text-lg text-white/80 max-w-md">
            Interactive lessons, smart practice, and 24/7 AI tutoring to accelerate your learning.
          </p>
        </div>
      </div>
    </div>
  );
}
