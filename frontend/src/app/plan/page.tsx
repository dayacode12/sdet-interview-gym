"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  CalendarClock,
  Coffee,
  HelpCircle,
  ListChecks,
  Moon,
  Rocket,
  Sun,
  Target,
  TrendingUp,
  Wallet,
} from "lucide-react";
import { cn } from "@/lib/utils";

const STORAGE_KEY = "plan-progress";
const INTERVIEW_AT = new Date("2026-11-12T21:00:00").getTime();
const DAY_2_START = new Date("2026-11-11T00:00:00").getTime();
const DAY_3_START = new Date("2026-11-12T00:00:00").getTime();

interface PlanItem {
  id: string;
  label: string;
  minutes?: number;
  href?: string;
  note?: string;
}

interface PlanBlock {
  id: "nov-10" | "nov-11" | "nov-12";
  when: string;
  date: string;
  subtitle: string;
  tone: "night" | "main" | "final";
  icon: typeof Moon;
  items: PlanItem[];
}

const DAYS: PlanBlock[] = [
  {
    id: "nov-10",
    when: "Tonight",
    date: "Tue, Nov 10",
    subtitle: "45 minutes total — then stop and sleep on time",
    tone: "night",
    icon: Moon,
    items: [
      {
        id: "n10-company",
        label: "Read the Company Brief end to end",
        minutes: 30,
        href: "/company",
        note: "Mission, the four values (say each out loud with your QA angle), the scale numbers, the 5-step hiring process.",
      },
      {
        id: "n10-drill",
        label: "Quick-facts drill with answers covered",
        minutes: 10,
        href: "/company",
        note: "Stay on the drill at the bottom of the page until you can answer 12 of 14.",
      },
      {
        id: "n10-map",
        label: "Open the Mind Map and expand every branch once",
        minutes: 5,
        href: "/mind-map",
        note: "The goal is the whole territory in view so nothing surprises you — not memorizing it.",
      },
      {
        id: "n10-sleep",
        label: "Stop. Sleep on time",
        note: "Cramming tonight costs you recall tomorrow — the trade is a bad one.",
      },
    ],
  },
  {
    id: "nov-11",
    when: "The main prep day",
    date: "Wed, Nov 11",
    subtitle: "~3 hours around your job — morning, lunch and one protected evening block",
    tone: "main",
    icon: Sun,
    items: [
      {
        id: "n11-pitch",
        label: "Write your 90-second pitch, then say it out loud 3×",
        minutes: 30,
        href: "/resume",
        note: "SDET → IAM/IGA for TCS/Admiral → Playwright migration (60→40 min) → 300+ cases → why Schwab. This is the single highest-value half hour of the two days.",
      },
      {
        id: "n11-work",
        label: "Work — no studying at your desk",
        note: "Keep the job intact; your lunch slot covers flashcards.",
      },
      {
        id: "n11-lunch",
        label: "Flashcards on your phone: IAM Fundamentals + IGA",
        minutes: 20,
        href: "/flashcards?topic=IAM",
        note: "The hosted site works on mobile — commute or lunch, either is fine.",
      },
      {
        id: "n11-mock",
        label: "Full timed mock interview — the dress rehearsal",
        minutes: 45,
        href: "/mock-interview",
        note: "Don't skip this. Afterwards, read the rubric feedback on your two weakest answers.",
      },
      {
        id: "n11-stories",
        label: "Three anchor stories out loud, S.T.A.R.",
        minutes: 25,
        href: "/resume",
        note: "Playwright migration, the 300+ case suite, and one cross-layer debugging investigation (UI vs API vs logs vs SQL).",
      },
      {
        id: "n11-java",
        label: "Five timed Java Lab questions, then read the solutions",
        minutes: 25,
        href: "/java-lab",
        note: "15 minutes for the five, 10 minutes reading the model answers.",
      },
      {
        id: "n11-scenarios",
        label: "Two scenarios in writing, then compare with the model",
        minutes: 25,
        href: "/scenarios",
        note: "Terminated-user-retains-access, plus one data-mismatch scenario. Use the save button if you need to pause mid-answer.",
      },
    ],
  },
  {
    id: "nov-12",
    when: "Interview day — light",
    date: "Thu, Nov 12",
    subtitle: "Protect your energy. No new material today.",
    tone: "final",
    icon: Rocket,
    items: [
      {
        id: "n12-morning",
        label: "Cheat Sheet — Overview tab only",
        minutes: 20,
        href: "/cheatsheet?tab=overview",
        note: "The 10-second scan table and the big picture. Nothing else.",
      },
      {
        id: "n12-lunch",
        label: "Quick-facts drill once more + rehearse your reverse questions",
        minutes: 15,
        href: "/company",
        note: "Pick your two questions below and say them out loud once each.",
      },
      {
        id: "n12-stop",
        label: "6:00 PM — stop studying. Eat a real dinner",
        note: "Anything learned after this point does not stick; it only adds noise.",
      },
      {
        id: "n12-tech",
        label: "8:15 PM — tech setup",
        note: "Quiet room, webcam/mic test, phone hotspot as backup, water, résumé + the numbers below open in tabs.",
      },
      {
        id: "n12-warm",
        label: "8:45 PM — say the pitch out loud one last time",
        note: "Then read only the final mnemonic line on the cheat sheet.",
      },
      {
        id: "n12-go",
        label: "9:00 PM — go. First 90 seconds = the pitch",
        note: "You've prepared more thoroughly than most candidates prepare for anything.",
      },
    ],
  },
];

