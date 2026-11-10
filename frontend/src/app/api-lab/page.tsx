"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, ChevronDown, Database, Send, Webhook } from "lucide-react";
import { api } from "@/lib/api";
import { CodeEditor } from "@/components/code-editor";
import { cn, difficultyBadge } from "@/lib/utils";

interface Challenge {
  id: string;
  title: string;
  difficulty: string;
  tool: string;
  exercise: string;
}

interface Revealed {
  solution: string;
  explanation: string;
  followups: string[];
}

const DEFAULT_REQUEST = `// REST Assured practice — write your test below.
given()
    .header("Authorization", "Bearer " + token)
    .queryParam("department", "IT")
.when()
    .get("/api/users")
.then()
    .statusCode(200)
    .body("size()", greaterThan(0));`;

export default function ApiLabPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [selected, setSelected] = useState<Challenge | null>(null);
  const [revealed, setRevealed] = useState<Revealed | null>(null);
  const [code, setCode] = useState(DEFAULT_REQUEST);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<{ exercises: Challenge[] }>("/api/automation/exercises").then((r) => {
      setChallenges(r.exercises.filter((e) => e.tool === "REST Assured"));
    }).catch((e) => setError(e.message));
  }, []);

  async function reveal() {
    if (!selected) return;
    try {
      setRevealed(await api.post<Revealed>(`/api/automation/exercises/${selected.id}/reveal`));
    } catch (e) {
      setError((e as Error).message);
    }
  }

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">API Testing Lab</h1>
        <p className="mt-1 text-sm text-slate-600">
          REST Assured exercises: authentication/authorization matrices, request chaining,
          schema validation and database cross-checks — the four themes API interviews probe.
          Write your attempt in the editor, then compare with the model solution.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="flex items-start gap-2 text-sm text-slate-700">
          <Webhook className="mt-0.5 h-4 w-4 shrink-0 text-indigo-600" />
          <div>
            <p className="font-medium">The 401 vs 403 contract — assert both, never conflate:</p>
            <ul className="mt-1.5 list-inside list-disc text-xs text-slate-600">
              <li>401 Unauthorized = missing or invalid credentials (not authenticated)</li>
              <li>403 Forbidden = valid credentials that lack permission (not authorized)</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[300px_1fr]">
        <aside className="max-h-[80vh] space-y-1.5 overflow-y-auto pr-1">
          {challenges.map((c) => (
            <button
              key={c.id}
              onClick={() => {
                setSelected(c);
                setRevealed(null);
              }}
              className={cn(
                "w-full rounded-lg border p-3 text-left transition",
                selected?.id === c.id ? "border-indigo-400 bg-indigo-50" : "border-slate-200 bg-white hover:border-slate-300"
              )}
            >
              <div className="flex items-center justify-between gap-2">
                <p className="text-[13px] font-medium leading-snug text-slate-800">{c.title}</p>
                <span className={cn("shrink-0 rounded px-1.5 py-0.5 text-[10px] font-semibold", difficultyBadge(c.difficulty))}>
                  {c.difficulty}
                </span>
              </div>
            </button>
          ))}
        </aside>

        <section className="space-y-4">
          {selected ? (
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <h2 className="font-semibold text-slate-900">{selected.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-slate-700">{selected.exercise}</p>
            </div>
          ) : (
            <div className="flex h-40 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 text-sm text-slate-500">
              Pick an exercise on the left.
            </div>
          )}

          <CodeEditor value={code} onChange={setCode} language="java" height={320} />

          {selected && !revealed ? (
            <button
              onClick={reveal}
              className="flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              <Send className="h-4 w-4" /> Reveal model solution
            </button>
          ) : null}

          {revealed ? (
            <div className="space-y-3">
              <p className="flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-slate-500">
                <Database className="h-3.5 w-3.5" /> Model solution
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
          ) : null}
        </section>
      </div>
    </div>
  );
}
