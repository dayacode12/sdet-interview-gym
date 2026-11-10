"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  AlertTriangle,
  BadgeCheck,
  Building2,
  ChevronDown,
  Eye,
  EyeOff,
  Handshake,
  History,
  Landmark,
  Mic,
  Network,
  Quote,
  ScrollText,
  ShieldCheck,
} from "lucide-react";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Value {
  name: string;
  meaning: string;
  qa_link: string;
}

interface NumberFact {
  label: string;
  value: string;
  as_of: string;
}

interface HistoryEvent {
  year: string;
  event: string;
  say_it?: string | null;
}

interface InterviewAngle {
  question: string;
  talking_points: string[];
  model_answer: string;
}

interface CompanyProfile {
  name: string;
  target_role: string;
  mission: string;
  philosophy: string;
  tagline: string;
  nickname: string;
  business: string;
  values: Value[];
  numbers: NumberFact[];
  history: HistoryEvent[];
  tech_org: {
    sts: { name: string; description: string };
    scs: { name: string; description: string };
    role_families: string[];
    your_role_note: string;
    stack: string[];
  };
  hiring: {
    methodology: string;
    steps: { n: number; name: string; detail: string }[];
    background_check: string;
    transferable_skills: string;
    ai_policy: string;
  };
  interview_angles: InterviewAngle[];
  quick_facts_drill: { q: string; a: string }[];
  sources: { name: string; url: string; what: string }[];
  disclaimer: string;
}

