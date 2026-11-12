"use client";

import { useEffect, useState } from "react";
import { GraduationCap, LogOut } from "lucide-react";
import { cn } from "@/lib/utils";
import { AUTH_KEY, AUTH_TOKEN, hasValidSession, verifyCredentials } from "@/lib/auth";
import { syncDrafts } from "@/lib/drafts";

/**
 * Locks the app behind a client-side sign-in. children always render — the
 * gate hides them with CSS after mount instead of omitting them, so every
 * segment stays in the prerendered render tree (instant navigation). The
 * session token lives in localStorage until "Sign out".
 */
export function AuthGate({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<"checking" | "locked" | "open">("checking");

  useEffect(() => {
    setState(hasValidSession() ? "open" : "locked");
  }, []);

  // Signed in: pull drafts saved from other devices, and refresh whenever the
  // tab regains focus/visibility so work done elsewhere shows up here.
  useEffect(() => {
    if (state !== "open") return;
    void syncDrafts();
    const refresh = () => void syncDrafts();
    const onVisible = () => {
      if (document.visibilityState === "visible") refresh();
    };
    window.addEventListener("focus", refresh);
    document.addEventListener("visibilitychange", onVisible);
    return () => {
      window.removeEventListener("focus", refresh);
      document.removeEventListener("visibilitychange", onVisible);
    };
  }, [state]);

  return (
    <>
      <div className={state === "open" ? "" : "hidden"} aria-hidden={state !== "open"}>
        {children}
      </div>
      {state === "locked" ? <LoginScreen onSuccess={() => setState("open")} /> : null}
      {state === "checking" ? (
        <div className="fixed inset-0 z-[60] flex items-center justify-center bg-slate-950">
          <span className="h-9 w-9 animate-pulse rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600" />
        </div>
      ) : null}
    </>
  );
}

function LoginScreen({ onSuccess }: { onSuccess: () => void }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (busy) return;
    setBusy(true);
    setError(null);
    const ok = await verifyCredentials(username, password);
    if (ok) {
      try {
        localStorage.setItem(AUTH_KEY, AUTH_TOKEN);
      } catch {
        /* storage unavailable — session lives until the tab closes */
      }
      onSuccess();
    } else {
      setError("Incorrect username or password.");
      setBusy(false);
    }
  }

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950 px-4 py-10">
      {/* Soft indigo glow behind the card */}
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 bg-[radial-gradient(60%_50%_at_50%_0%,rgba(99,102,241,0.28),transparent)]"
      />
      <div className="relative w-full max-w-sm">
        <div className="rounded-2xl border border-slate-800 bg-slate-900/80 p-8 shadow-2xl backdrop-blur">
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-lg">
              <GraduationCap className="h-6 w-6" />
            </span>
            <div className="min-w-0">
              <h1 className="truncate text-lg font-semibold leading-tight text-slate-100">
                SDET Interview Gym
              </h1>
              <p className="truncate text-xs text-slate-400">Daya Sagar · Schwab Cyber Security QA</p>
            </div>
          </div>

          <p className="mt-6 text-sm font-medium text-slate-300">Sign in to open your gym</p>
          <form className="mt-3 space-y-3" onSubmit={submit}>
            <div>
              <label htmlFor="username" className="mb-1 block text-xs font-medium text-slate-400">
                Username
              </label>
              <input
                id="username"
                name="username"
                autoComplete="username"
                autoCapitalize="none"
                spellCheck={false}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
                placeholder="dayacode12"
              />
            </div>
            <div>
              <label htmlFor="password" className="mb-1 block text-xs font-medium text-slate-400">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full rounded-lg border border-slate-700 bg-slate-950/60 px-3 py-2 text-sm text-slate-100 placeholder-slate-600 focus:border-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40"
                placeholder="••••••••••"
              />
            </div>
            {error ? (
              <p
                role="alert"
                className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-xs text-red-400"
              >
                {error}
              </p>
            ) : null}
            <button
              type="submit"
              disabled={busy}
              className="w-full rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/40 disabled:opacity-60"
            >
              {busy ? "Checking…" : "Sign in"}
            </button>
          </form>
        </div>
        <p className="mt-4 text-center text-[11px] leading-relaxed text-slate-500">
          Private practice gym — predicted questions only, not actual Schwab material.
        </p>
      </div>
    </div>
  );
}

/** Ends the session by clearing the token; reload re-locks the gate. */
export function SignOutButton({ className }: { className?: string }) {
  return (
    <button
      type="button"
      aria-label="Sign out"
      title="Sign out"
      onClick={() => {
        try {
          localStorage.removeItem(AUTH_KEY);
        } catch {
          /* storage unavailable — a reload still re-checks */
        }
        window.location.reload();
      }}
      className={cn(
        "flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800",
        className
      )}
    >
      <LogOut className="h-3.5 w-3.5" />
      <span className="hidden sm:inline">Sign out</span>
    </button>
  );
}
