"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  BookMarked,
  Brain,
  Compass,
  Eye,
  EyeOff,
  Gauge,
  Library,
  Scale,
  Sparkles,
  Zap,
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Section {
  id: string;
  title: string;
  items: string[];
}

interface StatusCode {
  code: string;
  meaning: string;
}

interface TrickProgram {
  n: number;
  letter: string;
  keyword: string;
  name: string;
  hook: string;
  trick: string;
  how: string;
  structure: string;
  remember: string[];
  code?: string;
  contrast?: { left: string; right: string; rows: string[][] };
  practice_id: string;
}

interface Comparison {
  title: string;
  headers?: string[];
  rows?: string[][];
  lines?: string[];
}

interface JavaTricks {
  mnemonic: string;
  story: string;
  final_line: string;
  final_note: string;
  programs: TrickProgram[];
  comparisons: Comparison[];
  traps: { program: string; trap: string; fix: string }[];
  complexity: { n: number; time: string; space: string; best?: boolean }[];
  flashcards: { q: string; a: string }[];
  big_picture: { need: string; use: string }[];
}

function Heading({ icon: Icon, children }: { icon: typeof Zap; children: React.ReactNode }) {
  return (
    <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
      <Icon className="h-4 w-4 text-indigo-600" />
      {children}
    </h2>
  );
}

