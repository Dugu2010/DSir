"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { ArrowRight, BookOpen, Code2, Brain, Briefcase } from "lucide-react";

interface ProgramsSectionProps {
  programs: Array<{
    number: string;
    title: string;
    desc: string;
    meta: string;
    icon: React.ElementType;
  }>;
}

export default function ProgramsSection({ programs }: ProgramsSectionProps) {
  return (
    <section className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
      <div className="lg:grid-cols-[1fr_2fr] gap-10 lg:gap-16">
        <div className="lg:sticky lg:top-24 lg:self-start">
          <p className="eyebrow mb-4">No. 02 — Our popular programs</p>
          <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
            A focused path, <em className="italic text-coral-600 dark:text-coral-400">not</em> an infinite library.
          </h2>
          <p className="mt-4 text-ink-secondary leading-relaxed">
            Every program is a finite sequence of modules, lessons and exercises designed
            by engineers — with a clear start, middle, and end.
          </p>
          <Link href="/courses" className="inline-block mt-6">
            <Button variant="outline" rightIcon={<ArrowRight className="h-4 w-4" />}>
              Explore the full catalog
            </Button>
          </Link>
        </div>

        <div className="grid sm:grid-cols-2 gap-4">
          {programs.map((p) => {
            const Icon = p.icon;
            return (
              <div
                key={p.number}
                className="rounded-2xl border border-border bg-surface dark:bg-night-500 p-6 hover:border-coral-400/60 dark:hover:border-coral-500/40 transition-colors"
              >
                <div className="flex items-center justify-between mb-5">
                  {Icon && (
                    <Icon className="h-6 w-6 text-coral-500" aria-hidden="true" />
                  )}
                  <span className="font-mono text-xs tracking-eyebrow text-ink-tertiary">No. {p.number}</span>
                </div>
                <h3 className="font-display text-xl font-semibold text-ink">{p.title}</h3>
                <p className="mt-2 text-sm text-ink-secondary leading-relaxed">{p.desc}</p>
                <p className="mt-4 font-mono text-xs uppercase tracking-eyebrow text-ink-tertiary">{p.meta}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}