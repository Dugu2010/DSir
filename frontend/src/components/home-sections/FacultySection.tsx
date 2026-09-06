"use client";

import { Quote } from "lucide-react";

interface FacultySectionProps {
  faculty: Array<{
    name: string;
    role: string;
    quote: string;
  }>;
}

export default function FacultySection({ faculty }: FacultySectionProps) {
  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
      <div className="max-w-2xl mb-12 sm:mb-16">
        <p className="eyebrow mb-4">No. 04 — Faculty</p>
        <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
          Built by people who <em className="italic text-coral-600 dark:text-coral-400">build</em>.
        </h2>
      </div>
      <div className="grid md:grid-cols-3 gap-4 sm:gap-6">
        {faculty.map((f) => (
          <figure
            key={f.name}
            className="rounded-2xl border border-border bg-surface dark:bg-night-500 p-6 sm:p-8"
          >
            <Quote className="h-6 w-6 text-coral-500 mb-5" aria-hidden="true" />
            <blockquote className="text-sm sm:text-base text-ink-secondary leading-relaxed">
              “{f.quote}”
            </blockquote>
            <figcaption className="mt-6 pt-5 border-t border-border dark:border-white/5">
              <p className="font-display font-semibold text-ink">{f.name}</p>
              <p className="mt-0.5 font-mono text-xs uppercase tracking-eyebrow text-ink-tertiary">{f.role}</p>
            </figcaption>
          </figure>
        ))}
      </div>
    </section>
  );
}