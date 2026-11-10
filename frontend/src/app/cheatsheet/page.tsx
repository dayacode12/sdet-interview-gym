"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  BookMarked,
  Brain,
  ChevronDown,
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

type TabId = "overview" | "programs" | "comparisons" | "traps" | "drill" | "topics";

const TABS: { id: TabId; label: string; icon: typeof Zap }[] = [
  { id: "overview", label: "Overview", icon: Compass },
  { id: "programs", label: "Cheat codes", icon: Sparkles },
  { id: "comparisons", label: "Comparisons", icon: Scale },
  { id: "traps", label: "Traps & complexity", icon: AlertTriangle },
  { id: "drill", label: "Drill", icon: Library },
  { id: "topics", label: "All topics", icon: BookMarked },
];

const CARD = "rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900";

function Heading({ icon: Icon, children }: { icon: typeof Zap; children: React.ReactNode }) {
  return (
    <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
      <Icon className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
      {children}
    </h2>
  );
}

export default function CheatsheetPage() {
  const [sections, setSections] = useState<Section[]>([]);
  const [statusCodes, setStatusCodes] = useState<StatusCode[]>([]);
  const [tricks, setTricks] = useState<JavaTricks | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [tab, setTab] = useState<TabId>("overview");
  const [showAll, setShowAll] = useState(false);
  const [revealed, setRevealed] = useState<Set<number>>(new Set());
  const [openProgram, setOpenProgram] = useState<number | null>(1);

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
    // Deep link support: /cheatsheet?tab=<id> opens that tab.
    const wanted = new URLSearchParams(window.location.search).get("tab") as TabId | null;
    if (wanted && TABS.some((t) => t.id === wanted)) setTab(wanted);
  }, []);

  const toggleCard = (i: number) =>
    setRevealed((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });

  const programCount = useMemo(() => tricks?.programs.length ?? 0, [tricks]);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Interview Cheat Sheet</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Last-mile revision: the fifteen-minute pass through everything that matters, split into
          focused tabs instead of one endless scroll. Read it the morning of the interview.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50 p-3 text-sm text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-300">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      {/* Sticky tab bar — one category at a time */}
      <div className="sticky top-0 z-20 -mx-4 border-b border-slate-200 bg-background/95 px-4 py-2 backdrop-blur dark:border-slate-700 sm:-mx-6 sm:px-6 md:top-0">
        <nav className="scrollbar-none flex gap-1.5 overflow-x-auto">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => {
                setTab(id);
                window.scrollTo({ top: 0 });
              }}
              className={cn(
                "flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition",
                tab === id
                  ? "bg-indigo-600 text-white"
                  : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
              )}
            >
              <Icon className="h-3.5 w-3.5" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {!tricks && !error ? (
        <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
          Loading the cheat sheet…
        </div>
      ) : null}

      {tricks ? (
        <>
          {/* ---------------- OVERVIEW ---------------- */}
          {tab === "overview" ? (
            <div className="space-y-6">
              <section className="overflow-hidden rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 p-5 text-white">
                <div className="flex items-center gap-2">
                  <Brain className="h-5 w-5" />
                  <h2 className="text-sm font-semibold uppercase tracking-wide">
                    Java memory tricks — {programCount} core programs
                  </h2>
                </div>
                <p className="mt-3 font-mono text-xl font-bold tracking-widest">{tricks.mnemonic}</p>
                <p className="mt-1 text-sm text-indigo-100">&ldquo;{tricks.story}&rdquo;</p>
              </section>

              <section className="space-y-3">
                <Heading icon={Zap}>Master framework — the 10-second scan</Heading>
                <div className={cn(CARD, "overflow-x-auto")}>
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="text-slate-500 dark:text-slate-400">
                        <th className="py-1.5 pr-4 font-medium">#</th>
                        <th className="py-1.5 pr-4 font-medium">Keyword</th>
                        <th className="py-1.5 pr-4 font-medium">Trick</th>
                        <th className="py-1.5 font-medium">Data structure</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tricks.programs.map((p) => (
                        <tr key={p.n} className="border-t border-slate-100 dark:border-slate-800">
                          <td className="py-1.5 pr-4 font-mono font-semibold text-indigo-700 dark:text-indigo-400">
                            {p.n}
                          </td>
                          <td className="py-1.5 pr-4 font-medium text-slate-800 dark:text-slate-200">
                            {p.keyword}
                          </td>
                          <td className="py-1.5 pr-4 text-slate-600 dark:text-slate-300">{p.trick}</td>
                          <td className="py-1.5 font-mono text-slate-600 dark:text-slate-300">
                            {p.structure}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Want the full memory hooks?{" "}
                  <button
                    onClick={() => setTab("programs")}
                    className="font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                  >
                    Open the cheat codes tab →
                  </button>
                </p>
              </section>

              <section className="space-y-3">
                <Heading icon={Compass}>The big picture — which structure when?</Heading>
                <div className={CARD}>
                  <div className="space-y-1">
                    {tricks.big_picture.map((row, i) => (
                      <div
                        key={i}
                        className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-0.5 rounded-lg bg-slate-50 px-3 py-1.5 text-xs dark:bg-slate-800/60"
                      >
                        <span className="font-medium text-slate-700 dark:text-slate-200">{row.need}</span>
                        <span className="font-mono text-indigo-700 dark:text-indigo-400">{row.use}</span>
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
            </div>
          ) : null}

          {/* ---------------- PROGRAMS (collapsible) ---------------- */}
          {tab === "programs" ? (
            <section className="space-y-2">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Heading icon={Sparkles}>Cheat codes — one card per program</Heading>
                <div className="flex gap-1.5">
                  <button
                    onClick={() => setOpenProgram(null)}
                    className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
                  >
                    Collapse all
                  </button>
                  <button
                    onClick={() => setOpenProgram(-1)}
                    className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
                  >
                    Expand all
                  </button>
                </div>
              </div>
              {tricks.programs.map((p) => {
                const open = openProgram === -1 || openProgram === p.n;
                return (
                  <article key={p.n} className={CARD}>
                    <button
                      onClick={() => setOpenProgram(openProgram === p.n ? null : p.n)}
                      className="flex w-full items-start gap-3 text-left"
                    >
                      <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-indigo-600 font-mono text-sm font-bold text-white">
                        {p.letter}
                      </span>
                      <div className="min-w-0 flex-1">
                        <div className="flex flex-wrap items-baseline justify-between gap-x-2 gap-y-1">
                          <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                            {p.n}. {p.name}
                          </h3>
                          <span className="shrink-0 rounded-full bg-violet-100 px-2 py-0.5 text-[10px] font-semibold text-violet-800 dark:bg-violet-900 dark:text-violet-300">
                            {p.hook}
                          </span>
                        </div>
                        <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                          {p.trick} — <span className="font-mono">{p.structure}</span>
                        </p>
                      </div>
                      <ChevronDown
                        className={cn(
                          "mt-1 h-4 w-4 shrink-0 text-slate-400 transition-transform dark:text-slate-500",
                          open && "rotate-180"
                        )}
                      />
                    </button>

                    {open ? (
                      <div className="mt-3 space-y-2 border-t border-slate-100 pt-3 dark:border-slate-800">
                        <p className="text-xs leading-relaxed text-slate-600 dark:text-slate-300">{p.how}</p>

                        {p.contrast ? (
                          <table className="w-full text-left text-[11px]">
                            <thead>
                              <tr className="text-slate-500 dark:text-slate-400">
                                <th className="w-1/2 py-1 pr-3 font-medium">{p.contrast.left}</th>
                                <th className="py-1 font-medium">{p.contrast.right}</th>
                              </tr>
                            </thead>
                            <tbody>
                              {p.contrast.rows.map((row, i) => (
                                <tr key={i} className="border-t border-slate-100 dark:border-slate-800">
                                  <td className="py-1 pr-3 align-top text-slate-600 dark:text-slate-300">
                                    {row[0]}
                                  </td>
                                  <td className="py-1 align-top font-medium text-indigo-700 dark:text-indigo-400">
                                    {row[1]}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        ) : null}

                        {p.code ? (
                          <pre className="overflow-x-auto rounded-lg bg-slate-900 p-3 text-[11px] leading-relaxed text-slate-100">
                            {p.code}
                          </pre>
                        ) : null}

                        <ul className="space-y-1">
                          {p.remember.map((r, i) => (
                            <li
                              key={i}
                              className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300"
                            >
                              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-amber-400" />
                              {r}
                            </li>
                          ))}
                        </ul>

                        {p.practice_id ? (
                          <Link
                            href={`/java-lab?q=${p.practice_id}`}
                            className="mt-1 inline-flex items-center gap-1 text-xs font-medium text-indigo-600 transition hover:text-indigo-700 dark:text-indigo-400 dark:hover:text-indigo-300"
                          >
                            Practice in Java Lab <ArrowRight className="h-3 w-3" />
                          </Link>
                        ) : null}
                      </div>
                    ) : null}
                  </article>
                );
              })}
            </section>
          ) : null}

          {/* ---------------- COMPARISONS ---------------- */}
          {tab === "comparisons" ? (
            <section className="space-y-3">
              <Heading icon={Scale}>Key comparisons — interviewers love these</Heading>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {tricks.comparisons.map((c, i) => (
                  <div key={i} className={CARD}>
                    <h3 className="text-xs font-semibold text-slate-900 dark:text-slate-100">{c.title}</h3>
                    {c.rows && c.headers ? (
                      <table className="mt-2 w-full text-left text-[11px]">
                        <thead>
                          <tr className="text-slate-500 dark:text-slate-400">
                            {c.headers.map((h, j) => (
                              <th key={j} className="py-1 pr-3 font-medium">
                                {h}
                              </th>
                            ))}
                          </tr>
                        </thead>
                        <tbody>
                          {c.rows.map((row, j) => (
                            <tr key={j} className="border-t border-slate-100 dark:border-slate-800">
                              {row.map((cell, k) => (
                                <td
                                  key={k}
                                  className={cn(
                                    "py-1 pr-3 align-top",
                                    k === 0
                                      ? "font-medium text-slate-800 dark:text-slate-200"
                                      : "text-slate-600 dark:text-slate-300"
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
                          <li
                            key={j}
                            className="flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300"
                          >
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
          ) : null}

          {/* ---------------- TRAPS & COMPLEXITY ---------------- */}
          {tab === "traps" ? (
            <div className="space-y-6">
              <section className="space-y-3">
                <Heading icon={AlertTriangle}>Traps interviewers test</Heading>
                <div className={cn(CARD, "overflow-x-auto")}>
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="text-slate-500 dark:text-slate-400">
                        <th className="py-1.5 pr-4 font-medium">Program</th>
                        <th className="py-1.5 pr-4 font-medium">Trap</th>
                        <th className="py-1.5 font-medium">Fix</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tricks.traps.map((t, i) => (
                        <tr key={i} className="border-t border-slate-100 dark:border-slate-800">
                          <td className="py-1.5 pr-4 font-medium text-slate-800 dark:text-slate-200">
                            {t.program}
                          </td>
                          <td className="py-1.5 pr-4 text-rose-700 dark:text-rose-400">{t.trap}</td>
                          <td className="py-1.5 font-mono text-emerald-700 dark:text-emerald-400">{t.fix}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>

              <section className="space-y-3">
                <Heading icon={Gauge}>Complexity quick reference</Heading>
                <div className={cn(CARD, "overflow-x-auto")}>
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="text-slate-500 dark:text-slate-400">
                        <th className="py-1.5 pr-4 font-medium">#</th>
                        <th className="py-1.5 pr-4 font-medium">Time</th>
                        <th className="py-1.5 font-medium">Space</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tricks.complexity.map((c) => (
                        <tr
                          key={c.n}
                          className={cn(
                            "border-t border-slate-100 dark:border-slate-800",
                            c.best && "bg-emerald-50 dark:bg-emerald-950"
                          )}
                        >
                          <td className="py-1.5 pr-4 font-mono font-semibold text-indigo-700 dark:text-indigo-400">
                            {c.n}
                          </td>
                          <td className="py-1.5 pr-4 font-mono text-slate-600 dark:text-slate-300">{c.time}</td>
                          <td className="py-1.5 font-mono text-slate-600 dark:text-slate-300">
                            {c.space}
                            {c.best ? <span className="ml-1 text-emerald-600 dark:text-emerald-400">★</span> : null}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </section>
            </div>
          ) : null}

          {/* ---------------- DRILL ---------------- */}
          {tab === "drill" ? (
            <section className="space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <Heading icon={Library}>Flashcard drill — cover the answers</Heading>
                <button
                  onClick={() => {
                    setShowAll(!showAll);
                    if (showAll) setRevealed(new Set());
                  }}
                  className="flex items-center gap-1.5 rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 transition hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-200 dark:hover:bg-slate-800"
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
                          ? "border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950"
                          : "border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-slate-600"
                      )}
                    >
                      <p className="text-xs font-semibold text-slate-800 dark:text-slate-200">{card.q}</p>
                      {visible ? (
                        <p className="mt-1.5 font-mono text-xs text-emerald-800 dark:text-emerald-300">{card.a}</p>
                      ) : (
                        <p className="mt-1.5 flex items-center gap-1 text-[11px] italic text-slate-400 dark:text-slate-500">
                          <EyeOff className="h-3 w-3" /> click to reveal
                        </p>
                      )}
                    </button>
                  );
                })}
              </div>
            </section>
          ) : null}

          {/* ---------------- TOPICS ---------------- */}
          {tab === "topics" ? (
            <div className="space-y-6">
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                {sections.map((section) => (
                  <div key={section.id} className={CARD}>
                    <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
                      <BookMarked className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> {section.title}
                    </h2>
                    <ul className="mt-2 space-y-1.5">
                      {section.items.map((item, i) => (
                        <li
                          key={i}
                          className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-700 dark:text-slate-300"
                        >
                          <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>

              <section className={CARD}>
                <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">HTTP status codes</h2>
                <div className="mt-2 grid grid-cols-1 gap-1 sm:grid-cols-2">
                  {statusCodes.map((s) => (
                    <div
                      key={s.code}
                      className="flex items-baseline gap-2 rounded px-2 py-1 text-xs odd:bg-slate-50 dark:odd:bg-slate-800/60"
                    >
                      <span className="font-mono font-bold text-indigo-700 dark:text-indigo-400">{s.code}</span>
                      <span className="text-slate-700 dark:text-slate-300">{s.meaning}</span>
                    </div>
                  ))}
                </div>
              </section>
            </div>
          ) : null}
        </>
      ) : null}
    </div>
  );
}
