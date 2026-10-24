/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow the sandbox preview/tunnel hostnames to hit the dev server
  allowedDevOrigins: ["*.e2b.app"],
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
