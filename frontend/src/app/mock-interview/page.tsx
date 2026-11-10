"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { AlertTriangle, ChevronLeft, ChevronRight, Clock, Flag, Play, Square } from "lucide-react";
import { api, type EvaluationResult } from "@/lib/api";
import { RubricDisplay } from "@/components/rubric";
import { cn } from "@/lib/utils";

interface Section {
  id: string;
  title: string;
  minutes: number;
  weight: number;
  start_minute: number;
  question_count: number;
}

interface Question {
  id: string;
  section_id: string;
  prompt: string;
  guidance: string;
}

interface AnswerResponse {
  evaluation: EvaluationResult;
  model_answer: string;
  keywords: string[];
  delivery_note: string | null;
}

interface Research {
  sources: { source: string; reports: string; what_it_means: string }[];
  process: { rounds: { round: number; name: string; detail: string }[]; note: string };
  reported_themes: string[];
  disclaimer: string;
}

interface FinishResult {
  session_id: number;
  total_score: number;
  dimension_scores: Record<string, number>;
  sections: { section_id: string; title: string; weight: number; answered: number; question_count: number; average_score: number | null }[];
  answered_questions: number;
  total_questions: number;
  weakest_dimension: string | null;
  advice: string;
}

function fmt(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
}

export default function MockInterviewPage() {
  const [plan, setPlan] = useState<{ sections: Section[]; total_minutes: number; total_questions: number } | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [research, setResearch] = useState<Research | null>(null);
  const [sessionId, setSessionId] = useState<number | null>(null);
  const [index, setIndex] = useState(0);
  const [answer, setAnswer] = useState("");
  const [lastEval, setLastEval] = useState<AnswerResponse | null>(null);
  const [finishResult, setFinishResult] = useState<FinishResult | null>(null);
  const [remaining, setRemaining] = useState(3600);
  const [running, setRunning] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const questionStart = useRef<number>(0);

  useEffect(() => {
    api.get<{ sections: Section[]; total_minutes: number; total_questions: number }>("/api/mock/plan").then(setPlan).catch((e) => setError(e.message));
    api.get<{ questions: Question[] }>("/api/mock/questions").then((r) => setQuestions(r.questions)).catch((e) => setError(e.message));
    api.get<Research>("/api/mock/research").then(setResearch).catch(() => {});
  }, []);

  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          setRunning(false);
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [running]);

  const currentQuestion = questions[index];
  const currentSection = plan?.sections.find((s) => s.id === currentQuestion?.section_id);

  const start = useCallback(async () => {
    setBusy(true);
    setError(null);
    try {
      const s = await api.post<{ session_id: number }>("/api/mock/start", {});
      setSessionId(s.session_id);
      setIndex(0);
      setAnswer("");
      setLastEval(null);
      setFinishResult(null);
      setRemaining(3600);
      setRunning(true);
      questionStart.current = Date.now();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }, []);

  async function submitAnswer() {
    if (!sessionId || !currentQuestion) return;
    setBusy(true);
    try {
      const elapsed = Math.round((Date.now() - questionStart.current) / 1000);
      const resp = await api.post<AnswerResponse>(`/api/mock/${sessionId}/answer`, {
        question_id: currentQuestion.id,
        answer,
        elapsed_seconds: elapsed,
      });
      setLastEval(resp);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function nextQuestion() {
    setLastEval(null);
    setAnswer("");
    setIndex((i) => Math.min(i + 1, questions.length - 1));
    questionStart.current = Date.now();
  }

  async function finish() {
    if (!sessionId) return;
    setBusy(true);
    setRunning(false);
    try {
      setFinishResult(await api.post<FinishResult>(`/api/mock/${sessionId}/finish`, {}));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (!plan || questions.length === 0) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Mock Interview</h1>
        {error ? (
          <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
            <AlertTriangle className="h-4 w-4" /> {error}
          </div>
        ) : (
          <p className="text-sm text-slate-500">Loading…</p>
        )}
      </div>
    );
  }

  if (!sessionId) {
    return (
      <div className="space-y-6">
        <header>
          <h1 className="text-2xl font-bold">Mock Interview</h1>
          <p className="mt-1 text-sm text-slate-600">
            A 60-minute simulated interview: {plan.total_questions} questions across{" "}
            {plan.sections.length} sections. One timer runs for the whole session, just like the
            real thing. The introduction is a warm-up and is not scored.
          </p>
        </header>

        <div className="space-y-2">
          {plan.sections.map((s) => (
            <div key={s.id} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3">
              <div>
                <p className="text-sm font-medium text-slate-800">{s.title}</p>
                <p className="text-xs text-slate-500">
                  starts at minute {s.start_minute} · {s.question_count} questions
                </p>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold text-slate-700">{s.minutes} min</p>
                <p className="text-xs text-slate-500">
                  {s.weight > 0 ? `${Math.round(s.weight * 100)}% of score` : "unscored"}
                </p>
              </div>
            </div>
          ))}
        </div>

        {research ? (
          <section className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="text-sm font-semibold text-slate-900">
              Field research — what candidates report about Schwab interviews
            </h2>
            <div className="mt-3 grid grid-cols-1 gap-2 sm:grid-cols-2">
              {research.process.rounds.map((r) => (
                <div key={r.round} className="rounded-lg bg-slate-50 p-3">
                  <p className="text-xs font-semibold text-slate-800">
                    Round {r.round}: {r.name}
                  </p>
                  <p className="mt-1 text-[11px] leading-relaxed text-slate-600">{r.detail}</p>
                </div>
              ))}
            </div>
            <ul className="mt-3 space-y-1.5">
              {research.reported_themes.map((theme, i) => (
                <li key={i} className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-700">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
                  {theme}
                </li>
              ))}
            </ul>
            <p className="mt-3 border-t border-slate-100 pt-2 text-[11px] leading-relaxed text-slate-500">
              {research.disclaimer}
            </p>
            <details className="mt-2">
              <summary className="cursor-pointer text-[11px] font-medium text-indigo-600">
                Show reported sources
              </summary>
              <ul className="mt-2 space-y-2">
                {research.sources.map((s, i) => (
                  <li key={i} className="rounded-lg bg-slate-50 p-2.5">
                    <p className="text-[11px] font-semibold text-slate-800">{s.source}</p>
                    <p className="mt-0.5 text-[11px] leading-relaxed text-slate-600">{s.reports}</p>
                    <p className="mt-1 text-[11px] leading-relaxed text-indigo-800">{s.what_it_means}</p>
                  </li>
                ))}
              </ul>
            </details>
          </section>
        ) : null}

        <button
          onClick={start}
          disabled={busy}
          className="flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
        >
          <Play className="h-4 w-4" /> Start the 60-minute interview
        </button>
        {error ? (
          <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
            <AlertTriangle className="h-4 w-4" /> {error}
          </div>
        ) : null}
      </div>
    );
  }

  if (finishResult) {
    return (
      <div className="space-y-6">
        <header>
          <h1 className="text-2xl font-bold">Interview results</h1>
          <p className="mt-1 text-sm text-slate-600">
            {finishResult.answered_questions} of {finishResult.total_questions} questions answered.
          </p>
        </header>

        <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-6 text-center">
          <p className="text-xs font-semibold uppercase tracking-wide text-indigo-600">Weighted total score</p>
          <p className="mt-1 text-4xl font-bold text-indigo-900">{finishResult.total_score.toFixed(1)}</p>
          <p className="mt-1 text-xs text-slate-600">/ 100</p>
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-5">
          {Object.entries(finishResult.dimension_scores).map(([dim, score]) => (
            <div key={dim} className="rounded-xl border border-slate-200 bg-white p-3 text-center">
              <p className="text-[11px] font-medium text-slate-500">{dim.replace(/_/g, " ")}</p>
              <p className="mt-1 text-lg font-bold text-slate-800">{score.toFixed(1)}</p>
            </div>
          ))}
        </div>

        <div className="space-y-2">
          {finishResult.sections.map((s) => (
            <div key={s.section_id} className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3">
              <div>
                <p className="text-sm font-medium text-slate-800">{s.title}</p>
                <p className="text-xs text-slate-500">
                  {s.answered}/{s.question_count} answered · {Math.round(s.weight * 100)}% weight
                </p>
              </div>
              <p className="text-sm font-semibold text-slate-700">
                {s.average_score !== null ? s.average_score.toFixed(1) : "—"}
              </p>
            </div>
          ))}
        </div>

        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          {finishResult.advice}
        </div>

        <button
          onClick={() => setSessionId(null)}
          className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          Back to setup
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold">{currentSection?.title ?? "Mock Interview"}</h1>
          <p className="text-xs text-slate-500">
            Question {index + 1} of {questions.length} · section {Math.round(((currentSection?.weight ?? 0) * 100))}% of final score
          </p>
        </div>
        <div
          className={cn(
            "flex items-center gap-2 rounded-lg px-4 py-2 font-mono text-lg font-bold",
            remaining > 600 ? "bg-slate-100 text-slate-800" : "bg-rose-100 text-rose-800"
          )}
        >
          <Clock className="h-4 w-4" />
          {fmt(remaining)}
          {!running && remaining > 0 ? (
            <button onClick={() => setRunning(true)} className="ml-1 text-xs text-indigo-600 underline">
              resume
            </button>
          ) : null}
        </div>
      </header>

      <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200">
        <div className="h-full bg-indigo-500 transition-all" style={{ width: `${(100 * (index + 1)) / questions.length}%` }} />
      </div>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <p className="font-medium leading-relaxed text-slate-900">{currentQuestion?.prompt}</p>
        <p className="mt-2 rounded-lg bg-slate-50 p-2.5 text-xs text-slate-600">{currentQuestion?.guidance}</p>
      </div>

      {lastEval ? (
        <>
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
              <h3 className="mb-3 font-semibold text-indigo-900">Your answer — evaluated</h3>
              <RubricDisplay evaluation={lastEval.evaluation} />
            </div>
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4">
              <h3 className="mb-2 font-semibold text-emerald-900">Model answer</h3>
              <p className="text-sm leading-relaxed text-emerald-950">{lastEval.model_answer}</p>
              {lastEval.delivery_note ? (
                <div className="mt-3 rounded-lg border border-amber-200 bg-amber-50 p-2.5">
                  <p className="text-[11px] font-semibold uppercase tracking-wide text-amber-700">
                    What interviewers probe (per reported research)
                  </p>
                  <p className="mt-1 text-xs leading-relaxed text-amber-900">{lastEval.delivery_note}</p>
                </div>
              ) : null}
              <div className="mt-3 flex flex-wrap gap-1">
                {lastEval.keywords.map((k) => (
                  <span key={k} className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-medium text-emerald-800">
                    {k}
                  </span>
                ))}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={nextQuestion}
              disabled={index >= questions.length - 1}
              className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              Next question <ChevronRight className="h-4 w-4" />
            </button>
            <button
              onClick={finish}
              disabled={busy}
              className="flex items-center gap-1.5 rounded-lg border border-rose-300 bg-white px-4 py-2 text-sm font-medium text-rose-700 hover:bg-rose-50"
            >
              <Flag className="h-4 w-4" /> Finish interview
            </button>
          </div>
        </>
      ) : (
        <>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            rows={9}
            placeholder="Answer as you would out loud in the interview…"
            className="w-full rounded-xl border border-slate-300 bg-white p-4 text-sm leading-relaxed focus:border-indigo-500 focus:outline-none"
          />
          <div className="flex items-center gap-3">
            <button
              onClick={submitAnswer}
              disabled={busy || !answer.trim()}
              className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {busy ? "Scoring…" : "Submit answer"}
            </button>
            {index > 0 ? (
              <button
                onClick={() => setIndex((i) => Math.max(0, i - 1))}
                className="flex items-center gap-1 rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
              >
                <ChevronLeft className="h-4 w-4" /> Back
              </button>
            ) : null}
            <button
              onClick={() => {
                nextQuestion();
              }}
              className="text-sm text-slate-500 underline hover:text-slate-700"
            >
              Skip this question
            </button>
          </div>
        </>
      )}

      {remaining === 0 ? (
        <div className="flex items-center gap-2 rounded-xl border border-rose-300 bg-rose-50 p-4 text-sm text-rose-800">
          <Square className="h-4 w-4" /> Time is up. Finish the interview to see your results.
        </div>
      ) : null}
    </div>
  );
}
