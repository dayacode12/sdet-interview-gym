"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertTriangle, ChevronDown, RotateCcw, Send, ShieldAlert } from "lucide-react";
import { api, type EvaluationResult } from "@/lib/api";
import { RubricDisplay } from "@/components/rubric";
import { cn } from "@/lib/utils";

interface ScenarioMeta {
  id: string;
  title: string;
  severity: string;
  topic: string;
  situation: string;
  interviewer_question: string;
}

interface SubmitResult {
  evaluation: EvaluationResult;
  key_points: string[];
  strong_answer: string;
  test_cases: { type: string; title: string; expected: string }[];
  api_checks: string;
  db_checks: string;
  job_checks: string;
  security_consideration: string;
  root_cause_paths: string[];
  followups: string[];
}

const SEVERITY_STYLES: Record<string, string> = {
  critical: "bg-rose-100 text-rose-800",
  high: "bg-orange-100 text-orange-800",
  medium: "bg-amber-100 text-amber-800",
  low: "bg-emerald-100 text-emerald-800",
};

export default function ScenariosPage() {
  const [scenarios, setScenarios] = useState<ScenarioMeta[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [selectedTopic, setSelectedTopic] = useState("all");
  const [selected, setSelected] = useState<ScenarioMeta | null>(null);
  const [answer, setAnswer] = useState("");
  const [result, setResult] = useState<SubmitResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<{ scenarios: ScenarioMeta[]; topics: string[] }>("/api/scenarios")
      .then((r) => {
        setScenarios(r.scenarios);
        setTopics(r.topics);
      })
      .catch((e) => setError(e.message));
  }, []);

  const filtered = useMemo(
    () => (selectedTopic === "all" ? scenarios : scenarios.filter((s) => s.topic === selectedTopic)),
    [scenarios, selectedTopic]
  );

  async function submit() {
    if (!selected || !answer.trim()) return;
    setBusy(true);
    setError(null);
    try {
      setResult(
        await api.post<SubmitResult>(`/api/scenarios/${selected.id}/submit`, { answer, duration_seconds: 0 })
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function reveal() {
    if (!selected) return;
    setBusy(true);
    try {
      setResult(
        await api.post<SubmitResult>(`/api/scenarios/${selected.id}/submit`, { answer: "", duration_seconds: 0 })
      );
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Scenario Simulator</h1>
        <p className="mt-1 text-sm text-slate-600">
          {scenarios.length} enterprise cybersecurity QA scenarios. Answer as you would in the
          interview — the rubric below scores your answer, then everything is revealed: key
          points, test cases, API/DB/job checks and a strong model answer.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-1.5">
        <button
          onClick={() => setSelectedTopic("all")}
          className={cn(
            "rounded-full px-3 py-1 text-xs font-medium",
            selectedTopic === "all" ? "bg-indigo-600 text-white" : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100"
          )}
        >
          all ({scenarios.length})
        </button>
        {topics.map((topic) => (
          <button
            key={topic}
            onClick={() => setSelectedTopic(topic)}
            className={cn(
              "rounded-full px-3 py-1 text-xs font-medium",
              selectedTopic === topic ? "bg-indigo-600 text-white" : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100"
            )}
          >
            {topic}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
        <aside className="max-h-[80vh] space-y-1.5 overflow-y-auto pr-1">
          {filtered.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setSelected(s);
                setResult(null);
                setAnswer("");
              }}
              className={cn(
                "w-full rounded-lg border p-3 text-left transition",
                selected?.id === s.id ? "border-indigo-400 bg-indigo-50" : "border-slate-200 bg-white hover:border-slate-300"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-sm font-medium text-slate-800">{s.title}</p>
                <span className={cn("shrink-0 rounded px-1.5 py-0.5 text-[10px] font-semibold", SEVERITY_STYLES[s.severity] ?? "bg-slate-100")}>
                  {s.severity}
                </span>
              </div>
              <p className="mt-0.5 text-[11px] text-slate-500">{s.topic}</p>
            </button>
          ))}
        </aside>

        <section className="space-y-4">
          {!selected ? (
            <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 text-sm text-slate-500">
              Pick a scenario to attempt.
            </div>
          ) : (
            <>
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <h2 className="font-semibold text-slate-900">{selected.title}</h2>
                <div className="mt-3 space-y-2 text-sm leading-relaxed text-slate-700">
                  <p>
                    <span className="font-semibold text-slate-500">Situation: </span>
                    {selected.situation}
                  </p>
                  <p className="rounded-lg bg-slate-50 p-3">
                    <span className="font-semibold text-slate-500">Interviewer: </span>
                    {selected.interviewer_question}
                  </p>
                </div>
              </div>

              {!result ? (
                <>
                  <textarea
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    rows={10}
                    placeholder="How would you test this? Walk through your approach, test cases, API/DB checks and security considerations…"
                    className="w-full rounded-xl border border-slate-300 bg-white p-4 text-sm leading-relaxed focus:border-indigo-500 focus:outline-none"
                  />
                  <div className="flex items-center gap-3">
                    <button
                      onClick={submit}
                      disabled={busy || !answer.trim()}
                      className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
                    >
                      <Send className="h-4 w-4" /> Submit answer
                    </button>
                    <button
                      onClick={reveal}
                      disabled={busy}
                      className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                    >
                      Skip and reveal
                    </button>
                  </div>
                </>
              ) : (
                <ScenarioResult scenario={selected} result={result} onRetry={() => { setResult(null); setAnswer(""); }} />
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
}

function ScenarioResult({
  scenario,
  result,
  onRetry,
}: {
  scenario: ScenarioMeta;
  result: SubmitResult;
  onRetry: () => void;
}) {
  const [showAnswer, setShowAnswer] = useState(false);
  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
        <h3 className="mb-3 font-semibold text-indigo-900">Rubric evaluation</h3>
        <RubricDisplay evaluation={result.evaluation} />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="font-semibold text-slate-900">Key points to cover</h3>
        <ul className="mt-2 space-y-1.5">
          {result.key_points.map((p, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
              <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-indigo-400" /> {p}
            </li>
          ))}
        </ul>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="font-semibold text-slate-900">Test cases</h3>
        <div className="mt-2 space-y-1.5">
          {result.test_cases.map((tc, i) => (
            <div key={i} className="rounded-lg bg-slate-50 p-2.5">
              <p className="text-sm font-medium text-slate-800">
                <span className="mr-1.5 rounded bg-indigo-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-indigo-700">
                  {tc.type}
                </span>
                {tc.title}
              </p>
              <p className="mt-0.5 text-xs text-slate-600">{tc.expected}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        {[
          { label: "API checks", body: result.api_checks },
          { label: "Database checks", body: result.db_checks },
          { label: "Job/scheduler checks", body: result.job_checks },
        ].map(({ label, body }) => (
          <div key={label} className="rounded-xl border border-slate-200 bg-white p-3">
            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
            <p className="mt-1 text-xs leading-relaxed text-slate-700">{body}</p>
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <h3 className="font-semibold text-slate-900">Likely root causes</h3>
        <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-700">
          {result.root_cause_paths.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </div>

      <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 p-4">
        <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />
        <p className="text-sm text-amber-900">{result.security_consideration}</p>
      </div>

      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
        <button
          onClick={() => setShowAnswer(!showAnswer)}
          className="flex w-full items-center justify-between font-semibold text-emerald-900"
        >
          Strong model answer
          <ChevronDown className={cn("h-4 w-4 transition-transform", showAnswer && "rotate-180")} />
        </button>
        {showAnswer ? (
          <p className="mt-2 text-sm leading-relaxed text-emerald-950">{result.strong_answer}</p>
        ) : null}
      </div>

      {result.followups?.length ? (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <h3 className="font-semibold text-slate-900">Follow-up questions they may ask</h3>
          <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-700">
            {result.followups.map((f, i) => (
              <li key={i}>{f}</li>
            ))}
          </ul>
        </div>
      ) : null}

      <button
        onClick={onRetry}
        className="flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
      >
        <RotateCcw className="h-4 w-4" /> Try again
      </button>
    </div>
  );
}
