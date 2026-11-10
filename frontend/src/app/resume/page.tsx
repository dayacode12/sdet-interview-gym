"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, ChevronDown, UserCheck } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface QuestionMeta {
  id: string;
  title: string;
  category: string;
  needs_candidate_detail: boolean;
}

interface QuestionDetail {
  id: string;
  title: string;
  category: string;
  needs_candidate_detail: boolean;
  guidance: string;
  star: { situation: string; task: string; action: string; result: string };
  strong_answer: string;
  followups: string[];
}

export default function ResumePage() {
  const [questions, setQuestions] = useState<QuestionMeta[]>([]);
  const [selected, setSelected] = useState<QuestionMeta | null>(null);
  const [detail, setDetail] = useState<QuestionDetail | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<{ questions: QuestionMeta[] }>("/api/resume/questions").then((r) => setQuestions(r.questions)).catch((e) => setError(e.message));
  }, []);

  async function select(q: QuestionMeta) {
    setSelected(q);
    setShowAnswer(false);
    try {
      setDetail(await api.get<QuestionDetail>(`/api/resume/questions/${q.id}`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const categories = Array.from(new Set(questions.map((q) => q.category)));

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Resume Deep Dive</h1>
        <p className="mt-1 text-sm text-slate-600">
          {questions.length} questions drawn from your actual resume. Questions flagged
          <span className="mx-1 rounded bg-amber-100 px-1.5 py-0.5 text-xs font-medium text-amber-800">needs your details</span>
          contain gaps only you can fill — the platform will not invent numbers or events for you.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
        <aside className="max-h-[80vh] space-y-3 overflow-y-auto pr-1">
          {categories.map((cat) => (
            <div key={cat}>
              <p className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-slate-500">{cat}</p>
              <div className="space-y-1.5">
                {questions.filter((q) => q.category === cat).map((q) => (
                  <button
                    key={q.id}
                    onClick={() => select(q)}
                    className={cn(
                      "w-full rounded-lg border p-2.5 text-left transition",
                      selected?.id === q.id ? "border-indigo-400 bg-indigo-50" : "border-slate-200 bg-white hover:border-slate-300"
                    )}
                  >
                    <p className="text-[13px] font-medium leading-snug text-slate-800">{q.title}</p>
                    {q.needs_candidate_detail ? (
                      <span className="mt-1 inline-flex items-center gap-1 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-medium text-amber-800">
                        <UserCheck className="h-2.5 w-2.5" /> needs your details
                      </span>
                    ) : null}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </aside>

        <section className="space-y-4">
          {!selected || !detail ? (
            <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 text-sm text-slate-500">
              Pick a resume question to rehearse.
            </div>
          ) : (
            <>
              <div className="rounded-xl border border-slate-200 bg-white p-4">
                <h2 className="font-semibold text-slate-900">{detail.title}</h2>
                <p className="mt-2 text-sm leading-relaxed text-slate-700">{detail.guidance}</p>
              </div>

              <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">
                <h3 className="mb-2 text-sm font-semibold text-indigo-900">STAR scaffold</h3>
                <dl className="space-y-2">
                  {(
                    [
                      ["Situation", detail.star.situation],
                      ["Task", detail.star.task],
                      ["Action", detail.star.action],
                      ["Result", detail.star.result],
                    ] as const
                  ).map(([label, body]) => (
                    <div key={label} className="rounded-lg bg-white/70 p-2.5">
                      <dt className="text-xs font-semibold text-indigo-700">{label}</dt>
                      <dd className="mt-0.5 text-sm text-slate-700">{body}</dd>
                    </div>
                  ))}
                </dl>
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
                  <p className="mt-2 text-sm leading-relaxed text-emerald-950">{detail.strong_answer}</p>
                ) : null}
              </div>

              {detail.followups?.length ? (
                <div className="rounded-xl border border-slate-200 bg-white p-4">
                  <h3 className="text-sm font-semibold text-slate-900">Follow-up questions they may ask</h3>
                  <ul className="mt-2 list-inside list-disc space-y-1 text-sm text-slate-700">
                    {detail.followups.map((f, i) => (
                      <li key={i}>{f}</li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </>
          )}
        </section>
      </div>
    </div>
  );
}
