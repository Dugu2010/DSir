"use client";

interface BeliefsSectionProps {
  beliefs: Array<{
    title: string;
    desc: string;
  }>;
}

export default function BeliefsSection({ beliefs }: BeliefsSectionProps) {
  return (
    <section className="border-y border-border dark:border-white/5 bg-surface dark:bg-night-500/40">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-28">
        <div className="max-w-2xl mb-12 sm:mb-16">
          <p className="eyebrow mb-4">No. 03 — What we believe</p>
          <h2 className="font-display text-3xl sm:text-4xl font-semibold text-ink tracking-tight">
            Four principles behind <span className="highlight-coral">every lesson</span>.
          </h2>
        </div>
        <div className="grid sm:grid-cols-2 gap-x-10 gap-y-10">
          {beliefs.map((b, i) => (
            <div key={b.title} className="flex gap-5">
              <span className="font-mono text-sm text-coral-500 pt-1">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div>
                <h3 className="font-display text-lg font-semibold text-ink">{b.title}</h3>
                <p className="mt-1.5 text-sm text-ink-secondary leading-relaxed">{b.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}