export default function CompanyPage() {
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openAngle, setOpenAngle] = useState<number | null>(null);
  const [showAllFacts, setShowAllFacts] = useState(false);
  const [revealedFacts, setRevealedFacts] = useState<Set<number>>(new Set());

  useEffect(() => {
    api
      .get<CompanyProfile>("/api/company")
      .then(setProfile)
      .catch((e) => setError(e.message));
  }, []);

  const toggleFact = (i: number) =>
    setRevealedFacts((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });

  return (
    <div className="space-y-8">
      <header>
        <div className="flex items-center gap-2">
          <Building2 className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
          <h1 className="text-2xl font-bold">Company Brief — Charles Schwab</h1>
        </div>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Everything about the company you&apos;re interviewing with: mission, values, scale,
          history, technology organization and hiring process — researched from public sources and
          shaped into interview-ready answers.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 p-3 text-sm text-rose-800 dark:text-rose-400">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      {profile ? (
        <>
          {/* Identity header */}
          <section className="overflow-hidden rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 p-5 text-white">
            <p className="text-xs font-semibold uppercase tracking-wide text-indigo-200">
              Target role: {profile.target_role}
            </p>
            <h2 className="mt-1 text-xl font-bold">{profile.name}</h2>
            <div className="mt-3 grid gap-2 sm:grid-cols-3">
              <div className="rounded-lg bg-white/10 p-2.5">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-indigo-200">Mission</p>
                <p className="mt-0.5 text-sm font-medium leading-snug">{profile.mission}</p>
              </div>
              <div className="rounded-lg bg-white/10 p-2.5">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-indigo-200">Philosophy</p>
                <p className="mt-0.5 text-sm font-medium leading-snug">{profile.philosophy}</p>
              </div>
              <div className="rounded-lg bg-white/10 p-2.5">
                <p className="text-[10px] font-semibold uppercase tracking-wide text-indigo-200">Tagline</p>
                <p className="mt-0.5 text-sm font-medium leading-snug">{profile.tagline}</p>
              </div>
            </div>
            <p className="mt-3 text-xs leading-relaxed text-indigo-100">{profile.business}</p>
          </section>

          {/* Values */}
          <section className="space-y-3">
            <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
              <ShieldCheck className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> The four values — memorize, then connect
            </h2>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              {profile.values.map((v) => (
                <div key={v.name} className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
                  <div className="flex items-center gap-2">
                    <span className="rounded-full bg-indigo-600 px-2.5 py-0.5 text-[10px] font-bold uppercase text-white">
                      Value
                    </span>
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">{v.name}</h3>
                  </div>
                  <p className="mt-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{v.meaning}</p>
                  <p className="mt-2 rounded-lg bg-indigo-50 dark:bg-indigo-950 p-2 text-[11px] leading-relaxed text-indigo-900 dark:text-indigo-300">
                    <strong>Your QA angle: </strong>{v.qa_link}
                  </p>
                </div>
              ))}
            </div>
          </section>

          {/* Scale numbers */}
          <section className="space-y-3">
            <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
              <Landmark className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> The numbers — say these out loud in answers
            </h2>
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-3 lg:grid-cols-4">
              {profile.numbers.map((n) => (
                <div key={n.label} className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-3">
                  <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">{n.label}</p>
                  <p className="mt-1 font-mono text-sm font-bold text-indigo-700 dark:text-indigo-400">{n.value}</p>
                  {n.as_of !== "—" ? (
                    <p className="mt-0.5 text-[10px] text-slate-400 dark:text-slate-500">as of {n.as_of}</p>
                  ) : null}
                </div>
              ))}
            </div>
          </section>

            {/* History timeline */}
            <section className="space-y-3">
              <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
                <History className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> History — the 60-second version
              </h2>
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
                <ol className="relative ml-2 space-y-3 border-l-2 border-indigo-200 dark:border-indigo-800 pl-4">
                  {profile.history.map((h, i) => (
                    <li key={i} className="relative">
                      <span className="absolute -left-[21px] top-1 h-2.5 w-2.5 rounded-full bg-indigo-600" />
                      <p className="text-[13px] font-semibold text-slate-900 dark:text-slate-100">
                        {h.year !== "—" ? `${h.year} — ` : ""}
                        {h.event}
                      </p>
                      {h.say_it ? (
                        <p className="mt-0.5 flex items-start gap-1.5 text-[11px] italic text-emerald-700 dark:text-emerald-400">
                          <Quote className="mt-0.5 h-3 w-3 shrink-0" /> {h.say_it}
                        </p>
                      ) : null}
                    </li>
                  ))}
                </ol>
              </div>
            </section>

            {/* Technology org */}
            <section className="space-y-3">
              <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
                <Network className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Where your role sits — the technology org
              </h2>
              <div className="grid grid-cols-1 gap-3 lg:grid-cols-2">
                {[profile.tech_org.sts, profile.tech_org.scs].map((org) => (
                  <div key={org.name} className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
                    <h3 className="text-sm font-bold text-slate-900 dark:text-slate-100">{org.name}</h3>
                    <p className="mt-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{org.description}</p>
                  </div>
                ))}
              </div>
              <div className="rounded-xl border border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-950 p-4">
                <p className="text-[13px] leading-relaxed text-indigo-900 dark:text-indigo-300">
                  <BadgeCheck className="mr-1 inline h-4 w-4 align-text-bottom text-indigo-600 dark:text-indigo-400" />
                  {profile.tech_org.your_role_note}
                </p>
                <div className="mt-2 flex flex-wrap gap-1.5">
                  {profile.tech_org.role_families.map((r) => (
                    <span
                      key={r}
                      className={cn(
                        "rounded-full px-2.5 py-0.5 text-[11px] font-semibold",
                        r === "SDET"
                          ? "bg-indigo-600 text-white"
                          : "border border-indigo-300 dark:border-indigo-800 bg-white dark:bg-slate-900 text-indigo-800 dark:text-indigo-300"
                      )}
                    >
                      {r}
                    </span>
                  ))}
                </div>
                <p className="mt-2 text-[11px] text-indigo-800 dark:text-indigo-300">
                  Stack they cite: {profile.tech_org.stack.join(" · ")}
                </p>
              </div>
            </section>

            {/* Hiring process */}
            <section className="space-y-3">
              <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
                <Handshake className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> How Schwab hires
              </h2>
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
                <p className="text-xs font-semibold uppercase tracking-wide text-indigo-700 dark:text-indigo-400">
                  {profile.hiring.methodology}
                </p>
                <div className="mt-3 space-y-2">
                  {profile.hiring.steps.map((s) => (
                    <div key={s.n} className="flex items-start gap-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 p-2.5">
                      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-indigo-600 font-mono text-[11px] font-bold text-white">
                        {s.n}
                      </span>
                      <div>
                        <p className="text-[13px] font-semibold text-slate-900 dark:text-slate-100">{s.name}</p>
                        <p className="mt-0.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">{s.detail}</p>
                      </div>
                    </div>
                  ))}
                </div>
                <ul className="mt-3 space-y-1.5 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300">
                  <li>
                    <strong>Background check:</strong> {profile.hiring.background_check}
                  </li>
                  <li>
                    <strong>Transferable skills:</strong> {profile.hiring.transferable_skills}
                  </li>
                  <li className="rounded-lg bg-amber-50 dark:bg-amber-950 p-2 text-amber-900 dark:text-amber-300">
                    <strong>AI policy (their words):</strong> {profile.hiring.ai_policy}
                  </li>
                </ul>
              </div>
            </section>

            {/* Interview angles */}
            <section className="space-y-3">
              <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
                <Mic className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Company questions — model answers
              </h2>
              <div className="space-y-1.5">
                {profile.interview_angles.map((a, i) => (
                  <div key={i} className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900">
                    <button
                      onClick={() => setOpenAngle(openAngle === i ? null : i)}
                      className="flex w-full items-center justify-between gap-2 p-3 text-left text-sm font-semibold text-slate-800 dark:text-slate-100"
                    >
                      {a.question}
                      <ChevronDown
                        className={cn("h-4 w-4 shrink-0 text-slate-400 dark:text-slate-500 transition-transform", openAngle === i && "rotate-180")}
                      />
                    </button>
                    {openAngle === i ? (
                      <div className="space-y-2 border-t border-slate-100 dark:border-slate-800 p-3">
                        <div className="space-y-1">
                          {a.talking_points.map((t, j) => (
                            <p key={j} className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
                              {t}
                            </p>
                          ))}
                        </div>
                        <div className="rounded-lg bg-slate-50 dark:bg-slate-800/60 p-3">
                          <p className="text-[10px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                            Model answer
                          </p>
                          <p className="mt-1 text-[13px] leading-relaxed text-slate-800 dark:text-slate-100">{a.model_answer}</p>
                        </div>
                      </div>
                    ) : null}
                  </div>
                ))}
              </div>
            </section>

            {/* Quick facts drill */}
            <section className="space-y-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
                  <ScrollText className="h-4 w-4 text-indigo-600 dark:text-indigo-400" /> Quick-facts drill — cover the answers
                </h2>
                <button
                  onClick={() => {
                    setShowAllFacts(!showAllFacts);
                    if (showAllFacts) setRevealedFacts(new Set());
                  }}
                  className="flex items-center gap-1.5 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800/60"
                >
                  {showAllFacts ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                  {showAllFacts ? "Hide all answers" : "Show all answers"}
                </button>
              </div>
              <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {profile.quick_facts_drill.map((f, i) => {
                  const visible = showAllFacts || revealedFacts.has(i);
                  return (
                    <button
                      key={i}
                      onClick={() => toggleFact(i)}
                      className={cn(
                        "rounded-xl border p-3 text-left transition",
                        visible
                          ? "border-emerald-200 dark:border-emerald-800 bg-emerald-50 dark:bg-emerald-950"
                          : "border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-slate-300 dark:hover:border-slate-600"
                      )}
                    >
                      <p className="text-xs font-semibold text-slate-800 dark:text-slate-100">{f.q}</p>
                      {visible ? (
                        <p className="mt-1.5 font-mono text-[11px] leading-relaxed text-emerald-800 dark:text-emerald-400">{f.a}</p>
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

            {/* Sources + disclaimer */}
            <section className="space-y-3">
              <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">Sources — all public</h2>
              <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
                <ul className="space-y-1.5">
                  {profile.sources.map((s) => (
                    <li key={s.name} className="text-[11px] leading-relaxed text-slate-600 dark:text-slate-300">
                      <a
                        href={s.url}
                        target="_blank"
                        rel="noreferrer"
                        className="font-medium text-indigo-600 dark:text-indigo-400 hover:underline"
                      >
                        {s.name}
                      </a>{" "}
                      — {s.what}
                    </li>
                  ))}
                </ul>
                <p className="mt-3 rounded-lg bg-slate-100 dark:bg-slate-800 p-2.5 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300">
                  {profile.disclaimer}
                </p>
              </div>
            </section>

            {/* Cross-links */}
            <section className="rounded-xl border border-indigo-200 dark:border-indigo-800 bg-indigo-50 dark:bg-indigo-950 p-4">
              <p className="text-[13px] font-medium text-indigo-900 dark:text-indigo-300">
                Ready to practice this out loud?
              </p>
              <div className="mt-2 flex flex-wrap gap-2">
                <Link
                  href="/mock-interview"
                  className="rounded-lg bg-indigo-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-indigo-700"
                >
                  Mock interview (timed)
                </Link>
                <Link
                  href="/flashcards?topic=IAM"
                  className="rounded-lg border border-indigo-300 dark:border-indigo-800 bg-white dark:bg-slate-900 px-3 py-1.5 text-xs font-medium text-indigo-700 dark:text-indigo-400 hover:bg-white/70"
                >
                  Flashcards: IAM
                </Link>
                <Link
                  href="/mind-map"
                  className="rounded-lg border border-indigo-300 dark:border-indigo-800 bg-white dark:bg-slate-900 px-3 py-1.5 text-xs font-medium text-indigo-700 dark:text-indigo-400 hover:bg-white/70"
                >
                  Mind map
                </Link>
              </div>
            </section>
        </>
      ) : !error ? (
        <div className="flex h-64 items-center justify-center rounded-xl border-2 border-dashed border-slate-300 dark:border-slate-600 text-sm text-slate-500 dark:text-slate-400">
          Loading the company brief…
        </div>
      ) : null}
    </div>
  );
}
