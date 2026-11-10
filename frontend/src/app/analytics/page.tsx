"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  XAxis,
  YAxis,
} from "recharts";
import { AlertTriangle, TrendingUp } from "lucide-react";
import { api } from "@/lib/api";
import { RUBRIC_LABELS, scoreColor } from "@/lib/utils";

interface Summary {
  java: { total: number; attempted: number; passed: number; revealed: number; unseen: number; completion_pct: number };
  sql: { total: number; attempted: number; passed: number; revealed: number; unseen: number; completion_pct: number };
  scenarios: { total: number; attempted: number; submissions: number; average_score: number | null };
  mock: { sessions: number; finished: number; last_score: number | null; best_score: number | null; dimension_averages: Record<string, number> | null };
  flashcards: { total: number; reviewed: number; known: number; needs_revision: number };
  weak_java_categories: { category: string; pass_rate: number; attempts: number }[];
  time_by_topic: Record<string, number>;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<Summary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<Summary>("/api/analytics/summary").then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Progress Analytics</h1>
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 p-3 text-sm text-rose-800 dark:text-rose-400">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      </div>
    );
  }

  const dimensionData = data?.mock?.dimension_averages
    ? Object.entries(data.mock.dimension_averages).map(([dim, score]) => ({
        dimension: RUBRIC_LABELS[dim]?.split(" (")[0] ?? dim,
        score,
      }))
    : [];

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Progress Analytics</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Honest numbers only: everything below counts what you actually did in this app.
        </p>
      </header>

      <section className="grid grid-cols-2 gap-3 lg:grid-cols-4">
        {[
          { label: "Java passed", value: `${data?.java.passed ?? 0}/${data?.java.total ?? 33}`, sub: `${data?.java.revealed ?? 0} revealed` },
          { label: "SQL passed", value: `${data?.sql.passed ?? 0}/${data?.sql.total ?? 26}`, sub: `${data?.sql.revealed ?? 0} revealed` },
          { label: "Scenarios attempted", value: `${data?.scenarios.attempted ?? 0}/${data?.scenarios.total ?? 30}`, sub: data?.scenarios.average_score != null ? `avg ${data.scenarios.average_score}` : "no submissions yet" },
          { label: "Flashcards known", value: `${data?.flashcards.known ?? 0}/${data?.flashcards.total ?? 100}`, sub: `${data?.flashcards.needs_revision ?? 0} need revision` },
        ].map((stat) => (
          <div key={stat.label} className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
            <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{stat.label}</p>
            <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-slate-100">{stat.value}</p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">{stat.sub}</p>
          </div>
        ))}
      </section>

      {data?.mock?.sessions ? (
        <section className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <h2 className="mb-3 flex items-center gap-1.5 font-semibold">
            <TrendingUp className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Mock interviews
          </h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            {data.mock.sessions} session{data.mock.sessions === 1 ? "" : "s"} started, {data.mock.finished} finished.
            {data.mock.last_score != null ? ` Latest score: ${data.mock.last_score.toFixed(1)}.` : ""}
            {data.mock.best_score != null ? ` Best: ${data.mock.best_score.toFixed(1)}.` : ""}
          </p>
        </section>
      ) : null}

      {dimensionData.length > 0 ? (
        <section className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <h2 className="mb-3 font-semibold">Rubric dimension averages (across finished mocks)</h2>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart data={dimensionData}>
                <PolarGrid />
                <PolarAngleAxis dataKey="dimension" tick={{ fontSize: 11 }} />
                <Radar dataKey="score" stroke="#4f46e5" fill="#6366f1" fillOpacity={0.5} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </section>
      ) : null}

      {data?.weak_java_categories?.length ? (
        <section className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <h2 className="mb-3 font-semibold">Weakest Java categories (pass rate, attempted only)</h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.weak_java_categories}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="category" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={50} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Bar dataKey="pass_rate" radius={[4, 4, 0, 0]}>
                  {data.weak_java_categories.map((c) => (
                    <Cell key={c.category} fill={c.pass_rate >= 70 ? "#10b981" : c.pass_rate >= 50 ? "#f59e0b" : "#f43f5e"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      ) : null}

      {data?.time_by_topic && Object.keys(data.time_by_topic).length > 0 ? (
        <section className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <h2 className="mb-3 font-semibold">Time on topic (minutes)</h2>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={Object.entries(data.time_by_topic).map(([topic, seconds]) => ({ topic, minutes: Math.round(seconds / 60) }))}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="topic" tick={{ fontSize: 10 }} interval={0} angle={-15} textAnchor="end" height={50} />
                <YAxis tick={{ fontSize: 11 }} />
                <Bar dataKey="minutes" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      ) : (
        <p className="rounded-xl border border-dashed border-slate-300 dark:border-slate-600 p-6 text-center text-sm text-slate-500 dark:text-slate-400">
          No activity recorded yet — use the labs and charts will appear here.
        </p>
      )}
    </div>
  );
}
