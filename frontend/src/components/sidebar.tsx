"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BookOpen,
  Braces,
  CalendarCheck,
  Database,
  Dumbbell,
  FileText,
  FlaskConical,
  GraduationCap,
  Layers,
  LayoutDashboard,
  Library,
  Mic,
  ScrollText,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/roadmap", label: "Roadmap", icon: CalendarCheck },
  { href: "/java-lab", label: "Java Lab", icon: Braces },
  { href: "/automation-lab", label: "Automation Lab", icon: FlaskConical },
  { href: "/api-lab", label: "API Lab", icon: Layers },
  { href: "/sql-playground", label: "SQL Playground", icon: Database },
  { href: "/iam-lab", label: "IAM Lab", icon: ShieldCheck },
  { href: "/scenarios", label: "Scenario Simulator", icon: Dumbbell },
  { href: "/mock-interview", label: "Mock Interview", icon: Mic },
  { href: "/resume", label: "Resume Deep Dive", icon: FileText },
  { href: "/flashcards", label: "Flashcards", icon: Library },
  { href: "/analytics", label: "Analytics", icon: Activity },
  { href: "/cheatsheet", label: "Cheat Sheet", icon: ScrollText },
];

function Brand() {
  return (
    <div className="flex items-center gap-2.5">
      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-white shadow-sm">
        <GraduationCap className="h-5 w-5" />
      </span>
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold leading-tight text-slate-900">
          SDET Interview Gym
        </p>
        <p className="truncate text-[11px] leading-tight text-slate-500">
          Daya Sagar · Schwab Cyber Security QA
        </p>
      </div>
    </div>
  );
}

function HonestyNote() {
  return (
    <div className="border-t border-slate-200/80 px-4 py-3">
      <p className="flex items-start gap-1.5 text-[11px] leading-snug text-slate-500">
        <BookOpen className="mt-0.5 h-3 w-3 shrink-0" />
        Predicted questions only — not actual Schwab material.
      </p>
    </div>
  );
}

export function Sidebar() {
  const pathname = usePathname();
  const activeIndex = NAV.findIndex((n) => n.href === pathname);

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-slate-200 bg-white md:flex">
        <div className="border-b border-slate-200/80 px-4 py-4">
          <Brand />
        </div>
        <nav className="flex-1 overflow-y-auto px-3 py-4">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "group relative mb-0.5 flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-indigo-50 font-medium text-indigo-700"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                )}
              >
                {active ? (
                  <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-indigo-600" />
                ) : null}
                <Icon
                  className={cn(
                    "h-4 w-4 shrink-0 transition-colors",
                    active ? "text-indigo-600" : "text-slate-400 group-hover:text-slate-600"
                  )}
                />
                {label}
              </Link>
            );
          })}
        </nav>
        <HonestyNote />
      </aside>

      {/* Mobile top bar + scrollable nav */}
      <div className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur md:hidden">
        <div className="px-4 py-3">
          <Brand />
        </div>
        <nav className="scrollbar-none flex gap-1 overflow-x-auto px-3 pb-2">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = pathname === href;
            return (
              <Link
                key={href}
                href={href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex shrink-0 items-center gap-1.5 rounded-full px-3 py-1.5 text-xs font-medium transition-colors",
                  active
                    ? "bg-indigo-600 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                )}
              >
                <Icon className="h-3.5 w-3.5" />
                {label}
              </Link>
            );
          })}
        </nav>
      </div>
    </>
  );
}
