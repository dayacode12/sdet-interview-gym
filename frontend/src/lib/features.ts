/**
 * Build-time feature flags for the public site.
 *
 * The source repo stays private; only the static export is published to the
 * public site repo (see .github/workflows/deploy-ui.yml). Two things must not
 * ship there: the Admiral IGA playbook (a live interview brief) and the
 * Groq-backed assistant. The deploy job sets these to "1" for that build, so
 * the code and copy for both are dropped from it. Local development leaves
 * them unset and gets the full app.
 *
 * Next.js inlines `process.env.NEXT_PUBLIC_*` at build time, so these are plain
 * booleans with no runtime lookup — and no dead code in the public bundle.
 */
export const HIDE_ADMIRAL = process.env.NEXT_PUBLIC_HIDE_ADMIRAL === "1";
export const HIDE_ASSISTANT = process.env.NEXT_PUBLIC_HIDE_ASSISTANT === "1";
