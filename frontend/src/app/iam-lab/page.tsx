"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, BookOpen, CheckCircle2, ChevronDown, HelpCircle, XCircle } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface ModuleMeta {
  id: string;
  title: string;
  summary: string;
  concept_count: number;
  interview_question_count: number;
  test_case_count: number;
  quiz_count: number;
}

interface Concept {
  name: string;
  explanation: string;
  practical_example: string;
}

interface ModuleDetail {
  id: string;
  title: string;
  summary: string;
  concepts: Concept[];
  architecture: string;
  interview_questions: { question: string; answer: string }[];
  test_cases: { type: string; title: string; expected: string }[];
  quiz: { index: number; question: string; options: string[] }[];
}

export default function IamLabPage() {
  const [modules, setModules] = useState<ModuleMeta[]>([]);
  const [selected, setSelected] = useState<ModuleMeta | null>(null);
  const [detail, setDetail] = useState<ModuleDetail | null>(null);
  const [openConcept, setOpenConcept] = useState<number | null>(0);
  const [error, setError] = useState<string | null>(null);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, { chosen: number; correct: boolean; correct_index: number; explanation: string }>>({});

  useEffect(() => {
    api
      .get<{ modules: ModuleMeta[] }>("/api/iam/modules")
      .then((r) => {
        setModules(r.modules);
        // Deep link support: /iam-lab?module=<id> pre-selects that module.
        const wanted = new URLSearchParams(window.location.search).get("module");
        const match = wanted ? r.modules.find((m) => m.id === wanted) : null;
        if (match) select(match);
      })
      .catch((e) => setError(e.message));
  }, []);

  async function select(m: ModuleMeta) {
    setSelected(m);
    setQuizAnswers({});
    setOpenConcept(0);
    try {
      setDetail(await api.get<ModuleDetail>(`/api/iam/modules/${m.id}`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  async function answerQuiz(qIndex: number, choice: number) {
    if (!detail || quizAnswers[qIndex]) return;
    try {
      const r = await api.post<{ correct: boolean; correct_index: number; explanation: string }>(
        `/api/iam/modules/${detail.id}/quiz`,
        { question_index: qIndex, chosen_index: choice }
      );
      setQuizAnswers((prev) => ({ ...prev, [qIndex]: { chosen: choice, ...r } }));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">IAM Lab</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          {modules.length} modules covering identity and access management, IGA, privileged access,
          authentication protocols and DLP — the security domains the role tests hardest.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 p-3 text-sm text-rose-800 dark:text-rose-400">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[280px_1fr]">
        <aside className="space-y-1.5">
          {modules.map((m) => (
            <button
              key={m.id}
              onClick={() => select(m)}
              className={cn(
                "w-full rounded-lg border p-3 text-left transition",
                selected?.id === m.id ? "border-indigo-400 dark:border-indigo-500 bg-indigo-50 dark:bg-indigo-950" : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-600"
              )}
            >
              <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{m.title}</p>
              <p className="mt-0.5 text-[11px] text-slate-500 dark:text-slate-400">
                {m.concept_count} concepts · {m.quiz_count} quiz questions
              </p>
            </button>
          ))}
        </aside>

        <section className="space-y-5">
          {!selected || !detail ? (
            <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 text-sm text-slate-500 dark:text-slate-400">
              Pick a module to study.
            </div>
          ) : (
            <>
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
                <h2 className="font-semibold text-slate-900 dark:text-slate-100">{detail.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-700 dark:text-slate-300">{detail.summary}</p>
              </div>

              <div>
                <h3 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-slate-700 dark:text-slate-300">
                  <BookOpen className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Concepts
                </h3>
                <div className="space-y-1.5">
                  {detail.concepts.map((c, i) => (
                    <div key={i} className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
                      <button
                        onClick={() => setOpenConcept(openConcept === i ? null : i)}
                        className="flex w-full items-center justify-between p-3 text-left text-sm font-medium text-slate-800 dark:text-slate-100"
                      >
                        {c.name}
                        <ChevronDown className={cn("h-4 w-4 text-slate-400 dark:text-slate-500 transition-transform", openConcept === i && "rotate-180")} />
                      </button>
                      {openConcept === i ? (
                        <div className="space-y-2 border-t border-slate-100 dark:border-slate-800 px-3 pb-3 pt-2">
                          <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-300">{c.explanation}</p>
                          <p className="rounded-lg bg-indigo-50 dark:bg-indigo-950 p-2.5 text-xs leading-relaxed text-indigo-900 dark:text-indigo-300">
                            <strong>Practical example: </strong>
                            {c.practical_example}
                          </p>
                        </div>
                      ) : null}
                    </div>
                  ))}
                </div>
              </div>

              {detail.architecture ? (
                <div>
                  <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Architecture</h3>
                  <pre className="overflow-x-auto rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-900 p-4 text-[11px] leading-relaxed text-slate-100">
                    {detail.architecture}
                  </pre>
                </div>
              ) : null}

              <div>
                <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Interview Q&A</h3>
                <div className="space-y-2">
                  {detail.interview_questions.map((qa, i) => (
                    <div key={i} className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3">
                      <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{qa.question}</p>
                      <p className="mt-1.5 text-sm leading-relaxed text-slate-700 dark:text-slate-300">{qa.answer}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="mb-2 text-sm font-semibold text-slate-700 dark:text-slate-300">Test cases to know</h3>
                <div className="space-y-1.5">
                  {detail.test_cases.map((tc, i) => (
                    <div key={i} className="rounded-lg bg-slate-50 dark:bg-slate-800/60 p-2.5">
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-100">
                        <span className="mr-1.5 rounded bg-indigo-100 dark:bg-indigo-900 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-indigo-700 dark:text-indigo-400">
                          {tc.type}
                        </span>
                        {tc.title}
                      </p>
                      <p className="mt-0.5 text-xs text-slate-600 dark:text-slate-300">{tc.expected}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <h3 className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-slate-700 dark:text-slate-300">
                  <HelpCircle className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Quiz — graded server-side
                </h3>
                <div className="space-y-3">
                  {detail.quiz.map((q) => {
                    const answered = quizAnswers[q.index];
                    return (
                      <div key={q.index} className="rounded-lg border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3">
                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100">{q.question}</p>
                        <div className="mt-2 space-y-1.5">
                          {q.options.map((opt, oi) => {
                            const isCorrect = answered && oi === answered.correct_index;
                            const isWrongPick = answered && oi === answered.chosen && !answered.correct;
                            return (
                              <button
                                key={oi}
                                onClick={() => answerQuiz(q.index, oi)}
                                disabled={!!answered}
                                className={cn(
                                  "flex w-full items-center gap-2 rounded-lg border px-3 py-2 text-left text-sm transition",
                                  !answered && "border-slate-200 dark:border-slate-700 hover:border-indigo-300 dark:hover:border-indigo-800 hover:bg-indigo-50 dark:hover:bg-indigo-950",
                                  answered && isCorrect && "border-emerald-300 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950 text-emerald-800 dark:text-emerald-400",
                                  answered && isWrongPick && "border-rose-300 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 text-rose-800 dark:text-rose-400",
                                  answered && !isCorrect && !isWrongPick && "border-slate-200 dark:border-slate-700 text-slate-500 dark:text-slate-400"
                                )}
                              >
                                {answered && isCorrect ? <CheckCircle2 className="h-4 w-4 shrink-0" /> : null}
                                {answered && isWrongPick ? <XCircle className="h-4 w-4 shrink-0" /> : null}
                                {opt}
                              </button>
                            );
                          })}
                        </div>
                        {answered ? (
                          <p className="mt-2 rounded bg-slate-50 dark:bg-slate-800/60 p-2 text-xs text-slate-700 dark:text-slate-300">{answered.explanation}</p>
                        ) : null}
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </section>
      </div>
    </div>
  );
}
