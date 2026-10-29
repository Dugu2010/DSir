import type { Config } from "tailwindcss";

// ─────────────────────────────────────────────────────────────────────────────
// DSir Academy — Obsidian Protocol editorial tokens
//
// Single source of truth for the design language. The `surface`, `ink` and
// `border` families are theme-aware: they resolve to CSS variables defined in
// globals.css, so the SAME class names automatically render the warm paper
// palette in light mode and the obsidian palette in dark mode.
//
// Dark (default, from the Stitch "Obsidian Protocol" spec):
//   base #0B0F17 · card #111827 · elevated #1A2234
//   borders #1F2937 / #374151 · text #F9FAFB / #9CA3AF / #6B7280
//   electric coral #F95738 · indigo #6366F1 · terminal cyan #38BDF8
//
// Light: warm paper surfaces, deep navy ink, coral darkened for AA contrast.
// ─────────────────────────────────────────────────────────────────────────────
const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Editorial paper ramp — warm cream surfaces (light mode) and the
        // paper-tinted TEXT ramp used on dark backgrounds.
        paper: {
          50: "#FBF7EE", // paper-light
          100: "#F4EFE6", // paper
          200: "#E8DEC9", // paper-dark
          300: "#D9D2C2", // deeper warm stone
        },
        // Night ramp — obsidian dark surfaces (never pure black).
        night: {
          100: "#F9FAFB", // primary text on dark
          200: "#9CA3AF", // secondary text on dark
          300: "#374151", // active border / hover chrome
          400: "#1A2234", // elevated surface
          500: "#111827", // card surface
          600: "#0B0F17", // page background
          700: "#080C13", // deeper wells / footer
          800: "#05080E", // deepest
        },
        // Electric coral — the single accent, used sparingly (#F95738).
        coral: {
          50: "#FFF2EE",
          100: "#FFE1D8",
          200: "#FFC5B6",
          300: "#FFA28B",
          400: "#FC7757",
          500: "#F95738", // signature accent
          600: "#E24428",
          700: "#B8301A", // AA-safe coral for text on paper (light mode)
          800: "#992617",
          900: "#7C1E12",
          950: "#45100A",
        },
        // Muted warm gray for secondary copy (reference #6E6A60).
        muted: {
          DEFAULT: "#6E6A60",
          dark: "#A8A6A0",
        },
        // Theme-aware surfaces (CSS variables, see globals.css)
        surface: {
          DEFAULT: "rgb(var(--surface) / <alpha-value>)",
          secondary: "rgb(var(--surface-secondary) / <alpha-value>)",
          tertiary: "rgb(var(--surface-tertiary) / <alpha-value>)",
        },
        // Theme-aware text
        ink: {
          DEFAULT: "rgb(var(--ink) / <alpha-value>)",
          secondary: "rgb(var(--ink-secondary) / <alpha-value>)",
          tertiary: "rgb(var(--ink-tertiary) / <alpha-value>)",
          inverse: "rgb(var(--ink-inverse) / <alpha-value>)",
        },
        // Theme-aware borders
        border: {
          DEFAULT: "rgb(var(--border) / <alpha-value>)",
          light: "rgb(var(--border-light) / <alpha-value>)",
        },
        // Legacy blue brand ramp — kept for compatibility, no longer the
        // primary accent (pages use coral now).
        brand: {
          50: "#eff6ff",
          100: "#dbeafe",
          200: "#bfdbfe",
          300: "#93c5fd",
          400: "#60a5fa",
          500: "#3b82f6",
          600: "#2563eb",
          700: "#1d4ed8",
          800: "#1e40af",
          900: "#1e3a8a",
          950: "#172554",
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "Plus Jakarta Sans", "system-ui", "-apple-system", "sans-serif"],
        display: ["var(--font-display)", "Fraunces", "Georgia", "serif"],
        mono: ["var(--font-mono)", "JetBrains Mono", "Fira Code", "monospace"],
      },
      fontSize: {
        "2xs": ["0.625rem", { lineHeight: "0.875rem" }],
      },
      spacing: {
        18: "4.5rem",
        88: "22rem",
        128: "32rem",
      },
      borderRadius: {
        sm: "0.125rem",
        DEFAULT: "0.25rem",
        md: "0.375rem",
        lg: "0.5rem",
        xl: "0.625rem",
        "2xl": "0.75rem",
        "3xl": "0.875rem",
        "4xl": "1rem",
        full: "9999px",
      },
      letterSpacing: {
        eyebrow: "0.22em",
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-out",
        "slide-up": "slideUp 0.3s ease-out",
        "slide-down": "slideDown 0.2s ease-out",
        "scale-in": "scaleIn 0.2s ease-out",
        "shimmer": "shimmer 2s infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        slideDown: {
          "0%": { opacity: "0", transform: "translateY(-10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        scaleIn: {
          "0%": { opacity: "0", transform: "scale(0.95)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
