"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, Database, Languages, Lightbulb, Play, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { CodeEditor } from "@/components/code-editor";
import { SaveProgress } from "@/components/save-progress";
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
  expected_english?: SqlEnglish | null;
  explanation: string;
  security_note: string;
  followups: string[];
}

interface SqlEnglish {
  statement: string;
  summary: string;
  clauses: { label: string; text: string }[];
  basics?: { term: string; text: string }[];
  tables: string[];
  subqueries: number;
  notes: string[];
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
  const [explanation, setExplanation] = useState<SqlEnglish | null>(null);
  const [explainBusy, setExplainBusy] = useState(false);

  useEffect(() => {
    api.get<{ challenges: ChallengeMeta[] }>("/api/sql/challenges").then((r) => {
      setChallenges(r.challenges);
      // Deep link support: /sql-playground?q=<challenge-id> opens that challenge directly.
      const wanted = new URLSearchParams(window.location.search).get("q");
      const match = wanted ? r.challenges.find((c) => c.id === wanted) : null;
      if (match) {
        setTab("challenges");
        selectChallenge(match);
      }
    }).catch((e) => setError(e.message));
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

  async function explainSql() {
    setExplainBusy(true);
    setError(null);
    try {
      setExplanation(await api.post<SqlEnglish>("/api/sql/explain", { sql }));
    } catch (e) {
      setExplanation(null);
      setError((e as Error).message);
    } finally {
      setExplainBusy(false);
    }
  }

  async function selectChallenge(c: ChallengeMeta) {
    setSelected(c);
    setSubmitResult(null);
    setResult(null);
    setError(null);
    setExplanation(null);
    // Reset the editor to the scratch query so the previous challenge's SQL
    // can't be accidentally submitted against this one.
    setSql(DEFAULT_SQL);
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
      const r = await api.post<{ expected_sql: string; expected_english: SqlEnglish | null }>(
        `/api/sql/challenges/${selected.id}/reveal`
      );
      setSql(r.expected_sql);
      // The reference query arrives with its English translation — show it.
      setExplanation(r.expected_english ?? null);
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
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          {challenges.length} challenges on a realistic IAM dataset. Every query runs against a
          fresh <strong>in-memory SQLite sandbox</strong> — read-only, isolated from the app database,
          and no credentials are ever exposed to the browser. Reading a query you don't
          understand? Hit <strong>Explain in English</strong> and get a clause-by-clause plain-English
          translation — every reference answer ships with one too.
        </p>
      </header>

      <div className="flex gap-1.5">
        {(["playground", "challenges"] as const).map((t) => (
          <button
            key={t}
            onClick={() => {
              setTab(t);
              setExplanation(null); // the panel belongs to the editor of one tab
            }}
            className={cn(
              "rounded-full px-4 py-1.5 text-sm font-medium transition",
              tab === t ? "bg-indigo-600 text-white" : "border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
            )}
          >
            {t === "playground" ? "Free playground" : "Challenges"}
          </button>
        ))}
      </div>

      {error ? (
        <div className="flex items-start gap-2 rounded-lg border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 p-3 text-sm text-rose-800 dark:text-rose-400">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" /> {error}
        </div>
      ) : null}

      {schema ? (
        <details className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
          <summary className="flex cursor-pointer items-center gap-2 text-sm font-medium text-slate-700 dark:text-slate-300">
            <Database className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Data dictionary ({Object.keys(schema).length} tables)
          </summary>
          <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {Object.entries(schema).map(([table, cols]) => (
              <div key={table} className="rounded-lg border border-slate-200 dark:border-slate-700 p-3">
                <p className="mb-1.5 font-mono text-xs font-bold text-indigo-700 dark:text-indigo-400">{table}</p>
                <ul className="space-y-0.5">
                  {cols.map(([name, desc]) => (
                    <li key={name} className="text-[11px] text-slate-600 dark:text-slate-300">
                      <span className="font-mono font-medium">{name}</span>
                      <span className="text-slate-400 dark:text-slate-500"> — {desc}</span>
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
          <SaveProgress
            storageKey="sql:playground"
            value={sql}
            pristine={DEFAULT_SQL}
            onRestore={setSql}
          />
          <div className="flex flex-wrap items-center gap-3">
            <button
              onClick={runQuery}
              disabled={busy}
              className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              <Play className="h-4 w-4" /> {busy ? "Running…" : "Run query"}
            </button>
            <button
              onClick={explainSql}
              disabled={explainBusy}
              className="flex items-center gap-1.5 rounded-lg border border-sky-300 dark:border-sky-700 bg-white dark:bg-slate-900 px-4 py-2 text-sm font-medium text-sky-700 dark:text-sky-300 hover:bg-sky-50 dark:hover:bg-sky-950 disabled:opacity-50"
            >
              <Languages className="h-4 w-4" /> {explainBusy ? "Translating…" : "Explain in English"}
            </button>
          </div>
          {explanation ? <EnglishPanel english={explanation} /> : null}
          <ResultTable result={result} />
        </>
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
          <aside className="max-h-[80vh] space-y-3 overflow-y-auto pr-1">
            {Object.entries(groupedChallenges).map(([cat, items]) => (
              <div key={cat}>
                <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{cat}</p>
                <div className="space-y-1.5">
                  {items.map((c) => (
                    <button
                      key={c.id}
                      onClick={() => selectChallenge(c)}
                      className={cn(
                        "w-full rounded-lg border p-2.5 text-left transition",
                        selected?.id === c.id ? "border-indigo-400 dark:border-indigo-500 bg-indigo-50 dark:bg-indigo-950" : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-600"
                      )}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <p className="text-[13px] font-medium text-slate-800 dark:text-slate-100">{c.title}</p>
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
              <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 text-sm text-slate-500 dark:text-slate-400">
                Pick a challenge to start.
              </div>
            ) : (
              <>
                <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
                  <h2 className="font-semibold text-slate-900 dark:text-slate-100">{selected.title}</h2>
                  <p className="mt-2 text-sm leading-relaxed text-slate-700 dark:text-slate-300">{detail?.problem ?? selected.problem}</p>
                  {detail?.hints?.length ? (
                    <ul className="mt-3 space-y-1.5">
                      {detail.hints.map((h, i) => (
                        <li key={i} className="flex items-start gap-1.5 rounded bg-amber-50 dark:bg-amber-950 p-2 text-xs text-amber-900 dark:text-amber-300">
                          <Lightbulb className="mt-0.5 h-3 w-3 shrink-0" /> {h}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>

                <CodeEditor value={sql} onChange={setSql} language="sql" height={200} />
                <SaveProgress
                  storageKey={`sql:${selected.id}`}
                  value={sql}
                  pristine={DEFAULT_SQL}
                  onRestore={setSql}
                />
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
                    className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                  >
                    Load reference query
                  </button>
                  <button
                    onClick={explainSql}
                    disabled={explainBusy}
                    className="flex items-center gap-1.5 rounded-lg border border-sky-300 dark:border-sky-700 bg-white dark:bg-slate-900 px-3 py-2 text-sm font-medium text-sky-700 dark:text-sky-300 hover:bg-sky-50 dark:hover:bg-sky-950 disabled:opacity-50"
                  >
                    <Languages className="h-4 w-4" /> {explainBusy ? "Translating…" : "Explain in English"}
                  </button>
                </div>

                {explanation ? <EnglishPanel english={explanation} /> : null}

                {submitResult ? (
                  <div
                    className={cn(
                      "rounded-xl border p-4",
                      submitResult.correct ? "border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950" : "border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950"
                    )}
                  >
                    <div className="flex items-center gap-2 font-semibold">
                      {submitResult.correct ? (
                        <>
                          <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
                          <span className="text-emerald-800 dark:text-emerald-400">Correct — result rows match the reference answer.</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="h-5 w-5 text-rose-600 dark:text-rose-400" />
                          <span className="text-rose-800 dark:text-rose-400">Not correct yet — compare your rows with the expected ones.</span>
                        </>
                      )}
                    </div>
                    <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">Row order is ignored; only the result set matters.</p>
                    <div className="mt-3 grid grid-cols-1 gap-3 sm:grid-cols-2">
                      <div>
                        <p className="text-xs font-semibold text-slate-600 dark:text-slate-300">Your rows ({submitResult.your_rows.length})</p>
                        <pre className="mt-1 max-h-48 overflow-auto rounded bg-white dark:bg-slate-900 p-2 text-[11px]">
                          {submitResult.your_rows.map((r, i) => `${r.join(" | ")}`).join("\n") || "(empty)"}
                        </pre>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-slate-600 dark:text-slate-300">Expected rows ({submitResult.expected_rows.length})</p>
                        <pre className="mt-1 max-h-48 overflow-auto rounded bg-white dark:bg-slate-900 p-2 text-[11px]">
                          {submitResult.expected_rows.map((r) => r.join(" | ")).join("\n") || "(empty)"}
                        </pre>
                      </div>
                    </div>
                    <div className="mt-3 space-y-2 border-t border-slate-200 dark:border-slate-700 pt-3">
                      <p className="text-sm text-slate-700 dark:text-slate-300">{submitResult.explanation}</p>
                      {submitResult.expected_english ? (
                        <EnglishPanel english={submitResult.expected_english} title="The reference answer, in English" />
                      ) : null}
                      {submitResult.security_note ? (
                        <p className="rounded bg-slate-100 dark:bg-slate-800 p-2 text-xs text-slate-700 dark:text-slate-300">
                          <strong>Security note:</strong> {submitResult.security_note}
                        </p>
                      ) : null}
                      {submitResult.followups?.length ? (
                        <ul className="list-inside list-disc text-xs text-slate-600 dark:text-slate-300">
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

function EnglishPanel({ english, title = "In plain English" }: { english: SqlEnglish; title?: string }) {
  return (
    <div className="rounded-xl border border-sky-200 dark:border-sky-800 bg-sky-50 dark:bg-sky-950 p-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="flex items-center gap-1.5 text-sm font-semibold text-sky-900 dark:text-sky-300">
          <Languages className="h-4 w-4 shrink-0" /> {title}
        </p>
        <span className="rounded-full bg-sky-100 dark:bg-sky-900 px-2.5 py-0.5 text-[10px] font-semibold text-sky-800 dark:text-sky-300">
          {english.statement} · tables: {english.tables.join(", ") || "none"}
        </span>
      </div>
      <p className="mt-2 text-sm leading-relaxed text-slate-800 dark:text-slate-200">{english.summary}</p>
      <div className="mt-3 space-y-1.5">
        {english.clauses.map((c, i) => (
          <div key={i} className="flex flex-wrap items-baseline gap-2">
            <span className="shrink-0 rounded bg-sky-600 px-1.5 py-0.5 font-mono text-[10px] font-bold text-white">
              {c.label}
            </span>
            <span className="min-w-0 flex-1 text-xs leading-relaxed text-slate-700 dark:text-slate-300">{c.text}</span>
          </div>
        ))}
      </div>
      {english.basics?.length ? (
        <div className="mt-3 rounded-lg border border-sky-200 dark:border-sky-800 bg-white dark:bg-slate-900 p-3">
          <p className="text-xs font-semibold text-sky-900 dark:text-sky-300">
            SQL basics in this query — what each term means, using your own query
          </p>
          <ul className="mt-2 space-y-1.5">
            {english.basics.map((b, i) => (
              <li key={i} className="text-xs leading-relaxed text-slate-700 dark:text-slate-300">
                <span className="font-semibold text-sky-700 dark:text-sky-400">{b.term}: </span>
                {b.text}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
      {english.notes?.length ? (
        <p className="mt-3 border-t border-sky-200 dark:border-sky-800 pt-2 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
          {english.notes.join(" ")}
        </p>
      ) : null}
    </div>
  );
}

function ResultTable({ result }: { result: QueryResult | null }) {
  if (!result) return null;
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
      <p className="border-b border-slate-200 dark:border-slate-700 px-4 py-2 text-xs text-slate-500 dark:text-slate-400">
        {result.row_count} row{result.row_count === 1 ? "" : "s"} returned{result.truncated ? " (truncated at 200)" : ""}
      </p>
      <table className="w-full text-left text-xs">
        <thead className="bg-slate-50 dark:bg-slate-800/60">
          <tr>
            {result.columns.map((c) => (
              <th key={c} className="whitespace-nowrap px-3 py-2 font-semibold text-slate-700 dark:text-slate-300">
                {c}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {result.rows.map((row, i) => (
            <tr key={i} className="border-t border-slate-100 dark:border-slate-800">
              {row.map((cell, j) => (
                <td key={j} className="whitespace-nowrap px-3 py-1.5 font-mono text-slate-700 dark:text-slate-300">
                  {cell === null ? <span className="text-slate-400 dark:text-slate-500">NULL</span> : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
