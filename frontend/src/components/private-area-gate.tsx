"use client";

import { useState } from "react";
import { KeyRound, Loader2, LockKeyhole, ShieldCheck } from "lucide-react";

import { ApiError } from "@/lib/api";
import { unlockPrivateArea } from "@/lib/private-area";

/**
 * Password prompt for the private area (Admiral playbook + assistant).
 *
 * The password goes to the backend once. A wrong password, a throttled client
 * and a server with no password configured each get their own message instead
 * of a generic failure.
 */
export function PrivateAreaGate() {
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    if (!password.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      await unlockPrivateArea(password);
      setPassword("");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Could not reach the server. Check the connection and try again.",
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-md">
      <form
        onSubmit={submit}
        className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900"
      >
        <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
          <LockKeyhole className="h-5 w-5" />
        </span>
        <h1 className="mt-4 text-lg font-semibold text-slate-900 dark:text-slate-100">
          Private area
        </h1>
        <p className="mt-1 text-sm leading-relaxed text-slate-600 dark:text-slate-300">
          The Admiral playbook and the AI assistant are not published. Enter the
          access password to load them from the server.
        </p>

        <label
          htmlFor="private-password"
          className="mt-5 block text-xs font-medium text-slate-700 dark:text-slate-300"
        >
          Access password
        </label>
        <div className="mt-1 flex gap-2">
          <input
            id="private-password"
            type="password"
            autoComplete="current-password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            disabled={busy}
            placeholder="Password"
            className="h-10 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 disabled:opacity-60 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:focus:ring-indigo-900"
          />
          <button
            type="submit"
            disabled={busy || !password.trim()}
            className="inline-flex h-10 shrink-0 items-center gap-1.5 rounded-lg bg-indigo-600 px-4 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {busy ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <KeyRound className="h-4 w-4" />
            )}
            Unlock
          </button>
        </div>

        {error ? (
          <p
            role="alert"
            className="mt-3 rounded-lg border border-rose-200 bg-rose-50 px-3 py-2 text-xs leading-relaxed text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300"
          >
            {error}
          </p>
        ) : null}

        <p className="mt-4 flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
          <ShieldCheck className="mt-0.5 h-3 w-3 shrink-0" />
          Checked on the server, so the password is never part of this site&apos;s
          files. The unlock lasts 12 hours in this tab.
        </p>
      </form>
    </div>
  );
}