const JOB_RULES = [
  "Tomorrow: work ends at 6 PM and the evening block is sacred. No “quick check” of work email after dinner.",
  "Nov 12: if WFH or a half-day is possible, take it — a 9–10 PM interview after a full office day is draining. If not, take a real lunch break away from your desk and zero prep after 6 PM.",
  "Commute and lunch = flashcards (phone). Evening = out-loud practice (the hard, high-value part). Never swap these.",
  "Keep it confidential at your current company until you have an offer in hand.",
];

const REVERSE_QUESTIONS = [
  "How does the SDET team plug into shift-left security — at what stage do you get threat models or security requirements?",
  "What does the path from manual IAM testing to full automation coverage look like on your side?",
  "What would a successful first 90 days look like for this role?",
];

const KEY_NUMBERS = [
  { value: "$10.10T", label: "client assets" },
  { value: "36.5M", label: "brokerage accounts (Dec 31, 2024)" },
  { value: "1971", label: "founded, San Francisco" },
  { value: "Westlake, TX", label: "HQ today · 380+ branches" },
  { value: "Through Clients' Eyes", label: "the strategy in three words" },
  { value: "Trust · Innovation · Teamwork · Stewardship", label: "the four values" },
];

function useCountdown() {
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => {
    setNow(Date.now());
    const t = setInterval(() => setNow(Date.now()), 30_000);
    return () => clearInterval(t);
  }, []);
  return now;
}

function fmtCountdown(ms: number): string {
  const totalMinutes = Math.max(0, Math.round(ms / 60_000));
  const days = Math.floor(totalMinutes / (60 * 24));
  const hours = Math.floor((totalMinutes % (60 * 24)) / 60);
  const minutes = totalMinutes % 60;
  if (days > 0) return `${days} day${days === 1 ? "" : "s"} ${hours} hr`;
  if (hours > 0) return `${hours} hr ${minutes} min`;
  return `${minutes} min`;
}

