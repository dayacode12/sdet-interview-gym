"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, ChevronDown, Code2, MessageSquare, Play } from "lucide-react";
import { api } from "@/lib/api";
import { cn, difficultyBadge } from "@/lib/utils";

interface Exercise {
  id: string;
  title: string;
  tool: string;
  difficulty: string;
  exercise: string;
}

interface ExerciseDetail extends Exercise {
  starter_code?: string;
}

interface Revealed {
  solution: string;
  explanation: string;
  followups: string[];
}

interface ArchQA {
  id: string;
  question: string;
  model_answer: string;
}

export default function AutomationLabPage() {
  const [exercises, setExercises] = useState<Exercise[]>([]);
  const [archQA, setArchQA] = useState<ArchQA[]>([]);
  const [selected, setSelected] = useState<Exercise | null>(null);
  const [detail, setDetail] = useState<ExerciseDetail | null>(null);
  const [revealed, setRevealed] = useState<Revealed | null>(null);
  const [openQA, setOpenQA] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<{ exercises: Exercise[] }>("/api/automation/exercises").then((r) => setExercises(r.exercises)).catch((e) => setError(e.message));
    api.get<{ questions: ArchQA[] }>("/api/automation/architecture").then((r) => setArchQA(r.questions)).catch(() => {});
  }, []);

  async function select(e: Exercise) {
    setSelected(e);
    setRevealed(null);
    try {
      setDetail(await api.get<ExerciseDetail>(`/api/automation/exercises/${e.id}`));
    } catch (err) {
      setError((err as Error).message);
    }
  }

  async function reveal() {
    if (!selected) return;
    try {
      setRevealed(await api.post<Revealed>(`/api/automation/exercises/${selected.id}/reveal`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const tools = Array.from(new Set(exercises.map((e) => e.tool)));

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Automation Lab</h1>
        <p className="mt-1 text-sm text-slate-600">
          {exercises.length} hands-on exercises ({tools.join(", ")}) plus {archQA.length} framework
          architecture questions. Exercises are code review — write your attempt, then compare with
          the model solution. Nothing here executes; use the Java Lab for runnable problems.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
        <aside className="max-h-[80vh] space-y-3 overflow-y-auto pr-1">
          {tools.map((tool) => (
            <div key={tool}>
              <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">{tool}</p>
              <div className="space-y-1.5">
                {exercises.filter((e) => e.tool === tool).map((e) => (
                  <button
                    key={e.id}
                    onClick={() => select(e)}
                    className={cn(
                      "w-full rounded-lg border p-2.5 text-left transition",
                      selected?.id === e.id ? "border-indigo-400 bg-indigo-50" : "border-slate-200 bg-white hover:border-slate-300"
                    )}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <p className="text-[13px] font-medium leading-snug text-slate-800">{e.title}</p>
                      <span className={cn("shrink-0 rounded px-1.5 py-0.5 text-[10px] font-semibold", difficultyBadge(e.difficulty))}>
                        {e.difficulty}
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
              Pick an exercise to attempt.
            </div>
          ) : (
            <>
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <h2 className="font-semibold text-slate-900">{selected.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-700">{detail?.exercise ?? selected.exercise}</p>
              </div>

              {detail?.starter_code ? (
                <div>
                  <p className="mb-1.5 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <Code2 className="h-3.5 w-3.5" /> Starter code
                  </p>
                  <pre className="overflow-x-auto rounded-lg border border-slate-200 bg-slate-900 p-4 text-xs leading-relaxed text-slate-100">
                    {detail.starter_code}
                  </pre>
                </div>
              ) : null}

              {!revealed ? (
                <button
                  onClick={reveal}
                  className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
                >
                  Reveal model solution
                </button>
              ) : (
                <div className="space-y-3">
                  <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    <Play className="h-3.5 w-3.5" /> Model solution
                  </p>
                  <pre className="overflow-x-auto rounded-lg border border-slate-200 bg-slate-900 p-4 text-xs leading-relaxed text-slate-100">
                    {revealed.solution}
                  </pre>
                  <p className="text-sm leading-relaxed text-slate-700">{revealed.explanation}</p>
                  {revealed.followups?.length ? (
                    <ul className="list-inside list-disc space-y-1 text-sm text-slate-700">
                      {revealed.followups.map((f, i) => (
                        <li key={i}>{f}</li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              )}
            </>
          )}
        </section>
      </div>

      <section>
        <h2 className="mb-3 flex items-center gap-1.5 text-lg font-semibold">
          <MessageSquare className="h-5 w-5 text-indigo-600" /> Framework architecture Q&A
        </h2>
        <div className="space-y-1.5">
          {archQA.map((qa, i) => (
            <div key={qa.id} className="rounded-lg border border-slate-200 bg-white">
              <button
                onClick={() => setOpenQA(openQA === i ? null : i)}
                className="flex w-full items-center justify-between p-3 text-left text-sm font-medium text-slate-800"
              >
                {qa.question}
                <ChevronDown className={cn("h-4 w-4 text-slate-400 transition-transform", openQA === i && "rotate-180")} />
              </button>
              {openQA === i ? (
                <p className="border-t border-slate-100 px-3 pb-3 pt-2 text-sm leading-relaxed text-slate-700">
                  {qa.model_answer}
                </p>
              ) : null}
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
