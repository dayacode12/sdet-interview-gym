"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  ArrowRight,
  BadgeCheck,
  BookOpen,
  Braces,
  CheckCircle2,
  ChevronDown,
  Clock,
  Database,
  ExternalLink,
  FileText,
  Fingerprint,
  Lightbulb,
  Link2,
  Quote,
  ShieldCheck,
  Target,
  Users,
  XCircle,
} from "lucide-react";
import { api } from "@/lib/api";
import { SaveProgress } from "@/components/save-progress";
import { loadDraft } from "@/lib/drafts";
import { HIDE_ADMIRAL } from "@/lib/features";
import { cn } from "@/lib/utils";

type Evidence = "official" | "jd" | "reported" | "standard";

interface Source {
  id: string;
  name: string;
  publisher: string;
  type: "official" | "brief" | "standard" | "internal";
  url: string;
  supports: string;
  accessed: string;
}

interface Question {
  id: string;
  prompt: string;
  evidence: Evidence;
  why: string;
  model_answer: string;
  code: string;
  key_points: string[];
  follow_ups: string[];
  traps: string[];
  source_ids: string[];
  admiral_evidence?: string;
}

interface Section {
  id: string;
  title: string;
  icon: string;
  intro: string;
  questions: Question[];
}

interface FlowSegment {
  minutes: string;
  title: string;
  do: string;
  evidence: Evidence;
  source_ids: string[];
  must_cover: string[];
  example: string;
  example_code: string;
}

interface Playbook {
  title: string;
  subtitle: string;
  question_count: number;
  official_process: {
    headline: string;
    facts: { claim: string; source_ids: string[] }[];
    implication: string;
    what_it_does_not_say: string;
  };
  sections: Section[];
  flow: { title: string; note: string; segments: FlowSegment[] };
  gap: {
    the_issue: string;
    do: string[];
    dont: string[];
    script: string;
  };
  teams_notes: { title: string; detail: string; source_ids: string[] }[];
  sources: Source[];
  disclaimer: string;
}

const EVIDENCE: Record<
  Evidence,
  { label: string; className: string; title: string }
> = {
  official: {
    label: "Official Schwab",
    className:
      "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
    title: "Published by Charles Schwab on schwabjobs.com.",
  },
  jd: {
    label: "Role / JD evidence",
    className:
      "border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-800 dark:bg-indigo-950 dark:text-indigo-300",
    title:
      "Named in the job description or in Schwab's published technology role families — still a prediction of the question, not a leaked one.",
  },
  reported: {
    label: "Public report",
    className:
      "border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300",
    title:
      "Publicly reported by candidates or predicted in your round1.md brief. Not official Schwab material.",
  },
  standard: {
    label: "Standards-backed",
    className:
      "border-slate-200 bg-slate-50 text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300",
    title: "The answer is checked against vendor documentation or a standard.",
  },
};

function EvidenceBadge({ kind }: { kind: Evidence }) {
  const meta = EVIDENCE[kind];
  return (
    <span
      title={meta.title}
      className={cn(
        "inline-flex shrink-0 items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold",
        meta.className
      )}
    >
      {meta.label}
    </span>
  );
}

function SectionIcon({ icon }: { icon: string }) {
  if (icon === "database") return <Database className="h-5 w-5" />;
  if (icon === "shield") return <ShieldCheck className="h-5 w-5" />;
  return <Braces className="h-5 w-5" />;
}

function SourceChip({ source }: { source: Source }) {
  const label = `${source.publisher.split("(")[0].trim()} — ${source.name}`;
  if (!source.url) {
    return (
      <span
        title={source.supports}
        className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] text-slate-500 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400"
      >
        <FileText className="h-2.5 w-2.5" />
        {label}
      </span>
    );
  }
  return (
    <a
      href={source.url}
      target="_blank"
      rel="noreferrer"
      title={source.supports}
      className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-1.5 py-0.5 text-[10px] text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-indigo-700 dark:hover:text-indigo-300"
    >
      <ExternalLink className="h-2.5 w-2.5" />
      {label}
    </a>
  );
}

function CopyButton({ text }: { text: string }) {
  const [copied, setCopied] = useState(false);
  return (
    <button
      type="button"
      onClick={async () => {
        try {
          await navigator.clipboard.writeText(text);
          setCopied(true);
          setTimeout(() => setCopied(false), 1500);
        } catch {
          // clipboard unavailable — the code is still selectable
        }
      }}
      className="rounded-md border border-slate-300 bg-white px-2 py-1 text-[10px] font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300"
    >
      {copied ? "Copied" : "Copy"}
    </button>
  );
}

