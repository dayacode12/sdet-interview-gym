import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export const RUBRIC_LABELS: Record<string, string> = {
  technical_accuracy: "Technical accuracy (30%)",
  practical_implementation: "Practical implementation (25%)",
  problem_solving: "Problem solving (20%)",
  communication: "Communication (15%)",
  security_awareness: "Security awareness (10%)",
};

export function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-600";
  if (score >= 60) return "text-amber-600";
  return "text-rose-600";
}

export function scoreBar(score: number): string {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-amber-500";
  return "bg-rose-500";
}

export function difficultyBadge(difficulty: string): string {
  switch (difficulty.toLowerCase()) {
    case "easy":
      return "bg-emerald-100 text-emerald-800";
    case "medium":
      return "bg-amber-100 text-amber-800";
    case "hard":
      return "bg-rose-100 text-rose-800";
    default:
      return "bg-slate-100 text-slate-800";
  }
}
