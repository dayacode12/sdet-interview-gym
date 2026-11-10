"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, RotateCcw, Volume2 } from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Card {
  id: string;
  front: string;
  back: string;
  topic: string;
}

interface CardState {
  confidence: string;
  known: boolean;
  reviews: number;
}

const CONFIDENCES = [
  { key: "again", label: "Again", style: "bg-rose-600 hover:bg-rose-700" },
  { key: "hard", label: "Hard", style: "bg-amber-500 hover:bg-amber-600" },
  { key: "good", label: "Good", style: "bg-emerald-600 hover:bg-emerald-700" },
  { key: "easy", label: "Easy", style: "bg-indigo-600 hover:bg-indigo-700" },
] as const;

export default function FlashcardsPage() {
  const [cards, setCards] = useState<Card[]>([]);
  const [topics, setTopics] = useState<string[]>([]);
  const [states, setStates] = useState<Record<string, CardState>>({});
  const [topic, setTopic] = useState("all");
  const [onlyUnknown, setOnlyUnknown] = useState(false);
  const [index, setIndex] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadStates = useCallback(() => {
    api.get<{ states: Record<string, CardState> }>("/api/flashcards/states").then((r) => setStates(r.states)).catch(() => {});
  }, []);

  useEffect(() => {
    api.get<{ cards: Card[]; topics: string[] }>("/api/flashcards").then((r) => {
      setCards(r.cards);
      setTopics(r.topics);
    }).catch((e) => setError(e.message));
    loadStates();
  }, [loadStates]);

  const deck = useMemo(() => {
    let d = topic === "all" ? cards : cards.filter((c) => c.topic === topic);
    if (onlyUnknown) d = d.filter((c) => !states[c.id]?.known);
    return d;
  }, [cards, topic, onlyUnknown, states]);

  const card = deck[index % Math.max(1, deck.length)];

  async function review(confidence: string) {
    if (!card) return;
    try {
      await api.post(`/api/flashcards/${card.id}/review`, { confidence });
      loadStates();
    } catch (e) {
      setError((e as Error).message);
    }
    setFlipped(false);
    setIndex((i) => (i + 1) % Math.max(1, deck.length));
  }

  async function reset() {
    try {
      await api.post("/api/flashcards/reset");
      setStates({});
      setIndex(0);
      setFlipped(false);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const known = Object.values(states).filter((s) => s.known).length;
  const reviewed = Object.keys(states).length;

  return (
    <div className="space-y-6">
      <header className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">Flashcards</h1>
          <p className="mt-1 text-sm text-slate-600">
            {cards.length} cards across {topics.length} topics. {reviewed} reviewed · {known} known.
          </p>
        </div>
        <button
          onClick={reset}
          className="flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-50"
        >
          <RotateCcw className="h-3.5 w-3.5" /> Reset progress
        </button>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="flex flex-wrap items-center gap-1.5">
        <button
          onClick={() => { setTopic("all"); setIndex(0); setFlipped(false); }}
          className={cn(
            "rounded-full px-3 py-1 text-xs font-medium",
            topic === "all" ? "bg-indigo-600 text-white" : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100"
          )}
        >
          all ({cards.length})
        </button>
        {topics.map((t) => {
          const total = cards.filter((c) => c.topic === t).length;
          const knownT = cards.filter((c) => c.topic === t && states[c.id]?.known).length;
          return (
            <button
              key={t}
              onClick={() => { setTopic(t); setIndex(0); setFlipped(false); }}
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium",
                topic === t ? "bg-indigo-600 text-white" : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100"
              )}
            >
              {t} {knownT}/{total}
            </button>
          );
        })}
        <label className="ml-2 flex items-center gap-1.5 text-xs text-slate-600">
          <input
            type="checkbox"
            checked={onlyUnknown}
            onChange={(e) => { setOnlyUnknown(e.target.checked); setIndex(0); setFlipped(false); }}
            className="h-3.5 w-3.5 accent-indigo-600"
          />
          only cards needing revision
        </label>
      </div>

      {card ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>
              Card {index + 1} of {deck.length} · {card.topic}
            </span>
            {states[card.id] ? (
              <span>
                reviewed {states[card.id].reviews}× · last: {states[card.id].confidence}
              </span>
            ) : (
              <span>new card</span>
            )}
          </div>

          <button
            onClick={() => setFlipped(!flipped)}
            className="flex min-h-64 w-full flex-col items-center justify-center rounded-2xl border-2 border-indigo-200 bg-white p-8 text-center shadow-sm transition hover:border-indigo-300"
          >
            <p className="text-xs font-semibold uppercase tracking-wide text-indigo-500">
              {flipped ? "Answer" : "Question"}
            </p>
            <p className="mt-4 max-w-2xl text-lg font-medium leading-relaxed text-slate-900">
              {flipped ? card.back : card.front}
            </p>
            {!flipped ? (
              <p className="mt-6 text-xs text-slate-400">Click to flip</p>
            ) : null}
          </button>

          {flipped ? (
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {CONFIDENCES.map((c) => (
                <button
                  key={c.key}
                  onClick={() => review(c.key)}
                  className={cn("rounded-lg px-4 py-2.5 text-sm font-medium text-white transition", c.style)}
                >
                  {c.label}
                </button>
              ))}
            </div>
          ) : (
            <p className="flex items-center justify-center gap-1.5 text-xs text-slate-400">
              <Volume2 className="h-3 w-3" /> Say the answer out loud, then flip and grade yourself honestly.
            </p>
          )}
        </div>
      ) : (
        <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 text-sm text-slate-500">
          No cards match this filter — everything here is marked known. Switch topics or uncheck the filter.
        </div>
      )}
    </div>
  );
}
