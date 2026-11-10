"use client";

import { useEffect, useState } from "react";
import { Check, FileClock, RotateCcw, Save, Trash2 } from "lucide-react";
import { clearDraft, loadDraft, saveDraft, timeAgo } from "@/lib/drafts";
import { cn } from "@/lib/utils";

interface SaveProgressProps {
  /** Unique per item, e.g. `java:reverse-words` — one draft per question. */
  storageKey: string;
  /** Current editor/textarea content. */
  value: string;
  /** The value the editor starts from (starter code / default SQL / "") —
   *  used to detect "you have an older draft but haven't typed yet". */
  pristine: string;
  /** Restore handler — usually the same setter as the editor. */
  onRestore: (text: string) => void;
}

/**
 * Save-progress control for in-progress work. Shows a Save button, a
 * "Saved · 2 min ago" status, and — when a stored draft differs from the
 * untouched editor — a restore banner so drafts survive reloads and
 * question switching.
 */
export function SaveProgress({ storageKey, value, pristine, onRestore }: SaveProgressProps) {
  const [savedText, setSavedText] = useState<string | null>(null);
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const [dismissed, setDismissed] = useState(false);

  // Load the stored draft whenever the target item changes.
  useEffect(() => {
    const d = loadDraft(storageKey);
    setSavedText(d?.text ?? null);
    setSavedAt(d?.savedAt ?? null);
    setDismissed(false);
  }, [storageKey]);

  const isSaved = savedText !== null && savedText === value;
  const offerRestore =
    !dismissed && savedText !== null && savedText !== value && value === pristine;

  const save = () => {
    const ts = saveDraft(storageKey, value);
    setSavedText(value);
    setSavedAt(ts);
    setDismissed(false);
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {offerRestore ? (
        <div className="flex w-full flex-wrap items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-800 dark:border-amber-800 dark:bg-amber-950 dark:text-amber-300">
          <FileClock className="h-3.5 w-3.5 shrink-0" />
          <span className="min-w-0 flex-1">
            You have a saved draft from {savedAt ? timeAgo(savedAt) : "earlier"}.
          </span>
          <button
            onClick={() => {
              onRestore(savedText ?? "");
              setDismissed(true);
            }}
            className="flex items-center gap-1 rounded-md bg-amber-600 px-2 py-1 font-medium text-white transition hover:bg-amber-700"
          >
            <RotateCcw className="h-3 w-3" /> Restore draft
          </button>
          <button
            onClick={() => {
              clearDraft(storageKey);
              setSavedText(null);
              setSavedAt(null);
              setDismissed(true);
            }}
            className="flex items-center gap-1 rounded-md border border-amber-300 px-2 py-1 font-medium transition hover:bg-amber-100 dark:border-amber-700 dark:hover:bg-amber-900"
            aria-label="Discard saved draft"
          >
            <Trash2 className="h-3 w-3" /> Discard
          </button>
        </div>
      ) : null}

      <button
        onClick={save}
        className={cn(
          "flex items-center gap-1.5 rounded-lg border px-3.5 py-2 text-sm font-medium transition",
          isSaved
            ? "border-emerald-300 bg-emerald-50 text-emerald-700 hover:bg-emerald-100 dark:border-emerald-800 dark:bg-emerald-950 dark:text-emerald-400 dark:hover:bg-emerald-900"
            : "border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-900 dark:text-slate-300 dark:hover:bg-slate-800"
        )}
      >
        {isSaved ? <Check className="h-4 w-4" /> : <Save className="h-4 w-4" />}
        {isSaved ? "Saved" : "Save progress"}
      </button>

      <span
        className={cn(
          "text-xs",
          isSaved
            ? "text-emerald-600 dark:text-emerald-400"
            : savedText !== null
              ? "text-amber-600 dark:text-amber-400"
              : "text-slate-400 dark:text-slate-500"
        )}
      >
        {isSaved
          ? `draft stored${savedAt ? ` · ${timeAgo(savedAt)}` : ""}`
          : savedText !== null
            ? "unsaved changes — your last save is kept until you save again"
            : "stored on this device, survives reloads"}
      </span>
    </div>
  );
}