export default function CheatsheetPage() {
  const [sections, setSections] = useState<Section[]>([]);
  const [statusCodes, setStatusCodes] = useState<StatusCode[]>([]);
  const [tricks, setTricks] = useState<JavaTricks | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [revealed, setRevealed] = useState<Set<number>>(new Set());

  useEffect(() => {
    api
      .get<{ sections: Section[]; http_status_codes: StatusCode[]; java_tricks: JavaTricks }>(
        "/api/cheatsheet"
      )
      .then((r) => {
        setSections(r.sections);
        setStatusCodes(r.http_status_codes);
        setTricks(r.java_tricks ?? null);
      })
      .catch((e) => setError(e.message));
  }, []);

  const toggleCard = (i: number) =>
    setRevealed((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">Interview Cheat Sheet</h1>
        <p className="mt-1 text-sm text-slate-600">
          Last-mile revision: the fifteen-minute pass through everything that matters. Read it the
          morning of the interview.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      {tricks ? (
        <>
          {/* Master memory framework */}
          <section className="overflow-hidden rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 p-5 text-white">
            <div className="flex items-center gap-2">
              <Brain className="h-5 w-5" />
              <h2 className="text-sm font-semibold uppercase tracking-wide">
                Java memory tricks — 10 core programs
              </h2>
            </div>
            <p className="mt-3 font-mono text-xl font-bold tracking-widest">{tricks.mnemonic}</p>
            <p className="mt-1 text-sm text-indigo-100">&ldquo;{tricks.story}&rdquo;</p>
          </section>

          {/* Master framework table — the quick scan */}
          <section className="space-y-3">
            <Heading icon={Zap}>Master framework — the 10-second scan</Heading>
            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-500">
                    <th className="py-1.5 pr-4 font-medium">#</th>
                    <th className="py-1.5 pr-4 font-medium">Keyword</th>
                    <th className="py-1.5 pr-4 font-medium">Trick</th>
                    <th className="py-1.5 font-medium">Data structure</th>
                  </tr>
                </thead>
                <tbody>
                  {tricks.programs.map((p) => (
                    <tr key={p.n} className="border-t border-slate-100">
                      <td className="py-1.5 pr-4 font-mono font-semibold text-indigo-700">{p.n}</td>
                      <td className="py-1.5 pr-4 font-medium text-slate-800">{p.keyword}</td>
                      <td className="py-1.5 pr-4 text-slate-600">{p.trick}</td>
                      <td className="py-1.5 font-mono text-slate-600">{p.structure}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Cheat codes — one card per program */}
          <section className="space-y-3">
            <Heading icon={Sparkles}>Cheat codes — one-line memory hooks</Heading>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {tricks.programs.map((p) => (
                <article key={p.n} className="rounded-xl border border-slate-200 bg-white p-4">
                  <div className="flex items-start gap-3">
                    <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-600 font-mono text-sm font-bold text-white">
                      {p.letter}
                    </span>
                    <div className="min-w-0 flex-1">
                      <div className="flex flex-wrap items-baseline justify-between gap-x-2 gap-y-1">
                        <h3 className="text-sm font-semibold text-slate-900">
                          {p.n}. {p.name}
                        </h3>
                        <span className="shrink-0 rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-semibold text-violet-800">
                          {p.hook}
                        </span>
                      </div>
                      <p className="mt-1 text-xs leading-relaxed text-slate-600">{p.how}</p>
                    </div>
                  </div>

                  {p.contrast ? (
                    <table className="mt-2 w-full text-left text-[11px]">
                      <thead>
                        <tr className="text-slate-500">
                          <th className="w-1/2 py-1 pr-3 font-medium">{p.contrast.left}</th>
                          <th className="py-1 font-medium">{p.contrast.right}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {p.contrast.rows.map((row, i) => (
                          <tr key={i} className="border-t border-slate-100">
                            <td className="py-1 pr-3 align-top text-slate-600">{row[0]}</td>
                            <td className="py-1 align-top font-medium text-indigo-700">{row[1]}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : null}

                  {p.code ? (
                    <pre className="mt-2 overflow-x-auto rounded-lg bg-slate-900 p-3 text-[11px] leading-relaxed text-slate-100">
                      {p.code}
                    </pre>
                  ) : null}

                  <ul className="mt-2 space-y-1">
                    {p.remember.map((r, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600">
                        <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-400" />
                        {r}
                      </li>
                    ))}
                  </ul>

                  {p.practice_id ? (
                    <Link
                      href={`/java-lab?q=${p.practice_id}`}
                      className="mt-3 inline-flex items-center gap-1 text-xs font-medium text-indigo-600 transition hover:text-indigo-700"
                    >
                      Practice in Java Lab <ArrowRight className="h-3 w-3" />
                    </Link>
                  ) : null}
                </article>
              ))}
            </div>
          </section>

          {/* Key comparisons */}
          <section className="space-y-3">
            <Heading icon={Scale}>Key comparisons — interviewers love these</Heading>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              {tricks.comparisons.map((c, i) => (
                <div key={i} className="rounded-xl border border-slate-200 bg-white p-4">
                  <h3 className="text-xs font-semibold text-slate-900">{c.title}</h3>
                  {c.rows && c.headers ? (
                    <table className="mt-2 w-full text-left text-[11px]">
                      <thead>
                        <tr className="text-slate-500">
                          {c.headers.map((h, j) => (
                            <th key={j} className="py-1 pr-3 font-medium">
                              {h}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {c.rows.map((row, j) => (
                          <tr key={j} className="border-t border-slate-100">
                            {row.map((cell, k) => (
                              <td
                                key={k}
                                className={cn(
                                  "py-1 pr-3 align-top",
                                  k === 0 ? "font-medium text-slate-800" : "text-slate-600"
                                )}
                              >
                                {cell}
                              </td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  ) : null}
                  {c.lines ? (
                    <ul className="mt-2 space-y-1">
                      {c.lines.map((line, j) => (
                        <li key={j} className="flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-600">
                          <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
                          {line}
                        </li>
                      ))}
                    </ul>
                  ) : null}
                </div>
              ))}
            </div>
          </section>

          {/* Traps */}
          <section className="space-y-3">
            <Heading icon={AlertTriangle}>Traps interviewers test</Heading>
            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-500">
                    <th className="py-1.5 pr-4 font-medium">Program</th>
                    <th className="py-1.5 pr-4 font-medium">Trap</th>
                    <th className="py-1.5 font-medium">Fix</th>
                  </tr>
                </thead>
                <tbody>
                  {tricks.traps.map((t, i) => (
                    <tr key={i} className="border-t border-slate-100">
                      <td className="py-1.5 pr-4 font-medium text-slate-800">{t.program}</td>
                      <td className="py-1.5 pr-4 text-rose-700">{t.trap}</td>
                      <td className="py-1.5 font-mono text-emerald-700">{t.fix}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Complexity */}
          <section className="space-y-3">
            <Heading icon={Gauge}>Complexity quick reference</Heading>
            <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white p-4">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="text-slate-500">
                    <th className="py-1.5 pr-4 font-medium">#</th>
                    <th className="py-1.5 pr-4 font-medium">Time</th>
                    <th className="py-1.5 font-medium">Space</th>
                  </tr>
                </thead>
                <tbody>
                  {tricks.complexity.map((c) => (
                    <tr
                      key={c.n}
                      className={cn("border-t border-slate-100", c.best && "bg-emerald-50")}
                    >
                      <td className="py-1.5 pr-4 font-mono font-semibold text-indigo-700">{c.n}</td>
                      <td className="py-1.5 pr-4 font-mono text-slate-600">{c.time}</td>
                      <td className="py-1.5 font-mono text-slate-600">
                        {c.space}
                        {c.best ? <span className="ml-1 text-emerald-600">★</span> : null}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {/* Flashcard drill */}
          <section className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <Heading icon={Library}>Flashcard drill — cover the answers</Heading>
              <button
                onClick={() => {
                  setShowAll(!showAll);
                  if (showAll) setRevealed(new Set());
                }}
                className="flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50"
              >
                {showAll ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                {showAll ? "Hide all answers" : "Show all answers"}
              </button>
            </div>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
              {tricks.flashcards.map((card, i) => {
                const visible = showAll || revealed.has(i);
                return (
                  <button
                    key={i}
                    onClick={() => toggleCard(i)}
                    className={cn(
                      "rounded-xl border p-3 text-left transition",
                      visible
                        ? "border-emerald-200 bg-emerald-50"
                        : "border-slate-200 bg-white hover:border-slate-300"
                    )}
                  >
                    <p className="text-xs font-semibold text-slate-800">{card.q}</p>
                    {visible ? (
                      <p className="mt-1.5 font-mono text-xs text-emerald-800">{card.a}</p>
                    ) : (
                      <p className="mt-1.5 flex items-center gap-1 text-[11px] italic text-slate-400">
                        <EyeOff className="h-3 w-3" /> click to reveal
                      </p>
                    )}
                  </button>
                );
              })}
            </div>
          </section>

          {/* Big picture + final mnemonic */}
          <section className="space-y-3">
            <Heading icon={Compass}>The big picture — which structure when?</Heading>
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="space-y-1">
                {tricks.big_picture.map((row, i) => (
                  <div
                    key={i}
                    className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 rounded-lg bg-slate-50 px-3 py-1.5 text-xs"
                  >
                    <span className="font-medium text-slate-700">{row.need}</span>
                    <span className="font-mono text-indigo-700">{row.use}</span>
                  </div>
                ))}
              </div>
              <div className="mt-4 rounded-lg bg-slate-900 p-4 text-center">
                <p className="font-mono text-sm font-semibold tracking-wide text-white">
                  {tricks.final_line}
                </p>
                <p className="mt-1 text-xs text-slate-400">{tricks.final_note}</p>
              </div>
            </div>
          </section>
        </>
      ) : null}

      {/* Topic sections */}
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {sections.map((section) => (
          <div key={section.id} className="rounded-xl border border-slate-200 bg-white p-4">
            <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900">
              <BookMarked className="h-4 w-4 text-indigo-600" /> {section.title}
            </h2>
            <ul className="mt-2 space-y-1.5">
              {section.items.map((item, i) => (
                <li key={i} className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-700">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-4">
        <h2 className="text-sm font-semibold text-slate-900">HTTP status codes</h2>
        <div className="mt-2 grid grid-cols-1 gap-1 sm:grid-cols-2">
          {statusCodes.map((s) => (
            <div key={s.code} className="flex items-baseline gap-2 rounded px-2 py-1 text-xs odd:bg-slate-50">
              <span className="font-mono font-bold text-indigo-700">{s.code}</span>
              <span className="text-slate-700">{s.meaning}</span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
