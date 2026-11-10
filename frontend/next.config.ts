import type { NextConfig } from "next";

// The GitHub Pages workflow (see .github/workflows/deploy-ui.yml) builds the
// UI as a static export by setting these environment variables at build time:
//   NEXT_OUTPUT=export                -> emit static files into out/
//   NEXT_PUBLIC_BASE_PATH=/<repo>     -> project pages serve under /<repo>/
// Local `next dev` / `next build` are unaffected when the variables are unset.
// Cache Components / Partial Prefetching stream a dynamic shell, which needs
// the Node.js server runtime ("PPR cannot be enabled in export mode") — so
// they stay on for local development and off for the static export.
const isStaticExport = process.env.NEXT_OUTPUT === "export";

const nextConfig: NextConfig = {
  ...(isStaticExport ? { output: "export" as const, trailingSlash: true } : {}),
  ...(process.env.NEXT_PUBLIC_BASE_PATH
    ? { basePath: process.env.NEXT_PUBLIC_BASE_PATH }
    : {}),
  ...(!isStaticExport ? { cacheComponents: true, partialPrefetching: true } : {}),
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
