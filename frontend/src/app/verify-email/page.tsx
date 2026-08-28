"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { auth } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { GraduationCap, CheckCircle2, XCircle, Loader2 } from "lucide-react";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token") || "";
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading");
  const [message, setMessage] = useState("");

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing verification token.");
      return;
    }
    auth
      .verifyEmail(token)
      .then(() => setStatus("success"))
      .catch((e: any) => {
        setStatus("error");
        setMessage(e?.detail || "Verification failed. The link may have expired.");
      });
  }, [token]);

  return (
    <div className="min-h-screen bg-surface-secondary dark:bg-night-600 flex items-center justify-center px-4 py-12 transition-colors">
      <div className="w-full max-w-md text-center">
        <Link href="/" className="inline-flex items-center gap-2.5 mb-8">
          <div className="h-8 w-8 rounded-lg bg-ink dark:bg-paper-50 border border-border dark:border-white/10 flex items-center justify-center">
            <GraduationCap className="h-4 w-4 text-coral-500" />
          </div>
          <span className="font-display font-bold text-xl text-ink">
            DSir <span className="font-mono text-[10px] uppercase tracking-eyebrow text-coral-500 align-middle ml-0.5">Academy</span>
          </span>
        </Link>

        <div className="rounded-3xl border border-border dark:border-white/5 bg-surface dark:bg-night-500 p-8">
          {status === "loading" && (
            <>
              <Loader2 className="h-8 w-8 animate-spin text-coral-500 mx-auto" />
              <p className="text-sm text-ink-secondary mt-4">Verifying your email...</p>
            </>
          )}
          {status === "success" && (
            <>
              <div className="h-14 w-14 rounded-2xl bg-emerald-50 dark:bg-emerald-500/10 flex items-center justify-center mx-auto mb-4">
                <CheckCircle2 className="h-7 w-7 text-emerald-500" />
              </div>
              <h1 className="font-display text-2xl font-semibold text-ink">Email verified!</h1>
              <p className="text-sm text-ink-secondary mt-2">Your account is now fully activated.</p>
              <Link href="/dashboard" className="block mt-6">
                <Button className="w-full">Go to dashboard</Button>
              </Link>
            </>
          )}
          {status === "error" && (
            <>
              <div className="h-14 w-14 rounded-2xl bg-red-50 dark:bg-red-500/10 flex items-center justify-center mx-auto mb-4">
                <XCircle className="h-7 w-7 text-red-500" />
              </div>
              <h1 className="font-display text-2xl font-semibold text-ink">Verification failed</h1>
              <p className="text-sm text-ink-secondary mt-2">{message}</p>
              <Link href="/login" className="block mt-6">
                <Button variant="outline" className="w-full">Back to sign in</Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
