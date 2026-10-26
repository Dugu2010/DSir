/** @type {import('next').NextConfig} */
const nextConfig = {
  // The repository root also contains an empty lockfile; trace the build from
  // this app directory so the standalone output does not include unrelated
  // workspace files.
  outputFileTracingRoot: __dirname,
  // Allow the sandbox preview/tunnel hostnames to hit the dev server. The
  // loopback alias is what automated browser checks use.
  allowedDevOrigins: [
    "*.e2b.app",
    "127.0.0.1",
    "pv-69474d2bd8d3-a0579d99-78d4-4167-a876-48d807a77bc3.style.dev",
  ],
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "**" },
    ],
  },
  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          // Content Security Policy — lock down to DSir resources only.
          {
            key: "Content-Security-Policy",
            value: [
              "default-src 'none'",
              "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline' 'wasm-unsafe-eval'",
              "style-src 'self' 'unsafe-inline'",
              "img-src 'self' data:",
              "connect-src 'self' http://localhost:8000 https: wss:",
              "font-src 'self'",
              "frame-src 'self' about:",
              "frame-ancestors 'none'",
              "base-uri 'none'",
              "form-action 'none'",
            ].join("; "),
          },
          // Prevent clickjacking.
          { key: "X-Frame-Options", value: "DENY" },
          // Referrer leak protection.
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          // HSTS — only on production over HTTPS.
          {
            key: "Strict-Transport-Security",
            value: "max-age=31536000; includeSubDomains; preload",
            // Only apply when ENV=production and request is HTTPS.
            // We set it via middleware for the API; here we set a default.
          },
        ],
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/:path*`,
      },
    ];
  },
};

module.exports = nextConfig;
