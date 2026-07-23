import Link from "next/link";
import {
  ArrowRight,
  BookOpen,
  BrainCircuit,
  CheckCircle2,
  Flame,
  Layers,
  Rocket,
  Sparkles,
  Trophy,
  Users,
} from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="sticky top-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <Link href="/" className="flex items-center gap-2 text-xl font-bold text-primary">
            <Sparkles className="h-5 w-5" />
            DSir
          </Link>
          <nav className="hidden items-center gap-8 md:flex">
            <Link href="/courses" className="text-sm font-medium text-muted-foreground hover:text-foreground">
              Courses
            </Link>
            <Link href="/roadmaps" className="text-sm font-medium text-muted-foreground hover:text-foreground">
              Roadmaps
            </Link>
            <Link href="/login" className="text-sm font-medium text-muted-foreground hover:text-foreground">
              Sign in
            </Link>
          </nav>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="hidden rounded-lg px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground md:block"
            >
              Sign in
            </Link>
            <Link
              href="/register"
              className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground transition hover:bg-primary/90"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="relative overflow-hidden px-6 pt-24 pb-20 sm:pt-32 sm:pb-24">
        <div className="absolute inset-0 -z-10 bg-dots" />
        <div className="mx-auto max-w-5xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
            <Sparkles className="h-4 w-4" />
            <span>AI-powered programming education</span>
          </div>
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            Master programming with an
            <span className="block bg-gradient-to-r from-primary to-indigo-500 bg-clip-text text-transparent">
              AI personal mentor
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted-foreground">
            DSir combines structured courses, hands-on projects, and intelligent revision to help you become a world-class engineer.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-xl bg-primary px-6 py-3 text-base font-semibold text-primary-foreground transition hover:bg-primary/90"
            >
              Start learning free <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/courses"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-card px-6 py-3 text-base font-semibold text-card-foreground transition hover:bg-accent"
            >
              Browse courses
            </Link>
          </div>
          <div className="mt-10 flex items-center justify-center gap-6 text-sm text-muted-foreground">
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              <span>Free to start</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              <span>Real projects</span>
            </div>
            <div className="flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4 text-emerald-500" />
              <span>AI mentorship</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-y border-border bg-card px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <div className="mb-12 text-center">
            <h2 className="text-3xl font-bold tracking-tight">Everything you need to level up</h2>
            <p className="mt-3 text-muted-foreground">A complete platform for learning, building, and remembering.</p>
          </div>
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <FeatureCard
              icon={<BookOpen className="h-6 w-6 text-primary" />}
              title="Curated Courses"
              description="Structured lessons across Python, JavaScript, React, FastAPI, SQL, and more."
            />
            <FeatureCard
              icon={<BrainCircuit className="h-6 w-6 text-primary" />}
              title="AI Mentor"
              description="Get instant explanations, code review, and hints whenever you get stuck."
            />
            <FeatureCard
              icon={<Flame className="h-6 w-6 text-primary" />}
              title="Streaks & XP"
              description="Stay motivated with daily streaks, XP, and achievements."
            />
            <FeatureCard
              icon={<Layers className="h-6 w-6 text-primary" />}
              title="Smart Revision"
              description="Never forget what you learned with spaced-repetition review sessions."
            />
          </div>
        </div>
      </section>

      {/* Stats / Social proof */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
            <StatCard icon={<BookOpen className="h-6 w-6" />} value="16+" label="Courses" />
            <StatCard icon={<Trophy className="h-6 w-6" />} value="100+" label="Lessons" />
            <StatCard icon={<Users className="h-6 w-6" />} value="AI" label="Mentor available 24/7" />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-20">
        <div className="mx-auto max-w-5xl rounded-3xl bg-gradient-to-br from-primary to-indigo-600 px-6 py-16 text-center text-white">
          <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/20 px-3 py-1 text-sm font-medium">
            <Rocket className="h-4 w-4" />
            <span>Ready to launch your career?</span>
          </div>
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Start learning today</h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-white/90">
            Join DSir and get access to premium courses, AI mentorship, and a personalized learning path.
          </p>
          <div className="mt-8 flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link
              href="/register"
              className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 text-base font-semibold text-primary transition hover:bg-white/90"
            >
              Create free account <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/courses"
              className="inline-flex items-center gap-2 rounded-xl border border-white/30 px-6 py-3 text-base font-semibold text-white transition hover:bg-white/10"
            >
              Explore courses
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border px-6 py-12">
        <div className="mx-auto max-w-7xl">
          <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
            <div className="flex items-center gap-2 text-xl font-bold text-primary">
              <Sparkles className="h-5 w-5" />
              DSir
            </div>
            <p className="text-sm text-muted-foreground">
              © {new Date().getFullYear()} DSir. Built for learners who want to ship.
            </p>
            <div className="flex gap-6">
              <Link href="/courses" className="text-sm text-muted-foreground hover:text-foreground">
                Courses
              </Link>
              <Link href="/roadmaps" className="text-sm text-muted-foreground hover:text-foreground">
                Roadmaps
              </Link>
              <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground">
                Sign in
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-background p-6 transition hover:-translate-y-1 hover:shadow-md">
      <div className="mb-4 w-fit rounded-xl bg-primary/10 p-3">{icon}</div>
      <h3 className="text-lg font-semibold">{title}</h3>
      <p className="mt-2 text-sm text-muted-foreground">{description}</p>
    </div>
  );
}

function StatCard({ icon, value, label }: { icon: React.ReactNode; value: string; label: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6 text-center transition hover:shadow-md">
      <div className="mb-3 inline-flex rounded-full bg-primary/10 p-3 text-primary">{icon}</div>
      <p className="text-3xl font-bold">{value}</p>
      <p className="text-sm text-muted-foreground">{label}</p>
    </div>
  );
}
