"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, CalendarDays, Clock, Save, Target } from "lucide-react";
import { api } from "@/lib/api";

interface RoadmapBlock {
  activity: string;
  minutes: number;
  labs: string[];
}

interface RoadmapDay {
  day: string;
  title: string;
  focus: string;
  blocks: RoadmapBlock[];
}

export default function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<RoadmapDay[]>([]);
  const [priority, setPriority] = useState<string[]>([]);
  const [interviewDate, setInterviewDate] = useState("");
  const [interviewTime, setInterviewTime] = useState("09:00");
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.get<{ roadmap: RoadmapDay[]; priority_questions: string[] }>("/api/roadmap").then((r) => {
      setRoadmap(r.roadmap);
      setPriority(r.priority_questions);
    }).catch((e) => setError(e.message));
    api.get<{ interview_datetime: string }>("/api/settings").then((r) => {
      const raw = r.interview_datetime ?? "";
      setInterviewDate(raw.slice(0, 10));
      const time = raw.slice(11, 16);
      if (/^\d{2}:\d{2}$/.test(time)) setInterviewTime(time);
    }).catch(() => {});
  }, []);

  async function saveDate() {
    try {
      await api.put("/api/settings", {
        interview_datetime: interviewDate ? `${interviewDate}T${interviewTime}:00` : "",
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (e) {
      setError((e as Error).message);
    }
  }

  const daysLeft = interviewDate
    ? Math.ceil((new Date(`${interviewDate}T${interviewTime}:00`).getTime() - Date.now()) / 86400000)
    : null;

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-bold">Preparation Roadmap</h1>
        <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
          A three-phase plan sized for the days before the interview. Set your date to track the countdown.
        </p>
      </header>

      {error ? (
        <div className="flex items-center gap-2 rounded-lg border border-rose-200 dark:border-rose-800 bg-rose-50 dark:bg-rose-950 p-3 text-sm text-rose-800 dark:text-rose-400">
          <AlertTriangle className="h-4 w-4" /> {error}
        </div>
      ) : null}

      <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-4">
        <div>
          <label className="flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-300">
            <CalendarDays className="h-3.5 w-3.5" /> Interview date
          </label>
          <input
            type="date"
            value={interviewDate}
            onChange={(e) => setInterviewDate(e.target.value)}
            className="mt-1 rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
        </div>
        <div>
          <label className="flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-300">
            <Clock className="h-3.5 w-3.5" /> Interview time
          </label>
          <input
            type="time"
            value={interviewTime}
            onChange={(e) => setInterviewTime(e.target.value)}
            className="mt-1 rounded-lg border border-slate-300 dark:border-slate-600 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
        </div>
        <button
          onClick={saveDate}
          className="flex items-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700"
        >
          <Save className="h-4 w-4" /> Save
        </button>
        {saved ? <span className="text-xs font-medium text-emerald-600 dark:text-emerald-400">Saved ✓</span> : null}
        {daysLeft !== null ? (
          <span className="flex items-center gap-1.5 rounded-full bg-indigo-50 dark:bg-indigo-950 px-3 py-1 text-xs font-semibold text-indigo-700 dark:text-indigo-400">
            <Clock className="h-3.5 w-3.5" />
            {daysLeft >= 0 ? `${daysLeft} day${daysLeft === 1 ? "" : "s"} to go` : "interview passed"}
          </span>
        ) : null}
      </div>

      <div className="space-y-4">
        {roadmap.map((day) => (
          <div key={day.day} className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 p-5">
            <div className="flex items-baseline justify-between">
              <h2 className="font-semibold text-slate-900 dark:text-slate-100">
                {day.day} — {day.title}
              </h2>
              <span className="text-xs text-slate-500 dark:text-slate-400">
                total {day.blocks.reduce((a, b) => a + b.minutes, 0)} min
              </span>
            </div>
            <p className="mt-0.5 text-xs text-slate-500 dark:text-slate-400">{day.focus}</p>
            <div className="mt-3 space-y-2">
              {day.blocks.map((block, i) => (
                <div key={i} className="flex items-start justify-between gap-3 rounded-lg bg-slate-50 dark:bg-slate-800/60 p-3">
                  <div>
                    <p className="text-sm font-medium text-slate-800 dark:text-slate-100">{block.activity}</p>
                    <div className="mt-1 flex flex-wrap gap-1">
                      {block.labs.map((lab) => (
                        <span key={lab} className="rounded-full bg-indigo-100 dark:bg-indigo-900 px-2 py-0.5 text-[10px] font-medium text-indigo-700 dark:text-indigo-400">
                          {lab}
                        </span>
                      ))}
                    </div>
                  </div>
                  <span className="shrink-0 text-xs font-medium text-slate-600 dark:text-slate-300">{block.minutes} min</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      <section className="rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950 p-5">
        <h2 className="flex items-center gap-1.5 font-semibold text-amber-900 dark:text-amber-300">
          <Target className="h-4 w-4" /> The ten highest-priority questions
        </h2>
        <p className="mt-0.5 text-xs text-amber-800 dark:text-amber-400">
          If you can only rehearse ten answers, rehearse these.
        </p>
        <ol className="mt-3 space-y-1.5">
          {priority.map((q, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-amber-950 dark:text-amber-200">
              <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-amber-200 dark:bg-amber-900/70 text-[11px] font-bold text-amber-900 dark:text-amber-300">
                {i + 1}
              </span>
              {q}
            </li>
          ))}
        </ol>
      </section>
    </div>
  );
}
