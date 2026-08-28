import type { Config } from "tailwindcss";

// ─────────────────────────────────────────────────────────────────────────────
// DSir Academy — editorial design tokens
//
// Single source of truth for the design language. The `surface`, `ink` and
// `border` families are theme-aware: they resolve to CSS variables defined in
// globals.css, so the SAME class names automatically render the warm paper
// palette in light mode and the calm deep-navy palette in dark mode.
//
// Light reference (from the DSir Academy landing):
//   paper #F4EFE6 · paper-light #FBF7EE · paper-dark #E8DEC9
//   ink #0B1729 (deep navy) · muted #6E6A60 · coral #FF5C39
//
// Dark mode (default): deep near-black navy derived from ink, warm
// paper-tinted text, coral used sparingly as the single accent.
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
        // Night ramp — calm deep-navy dark surfaces (never pure black).
        // Matches the static landing page dark palette for seamless flow.
        night: {
          100: "#e4e9f2", // primary text on dark — matches dm-text
          200: "#96a3bd", // secondary text — matches dm-text-muted
          300: "#232d42", // elevated / hover surface — matches dm-surface3
          400: "#1a2236", // card surface — matches dm-surface2
          500: "#111827", // secondary surface — matches dm-surface
          600: "#080d18", // page background — matches dm-bg
          700: "#060b14", // deeper wells / footer
          800: "#040810", // deepest
        },
        // Coral — the single accent, used sparingly. Derived from #FF5C39.
        coral: {
          50: "#FFF3EF",
          100: "#FFE3DA",
          200: "#FFC8B8",
          300: "#FFA68C",
          400: "#FF7E5C",
          500: "#FF5C39", // signature accent
          600: "#ED4A27",
          700: "#C0391B", // AA-safe coral for text on paper (light mode)
          800: "#9E2F16",
          900: "#7C2411",
          950: "#47130A",
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
        "4xl": "2rem",
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
