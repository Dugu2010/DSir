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
