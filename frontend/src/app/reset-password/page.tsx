"use client";

import { useState } from "react";
import Link from "next/link";
import { useSearchParams, useRouter } from "next/navigation";
import { auth } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { GraduationCap, Lock, CheckCircle2 } from "lucide-react";

export default function ResetPasswordPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const token = searchParams.get("token") || "";
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }
    setLoading(true);
    try {
      await auth.resetPassword(token, password);
      setDone(true);
    } catch (err: unknown) {
      const apiErr = err as { detail?: string };
      setError(apiErr?.detail || "Reset failed. The link may have expired.");
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
          {done ? (
            <div className="text-center">
              <div className="h-14 w-14 rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="h-7 w-7 text-emerald-500" />
              </div>
              <h1 className="font-display text-2xl font-semibold text-ink">Password reset!</h1>
              <p className="text-sm text-ink-secondary mt-2">You can now sign in with your new password.</p>
              <Button className="mt-6 w-full" onClick={() => router.push("/login")}>Go to sign in</Button>
            </div>
          ) : (
            <>
              <p className="eyebrow mb-4">New password</p>
              <h1 className="font-display text-2xl font-semibold text-ink">Reset your password</h1>
              <p className="text-sm text-ink-secondary mt-2">Choose a strong new password (min 8 characters).</p>
              {error && <p className="mt-4 text-sm text-red-600 dark:text-red-400">{error}</p>}
              {!token && <p className="mt-4 text-sm text-red-600 dark:text-red-400">Missing or invalid reset token.</p>}
              <form onSubmit={handleSubmit} className="mt-6 space-y-4">
                <Input
                  label="New password"
                  type="password"
                  placeholder="Min. 8 characters"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  leftIcon={<Lock className="h-4 w-4" />}
                  required
                />
                <Input
                  label="Confirm password"
                  type="password"
                  placeholder="Repeat your new password"
                  value={confirm}
                  onChange={(e) => setConfirm(e.target.value)}
                  leftIcon={<Lock className="h-4 w-4" />}
                  required
                />
                <Button type="submit" className="w-full" size="lg" loading={loading} disabled={!token}>
                  Reset password
                </Button>
              </form>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
