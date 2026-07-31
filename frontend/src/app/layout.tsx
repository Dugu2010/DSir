import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/lib/providers";
import { AuthProvider } from "@/lib/auth";
import { AppShell } from "@/components/layout/AppShell";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
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
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`} suppressHydrationWarning>
      <body className="font-sans antialiased">
        <Providers>
          <AuthProvider>
            <AppShell>{children}</AppShell>
          </AuthProvider>
        </Providers>
      </body>
    </html>
  );
}
