"use client";

import { useEffect, useRef, useState } from "react";
import { Check, CloudOff, CloudUpload, RotateCcw } from "lucide-react";
import {
  DRAFT_PUSHED_EVENT,
  clearDraft,
  loadDraft,
  onDraftsSynced,
  saveDraft,
  timeAgo,
} from "@/lib/drafts";
import { cn } from "@/lib/utils";

interface SaveProgressProps {
  /** Unique per item, e.g. `java:reverse-words` — one draft per question. */
  storageKey: string;
  /** Current editor/textarea content. */
  value: string;
  /** The value the editor starts from (starter code / default SQL / ""). */
  pristine: string;
  /** Restore handler — usually the same setter as the editor. */
  onRestore: (text: string) => void;
}

type SyncState = "idle" | "saving" | "synced" | "offline";

/**
 * Autosaving draft indicator. Parents restore the stored text when an item is
 * opened (loadDraft) and own the editor state; this component saves every
 * edit — localStorage instantly, the backend debounced — reports sync status
 * honestly, and can reset the editor to its pristine starting point.
 */
export function SaveProgress({ storageKey, value, pristine, onRestore }: SaveProgressProps) {
  const [savedAt, setSavedAt] = useState<number | null>(null);
  const [sync, setSync] = useState<SyncState>("idle");
  const baselineRef = useRef(value);
  const lastRef = useRef<string | null>(null);

  // New target: remember the initial value so the pristine starter is never
  // written over an existing draft before it gets restored.
  useEffect(() => {
    const stored = loadDraft(storageKey);
    baselineRef.current = value;
    lastRef.current = stored?.text ?? null;
    setSavedAt(stored?.savedAt ?? null);
    setSync("idle");
    // `value` is intentionally sampled once per key change.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [storageKey]);

  // Autosave user edits only (never the initial render / pristine value).
  useEffect(() => {
    if (value === baselineRef.current || value === lastRef.current) return;
    const ts = saveDraft(storageKey, value);
    lastRef.current = value;
    setSavedAt(ts);
    setSync("saving");
  }, [value, storageKey]);

  // A draft may arrive from another device after this editor mounted.
  useEffect(
    () =>
      onDraftsSynced(() => {
        const stored = loadDraft(storageKey);
        if (!stored) return;
        if (value === baselineRef.current && stored.text !== value) {
          onRestore(stored.text);
        }
        setSavedAt(stored.savedAt);
      }),
    [storageKey, value, onRestore]
  );

  // Honest sync status once the debounced push finishes.
  useEffect(() => {
    const handler = (event: Event) => {
      const detail = (event as CustomEvent<{ key: string; ok: boolean }>).detail;
      if (detail?.key === storageKey) setSync(detail.ok ? "synced" : "offline");
    };
    window.addEventListener(DRAFT_PUSHED_EVENT, handler);
    return () => window.removeEventListener(DRAFT_PUSHED_EVENT, handler);
  }, [storageKey]);

  const reset = () => {
    clearDraft(storageKey);
    baselineRef.current = pristine;
    lastRef.current = pristine;
    setSavedAt(null);
    setSync("idle");
    onRestore(pristine);
  };

  let Icon = Check;
  let tone = "text-slate-400 dark:text-slate-500";
  let label = "Drafts save automatically as you type — reload or switch questions and your work is still here.";
  if (savedAt !== null) {
    if (sync === "offline") {
      Icon = CloudOff;
      tone = "text-amber-600 dark:text-amber-400";
      label = `Saved on this device · ${timeAgo(savedAt)} — will sync when the server is reachable.`;
    } else if (sync === "saving") {
      Icon = CloudUpload;
      tone = "text-slate-500 dark:text-slate-400";
      label = "Autosaving…";
    } else if (sync === "synced") {
      Icon = Check;
      tone = "text-emerald-600 dark:text-emerald-400";
      label = `Autosaved and synced — opens on your other devices · ${timeAgo(savedAt)}.`;
    } else {
      Icon = Check;
      tone = "text-slate-500 dark:text-slate-400";
      label = `Autosaved · ${timeAgo(savedAt)}.`;
    }
  }

  return (
    <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5 text-xs">
      <span className={cn("flex min-w-0 items-center gap-1.5", tone)}>
        <Icon className="h-3.5 w-3.5 shrink-0" />
        <span className="min-w-0">{label}</span>
      </span>
      <button
        type="button"
        onClick={reset}
        className="flex shrink-0 items-center gap-1 rounded-md px-1.5 py-0.5 font-medium text-slate-500 transition hover:bg-slate-100 hover:text-slate-700 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
      >
        <RotateCcw className="h-3 w-3" />
        {pristine === "" ? "Clear draft" : "Reset to starter"}
      </button>
    </div>
  );
}
