"use client";

import type { EvaluationResult } from "@/lib/api";
import { RUBRIC_LABELS, scoreBar, scoreColor } from "@/lib/utils";

export function RubricDisplay({ evaluation }: { evaluation: EvaluationResult }) {
  const dims = Object.keys(RUBRIC_LABELS);
  return (
    <div className="space-y-3">
      <div className="flex items-baseline justify-between">
        <span className="text-sm font-medium text-slate-700 dark:text-slate-300">Overall</span>
        <span className={scoreColor(evaluation.overall) + " text-lg font-bold"}>
          {evaluation.overall.toFixed(1)} / 100
        </span>
      </div>
      {dims.map((dim) => {
        const score = evaluation.scores[dim as keyof typeof evaluation.scores] ?? 0;
        const feedback = evaluation.feedback?.[dim]?.note;
        return (
          <div key={dim}>
            <div className="mb-1 flex items-baseline justify-between text-xs">
              <span className="font-medium text-slate-600 dark:text-slate-300">{RUBRIC_LABELS[dim]}</span>
              <span className={scoreColor(score) + " font-semibold"}>{score.toFixed(1)}</span>
            </div>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-700">
              <div className={scoreBar(score) + " h-full rounded-full"} style={{ width: `${score}%` }} />
            </div>
            {feedback ? (
              <p className="mt-1 text-[11px] leading-snug text-slate-500 dark:text-slate-400">{feedback}</p>
            ) : null}
          </div>
        );
      })}
      <p className="border-t border-slate-200 dark:border-slate-700 pt-2 text-[11px] text-slate-400 dark:text-slate-500">
        Method: {evaluation.method}. Rule-based scoring measures keyword coverage, structure and
        length — it is a practice aid, not a human judge.
      </p>
    </div>
  );
}

export function ScoreBadge({ score }: { score: number }) {
  return (
    <span className={scoreColor(score) + " font-semibold"}>
      {score.toFixed(1)}
    </span>
  );
}
