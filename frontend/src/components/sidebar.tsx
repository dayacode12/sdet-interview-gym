"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Activity,
  BookOpen,
  Braces,
  Building2,
  CalendarCheck,
  CalendarClock,
  Database,
  Dumbbell,
  FileText,
  FlaskConical,
  GraduationCap,
  Layers,
  LayoutDashboard,
  Library,
  Mic,
  Network,
  PanelLeftClose,
  PanelLeftOpen,
  ScrollText,
  ShieldCheck,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/theme-toggle";
import { SignOutButton } from "@/components/auth-gate";

const NAV = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/mind-map", label: "Mind Map", icon: Network },
  { href: "/company", label: "Company Brief", icon: Building2 },
  { href: "/plan", label: "Interview Plan", icon: CalendarClock },
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
        <p className="truncate text-sm font-semibold leading-tight text-slate-900 dark:text-slate-100">
          SDET Interview Gym
        </p>
        <p className="truncate text-[11px] leading-tight text-slate-500 dark:text-slate-400">
          Daya Sagar · Schwab Cyber Security QA
        </p>
      </div>
    </div>
  );
}

function HonestyNote() {
  return (
    <div className="border-t border-slate-200/80 dark:border-slate-700/80 px-4 py-3">
      <p className="flex items-start gap-1.5 text-[11px] leading-snug text-slate-500 dark:text-slate-400">
        <BookOpen className="mt-0.5 h-3 w-3 shrink-0" />
        Predicted questions only — not actual Schwab material.
      </p>
    </div>
  );
}

/**
 * Collapse the desktop sidebar on/off. No React state on purpose: the CSS
 * class on <html> does the work (set before first paint by the script in
 * layout.tsx), so collapsing and reloading never flashes. Mirrors
 * ThemeToggle's contract, including the localStorage fallback.
 */
function setSidebarCollapsed(next: boolean) {
  document.documentElement.classList.toggle("sidebar-collapsed", next);
  try {
    localStorage.setItem("sidebar-collapsed", next ? "1" : "0");
  } catch {
    /* storage unavailable — still collapses for this session */
  }
}

export function Sidebar() {
  const pathname = usePathname();
  const activeIndex = NAV.findIndex((n) => n.href === pathname);

  return (
    <>
      {/* Desktop sidebar */}
      <aside
        aria-label="Main navigation"
        className="desktop-sidebar sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 md:flex"
      >
        <div className="flex items-center justify-between gap-2 border-b border-slate-200/80 dark:border-slate-700/80 px-4 py-4">
          <Brand />
          <button
            type="button"
            onClick={() => setSidebarCollapsed(true)}
            aria-label="Collapse sidebar"
            title="Collapse sidebar"
            className="shrink-0 rounded-md p-1 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600 dark:text-slate-500 dark:hover:bg-slate-800 dark:hover:text-slate-300"
          >
            <PanelLeftClose className="h-3.5 w-3.5" />
          </button>
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
                    ? "bg-indigo-50 dark:bg-indigo-950 font-medium text-indigo-700 dark:text-indigo-400"
                    : "text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-slate-100"
                )}
              >
                {active ? (
                  <span className="absolute left-0 top-1/2 h-5 w-1 -translate-y-1/2 rounded-r-full bg-indigo-600" />
                ) : null}
                <Icon
                  className={cn(
                    "h-4 w-4 shrink-0 transition-colors",
                    active ? "text-indigo-600 dark:text-indigo-400" : "text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300"
                  )}
                />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="flex items-center justify-between gap-2 border-t border-slate-200/80 dark:border-slate-700/80 px-4 py-3">
          <ThemeToggle />
          <SignOutButton />
        </div>
        <HonestyNote />
      </aside>

      {/* Reopen button. Lives OUTSIDE the aside (a fixed-position child of a
          display:none element would never render). Visibility is CSS-driven:
          hidden by default, shown only on desktop while collapsed. */}
      <button
        type="button"
        onClick={() => setSidebarCollapsed(false)}
        aria-label="Open sidebar"
        title="Open sidebar"
        className="sidebar-open-fab fixed left-3 top-3 z-50 h-8 w-8 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 shadow-sm transition-colors hover:text-indigo-600 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-400 dark:hover:text-indigo-400"
      >
        <PanelLeftOpen className="h-4 w-4" />
      </button>

      {/* Mobile top bar + scrollable nav */}
      <div className="sticky top-0 z-40 border-b border-slate-200 dark:border-slate-700 bg-white/95 dark:bg-slate-900/95 backdrop-blur md:hidden">
        <div className="flex items-center justify-between gap-2 px-4 py-3">
          <Brand />
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <SignOutButton />
          </div>
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
                    : "bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
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
