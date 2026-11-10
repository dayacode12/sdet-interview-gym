const STORAGE_KEY = "sdet-gym-api-url";

function getBase(): string {
  // Runtime override first (used when the static UI is hosted on GitHub Pages
  // against a Render backend), then the build-time env var, then localhost.
  if (typeof window !== "undefined") {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
}

function normalize(url: string): string {
  return url.trim().replace(/\/+$/, "");
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

/** Current backend base URL (localStorage override if set, else the default). */
export function getApiBaseUrl(): string {
  return getBase();
}

/** Persist a backend URL override in this browser (for the hosted UI). */
export function setApiBaseUrl(url: string): void {
  window.localStorage.setItem(STORAGE_KEY, normalize(url));
}

/** Remove the override and fall back to the build-time default. */
export function clearApiBaseUrl(): void {
  window.localStorage.removeItem(STORAGE_KEY);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`${getBase()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!resp.ok) {
    let message = `Request failed (${resp.status})`;
    try {
      const body = await resp.json();
      if (typeof body?.detail === "string") message = body.detail;
      else if (Array.isArray(body?.detail) && body.detail[0]?.msg) message = body.detail[0].msg;
    } catch {
      /* non-JSON error body */
    }
    throw new ApiError(resp.status, message);
  }
  return resp.json() as Promise<T>;
}

export const api = {
  get: <T,>(path: string) => request<T>(path),
  post: <T,>(path: string, body?: unknown) =>
    request<T>(path, { method: "POST", body: body === undefined ? "{}" : JSON.stringify(body) }),
  put: <T,>(path: string, body?: unknown) =>
    request<T>(path, { method: "PUT", body: body === undefined ? "{}" : JSON.stringify(body) }),
};

export interface RubricScores {
  technical_accuracy: number;
  practical_implementation: number;
  problem_solving: number;
  communication: number;
  security_awareness: number;
}

export interface EvaluationResult {
  method: string;
  scores: RubricScores;
  overall: number;
  feedback: Record<string, { matched?: string[]; missed?: string[]; note?: string }>;
}