export default function PlanPage() {
  const [done, setDone] = useState<Record<string, boolean>>({});
  const now = useCountdown();

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) setDone(JSON.parse(raw));
    } catch {
      // corrupted or unavailable — start fresh
    }
  }, []);

  const toggle = (id: string) => {
    setDone((prev) => {
      const next = { ...prev, [id]: !prev[id] };
      if (!next[id]) delete next[id];
      try {
        window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
      } catch {
        // best-effort
      }
      return next;
    });
  };

  const allItems = useMemo(() => DAYS.flatMap((d) => d.items), []);
  const doneCount = allItems.filter((i) => done[i.id]).length;
  const pct = allItems.length ? Math.round((100 * doneCount) / allItems.length) : 0;

  const activeDayId: PlanBlock["id"] | null =
    now === null ? null : now < DAY_2_START ? "nov-10" : now < DAY_3_START ? "nov-11" : "nov-12";
  const isInterviewTime = now !== null && now >= INTERVIEW_AT;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-900 dark:text-slate-100">
          <CalendarClock className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
          Interview Plan — 2 Days
        </h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          Built around a day job: tonight ~45 minutes, tomorrow ~3 hours split into
          morning / lunch / one protected evening block, and a light interview day.
          Check items off as you go — your progress is saved on this device.
        </p>
      </header>

      {/* Countdown + progress */}
      <section className="overflow-hidden rounded-xl bg-gradient-to-br from-indigo-600 to-violet-600 p-5 text-white">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-indigo-100">
              Interview — Thursday, Nov 12 · 9:00–10:00 PM
            </p>
            <p className="mt-1 text-3xl font-bold">
              {isInterviewTime
                ? "It's interview time — go."
                : now === null
                  ? "—"
                  : `${fmtCountdown(INTERVIEW_AT - now)} to go`}
            </p>
          </div>
          <div className="min-w-[200px] flex-1">
            <div className="flex items-center justify-between text-xs text-indigo-100">
              <span className="flex items-center gap-1.5">
                <Target className="h-3.5 w-3.5" /> Plan progress
              </span>
              <span>
                {doneCount}/{allItems.length} done
              </span>
            </div>
            <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-indigo-800/50">
              <div
                className="h-full rounded-full bg-white transition-all"
                style={{ width: `${pct}%` }}
              />
            </div>
            {doneCount > 0 ? (
              <button
                onClick={() => {
                  setDone({});
                  try {
                    window.localStorage.removeItem(STORAGE_KEY);
                  } catch {
                    // ignore
                  }
                }}
                className="mt-2 text-[11px] text-indigo-200 underline hover:text-white"
              >
                reset checklist
              </button>
            ) : null}
          </div>
        </div>
      </section>

      {/* The three days */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {DAYS.map((day) => {
          const Icon = day.icon;
          const isToday = day.id === activeDayId;
          const dayDone = day.items.filter((i) => done[i.id]).length;
          return (
            <section
              key={day.id}
              className={cn(
                "rounded-xl border bg-white p-4 dark:bg-slate-900",
                isToday
                  ? "border-indigo-400 ring-2 ring-indigo-200 dark:border-indigo-500 dark:ring-indigo-900"
                  : "border-slate-200 dark:border-slate-700"
              )}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span
                    className={cn(
                      "flex h-8 w-8 items-center justify-center rounded-lg",
                      day.tone === "night" && "bg-slate-800 text-white dark:bg-slate-700",
                      day.tone === "main" && "bg-indigo-600 text-white",
                      day.tone === "final" && "bg-emerald-600 text-white"
                    )}
                  >
                    <Icon className="h-4 w-4" />
                  </span>
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                      {day.when}
                    </h2>
                    <p className="text-[11px] text-slate-500 dark:text-slate-400">{day.date}</p>
                  </div>
                </div>
                {isToday ? (
                  <span className="rounded-full bg-indigo-600 px-2 py-0.5 text-[10px] font-semibold text-white">
                    TODAY
                  </span>
                ) : dayDone === day.items.length ? (
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-800 dark:bg-emerald-900 dark:text-emerald-400">
                    DONE
                  </span>
                ) : null}
              </div>
              <p className="mt-2 text-xs leading-relaxed text-slate-500 dark:text-slate-400">
                {day.subtitle}
              </p>

              <ul className="mt-3 space-y-2">
                {day.items.map((item) => {
                  const checked = !!done[item.id];
                  return (
                    <li
                      key={item.id}
                      className={cn(
                        "flex items-start gap-2 rounded-lg border p-2.5 transition",
                        checked
                          ? "border-emerald-200 bg-emerald-50 dark:border-emerald-800 dark:bg-emerald-950"
                          : "border-slate-200 bg-white hover:border-slate-300 dark:border-slate-700 dark:bg-slate-900 dark:hover:border-slate-600"
                      )}
                    >
                      <button
                        onClick={() => toggle(item.id)}
                        aria-label={`${checked ? "Uncheck" : "Mark done"}: ${item.label}`}
                        className={cn(
                          "mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border text-[10px] font-bold transition",
                          checked
                            ? "border-emerald-600 bg-emerald-600 text-white"
                            : "border-slate-300 hover:border-indigo-400 dark:border-slate-600 dark:hover:border-indigo-500"
                        )}
                      >
                        {checked ? "✓" : ""}
                      </button>
                      <div className="min-w-0 flex-1">
                        <p
                          className={cn(
                            "text-xs font-medium leading-snug",
                            checked
                              ? "text-emerald-900 line-through dark:text-emerald-400"
                              : "text-slate-800 dark:text-slate-200"
                          )}
                        >
                          {item.label}
                          {item.minutes ? (
                            <span className="ml-1.5 font-normal text-slate-400 dark:text-slate-500">
                              · {item.minutes} min
                            </span>
                          ) : null}
                        </p>
                        {item.note ? (
                          <p className="mt-1 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
                            {item.note}
                          </p>
                        ) : null}
                        {item.href ? (
                          <Link
                            href={item.href}
                            className="mt-1 inline-flex items-center gap-1 text-[11px] font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                          >
                            open <ArrowRight className="h-3 w-3" />
                          </Link>
                        ) : null}
                      </div>
                    </li>
                  );
                })}
              </ul>
            </section>
          );
        })}
      </div>

      {/* Managing the job alongside */}
      <section className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
          <Coffee className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          Managing the day job alongside
        </h2>
        <ul className="mt-2 space-y-1.5">
          {JOB_RULES.map((rule, i) => (
            <li key={i} className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-indigo-400" />
              {rule}
            </li>
          ))}
        </ul>
      </section>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        {/* Reverse questions */}
        <section className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
            <HelpCircle className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            Your reverse questions — pick two
          </h2>
          <ol className="mt-2 space-y-2">
            {REVERSE_QUESTIONS.map((q, i) => (
              <li
                key={i}
                className="rounded-lg bg-slate-50 p-2.5 text-xs leading-relaxed text-slate-700 dark:bg-slate-800/60 dark:text-slate-300"
              >
                <span className="mr-1.5 font-mono font-bold text-indigo-600 dark:text-indigo-400">
                  {i + 1}.
                </span>
                “{q}”
              </li>
            ))}
          </ol>
          <p className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
            These signal the exact intersection they hire for: QA × security × automation.
          </p>
        </section>

        {/* Key numbers */}
        <section className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
          <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
            <TrendingUp className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
            Numbers to have in reach
          </h2>
          <div className="mt-2 space-y-1.5">
            {KEY_NUMBERS.map((n) => (
              <div
                key={n.label}
                className="flex flex-wrap items-baseline justify-between gap-x-3 rounded-lg bg-slate-50 px-3 py-1.5 dark:bg-slate-800/60"
              >
                <span className="text-xs font-semibold text-slate-800 dark:text-slate-100">
                  {n.value}
                </span>
                <span className="text-[11px] text-slate-500 dark:text-slate-400">{n.label}</span>
              </div>
            ))}
          </div>
          <p className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
            Dropping one of these naturally into an answer is worth more than an hour of cramming.
          </p>
        </section>
      </div>

      {/* Compensation snapshot */}
      <section className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="flex items-center gap-1.5 text-sm font-semibold text-slate-900 dark:text-slate-100">
          <Wallet className="h-4 w-4 text-indigo-600 dark:text-indigo-400" />
          If compensation comes up
        </h2>
        <div className="mt-2 grid grid-cols-1 gap-3 sm:grid-cols-3">
          <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60">
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              Schwab India — SWE median (TC)
            </p>
            <p className="mt-1 text-lg font-bold text-slate-900 dark:text-slate-100">₹30.5 LPA</p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Bengaluru specifically: ₹39.87 LPA
            </p>
          </div>
          <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60">
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              Schwab India — 25th to 90th percentile
            </p>
            <p className="mt-1 text-lg font-bold text-slate-900 dark:text-slate-100">
              ₹17.6L – ₹69.9L
            </p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              Skews toward product companies
            </p>
          </div>
          <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/60">
            <p className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              Schwab US — Cybersecurity Analyst median
            </p>
            <p className="mt-1 text-lg font-bold text-slate-900 dark:text-slate-100">$150k TC</p>
            <p className="text-[11px] text-slate-500 dark:text-slate-400">
              SWE median $120k · all roles $149.5k
            </p>
          </div>
        </div>
        <p className="mt-3 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
          For ~3 years of experience, anchor on role scope and learning first; if pressed for a
          number, the Levels.fyi Schwab SWE median (₹30.5–40 LPA TC in India) is a realistic
          reference band. Data source:{" "}
          <a
            href="https://www.levels.fyi/companies/charles-schwab/salaries"
            target="_blank"
            rel="noreferrer"
            className="font-medium text-indigo-600 hover:underline dark:text-indigo-400"
          >
            Levels.fyi
          </a>
          .
        </p>
      </section>

      <p className="flex items-start gap-1.5 text-[11px] leading-snug text-slate-500 dark:text-slate-400">
        <ListChecks className="mt-0.5 h-3 w-3 shrink-0" />
        Checklist state is saved locally on this device (like your theme choice). Submitted scores
        and quiz results live in the server database.
      </p>
    </div>
  );
}
