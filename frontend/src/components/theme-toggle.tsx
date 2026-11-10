"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";
import { cn } from "@/lib/utils";

/**
 * Class-based theme toggle. The initial class is set by the inline script in
 * layout.tsx before paint; this component syncs to it after mount (so no
 * hydration mismatch) and persists the explicit choice to localStorage.
 */
export function ThemeToggle({ className }: { className?: string }) {
  const [dark, setDark] = useState<boolean | null>(null);

  useEffect(() => {
    setDark(document.documentElement.classList.contains("dark"));
  }, []);

  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    try {
      localStorage.setItem("theme", next ? "dark" : "light");
    } catch {
      /* storage unavailable — theme still applies for this session */
    }
  };

  return (
    <button
      onClick={toggle}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      title={dark ? "Switch to light mode" : "Switch to dark mode"}
      className={cn(
        "flex items-center gap-2 rounded-full border border-slate-200 bg-white px-2.5 py-1.5 text-xs font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800",
        className
      )}
    >
      {dark === null ? (
        <span className="h-3.5 w-3.5" />
      ) : dark ? (
        <Sun className="h-3.5 w-3.5 text-amber-500" />
      ) : (
        <Moon className="h-3.5 w-3.5 text-indigo-600" />
      )}
      <span className="hidden sm:inline">{dark ? "Light" : "Dark"} mode</span>
    </button>
  );
}
