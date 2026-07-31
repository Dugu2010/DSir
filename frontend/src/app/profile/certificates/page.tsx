'use client';

import { useQuery } from '@tanstack/react-query';
import { AppShell } from '@/components/layout/AppShell';
import { Card, Badge } from '@/components/ui';
import { Award, Download, ExternalLink, BookOpen } from 'lucide-react';
import { formatDate } from '@/lib/utils';

export default function CertificatesPage() {
  return (
    <AppShell>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold text-ink">Certificates</h1>
          <p className="mt-1 text-ink-secondary">Your earned certificates and achievements</p>
        </div>

        <div className="text-center py-16">
          <div className="h-20 w-20 rounded-2xl bg-brand-50 dark:bg-brand-950/50 flex items-center justify-center mx-auto mb-6">
            <Award className="h-10 w-10 text-brand-600" />
          </div>
          <h2 className="text-lg font-semibold text-ink mb-2">No certificates yet</h2>
          <p className="text-ink-secondary mb-6 max-w-sm mx-auto">
            Complete a course to earn your first certificate. Each certificate validates your skills and can be shared on your professional profiles.
          </p>
          <a href="/courses" className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-brand-600 text-white text-sm font-medium hover:bg-brand-700 transition-colors">
            <BookOpen className="h-4 w-4" /> Browse Courses
          </a>
        </div>
      </div>
    </AppShell>
  );
}
