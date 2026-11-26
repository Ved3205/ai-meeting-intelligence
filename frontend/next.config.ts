import type { NextConfig } from "next";

const staticExport = process.env.STATIC_EXPORT === "1";

const nextConfig: NextConfig = {
  env: { NEXT_PUBLIC_API_URL: staticExport ? "" : process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000" },
  ...(staticExport ? { output: "export" as const, trailingSlash: true } : {}),
  images: { unoptimized: true },
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
