"use client";

import { useState } from "react";
import Link from "next/link";
import { auth } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap, Mail, ArrowLeft, CheckCircle2 } from "lucide-react";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [resetLink, setResetLink] = useState<string | null>(null);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const res = await auth.forgotPassword(email);
      setSent(true);
      if (res.reset_link) setResetLink(res.reset_link);
    } catch (err: unknown) {
      const apiErr = err as { detail?: string };
      setError(apiErr?.detail || "Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600 flex items-center justify-center px-4 py-12 transition-colors">
      <div className="w-full max-w-md">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-8">
          <div className="h-8 w-8 rounded-lg bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center">
            <GraduationCap className="h-4 w-4 text-coral-500" />
          </div>
          <span className="font-display font-bold text-xl text-ink">
            DSir <span className="font-mono text-[10px] uppercase tracking-eyebrow text-coral-500 align-middle ml-0.5">Academy</span>
          </span>
        </Link>

        <div className="rounded-3xl border border-border dark:border-white/5 bg-surface dark:bg-night-500 p-8">
          {sent ? (
            <div className="text-center">
              <div className="h-14 w-14 rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="h-7 w-7 text-emerald-500" />
              </div>
              <h1 className="font-display text-2xl font-semibold text-ink">Check your inbox</h1>
              <p className="text-sm text-ink-secondary mt-2">
                If an account exists for <span className="font-medium text-ink">{email}</span>, we&apos;ve sent a password reset link.
              </p>
              {resetLink && (
                <a href={resetLink} className="block mt-4 text-sm text-coral-600 dark:text-coral-400 hover:underline break-all">
                  {resetLink}
                </a>
              )}
              <Link href="/login" className="inline-flex items-center gap-1 mt-6 text-sm text-ink-secondary hover:text-ink">
                <ArrowLeft className="h-4 w-4" /> Back to sign in
              </Link>
            </div>
          ) : (
            <>
              <p className="eyebrow mb-4">Account recovery</p>
              <h1 className="font-display text-2xl font-semibold text-ink">Forgot your password?</h1>
              <p className="text-sm text-ink-secondary mt-2">
                Enter your email and we&apos;ll send you a reset link.
              </p>
              {error && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>}
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
                <Button type="submit" className="w-full" size="lg" loading={loading}>
                  Send reset link
                </Button>
              </form>
              <Link href="/login" className="inline-flex items-center gap-1 mt-6 text-sm text-ink-secondary hover:text-ink">
                <ArrowLeft className="h-4 w-4" /> Back to sign in
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