function sourceMap(sources: Source[]): Map<string, Source> {
  return new Map(sources.map((s) => [s.id, s]));
}

export default function Round1Page() {
  const [data, setData] = useState<Playbook | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<string | null>(null);
  const [revealed, setRevealed] = useState<Set<string>>(new Set());
  const [answers, setAnswers] = useState<Record<string, string>>({});
  const [openSegments, setOpenSegments] = useState<Set<string>>(new Set());

  useEffect(() => {
    api
      .get<Playbook>("/api/round1")
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  const byId = useMemo(() => sourceMap(data?.sources ?? []), [data]);

  function toggleQuestion(id: string) {
    setExpanded((prev) => (prev === id ? null : id));
    setAnswers((prev) =>
      prev[id] !== undefined
        ? prev
        : { ...prev, [id]: loadDraft(`round1:${id}`)?.text ?? "" }
    );
  }

  function toggleReveal(id: string) {
    setRevealed((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function jumpTo(id: string) {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function toggleSegment(minutes: string) {
    setOpenSegments((prev) => {
      const next = new Set(prev);
      if (next.has(minutes)) next.delete(minutes);
      else next.add(minutes);
      return next;
    });
  }

  function setAllSegments(open: boolean) {
    setOpenSegments(
      open ? new Set((data?.flow.segments ?? []).map((segment) => segment.minutes)) : new Set()
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Round 1 Playbook</h1>
        <div className="flex items-start gap-2 rounded-lg border border-rose-200 bg-rose-50 p-4 text-sm text-rose-800 dark:border-rose-800 dark:bg-rose-950 dark:text-rose-400">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <div>
            <p className="font-medium">The playbook could not load.</p>
            <p className="mt-1 text-xs">{error}</p>
            <p className="mt-1 text-xs">
              Check the API URL on the dashboard (the hosted backend may be waking up).
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="space-y-3">
        <h1 className="text-2xl font-bold">Round 1 Playbook</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Loading the question bank…</p>
      </div>
    );
  }

  const sourceCount = data.sources.length;
  const officialCount = data.sources.filter((s) => s.type === "official").length;

  return (
    <div className="space-y-8">
      <header>
        <div className="flex flex-wrap items-center gap-2">
          <Target className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
          <h1 className="text-2xl font-bold">{data.title}</h1>
          <span className="rounded-full bg-indigo-600 px-2 py-0.5 text-[10px] font-semibold text-white">
            SCHWAB · ROUND 1
          </span>
        </div>
        <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
          {data.subtitle}
        </p>
        <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
          <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
            {data.question_count} predicted questions
          </span>
          <span className="rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 font-medium text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300">
            {officialCount} official Schwab sources
          </span>
          <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
            {sourceCount} sources in the ledger
          </span>
        </div>
      </header>

      {/* Honesty banner */}
      <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950">
        <p className="flex items-start gap-2 text-xs leading-relaxed text-amber-900 dark:text-amber-200">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>
            <strong>Read the labels.</strong> Schwab publishes its hiring process and its
            behavioural method — not technical question banks. &quot;Official Schwab&quot; marks
            what the company actually published. Technical questions are labelled{" "}
            <em>Role/JD evidence</em>, <em>Public report</em> or <em>Standards-backed</em>. Nothing
            here is leaked material.
          </span>
        </p>
      </section>

      {/* Official process */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h2 className="flex items-center gap-2 text-lg font-semibold">
            <BadgeCheck className="h-5 w-5 text-emerald-600 dark:text-emerald-400" />
            {data.official_process.headline}
          </h2>
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300">
            OFFICIAL
          </span>
        </div>
        <ul className="mt-3 space-y-3">
          {data.official_process.facts.map((fact, i) => (
            <li key={i} className="flex items-start gap-2.5">
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
              <div className="min-w-0">
                <p className="text-sm leading-relaxed text-slate-700 dark:text-slate-200">
                  {fact.claim}
                </p>
                <div className="mt-1 flex flex-wrap gap-1">
                  {fact.source_ids.map((id) => {
                    const source = byId.get(id);
                    return source ? <SourceChip key={id} source={source} /> : null;
                  })}
                </div>
              </div>
            </li>
          ))}
        </ul>
        <p className="mt-4 rounded-lg bg-slate-50 p-3 text-xs leading-relaxed text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
          <strong>What this means for you:</strong> {data.official_process.implication}
        </p>
        <p className="mt-2 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
          {data.official_process.what_it_does_not_say}
        </p>
      </section>

      {/* Jump nav */}
      <nav aria-label="Playbook sections" className="scrollbar-none flex gap-2 overflow-x-auto">
        {data.sections.map((section) => (
          <button
            key={section.id}
            type="button"
            onClick={() => jumpTo(section.id)}
            className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-indigo-700 dark:hover:text-indigo-300"
          >
            {section.title}
          </button>
        ))}
        <button
          type="button"
          onClick={() => jumpTo("flow")}
          className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-indigo-700 dark:hover:text-indigo-300"
        >
          The 60-minute flow
        </button>
        <button
          type="button"
          onClick={() => jumpTo("sources")}
          className="shrink-0 rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-indigo-700 dark:hover:text-indigo-300"
        >
          Sources
        </button>
      </nav>

      {/* Question sections */}
      {data.sections.map((section) => (
        <section key={section.id} id={section.id} className="scroll-mt-6 space-y-3">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <SectionIcon icon={section.icon} />
            </span>
            <div>
              <h2 className="text-lg font-semibold">{section.title}</h2>
              <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                {section.intro}
              </p>
            </div>
          </div>

          <div className="space-y-2.5">
            {section.questions.map((q, index) => {
              const open = expanded === q.id;
              const showAnswer = revealed.has(q.id);
              return (
                <article
                  key={q.id}
                  className={cn(
                    "overflow-hidden rounded-xl border bg-white transition dark:bg-slate-900",
                    open
                      ? "border-indigo-300 dark:border-indigo-700"
                      : "border-slate-200 dark:border-slate-700"
                  )}
                >
                  <button
                    type="button"
                    onClick={() => toggleQuestion(q.id)}
                    aria-expanded={open}
                    className="flex w-full items-start gap-3 p-3.5 text-left hover:bg-slate-50 dark:hover:bg-slate-800/50"
                  >
                    <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-slate-100 text-[11px] font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                      {index + 1}
                    </span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-sm font-medium leading-relaxed text-slate-800 dark:text-slate-100">
                        {q.prompt}
                      </span>
                      <span className="mt-1.5 flex flex-wrap items-center gap-1.5">
                        <EvidenceBadge kind={q.evidence} />
                        <span className="text-[10px] text-slate-400 dark:text-slate-500">
                          {q.source_ids.length} source{q.source_ids.length === 1 ? "" : "s"}
                        </span>
                      </span>
                    </span>
                    <ChevronDown
                      className={cn(
                        "mt-1 h-4 w-4 shrink-0 text-slate-400 transition-transform",
                        open && "rotate-180"
                      )}
                    />
                  </button>

                  {open ? (
                    <div className="space-y-4 border-t border-slate-200 p-4 dark:border-slate-700">
                      <p className="flex items-start gap-2 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                        <Lightbulb className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-500" />
                        <span>
                          <strong className="font-semibold">Why it is likely:</strong> {q.why}
                        </span>
                      </p>

                      {/* Practice box with cross-device draft autosave */}
                      <div>
                        <label
                          htmlFor={`answer-${q.id}`}
                          className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400"
                        >
                          Your answer — say it out loud, then type the shape
                        </label>
                        <textarea
                          id={`answer-${q.id}`}
                          value={answers[q.id] ?? ""}
                          onChange={(e) =>
                            setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))
                          }
                          rows={4}
                          placeholder="Opening sentence, two or three key points, one concrete example or number…"
                          className="mt-1.5 w-full resize-y rounded-lg border border-slate-300 bg-white p-3 text-xs leading-relaxed text-slate-800 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none dark:border-slate-600 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-500"
                        />
                        <div className="mt-1.5">
                          <SaveProgress
                            storageKey={`round1:${q.id}`}
                            value={answers[q.id] ?? ""}
                            pristine=""
                            onRestore={(text) =>
                              setAnswers((prev) => ({ ...prev, [q.id]: text }))
                            }
                          />
                        </div>
                      </div>

                      <div className="flex flex-wrap items-center gap-2">
                        <button
                          type="button"
                          onClick={() => toggleReveal(q.id)}
                          className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-white hover:bg-slate-700 dark:bg-indigo-600 dark:hover:bg-indigo-500"
                        >
                          {showAnswer ? (
                            <>
                              <ChevronDown className="h-3.5 w-3.5 rotate-180" /> Hide model answer
                            </>
                          ) : (
                            <>
                              <BookOpen className="h-3.5 w-3.5" /> Reveal model answer
                            </>
                          )}
                        </button>
                        <span className="text-[10px] text-slate-400 dark:text-slate-500">
                          Try your own version first — recall beats recognition.
                        </span>
                      </div>

                      {showAnswer ? (
                        <div className="space-y-3 rounded-lg border border-emerald-200 bg-emerald-50/50 p-3 dark:border-emerald-800 dark:bg-emerald-950/40">
                          <div>
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
                              Model answer
                            </p>
                            <p className="mt-1 whitespace-pre-wrap text-xs leading-relaxed text-slate-700 dark:text-slate-200">
                              {q.model_answer}
                            </p>
                          </div>

                          {q.admiral_evidence && !HIDE_ADMIRAL ? (
                            <div className="rounded-lg border border-indigo-200 bg-indigo-50/70 p-2.5 dark:border-indigo-800 dark:bg-indigo-950/50">
                              <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-indigo-700 dark:text-indigo-300">
                                <Fingerprint className="h-3 w-3" />
                                From your current role
                              </p>
                              <p className="mt-1 text-xs leading-relaxed text-indigo-950 dark:text-indigo-200">
                                {q.admiral_evidence}
                              </p>
                              <p className="mt-1 text-[10px] text-indigo-700/70 dark:text-indigo-300/70">
                                Your own IGA work at Admiral Group, from the brief you provided —
                                internal evidence, not Schwab material.
                              </p>
                            </div>
                          ) : null}

                          {q.code ? (
                            <div>
                              <div className="flex items-center justify-between gap-2">
                                <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                  Code
                                </p>
                                <CopyButton text={q.code} />
                              </div>
                              <pre className="mt-1 overflow-x-auto rounded-lg bg-slate-900 p-3 font-mono text-[11px] leading-relaxed text-slate-100">
                                {q.code}
                              </pre>
                            </div>
                          ) : null}

                          <div>
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                              Key points to land
                            </p>
                            <ul className="mt-1 space-y-1">
                              {q.key_points.map((point) => (
                                <li
                                  key={point}
                                  className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-700 dark:text-slate-200"
                                >
                                  <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600 dark:text-emerald-400" />
                                  {point}
                                </li>
                              ))}
                            </ul>
                          </div>

                          <div className="grid gap-3 sm:grid-cols-2">
                            <div>
                              <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                Likely follow-ups
                              </p>
                              <ul className="mt-1 space-y-1">
                                {q.follow_ups.map((item) => (
                                  <li
                                    key={item}
                                    className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300"
                                  >
                                    <ArrowRight className="mt-0.5 h-3 w-3 shrink-0 text-indigo-500" />
                                    {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                            <div>
                              <p className="text-[11px] font-semibold uppercase tracking-wide text-rose-600 dark:text-rose-400">
                                Traps to avoid
                              </p>
                              <ul className="mt-1 space-y-1">
                                {q.traps.map((item) => (
                                  <li
                                    key={item}
                                    className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300"
                                  >
                                    <XCircle className="mt-0.5 h-3 w-3 shrink-0 text-rose-500" />
                                    {item}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          </div>

                          <div className="flex flex-wrap gap-1">
                            {q.source_ids.map((id) => {
                              const source = byId.get(id);
                              return source ? <SourceChip key={id} source={source} /> : null;
                            })}
                          </div>
                        </div>
                      ) : null}
                    </div>
                  ) : null}
                </article>
              );
            })}
          </div>
        </section>
      ))}

      {/* 60-minute flow */}
      <section id="flow" className="scroll-mt-6 space-y-3">
        <div className="flex flex-wrap items-start justify-between gap-2">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <Clock className="h-5 w-5" />
            </span>
            <div>
              <h2 className="text-lg font-semibold">{data.flow.title}</h2>
              <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                {data.flow.note}
              </p>
              <p className="mt-1 max-w-3xl text-[11px] font-medium text-indigo-600 dark:text-indigo-400">
                Every segment below has a worked example you can rehearse out loud.
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={() =>
              setAllSegments(openSegments.size < data.flow.segments.length)
            }
            className="shrink-0 rounded-lg border border-slate-300 bg-white px-2.5 py-1.5 text-[11px] font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-indigo-700 dark:hover:text-indigo-300"
          >
            {openSegments.size < data.flow.segments.length
              ? "Show all examples"
              : "Hide all examples"}
          </button>
        </div>
        <ol className="space-y-2">
          {data.flow.segments.map((segment) => {
            const open = openSegments.has(segment.minutes);
            // Tolerate an older API during a deploy skew: the static UI can
            // ship before the backend does.
            const mustCover = segment.must_cover ?? [];
            const example = segment.example ?? "";
            return (
              <li
                key={segment.minutes}
                className={cn(
                  "overflow-hidden rounded-xl border bg-white dark:bg-slate-900",
                  open
                    ? "border-indigo-300 dark:border-indigo-700"
                    : "border-slate-200 dark:border-slate-700"
                )}
              >
                <div className="flex items-start gap-3 p-3.5">
                  <span className="w-14 shrink-0 rounded-md bg-slate-100 px-1.5 py-1 text-center text-[11px] font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                    {segment.minutes}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm font-medium text-slate-800 dark:text-slate-100">
                        {segment.title}
                      </h3>
                      <EvidenceBadge kind={segment.evidence} />
                    </div>
                    <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                      {segment.do}
                    </p>
                    <div className="mt-2 flex flex-wrap items-center gap-2">
                      {example ? (
                        <>
                          <button
                            type="button"
                            onClick={() => toggleSegment(segment.minutes)}
                            aria-expanded={open}
                            className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-slate-700 dark:bg-indigo-600 dark:hover:bg-indigo-500"
                          >
                            <BookOpen className="h-3 w-3" />
                            {open
                              ? "Hide example answer"
                              : `Show example answer for ${segment.title}`}
                          </button>
                          <span className="text-[10px] text-slate-400 dark:text-slate-500">
                            Say it out loud once, then again from memory.
                          </span>
                        </>
                      ) : null}
                    </div>
                  </div>
                </div>

                {open ? (
                  <div className="space-y-3 border-t border-slate-200 p-4 dark:border-slate-700">
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        What they are scoring
                      </p>
                      <ul className="mt-1 space-y-1">
                        {mustCover.map((point) => (
                          <li
                            key={point}
                            className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300"
                          >
                            <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600 dark:text-emerald-400" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="rounded-lg border border-emerald-200 bg-emerald-50/50 p-3 dark:border-emerald-800 dark:bg-emerald-950/40">
                      <p className="text-[11px] font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
                        Example answer — say it like this
                      </p>
                      <p className="mt-1 whitespace-pre-wrap text-xs leading-relaxed text-slate-700 dark:text-slate-200">
                        {example}
                      </p>
                      {segment.example_code ? (
                        <div className="mt-2">
                          <div className="flex items-center justify-between gap-2">
                            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                              Code
                            </p>
                            <CopyButton text={segment.example_code} />
                          </div>
                          <pre className="mt-1 overflow-x-auto rounded-lg bg-slate-900 p-3 font-mono text-[11px] leading-relaxed text-slate-100">
                            {segment.example_code}
                          </pre>
                        </div>
                      ) : null}
                    </div>

                    <div className="flex flex-wrap gap-1">
                      {segment.source_ids.map((id) => {
                        const source = byId.get(id);
                        return source ? <SourceChip key={id} source={source} /> : null;
                      })}
                    </div>
                  </div>
                ) : null}
              </li>
            );
          })}
        </ol>
      </section>

      {/* Experience gap */}
      <section id="gap" className="scroll-mt-6 space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-amber-500 text-white">
            <Users className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">Addressing the experience gap</h2>
            <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              {data.gap.the_issue}
            </p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 dark:border-emerald-800 dark:bg-emerald-950">
            <h3 className="flex items-center gap-1.5 text-sm font-semibold text-emerald-900 dark:text-emerald-300">
              <CheckCircle2 className="h-4 w-4" /> Do
            </h3>
            <ul className="mt-2 space-y-1.5">
              {data.gap.do.map((item) => (
                <li
                  key={item}
                  className="flex items-start gap-1.5 text-xs leading-relaxed text-emerald-900 dark:text-emerald-200"
                >
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-emerald-500" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div className="rounded-xl border border-rose-200 bg-rose-50 p-4 dark:border-rose-800 dark:bg-rose-950">
            <h3 className="flex items-center gap-1.5 text-sm font-semibold text-rose-900 dark:text-rose-300">
              <XCircle className="h-4 w-4" /> Don&apos;t
            </h3>
            <ul className="mt-2 space-y-1.5">
              {data.gap.dont.map((item) => (
                <li
                  key={item}
                  className="flex items-start gap-1.5 text-xs leading-relaxed text-rose-900 dark:text-rose-200"
                >
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-rose-500" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
        </div>
        <blockquote className="rounded-xl border-l-4 border-indigo-500 bg-slate-50 p-4 text-xs leading-relaxed text-slate-700 dark:bg-slate-800/60 dark:text-slate-200">
          <Quote className="mb-1 h-4 w-4 text-indigo-500" />
          {data.gap.script}
        </blockquote>
      </section>

      {/* Teams notes */}
      <section className="space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-700 text-white">
            <Link2 className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">Notes on the Teams / US format</h2>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">
              The medium changes delivery, not the technical bar.
            </p>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          {data.teams_notes.map((note) => (
            <div
              key={note.title}
              className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
            >
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                {note.title}
              </h3>
              <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                {note.detail}
              </p>
              <div className="mt-2 flex flex-wrap gap-1">
                {note.source_ids.map((id) => {
                  const source = byId.get(id);
                  return source ? <SourceChip key={id} source={source} /> : null;
                })}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Source ledger */}
      <section id="sources" className="scroll-mt-6 space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-emerald-600 text-white">
            <BookOpen className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">Source ledger</h2>
            <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              Every claim on this page traces to one of these. Official Schwab pages establish the
              process, the behavioural method and the role families; standards and vendor docs
              check the technical answers. The local brief is the topic map, not an official
              source.
            </p>
          </div>
        </div>

        {(["official", "brief", "internal", "standard"] as const).map((type) => {
          const rows = data.sources.filter((s) => s.type === type);
          if (!rows.length) return null;
          const heading =
            type === "official"
              ? "Official Charles Schwab"
              : type === "brief"
                ? "Your research brief"
                : type === "internal"
                  ? "Your current role (internal)"
                  : "Standards and vendor documentation";
          return (
            <div key={type} className="space-y-2">
              <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                {heading}
              </h3>
              <div className="space-y-2">
                {rows.map((source) => (
                  <div
                    key={source.id}
                    className={cn(
                      "rounded-xl border p-3.5",
                      type === "official"
                        ? "border-emerald-200 bg-emerald-50/40 dark:border-emerald-800 dark:bg-emerald-950/30"
                        : "border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
                    )}
                  >
                    <div className="flex flex-wrap items-start justify-between gap-2">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-100">
                          {source.name}
                        </p>
                        <p className="text-[11px] text-slate-500 dark:text-slate-400">
                          {source.publisher}
                        </p>
                      </div>
                      {source.url ? (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noreferrer"
                          className="flex shrink-0 items-center gap-1 rounded-md border border-slate-300 bg-white px-2 py-1 text-[10px] font-medium text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300"
                        >
                          <ExternalLink className="h-3 w-3" /> Open
                        </a>
                      ) : (
                        <span className="rounded-md border border-slate-200 bg-slate-50 px-2 py-1 text-[10px] text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">
                          {source.type === "internal" ? "Internal — not linked" : "Local file"}
                        </span>
                      )}
                    </div>
                    <p className="mt-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                      {source.supports}
                    </p>
                    <p className="mt-1 text-[10px] text-slate-400 dark:text-slate-500">
                      Accessed {source.accessed}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </section>

      <footer className="rounded-xl border border-slate-200 bg-slate-50 p-4 text-[11px] leading-relaxed text-slate-500 dark:border-slate-700 dark:bg-slate-800/50 dark:text-slate-400">
        {data.disclaimer}
        <span className="mt-2 block">
          Practice with the{" "}
          <Link href="/java-lab" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
            Java Lab
          </Link>
          ,{" "}
          <Link href="/sql-playground" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
            SQL Playground
          </Link>{" "}
          and{" "}
          <Link href="/iam-lab" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
            IAM Lab
          </Link>
          , then run the{" "}
          <Link href="/mock-interview" className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
            Mock Interview
          </Link>{" "}
          for timing.
        </span>
      </footer>
    </div>
  );
}
