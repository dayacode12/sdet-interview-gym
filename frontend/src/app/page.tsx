"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  Clock,
  FlaskConical,
  ShieldCheck,
  Timer,
} from "lucide-react";
import { api, clearApiBaseUrl, getApiBaseUrl, setApiBaseUrl } from "@/lib/api";

interface Dashboard {
  candidate_name: string;
  java_mode: string;
  content: Record<string, number>;
  tagline: string;
  honesty: string;
}

interface Settings {
  interview_datetime: string;
  target_role: string;
}

interface Analytics {
  java: { passed: number; total: number };
  sql: { passed: number; total: number };
  flashcards: { known: number; total: number };
}

const MODE_STYLES: Record<string, string> = {
  docker: "bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-400",
  local: "bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-400",
  disabled: "bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300",
};

const MODE_TEXT: Record<string, string> = {
  docker: "Docker sandbox — isolated container, no network",
  local: "Local JVM — isolated subprocess on this machine",
  disabled: "Execution disabled — study mode only",
};

export default function DashboardPage() {
  const [dash, setDash] = useState<Dashboard | null>(null);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [apiUrl, setApiUrl] = useState("");

  useEffect(() => {
    api.get<Dashboard>("/api/dashboard").then(setDash).catch((e) => setError(String(e.message)));
    api.get<Settings>("/api/settings").then(setSettings).catch(() => {});
    api.get<Analytics>("/api/analytics/summary").then(setAnalytics).catch(() => {});
  }, []);

  function saveApiUrl() {
    if (!apiUrl.trim()) return;
    setApiBaseUrl(apiUrl);
    window.location.reload();
  }

  function resetApiUrl() {
    clearApiBaseUrl();
    window.location.reload();
  }

  const daysLeft = (() => {
    if (!settings?.interview_datetime) return null;
    const diff = new Date(settings.interview_datetime).getTime() - Date.now();
    return Math.ceil(diff / 86400000);
  })();

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Welcome back{dash ? `, ${dash.candidate_name}` : ""}</h1>
        <p className="mt-1 max-w-3xl text-sm text-slate-600 dark:text-slate-300">{dash?.tagline ?? "Loading…"}</p>
      </header>

      {error ? (
        <div className="flex items-start gap-2 rounded-lg border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 p-4 text-sm text-rose-800 dark:text-rose-400">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <div className="w-full">
            <p className="font-medium">Backend not reachable</p>
            <p className="mt-0.5 text-xs">
              Running locally? Start it with{" "}
              <code className="rounded bg-rose-100 dark:bg-rose-900 px-1">python -m uvicorn app.main:app --port 8000</code>{" "}
              from the backend directory. ({error})
            </p>
            <div className="mt-2.5 rounded-lg border border-rose-200 dark:border-rose-800 bg-white dark:bg-slate-900 p-2.5">
              <p className="text-[11px] font-medium text-slate-700 dark:text-slate-300">
                Using the hosted UI (GitHub Pages)? Point it at your Render backend:
              </p>
              <div className="mt-1.5 flex flex-wrap items-center gap-1.5">
                <input
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  onFocus={() => setApiUrl((v) => v || getApiBaseUrl())}
                  placeholder="https://your-render-service.onrender.com"
                  className="min-w-0 flex-1 rounded-md border border-slate-300 dark:border-slate-600 px-2.5 py-1.5 text-xs text-slate-800 dark:text-slate-100 focus:border-indigo-500 focus:outline-none"
                />
                <button
                  onClick={saveApiUrl}
                  disabled={!apiUrl.trim()}
                  className="rounded-md bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                >
                  Save
                </button>
                <button
                  onClick={resetApiUrl}
                  className="rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                >
                  Reset
                </button>
              </div>
              <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500">
                Saved in this browser only. Current backend: {getApiBaseUrl()}
              </p>
            </div>
          </div>
        </div>
      ) : null}

      {dash ? (
        <div className="flex items-start gap-2 rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 text-xs text-slate-600 dark:text-slate-300">
          <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600 dark:text-indigo-400" />
          <p>{dash.honesty}</p>
        </div>
      ) : null}

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
            <Clock className="h-3.5 w-3.5" /> Interview
          </div>
          {daysLeft !== null ? (
            <>
              <p className="mt-2 text-2xl font-bold">
                {daysLeft >= 0 ? `${daysLeft}d` : "done"}
              </p>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                {new Date(settings!.interview_datetime).toLocaleString()}
              </p>
            </>
          ) : (
            <>
              <p className="mt-2 text-sm font-medium text-slate-700 dark:text-slate-300">Not scheduled</p>
              <Link href="/roadmap" className="mt-1 inline-flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
                Set the date <ArrowRight className="h-3 w-3" />
              </Link>
            </>
          )}
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
            <FlaskConical className="h-3.5 w-3.5" /> Java Lab
          </div>
          <p className="mt-2 text-2xl font-bold">
            {analytics?.java.passed ?? 0}<span className="text-sm font-normal text-slate-400 dark:text-slate-500">/{dash?.content.java_questions ?? 33}</span>
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">questions passed</p>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
            <Timer className="h-3.5 w-3.5" /> Mock Interview
          </div>
          <p className="mt-2 text-sm font-medium text-slate-700 dark:text-slate-300">60 minutes, 6 sections</p>
          <Link href="/mock-interview" className="mt-1 inline-flex items-center gap-1 text-xs text-indigo-600 dark:text-indigo-400 hover:underline">
            Start a session <ArrowRight className="h-3 w-3" />
          </Link>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <div className="flex items-center gap-2 text-xs font-medium text-slate-500 dark:text-slate-400">
            <ShieldCheck className="h-3.5 w-3.5" /> Content
          </div>
          <p className="mt-2 text-lg font-bold">
            {(Object.values(dash?.content ?? {})).reduce((a, b) => a + b, 0)} items
          </p>
          <p className="text-xs text-slate-500 dark:text-slate-400">across all labs</p>
        </div>
      </section>

      {dash ? (
        <section>
          <h2 className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">Java execution mode</h2>
          <div className="flex flex-wrap items-center gap-2">
            <span className={`rounded-full px-3 py-1 text-xs font-semibold ${MODE_STYLES[dash.java_mode] ?? "bg-slate-100 dark:bg-slate-800"}`}>
              {dash.java_mode.toUpperCase()}
            </span>
            <span className="text-xs text-slate-600 dark:text-slate-300">{MODE_TEXT[dash.java_mode]}</span>
          </div>
        </section>
      ) : null}

      <section className="grid grid-cols-1 gap-3 md:grid-cols-2">
        {[
          { href: "/java-lab", title: "Java Coding Lab", desc: `${dash?.content.java_questions ?? 33} questions with a real run button` },
          { href: "/sql-playground", title: "SQL Playground", desc: `${dash?.content.sql_challenges ?? 26} challenges on a seeded IAM database` },
          { href: "/scenarios", title: "Scenario Simulator", desc: `${dash?.content.scenarios ?? 30} security QA scenarios` },
          { href: "/iam-lab", title: "IAM Lab", desc: `${dash?.content.iam_modules ?? 5} modules: IGA, PAM, protocols, DLP` },
          { href: "/mock-interview", title: "Mock Interview", desc: "Timed 60-minute simulation with weighted rubric" },
          { href: "/flashcards", title: "Flashcards", desc: `${dash?.content.flashcards ?? 100} cards with confidence tracking` },
        ].map((card) => (
          <Link
            key={card.href}
            href={card.href}
            className="group flex items-center justify-between rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4 transition hover:border-indigo-300 dark:hover:border-indigo-800 hover:shadow-sm"
          >
            <div>
              <p className="font-semibold text-slate-800 dark:text-slate-100 group-hover:text-indigo-700 dark:group-hover:text-indigo-400">{card.title}</p>
              <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{card.desc}</p>
            </div>
            <ArrowRight className="h-4 w-4 text-slate-400 dark:text-slate-500 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" />
          </Link>
        ))}
      </section>
    </div>
  );
}
