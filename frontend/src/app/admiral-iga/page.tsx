"use client";

import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  ArrowRight,
  BadgeCheck,
  BookOpen,
  Briefcase,
  Bug,
  CheckCircle2,
  ChevronDown,
  Clock,
  Code,
  Database,
  ExternalLink,
  FileText,
  GitBranch,
  Lightbulb,
  ListChecks,
  Network,
  Plug,
  ShieldCheck,
  Target,
  Users,
  Workflow,
} from "lucide-react";
import { api } from "@/lib/api";
import { SaveProgress } from "@/components/save-progress";
import { loadDraft } from "@/lib/drafts";
import { cn } from "@/lib/utils";
import { usePrivateGate } from "@/lib/private-area";
import { PrivateAreaGate } from "@/components/private-area-gate";

type Evidence = "internal" | "jira";

interface Source {
  id: string;
  name: string;
  publisher: string;
  type: "internal" | "jira";
  url: string;
  supports: string;
  accessed: string;
}

interface Ticket {
  key: string;
  title: string;
  note: string;
  url: string;
}

interface CiamStage {
  id: string;
  label: string;
  title: string;
  ticket: string;
  environment: string;
  detail: string;
  what_i_test: string[];
  risk: string;
  source_ids: string[];
}

interface Domain {
  id: string;
  title: string;
  icon: string;
  summary: string;
  tickets: Ticket[];
  what_i_test: string[];
  risk: string;
  approach: string;
  script: string;
  source_ids: string[];
}

interface Question {
  id: string;
  prompt: string;
  evidence: Evidence;
  why: string;
  answer: string;
  key_points: string[];
  follow_ups: string[];
  source_ids: string[];
}

interface Admiral {
  title: string;
  subtitle: string;
  question_count: number;
  ticket_count: number;
  role: {
    title: string;
    company: string;
    function: string;
    summary: string;
    focus: string[];
    stack: string[];
    environments: string[];
    sprint: string;
  };
  team: {
    engineers: string[];
    test_engineers: string[];
    leadership: string[];
    note: string;
  };
  sprint: {
    name: string;
    items: {
      key: string;
      status: string;
      title: string;
      detail: string;
      url: string;
    }[];
  };
  ciam_stages: CiamStage[];
  domains: Domain[];
  lifecycle: {
    title: string;
    note: string;
    stages: {
      id: string;
      label: string;
      ticket: string;
      what: string;
      artefact: string;
      question: string;
      source_ids: string[];
    }[];
  };
  questions: Question[];
  schwab_map: { schwab_topic: string; admiral_evidence: string; use_it: string }[];
  sources: Source[];
  disclaimer: string;
}

