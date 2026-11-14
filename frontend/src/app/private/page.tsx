"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight, Fingerprint, LockKeyhole, Sparkles } from "lucide-react";

import { ApiError } from "@/lib/api";
import {
  fetchPrivateStatus,
  lockPrivateArea,
  usePrivateGate,
  type PrivateStatus,
} from "@/lib/private-area";
import { PrivateAreaGate } from "@/components/private-area-gate";

export default function PrivatePage() {
  const gate = usePrivateGate();
  const [status, setStatus] = useState<PrivateStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPrivateStatus()
      .then(setStatus)
      .catch((err) =>
        setError(
          err instanceof ApiError
            ? err.message
            : "Could not reach the server to check the private area.",
        ),
      );
  }, [gate.locked]);

  if (gate.loading) return <GateChecking />;
  if (gate.locked) return <PrivateAreaGate />;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Private area</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          {gate.configured
            ? "Unlocked in this tab. Everything below is loaded from the server with your token, not published with the site."
            : "Nothing is locked yet: the server has no private-area password configured."}
        </p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2">
        <Link
          href="/admiral-iga"
          className="group rounded-xl border border-slate-200 bg-white p-5 transition hover:border-indigo-300 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-indigo-700"
        >
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
            <Fingerprint className="h-4 w-4" />
          </span>
          <p className="mt-3 font-semibold text-slate-900 dark:text-slate-100">
            Admiral IGA Playbook
          </p>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
            The current-role brief, the sprint tickets and the mapped questions.
          </p>
          <span className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-indigo-700 dark:text-indigo-300">
            Open
            <ArrowRight className="h-3 w-3 transition group-hover:translate-x-0.5" />
          </span>
        </Link>

        <div className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
          <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-indigo-50 text-indigo-600 dark:bg-indigo-950 dark:text-indigo-400">
            <Sparkles className="h-4 w-4" />
          </span>
          <p className="mt-3 font-semibold text-slate-900 dark:text-slate-100">
            AI assistant
          </p>
          <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-400">
            {gate.locked || gate.configured === false
              ? "Opens once this tab is unlocked."
              : "Unlocked for this tab. Open it with the button in the bottom-right corner or Alt+K."}
          </p>
        </div>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5 text-sm dark:border-slate-700 dark:bg-slate-900">
        <h2 className="font-semibold text-slate-900 dark:text-slate-100">Server checks</h2>
        <ul className="mt-2 space-y-1 text-xs text-slate-600 dark:text-slate-300">
          <li>
            Password gate on the server:{" "}
            <span className="font-medium">
              {status ? (status.configured ? "configured" : "not configured") : "checking…"}
            </span>
          </li>
          <li>
            Access token:{" "}
            <span className="font-medium">
              {status?.unlocked ? "valid" : "missing or expired"}
            </span>
          </li>
        </ul>
        {status && !status.configured ? (
          <p className="mt-3 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs leading-relaxed text-amber-900 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300">
            The backend has no <code>PRIVATE_AREA_PASSWORD</code> set, so the private
            area is open to anyone who knows the API URL. Set it on the server before
            relying on this gate.
          </p>
        ) : null}
        {error ? (
          <p role="alert" className="mt-3 text-xs text-rose-700 dark:text-rose-400">
            {error}
          </p>
        ) : null}
        <button
          type="button"
          onClick={lockPrivateArea}
          className="mt-4 inline-flex items-center gap-1.5 rounded-lg border border-slate-300 px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:border-rose-300 hover:text-rose-700 dark:border-slate-600 dark:text-slate-300 dark:hover:border-rose-700 dark:hover:text-rose-300"
        >
          <LockKeyhole className="h-3.5 w-3.5" />
          Lock this tab
        </button>
      </section>
    </div>
  );
}

function GateChecking() {
  return (
    <p className="text-sm text-slate-500 dark:text-slate-400">Checking access…</p>
  );
}
