"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Card, Badge } from "@/components/ui";
import { users } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { PageLoader, ErrorState } from "@/components/ui/States";
import { Award, Download, ExternalLink, BookOpen, ShieldCheck } from "lucide-react";
import { formatDate } from "@/lib/utils";
import type { Certificate } from "@/lib/types";
import toast from "react-hot-toast";

export default function CertificatesPage() {
  const { user } = useAuth();

  const { data: certificates, isLoading, error, refetch } = useQuery({
    queryKey: ["certificates"],
    queryFn: () => users.getCertificates(),
    enabled: !!user,
  });

  const handleDownload = (cert: Certificate) => {
    const html = buildCertificateHtml(cert, user?.display_name || "Student");
    const blob = new Blob([html], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `DSir-Certificate-${cert.course_slug}.html`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success("Certificate downloaded");
  };

  if (isLoading) return <PageLoader />;
  if (error) {
    return (
      <ErrorState
        title="Failed to load certificates"
        description="Could not connect to the server. Check your connection and try again."
        onRetry={() => refetch()}
      />
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <p className="eyebrow mb-2">Credentials</p>
        <h1 className="font-display text-2xl sm:text-3xl font-semibold tracking-tight text-ink">Certificates</h1>
        <p className="mt-1 text-ink-secondary">Your earned certificates and achievements</p>
      </div>

      {certificates && certificates.length > 0 ? (
        <div className="space-y-4">
          {certificates.map((cert) => (
            <Card key={cert.id} padding="md" className="flex flex-col sm:flex-row sm:items-center gap-4">
              <div className="h-14 w-14 rounded-2xl bg-coral-50 dark:bg-coral-500/10 flex items-center justify-center flex-shrink-0 border border-coral-200 dark:border-coral-500/20">
                <Award className="h-7 w-7 text-coral-600 dark:text-coral-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h2 className="font-display font-semibold text-ink">{cert.course_title}</h2>
                  <Badge size="sm" variant="success">Verified</Badge>
                </div>
                <p className="text-sm text-ink-secondary mt-0.5">
                  Issued {formatDate(cert.issued_at)}
                </p>
                <p className="text-xs text-ink-tertiary mt-1 font-mono">{cert.certificate_number}</p>
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={() => handleDownload(cert)}
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-coral-500 text-night-600 text-sm font-semibold hover:bg-coral-400 transition-colors"
                >
                  <Download className="h-4 w-4" /> Download
                </button>
                <Link
                  href={`/courses/${cert.course_slug}`}
                  className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg border border-border dark:border-white/10 text-ink-secondary hover:text-ink hover:border-coral-400/50 transition-colors text-sm font-medium"
                >
                  <ExternalLink className="h-4 w-4" /> Course
                </Link>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="text-center py-16">
          <div className="h-20 w-20 rounded-2xl bg-coral-50 dark:bg-coral-500/10 flex items-center justify-center mx-auto mb-6 border border-coral-200 dark:border-coral-500/20">
            <Award className="h-10 w-10 text-coral-600 dark:text-coral-400" />
          </div>
          <h2 className="font-display text-lg font-semibold text-ink mb-2">No certificates yet</h2>
          <p className="text-ink-secondary mb-6 max-w-sm mx-auto">
            Complete a course to earn your first certificate. Each certificate validates your skills and can be shared on your professional profiles.
          </p>
          <Link href="/courses" className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-coral-500 text-night-600 text-sm font-semibold hover:bg-coral-400 transition-colors">
            <BookOpen className="h-4 w-4" /> Browse Courses
          </Link>
        </div>
      )}
    </div>
  );
}

// Build a self-contained, printable certificate as an HTML document.
function buildCertificateHtml(cert: Certificate, studentName: string): string {
  const date = formatDate(cert.issued_at);
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Certificate — ${escapeHtml(cert.course_title)}</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    font-family: Georgia, 'Times New Roman', serif;
    background: #f4f1ea;
    display: flex; align-items: center; justify-content: center;
    min-height: 100vh; padding: 24px;
  }
  .certificate {
    width: 100%; max-width: 800px; background: #fffdf8;
    border: 2px solid #d9c9a3; border-radius: 12px; padding: 56px 48px;
    text-align: center; position: relative; box-shadow: 0 10px 40px rgba(0,0,0,.08);
  }
  .certificate::before {
    content: ""; position: absolute; inset: 12px;
    border: 1px solid #e6d9b8; border-radius: 8px; pointer-events: none;
  }
  .brand { font-size: 14px; letter-spacing: 4px; text-transform: uppercase; color: #b28a4c; font-family: Arial, sans-serif; }
  .logo { font-size: 28px; color: #ff5c39; font-weight: bold; margin-bottom: 8px; }
  h1 { font-size: 40px; font-weight: normal; color: #1f2937; margin: 16px 0 8px; }
  .name { font-size: 28px; font-style: italic; color: #374151; margin: 16px 0; }
  .body { font-size: 16px; color: #4b5563; line-height: 1.6; max-width: 560px; margin: 0 auto; }
  .course { font-size: 22px; font-weight: bold; color: #111827; margin: 20px 0 4px; }
  .meta { display: flex; justify-content: space-between; margin-top: 40px; font-family: Arial, sans-serif; font-size: 12px; color: #6b7280; }
  .number { font-family: monospace; letter-spacing: 1px; }
  .seal {
    position: absolute; right: 48px; top: 48px; width: 72px; height: 72px;
    border: 3px solid #ff5c39; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    color: #ff5c39; font-size: 11px; font-weight: bold; text-transform: uppercase;
    transform: rotate(-12deg); font-family: Arial, sans-serif;
  }
  @media print { body { background: #fff; } .certificate { box-shadow: none; } }
</style>
</head>
<body>
  <div class="certificate">
    <div class="seal">DSir<br/>Academy</div>
    <div class="logo">DSir Academy</div>
    <div class="brand">Certificate of Completion</div>
    <h1>This certifies that</h1>
    <div class="name">${escapeHtml(studentName)}</div>
    <div class="body">has successfully completed the course and demonstrated proficiency in its curriculum and assessments.</div>
    <div class="course">${escapeHtml(cert.course_title)}</div>
    <div class="meta">
      <span>Issued: ${escapeHtml(date)}</span>
      <span class="number">${escapeHtml(cert.certificate_number)}</span>
    </div>
  </div>
</body>
</html>`;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
