import Image from "next/image";
import Link from "next/link";
import { Sparkles } from "lucide-react";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      <div className="flex w-full flex-col justify-center px-6 py-12 sm:px-12 lg:w-1/2 lg:px-16 xl:px-24">
        <Link href="/" className="mb-12 flex items-center gap-2 text-2xl font-bold text-primary">
          <Sparkles className="h-6 w-6" />
          DSir
        </Link>
        <div className="mx-auto w-full max-w-md">{children}</div>
      </div>
      <div className="relative hidden w-1/2 overflow-hidden bg-slate-900 lg:block">
        <Image
          src="https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=1200&auto=format&fit=crop"
          alt="Learning"
          fill
          className="object-cover opacity-60"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-primary/80 to-indigo-900/80" />
        <div className="absolute bottom-16 left-16 right-16 text-white">
          <blockquote className="text-2xl font-semibold leading-relaxed">
            “The best investment you can make is in yourself. DSir helps you learn to build, ship, and grow.”
          </blockquote>
          <p className="mt-4 text-white/80">Start your journey today.</p>
        </div>
      </div>
    </div>
  );
}
