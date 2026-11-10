"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Database, Lightbulb, Play, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { CodeEditor } from "@/components/code-editor";
import { cn, difficultyBadge } from "@/lib/utils";

interface ChallengeMeta {
  id: string;
  title: string;
  difficulty: string;
  category: string;
  problem: string;
  security_note?: string;
}

interface ChallengeDetail extends ChallengeMeta {
  hints: string[];
}

interface QueryResult {
  columns: string[];
  rows: (string | number | null)[][];
  row_count: number;
  truncated: boolean;
}

interface SubmitResult {
  correct: boolean;
  your_rows: (string | number | null)[][];
  expected_rows: (string | number | null)[][];
  expected_sql: string;
  explanation: string;
  security_note: string;
  followups: string[];
}

const DEFAULT_SQL = "SELECT username, status FROM USERS ORDER BY username LIMIT 10";

export default function SqlPlaygroundPage() {
  const [challenges, setChallenges] = useState<ChallengeMeta[]>([]);
  const [schema, setSchema] = useState<Record<string, [string, string][]> | null>(null);
  const [selected, setSelected] = useState<ChallengeMeta | null>(null);
  const [detail, setDetail] = useState<ChallengeDetail | null>(null);
  const [sql, setSql] = useState(DEFAULT_SQL);
  const [result, setResult] = useState<QueryResult | null>(null);
  const [submitResult, setSubmitResult] = useState<SubmitResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [tab, setTab] = useState<"playground" | "challenges">("playground");

  useEffect(() => {
    api.get<{ challenges: ChallengeMeta[] }>("/api/sql/challenges").then((r) => setChallenges(r.challenges)).catch((e) => setError(e.message));
    api.get<{ tables: Record<string, [string, string][]> }>("/api/sql/schema").then((r) => setSchema(r.tables)).catch(() => {});
  }, []);

  async function runQuery() {
    setBusy(true);
    setError(null);
    setSubmitResult(null);
    try {
      setResult(await api.post<QueryResult>("/api/sql/run", { sql }));
    } catch (e) {
      setResult(null);
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function selectChallenge(c: ChallengeMeta) {
    setSelected(c);
    setSubmitResult(null);
    setResult(null);
    setError(null);
    try {
      setDetail(await api.get<ChallengeDetail>(`/api/sql/challenges/${c.id}`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function submitAnswer() {
    if (!selected) return;
    setBusy(true);
    setError(null);
    try {
      setSubmitResult(
        await api.post<SubmitResult>(`/api/sql/challenges/${selected.id}/submit`, { sql, duration_seconds: 0 })
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function revealAnswer() {
    if (!selected) return;
    setBusy(true);
    try {
      setSql((await api.post<{ expected_sql: string }>(`/api/sql/challenges/${selected.id}/reveal`)).expected_sql);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const groupedChallenges = useMemo(() => {
    const groups: Record<string, ChallengeMeta[]> = {};
    for (const c of challenges) {
      (groups[c.category] ??= []).push(c);
    }
    return groups;
  }, [challenges]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">SQL Playground</h1>
        <p className="mt-1 text-sm text-slate-600">
          {challenges.length} challenges on a realistic IAM dataset. Every query runs against a
          fresh <strong>in-memory SQLite sandbox</strong> — read-only, isolated from the app database,
          and no credentials are ever exposed to the browser.
        </p>
      </header>

      <div className="flex gap-1.5">
        {(["playground", "challenges"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              "rounded-full px-4 py-1.5 text-sm font-medium transition",
              tab === t ? "bg-indigo-600 text-white" : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100"
            )}
          >
            {t === "playground" ? "Free playground" : "Challenges"}
          </button>
        ))}
      </div>

      {error ? (
        <div className="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" /> {error}
        </div>
      ) : null}

      {schema ? (
        <details className="rounded-xl border border-slate-200 bg-white p-4">
          <summary className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700">
            <Database className="h-4 w-4 text-indigo-600" /> Data dictionary ({Object.keys(schema).length} tables)
          </summary>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(schema).map(([table, cols]) => (
              <div key={table} className="rounded-lg border border-slate-200 p-3">
                <p className="mb-1.5 font-mono text-xs font-bold text-indigo-700">{table}</p>
                <ul className="space-y-0.5">
                  {cols.map(([name, desc]) => (
                    <li key={name} className="text-[11px] text-slate-600">
                      <span className="font-mono font-medium">{name}</span>
                      <span className="text-slate-400"> — {desc}</span>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </details>
      ) : null}

      {tab === "playground" ? (
        <>
          <CodeEditor value={sql} onChange={setSql} language="sql" height={220} />
          <button
            onClick={runQuery}
            disabled={busy}
            className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
          >
            <Play className="h-4 w-4" /> {busy ? "Running…" : "Run query"}
          </button>
          <ResultTable result={result} />
        </>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
          <aside className="max-h-[80vh] space-y-3 overflow-y-auto pr-1">
            {Object.entries(groupedChallenges).map(([cat, items]) => (
              <div key={cat}>
                <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">{cat}</p>
                <div className="space-y-1.5">
                  {items.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => selectChallenge(c)}
                      className={cn(
                        "w-full rounded-lg border p-2.5 text-left transition",
                        selected?.id === c.id ? "border-indigo-400 bg-indigo-50" : "border-slate-200 bg-white hover:border-slate-300"
                      )}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-[13px] font-medium text-slate-800">{c.title}</p>
                        <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold", difficultyBadge(c.difficulty))}>
                          {c.difficulty}
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </aside>

          <section className="space-y-4">
            {!selected ? (
              <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 text-sm text-slate-500">
                Pick a challenge to start.
              </div>
            ) : (
              <>
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <h2 className="font-semibold text-slate-900">{selected.title}</h2>
                  <p className="mt-2 text-sm leading-relaxed text-slate-700">{detail?.problem ?? selected.problem}</p>
                  {detail?.hints?.length ? (
                    <ul className="mt-3 space-y-1.5">
                      {detail.hints.map((h, i) => (
                        <li key={i} className="flex items-start gap-1.5 rounded bg-amber-50 p-2 text-xs text-amber-900">
                          <Lightbulb className="mt-0.5 h-3 w-3 shrink-0" /> {h}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>

                <CodeEditor value={sql} onChange={setSql} language="sql" height={200} />
                <div className="flex flex-wrap items-center gap-3">
                  <button
                    onClick={submitAnswer}
                    disabled={busy}
                    className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                  >
                    Submit answer
                  </button>
                  <button
                    onClick={revealAnswer}
                    disabled={busy}
                    className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                  >
                    Load reference query
                  </button>
                </div>

                {submitResult ? (
                  <div
                    className={cn(
                      "rounded-xl border p-4",
                      submitResult.correct ? "border-emerald-200 bg-emerald-50" : "border-rose-200 bg-rose-50"
                    )}
                  >
                    <div className="flex items-center gap-2 font-semibold">
                      {submitResult.correct ? (
                        <>
                          <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                          <span className="text-emerald-800">Correct — result rows match the reference answer.</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="h-5 w-5 text-rose-600" />
                          <span className="text-rose-800">Not correct yet — compare your rows with the expected ones.</span>
                        </>
                      )}
                    </div>
                    <p className="mt-2 text-xs text-slate-500">Row order is ignored; only the result set matters.</p>
                    <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <div>
                        <p className="text-xs font-semibold text-slate-600">Your rows ({submitResult.your_rows.length})</p>
                        <pre className="mt-1 max-h-48 overflow-auto rounded bg-white p-2 text-[11px]">
                          {submitResult.your_rows.map((r, i) => `${r.join(" | ")}`).join("\n") || "(empty)"}
                        </pre>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-slate-600">Expected rows ({submitResult.expected_rows.length})</p>
                        <pre className="mt-1 max-h-48 overflow-auto rounded bg-white p-2 text-[11px]">
                          {submitResult.expected_rows.map((r) => r.join(" | ")).join("\n") || "(empty)"}
                        </pre>
                      </div>
                    </div>
                    <div className="mt-3 space-y-2 border-t border-slate-200 pt-3">
                      <p className="text-sm text-slate-700">{submitResult.explanation}</p>
                      {submitResult.security_note ? (
                        <p className="rounded bg-slate-100 p-2 text-xs text-slate-700">
                          <strong>Security note:</strong> {submitResult.security_note}
                        </p>
                      ) : null}
                      {submitResult.followups?.length ? (
                        <ul className="list-inside list-disc text-xs text-slate-600">
                          {submitResult.followups.map((f, i) => (
                            <li key={i}>{f}</li>
                          ))}
                        </ul>
                      ) : null}
                    </div>
                  </div>
                ) : null}
              </>
            )}
          </section>
        </div>
      )}
    </div>
  );
}

function ResultTable({ result }: { result: QueryResult | null }) {
  if (!result) return null;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
      <p className="border-b border-slate-200 px-4 py-2 text-xs text-slate-500">
        {result.row_count} row{result.row_count === 1 ? "" : "s"} returned{result.truncated ? " (truncated at 200)" : ""}
      </p>
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-50">
          <tr>
            {result.columns.map((c) => (
              <th key={c} className="whitespace-nowrap px-3 py-2 font-semibold text-slate-700">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {result.rows.map((row, i) => (
            <tr key={i} className="border-t border-slate-100">
              {row.map((cell, j) => (
                <td key={j} className="whitespace-nowrap px-3 py-1.5 font-mono text-slate-700">
                  {cell === null ? <span className="text-slate-400">NULL</span> : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
