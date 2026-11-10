"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, CheckCircle2, ChevronDown, Lightbulb, Play, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { CodeEditor } from "@/components/code-editor";
import { cn, difficultyBadge } from "@/lib/utils";

interface QuestionMeta {
  id: string;
  title: string;
  category: string;
  difficulty: string;
  type: string;
  problem: string;
  starter_code?: string;
  test_count: number;
}

interface QuestionDetail extends QuestionMeta {
  hints: string[];
}

interface TestResult {
  name: string;
  passed: boolean;
  expected?: string;
  actual?: string;
  timed_out?: boolean;
  stderr?: string;
}

interface RunResult {
  ok: boolean;
  passed: number;
  total: number;
  compile_error?: string | null;
  test_results?: TestResult[];
  mode: string;
  error?: string | null;
}

interface Revealed {
  solution: string;
  explanation: string;
  followups: string[];
}

export default function JavaLabPage() {
  const [questions, setQuestions] = useState<QuestionMeta[]>([]);
  const [meta, setMeta] = useState<{ java_mode: string; mode_label: string } | null>(null);
  const [selected, setSelected] = useState<QuestionMeta | null>(null);
  const [detail, setDetail] = useState<QuestionDetail | null>(null);
  const [code, setCode] = useState("");
  const [running, setRunning] = useState(false);
  const [runResult, setRunResult] = useState<RunResult | null>(null);
  const [revealed, setRevealed] = useState<Revealed | null>(null);
  const [showHints, setShowHints] = useState(false);
  const [category, setCategory] = useState("all");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<{ questions: QuestionMeta[] }>("/api/java/questions")
      .then((r) => {
        setQuestions(r.questions);
        // Deep link support: /java-lab?q=<question-id> pre-selects that question.
        const wanted = new URLSearchParams(window.location.search).get("q");
        const match = wanted ? r.questions.find((item) => item.id === wanted) : null;
        if (match) selectQuestion(match);
      })
      .catch((e) => setError(e.message));
    api.get<{ java_mode: string; mode_label: string }>("/api/java/meta").then(setMeta).catch(() => {});
  }, []);

  const categories = useMemo(() => {
    const cats = Array.from(new Set(questions.map((q) => q.category)));
    return ["all", ...cats];
  }, [questions]);

  const filtered = useMemo(
    () => (category === "all" ? questions : questions.filter((q) => q.category === category)),
    [questions, category]
  );

  async function selectQuestion(q: QuestionMeta) {
    setSelected(q);
    setRevealed(null);
    setRunResult(null);
    setShowHints(false);
    setError(null);
    try {
      const d = await api.get<QuestionDetail>(`/api/java/questions/${q.id}`);
      setDetail(d);
      setCode(d.starter_code ?? "");
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function runCode() {
    if (!selected) return;
    setRunning(true);
    setRunResult(null);
    try {
      const result = await api.post<RunResult>("/api/java/run", {
        question_id: selected.id,
        code,
      });
      setRunResult(result);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setRunning(false);
    }
  }

  async function reveal() {
    if (!selected) return;
    try {
      setRevealed(await api.post<Revealed>(`/api/java/questions/${selected.id}/reveal`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Java Coding Lab</h1>
        <p className="mt-1 text-sm text-slate-600">
          {questions.length || "…"} interview questions. Runnable problems follow a stdin/stdout
          contract: define <code className="rounded bg-slate-100 px-1 text-xs">public class Main</code>,
          read input from stdin, print the exact expected output. Design questions are code-review
          exercises — there is nothing to execute.
        </p>
        {meta ? (
          <div className="mt-3 flex items-center gap-2">
            <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-700">
              Execution: {meta.java_mode.toUpperCase()}
            </span>
            <span className="text-xs text-slate-500">{meta.mode_label}</span>
          </div>
        ) : null}
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-1.5">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setCategory(cat)}
            className={cn(
              "rounded-full px-3 py-1 text-xs font-medium transition",
              category === cat
                ? "bg-indigo-600 text-white"
                : "bg-white text-slate-600 hover:bg-slate-100 border border-slate-200"
            )}
          >
            {cat}
            {cat !== "all" ? (
              <span className="ml-1 text-slate-400">
                {questions.filter((q) => q.category === cat).length}
              </span>
            ) : null}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
        <aside className="max-h-[80vh] space-y-1.5 overflow-y-auto pr-1">
          {filtered.map((q) => (
            <button
              key={q.id}
              onClick={() => selectQuestion(q)}
              className={cn(
                "w-full rounded-lg border p-3 text-left transition",
                selected?.id === q.id
                  ? "border-indigo-400 bg-indigo-50"
                  : "border-slate-200 bg-white hover:border-slate-300"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium text-slate-800">{q.title}</p>
                <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-semibold", difficultyBadge(q.difficulty))}>
                  {q.difficulty}
                </span>
              </div>
              <div className="mt-1 flex items-center gap-2 text-[11px] text-slate-500">
                <span>{q.category}</span>
                {q.type === "code" ? (
                  <span className="text-emerald-600">● runnable ({q.test_count} tests)</span>
                ) : (
                  <span className="text-amber-600">● design</span>
                )}
              </div>
            </button>
          ))}
        </aside>

        <section className="space-y-4">
          {!selected ? (
            <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 text-sm text-slate-500">
              Pick a question from the list to start coding.
            </div>
          ) : (
            <>
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <div className="flex items-start justify-between gap-3">
                  <h2 className="font-semibold text-slate-900">{selected.title}</h2>
                  <span className={cn("shrink-0 rounded px-2 py-0.5 text-[10px] font-semibold", difficultyBadge(selected.difficulty))}>
                    {selected.difficulty}
                  </span>
                </div>
                <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-slate-700">
                  {detail?.problem ?? selected.problem}
                </p>
                {detail?.hints?.length ? (
                  <div className="mt-3">
                    <button
                      onClick={() => setShowHints(!showHints)}
                      className="flex items-center gap-1.5 text-xs font-medium text-amber-700 hover:text-amber-800"
                    >
                      <Lightbulb className="h-3.5 w-3.5" />
                      {showHints ? "Hide hints" : `Show hints (${detail.hints.length})`}
                      <ChevronDown className={cn("h-3 w-3 transition-transform", showHints && "rotate-180")} />
                    </button>
                    {showHints ? (
                      <ul className="mt-2 space-y-1.5">
                        {detail.hints.map((hint, i) => (
                          <li key={i} className="rounded bg-amber-50 p-2 text-xs text-amber-900">
                            {hint}
                          </li>
                        ))}
                      </ul>
                    ) : null}
                  </div>
                ) : null}
              </div>

              {selected.type === "code" ? (
                <>
                  <CodeEditor value={code} onChange={setCode} language="java" />
                  <div className="flex items-center gap-3">
                    <button
                      onClick={runCode}
                      disabled={running}
                      className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-indigo-700 disabled:opacity-50"
                    >
                      <Play className="h-4 w-4" />
                      {running ? "Running…" : "Run tests"}
                    </button>
                    {runResult ? (
                      <span
                        className={cn(
                          "flex items-center gap-1.5 text-sm font-medium",
                          runResult.ok ? "text-emerald-600" : "text-rose-600"
                        )}
                      >
                        {runResult.ok ? <CheckCircle2 className="h-4 w-4" /> : <XCircle className="h-4 w-4" />}
                        {runResult.passed}/{runResult.total} tests passed
                      </span>
                    ) : null}
                  </div>

                  {runResult?.error ? (
                    <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                      {runResult.error}
                    </div>
                  ) : null}

                  {runResult?.compile_error ? (
                    <pre className="overflow-x-auto rounded-lg border border-rose-200 bg-rose-50 p-3 text-xs text-rose-800">
                      {runResult.compile_error}
                    </pre>
                  ) : null}

                  {runResult?.test_results?.length ? (
                    <div className="space-y-2">
                      {runResult.test_results.map((t) => (
                        <div
                          key={t.name}
                          className={cn(
                            "rounded-lg border p-3",
                            t.passed ? "border-emerald-200 bg-emerald-50" : "border-rose-200 bg-rose-50"
                          )}
                        >
                          <div className="flex items-center gap-2 text-sm font-medium">
                            {t.passed ? (
                              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
                            ) : (
                              <XCircle className="h-4 w-4 text-rose-600" />
                            )}
                            {t.name}
                            {t.timed_out ? (
                              <span className="rounded bg-rose-200 px-1.5 text-[10px] font-semibold text-rose-800">
                                TIMED OUT
                              </span>
                            ) : null}
                          </div>
                          {!t.passed && t.expected !== undefined ? (
                            <div className="mt-2 grid grid-cols-1 gap-2 text-xs sm:grid-cols-2">
                              <div>
                                <p className="font-semibold text-slate-600">Expected</p>
                                <pre className="mt-0.5 whitespace-pre-wrap rounded bg-white p-2 text-slate-800">{t.expected}</pre>
                              </div>
                              <div>
                                <p className="font-semibold text-slate-600">Actual</p>
                                <pre className="mt-0.5 whitespace-pre-wrap rounded bg-white p-2 text-slate-800">{t.actual || "(empty)"}</pre>
                              </div>
                            </div>
                          ) : null}
                          {t.stderr ? (
                            <pre className="mt-2 whitespace-pre-wrap rounded bg-white p-2 text-[11px] text-rose-700">{t.stderr}</pre>
                          ) : null}
                        </div>
                      ))}
                    </div>
                  ) : null}
                </>
              ) : (
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                  This is a design/code-review question. Write your answer, then compare it with the
                  model solution below — nothing is executed.
                </div>
              )}

              <div className="border-t border-slate-200 pt-4">
                {!revealed ? (
                  <button
                    onClick={reveal}
                    className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                  >
                    Reveal model solution
                  </button>
                ) : (
                  <div className="space-y-3">
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Model solution</p>
                    <pre className="overflow-x-auto rounded-lg bg-slate-900 p-4 text-xs leading-relaxed text-slate-100">
                      {revealed.solution}
                    </pre>
                    <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Why it works</p>
                    <p className="text-sm leading-relaxed text-slate-700">{revealed.explanation}</p>
                    {revealed.followups?.length ? (
                      <>
                        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">Follow-up questions</p>
                        <ul className="list-inside list-disc space-y-1 text-sm text-slate-700">
                          {revealed.followups.map((f, i) => (
                            <li key={i}>{f}</li>
                          ))}
                        </ul>
                      </>
                    ) : null}
                  </div>
                )}
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