const EVIDENCE: Record<Evidence, { label: string; className: string; title: string }> = {
  internal: {
    label: "Your role",
    className:
      "border-emerald-200 bg-emerald-50 text-emerald-700 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-300",
    title: "From the Admiral IGA role brief you provided. First-hand, not a public source.",
  },
  jira: {
    label: "Internal Jira",
    className:
      "border-indigo-200 bg-indigo-50 text-indigo-700 dark:border-indigo-800 dark:bg-indigo-950 dark:text-indigo-300",
    title: "An IAMPAM ticket. Real work history, but the link requires Admiral SSO.",
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

function DomainIcon({ icon }: { icon: string }) {
  if (icon === "network") return <Network className="h-5 w-5" />;
  if (icon === "users") return <Users className="h-5 w-5" />;
  if (icon === "shield") return <ShieldCheck className="h-5 w-5" />;
  if (icon === "workflow") return <Workflow className="h-5 w-5" />;
  if (icon === "code") return <Code className="h-5 w-5" />;
  if (icon === "plug") return <Plug className="h-5 w-5" />;
  if (icon === "bug") return <Bug className="h-5 w-5" />;
  return <Target className="h-5 w-5" />;
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

export default function AdmiralIgaPage() {
  // The brief sits behind the private-area password wherever the server has
  // one configured — and always in the public build. Clicking the nav entry
  // therefore lands on the unlock prompt rather than a raw API error.
  const gate = usePrivateGate();
  if (gate.loading) return <GateLoading />;
  if (gate.locked) return <PrivateAreaGate />;
  return <AdmiralIgaContent />;
}

function GateLoading() {
  return (
    <p className="text-sm text-slate-500 dark:text-slate-400">Checking access…</p>
  );
}

function AdmiralIgaContent() {
  const [data, setData] = useState<Admiral | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [openQuestions, setOpenQuestions] = useState<Set<string>>(new Set());
  const [revealed, setRevealed] = useState<Set<string>>(new Set());
  const [openScripts, setOpenScripts] = useState<Set<string>>(new Set());
  const [answers, setAnswers] = useState<Record<string, string>>({});

  useEffect(() => {
    api
      .get<Admiral>("/api/admiral")
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  const byId = useMemo(
    () => new Map((data?.sources ?? []).map((s) => [s.id, s])),
    [data]
  );

  function toggleSet(
    setter: React.Dispatch<React.SetStateAction<Set<string>>>,
    id: string
  ) {
    setter((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleQuestion(id: string) {
    setOpenQuestions((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
    setAnswers((prev) =>
      prev[id] !== undefined
        ? prev
        : { ...prev, [id]: loadDraft(`admiral:${id}`)?.text ?? "" }
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <h1 className="text-2xl font-bold">Admiral IGA Playbook</h1>
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
        <h1 className="text-2xl font-bold">Admiral IGA Playbook</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">Loading the role brief…</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header>
        <div className="flex flex-wrap items-center gap-2">
          <ShieldCheck className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
          <h1 className="text-2xl font-bold">{data.title}</h1>
          <span className="rounded-full bg-indigo-600 px-2 py-0.5 text-[10px] font-semibold text-white">
            ADMIRAL · IGA
          </span>
        </div>
        <p className="mt-2 max-w-3xl text-sm text-slate-600 dark:text-slate-300">
          {data.subtitle}
        </p>
        <div className="mt-3 flex flex-wrap gap-2 text-[11px]">
          <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
            {data.question_count} role questions
          </span>
          <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
            {data.ticket_count} Jira tickets mapped
          </span>
          <span className="rounded-full border border-slate-200 bg-white px-2.5 py-1 font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300">
            {data.ciam_stages.length} CIAM stages
          </span>
          <span className="rounded-full border border-indigo-200 bg-indigo-50 px-2.5 py-1 font-medium text-indigo-700 dark:border-indigo-800 dark:bg-indigo-950 dark:text-indigo-300">
            Sprint {data.sprint.name}
          </span>
        </div>
      </header>

      <section className="rounded-xl border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-950">
        <p className="flex items-start gap-2 text-xs leading-relaxed text-amber-900 dark:text-amber-200">
          <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
          <span>
            <strong>Internal evidence only.</strong> This page comes from the Admiral IGA role
            brief you provided and the IAMPAM ticket keys it names. No Admiral source was
            queried or researched, and this app never fetches an Admiral URL. Jira links require
            Admiral SSO. Nothing here invents a number that the brief did not contain.
          </span>
        </p>
      </section>

      {/* Role snapshot */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <span className="mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
              <Briefcase className="h-5 w-5" />
            </span>
            <div>
              <h2 className="text-lg font-semibold">{data.role.title}</h2>
              <p className="text-xs font-medium text-indigo-600 dark:text-indigo-400">
                {data.role.company} · {data.role.function}
              </p>
            </div>
          </div>
          <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-semibold text-emerald-800 dark:bg-emerald-900 dark:text-emerald-300">
            CURRENT ROLE
          </span>
        </div>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-slate-700 dark:text-slate-200">
          {data.role.summary}
        </p>
        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Quality scope
            </p>
            <ul className="mt-1.5 space-y-1">
              {data.role.focus.map((item) => (
                <li
                  key={item}
                  className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300"
                >
                  <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600 dark:text-emerald-400" />
                  {item}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Stack and environments
            </p>
            <div className="mt-1.5 flex flex-wrap gap-1">
              {data.role.stack.map((tech) => (
                <span
                  key={tech}
                  className="rounded-md border border-slate-200 bg-slate-50 px-1.5 py-0.5 text-[10px] font-medium text-slate-600 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-300"
                >
                  {tech}
                </span>
              ))}
            </div>
            <p className="mt-2 text-[11px] text-slate-500 dark:text-slate-400">
              Environments: {data.role.environments.join(" · ")}
            </p>
          </div>
        </div>
      </section>

      {/* Sprint */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
        <div className="flex items-center gap-2">
          <Clock className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          <h2 className="text-lg font-semibold">In flight — {data.sprint.name}</h2>
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {data.sprint.items.map((item) => (
            <div
              key={item.key}
              className="rounded-lg border border-slate-200 bg-slate-50 p-3 dark:border-slate-700 dark:bg-slate-800/50"
            >
              <div className="flex flex-wrap items-center gap-2">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 font-mono text-[11px] font-semibold text-indigo-700 hover:underline dark:text-indigo-300"
                >
                  {item.key}
                  <ExternalLink className="h-2.5 w-2.5" />
                </a>
                <span className="rounded-full bg-indigo-100 px-2 py-0.5 text-[10px] font-semibold text-indigo-700 dark:bg-indigo-900 dark:text-indigo-300">
                  {item.status}
                </span>
              </div>
              <p className="mt-1.5 text-xs font-medium leading-relaxed text-slate-800 dark:text-slate-100">
                {item.title}
              </p>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
                {item.detail}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* CIAM stages */}
      <section id="ciam-stages" className="space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <Network className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">CIAM integration — tested stage by stage</h2>
            <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              Transmit Security CIAM into Saviynt, across Entra groups, REST-based accounts and
              roles, Pre-Prod and Production. Each stage is a gate, not a formality.
            </p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {data.ciam_stages.map((stage) => (
            <article
              key={stage.id}
              className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
            >
              <div className="flex flex-wrap items-center gap-2">
                <span className="rounded-md bg-indigo-600 px-2 py-0.5 text-[10px] font-bold text-white">
                  {stage.label}
                </span>
                <a
                  href={`https://admiralgroup.atlassian.net/browse/${stage.ticket}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1 font-mono text-[10px] font-semibold text-indigo-700 hover:underline dark:text-indigo-300"
                >
                  {stage.ticket}
                  <ExternalLink className="h-2.5 w-2.5" />
                </a>
                <span className="text-[10px] text-slate-400 dark:text-slate-500">
                  {stage.environment}
                </span>
              </div>
              <h3 className="mt-1.5 text-sm font-semibold text-slate-800 dark:text-slate-100">
                {stage.title}
              </h3>
              <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                {stage.detail}
              </p>
              <ul className="mt-2 space-y-1">
                {stage.what_i_test.map((point) => (
                  <li
                    key={point}
                    className="flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300"
                  >
                    <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600 dark:text-emerald-400" />
                    {point}
                  </li>
                ))}
              </ul>
              <p className="mt-2 rounded-lg bg-amber-50 p-2 text-[11px] leading-relaxed text-amber-800 dark:bg-amber-950/60 dark:text-amber-300">
                <strong>Why it matters:</strong> {stage.risk}
              </p>
            </article>
          ))}
        </div>
      </section>

      {/* Domains */}
      <section className="space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <ListChecks className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">What you actually own</h2>
            <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              Seven workstreams, each with its ticket trail, its risk and a first-person way to
              describe it.
            </p>
          </div>
        </div>
        <div className="space-y-3">
          {data.domains.map((domain) => {
            const open = openScripts.has(domain.id);
            return (
              <article
                key={domain.id}
                className="overflow-hidden rounded-xl border border-slate-200 bg-white dark:border-slate-700 dark:bg-slate-900"
              >
                <div className="p-4">
                  <div className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-100 text-indigo-600 dark:bg-slate-800 dark:text-indigo-400">
                      <DomainIcon icon={domain.icon} />
                    </span>
                    <div className="min-w-0 flex-1">
                      <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-100">
                        {domain.title}
                      </h3>
                      <p className="mt-1 text-xs leading-relaxed text-slate-600 dark:text-slate-300">
                        {domain.summary}
                      </p>
                    </div>
                  </div>

                  <div className="mt-3 grid gap-3 md:grid-cols-2">
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        What you test
                      </p>
                      <ul className="mt-1 space-y-1">
                        {domain.what_i_test.map((point) => (
                          <li
                            key={point}
                            className="flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300"
                          >
                            <CheckCircle2 className="mt-0.5 h-3 w-3 shrink-0 text-emerald-600 dark:text-emerald-400" />
                            {point}
                          </li>
                        ))}
                      </ul>
                    </div>
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        Tickets
                      </p>
                      <div className="mt-1 flex flex-wrap gap-1">
                        {domain.tickets.map((ticket) => (
                          <a
                            key={ticket.key}
                            href={ticket.url}
                            target="_blank"
                            rel="noreferrer"
                            title={`${ticket.title} — ${ticket.note}`}
                            className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-1.5 py-0.5 font-mono text-[10px] text-slate-600 hover:border-indigo-300 hover:text-indigo-700 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:border-indigo-700 dark:hover:text-indigo-300"
                          >
                            {ticket.key}
                            <ExternalLink className="h-2.5 w-2.5" />
                          </a>
                        ))}
                      </div>
                    </div>
                  </div>

                  <p className="mt-3 rounded-lg bg-rose-50 p-2 text-[11px] leading-relaxed text-rose-800 dark:bg-rose-950/50 dark:text-rose-300">
                    <strong>Risk if untested:</strong> {domain.risk}
                  </p>
                  <p className="mt-2 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
                    <strong className="text-slate-600 dark:text-slate-300">Approach:</strong>{" "}
                    {domain.approach}
                  </p>

                  <div className="mt-2 flex flex-wrap items-center gap-2">
                    <button
                      type="button"
                      onClick={() => toggleSet(setOpenScripts, domain.id)}
                      aria-expanded={open}
                      className="flex items-center gap-1.5 rounded-lg bg-slate-900 px-2.5 py-1 text-[11px] font-medium text-white hover:bg-slate-700 dark:bg-indigo-600 dark:hover:bg-indigo-500"
                    >
                      <BookOpen className="h-3 w-3" />
                      {open ? "Hide how to say it" : "Show how to say it"}
                    </button>
                    <div className="flex flex-wrap gap-1">
                      {domain.source_ids.map((id) => {
                        const source = byId.get(id);
                        return source ? <SourceChip key={id} source={source} /> : null;
                      })}
                    </div>
                  </div>
                </div>

                {open ? (
                  <div className="border-t border-slate-200 bg-emerald-50/50 p-4 dark:border-slate-700 dark:bg-emerald-950/30">
                    <p className="text-[11px] font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
                      Say it like this
                    </p>
                    <p className="mt-1 whitespace-pre-wrap text-xs leading-relaxed text-slate-700 dark:text-slate-200">
                      {domain.script}
                    </p>
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      </section>

      {/* Lifecycle */}
      <section className="space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <GitBranch className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">{data.lifecycle.title}</h2>
            <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              {data.lifecycle.note}
            </p>
          </div>
        </div>
        <ol className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {data.lifecycle.stages.map((stage, index) => (
            <li
              key={stage.id}
              className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="flex h-6 w-6 items-center justify-center rounded-full bg-indigo-600 text-[11px] font-bold text-white">
                  {index + 1}
                </span>
                <span className="font-mono text-[10px] text-slate-400 dark:text-slate-500">
                  {stage.ticket}
                </span>
              </div>
              <h3 className="mt-2 text-xs font-semibold text-slate-800 dark:text-slate-100">
                {stage.label}
              </h3>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300">
                {stage.what}
              </p>
              <p className="mt-2 text-[10px] text-slate-500 dark:text-slate-400">
                <strong className="text-slate-600 dark:text-slate-300">Artefact:</strong>{" "}
                {stage.artefact}
              </p>
              <p className="mt-1 text-[10px] italic text-indigo-600 dark:text-indigo-400">
                “{stage.question}”
              </p>
            </li>
          ))}
        </ol>
      </section>

      {/* Question bank */}
      <section id="questions" className="space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <Target className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">Questions you will actually get</h2>
            <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              {data.question_count} answers built on your real tickets. Type a draft to remember
              the shape — it autosaves and follows you across devices.
            </p>
          </div>
        </div>

        <div className="space-y-2">
          {data.questions.map((q) => {
            const open = openQuestions.has(q.id);
            const showAnswer = revealed.has(q.id);
            return (
              <article
                key={q.id}
                className={cn(
                  "overflow-hidden rounded-xl border bg-white dark:bg-slate-900",
                  open
                    ? "border-indigo-300 dark:border-indigo-700"
                    : "border-slate-200 dark:border-slate-700"
                )}
              >
                <button
                  type="button"
                  onClick={() => toggleQuestion(q.id)}
                  aria-expanded={open}
                  className="flex w-full items-start gap-3 p-4 text-left"
                >
                  <span className="mt-1 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-slate-100 text-[10px] font-bold text-slate-600 dark:bg-slate-800 dark:text-slate-300">
                    {data.questions.indexOf(q) + 1}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-sm font-medium text-slate-800 dark:text-slate-100">
                        {q.prompt}
                      </h3>
                      <EvidenceBadge kind={q.evidence} />
                    </div>
                    <p className="mt-1 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
                      {q.why}
                    </p>
                  </div>
                  <ChevronDown
                    className={cn(
                      "mt-1 h-4 w-4 shrink-0 text-slate-400 transition-transform",
                      open && "rotate-180"
                    )}
                  />
                </button>

                {open ? (
                  <div className="space-y-4 border-t border-slate-200 p-4 dark:border-slate-700">
                    <div>
                      <label
                        htmlFor={`admiral-answer-${q.id}`}
                        className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400"
                      >
                        Your answer — say it out loud, then type the shape
                      </label>
                      <textarea
                        id={`admiral-answer-${q.id}`}
                        value={answers[q.id] ?? ""}
                        onChange={(e) =>
                          setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))
                        }
                        rows={4}
                        placeholder="Opening sentence, two or three key points, one real ticket…"
                        className="mt-1.5 w-full resize-y rounded-lg border border-slate-300 bg-white p-3 text-xs leading-relaxed text-slate-800 placeholder:text-slate-400 focus:border-indigo-500 focus:outline-none dark:border-slate-600 dark:bg-slate-950 dark:text-slate-100 dark:placeholder:text-slate-500"
                      />
                      <div className="mt-1.5">
                        <SaveProgress
                          storageKey={`admiral:${q.id}`}
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
                        onClick={() => toggleSet(setRevealed, q.id)}
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
                      <div className="flex flex-wrap gap-1">
                        {q.source_ids.map((id) => {
                          const source = byId.get(id);
                          return source ? <SourceChip key={id} source={source} /> : null;
                        })}
                      </div>
                    </div>

                    {showAnswer ? (
                      <div className="space-y-3">
                        <div className="rounded-lg border border-emerald-200 bg-emerald-50/60 p-3 dark:border-emerald-800 dark:bg-emerald-950/40">
                          <p className="text-[11px] font-semibold uppercase tracking-wide text-emerald-700 dark:text-emerald-300">
                            Model answer
                          </p>
                          <p className="mt-1 whitespace-pre-wrap text-xs leading-relaxed text-slate-700 dark:text-slate-200">
                            {q.answer}
                          </p>
                        </div>

                        <div>
                          <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                            Key points they are listening for
                          </p>
                          <ul className="mt-1 space-y-1">
                            {q.key_points.map((point) => (
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

                        <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-800/50">
                          <p className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                            <Lightbulb className="h-3 w-3 text-amber-500" />
                            Follow-ups
                          </p>
                          <ul className="mt-1 space-y-1">
                            {q.follow_ups.map((followUp) => (
                              <li
                                key={followUp}
                                className="flex items-start gap-1.5 text-xs leading-relaxed text-slate-600 dark:text-slate-300"
                              >
                                <ArrowRight className="mt-0.5 h-3 w-3 shrink-0 text-slate-400" />
                                {followUp}
                              </li>
                            ))}
                          </ul>
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

      {/* Schwab mapping */}
      <section className="space-y-3">
        <div className="flex items-start gap-3">
          <span className="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white">
            <BadgeCheck className="h-5 w-5" />
          </span>
          <div>
            <h2 className="text-lg font-semibold">Where this plugs into the Schwab answers</h2>
            <p className="mt-0.5 max-w-3xl text-xs leading-relaxed text-slate-500 dark:text-slate-400">
              Your Admiral work is the evidence; the Schwab playbook is the script. Map the topic,
              then tell the story from here.
            </p>
          </div>
        </div>
        <div className="grid gap-3 md:grid-cols-2">
          {data.schwab_map.map((item) => (
            <div
              key={item.schwab_topic}
              className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
            >
              <p className="text-xs font-semibold text-indigo-700 dark:text-indigo-300">
                {item.schwab_topic}
              </p>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300">
                {item.admiral_evidence}
              </p>
              <p className="mt-2 flex items-start gap-1.5 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
                <ArrowRight className="mt-0.5 h-3 w-3 shrink-0" />
                {item.use_it}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* Team */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Users className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          Who you work with
        </h2>
        <div className="mt-3 grid gap-3 sm:grid-cols-3">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              IGA engineers
            </p>
            <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
              {data.team.engineers.join(", ")}
            </p>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Test engineers
            </p>
            <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
              {data.team.test_engineers.join(", ")}
            </p>
          </div>
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
              Leadership
            </p>
            <p className="mt-1 text-xs text-slate-600 dark:text-slate-300">
              {data.team.leadership.join(", ")}
            </p>
          </div>
        </div>
        <p className="mt-3 rounded-lg bg-slate-50 p-3 text-[11px] leading-relaxed text-slate-600 dark:bg-slate-800/60 dark:text-slate-300">
          {data.team.note}
        </p>
      </section>

      {/* Sources */}
      <section className="rounded-xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-900">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Database className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
          Source ledger
        </h2>
        <ul className="mt-3 space-y-3">
          {data.sources.map((source) => (
            <li key={source.id} className="rounded-lg border border-slate-200 p-3 dark:border-slate-700">
              <div className="flex flex-wrap items-center gap-2">
                <span className="text-xs font-semibold text-slate-800 dark:text-slate-100">
                  {source.name}
                </span>
                <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10px] font-medium uppercase text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">
                  {source.type}
                </span>
                {source.url ? (
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="inline-flex items-center gap-1 text-[10px] font-medium text-indigo-700 hover:underline dark:text-indigo-300"
                  >
                    Open
                    <ExternalLink className="h-2.5 w-2.5" />
                  </a>
                ) : null}
              </div>
              <p className="mt-1 text-[11px] text-slate-500 dark:text-slate-400">
                {source.publisher} · accessed {source.accessed}
              </p>
              <p className="mt-1 text-[11px] leading-relaxed text-slate-600 dark:text-slate-300">
                {source.supports}
              </p>
            </li>
          ))}
        </ul>
        <p className="mt-3 text-[11px] leading-relaxed text-slate-500 dark:text-slate-400">
          {data.disclaimer}
        </p>
      </section>
    </div>
  );
}
