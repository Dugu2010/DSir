import type { Metadata } from "next";
import { Fraunces, Plus_Jakarta_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { AuthProvider } from "@/lib/auth";
import { ThemeProvider } from "@/lib/theme";
import { AppShell } from "@/components/layout/AppShell";

// Editorial type system: Fraunces for display/headings, Plus Jakarta Sans for
// body/UI, JetBrains Mono for labels, tags and code.
const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "DSir — AI-Powered Programming Education",
  description:
    "Master programming from absolute beginner to job-ready software engineer. Interactive lessons, AI tutoring, practice engine, and real projects.",
  keywords: [
    "programming", "learn to code", "python", "javascript", "web development",
    "coding bootcamp", "online learning", "AI tutor", "DSir",
  ],
  openGraph: {
    title: "DSir — AI-Powered Programming Education",
    description: "The world's best AI-powered programming education platform.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${jakarta.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                try {
                  // DSir Academy defaults to DARK mode. First-time visitors get
                  // dark; explicit light preference is respected.
                  var t = localStorage.getItem('theme');
                  if (t === 'light') {
                    document.documentElement.classList.remove('dark');
                  } else {
                    document.documentElement.classList.add('dark');
                    if (!t) localStorage.setItem('theme', 'dark');
                  }
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body className="font-sans antialiased bg-surface-secondary text-ink transition-colors duration-300">
        <ThemeProvider>
          <Providers>
            <AuthProvider>
              <AppShell>{children}</AppShell>
            </AuthProvider>
          </Providers>
        </ThemeProvider>
      </body>
    </html>
  );
}
