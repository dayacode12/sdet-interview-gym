// Draft persistence for work-in-progress answers and code.
//
// Two layers on purpose:
//  1. localStorage  — instant, offline, survives reloads on this device.
//  2. /api/drafts   — debounced push + pull-on-focus, so the same program
//                     opens in any browser signed in with the same credentials.
//
// Newer copy wins per key (updated_ms vs savedAt). If the backend is running
// on Render's free tier its SQLite file is ephemeral, so the server layer is
// only durable when DATABASE_URL points at a real PostgreSQL.

import { api } from "@/lib/api";

export interface Draft {
  text: string;
  savedAt: number;
}

const PREFIX = "draft:";
const SYNC_EVENT = "sdet-gym:drafts-synced";
export const DRAFT_PUSHED_EVENT = "sdet-gym:draft-pushed";
const PUSH_DELAY_MS = 600;

const timers = new Map<string, ReturnType<typeof setTimeout>>();

function storage(): Storage | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage;
  } catch {
    return null;
  }
}

function writeLocal(key: string, text: string, savedAt: number): void {
  const store = storage();
  if (!store) return;
  try {
    store.setItem(PREFIX + key, JSON.stringify({ text, savedAt }));
  } catch {
    // Storage full or unavailable — drafts are best-effort only.
  }
}

export function loadDraft(key: string): Draft | null {
  const store = storage();
  if (!store) return null;
  try {
    const raw = store.getItem(PREFIX + key);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<Draft>;
    if (typeof parsed?.text !== "string") return null;
    return { text: parsed.text, savedAt: Number(parsed.savedAt) || 0 };
  } catch {
    return null;
  }
}

/** Save locally right now; queue a debounced push to the backend. */
export function saveDraft(key: string, text: string): number {
  const savedAt = Date.now();
  writeLocal(key, text, savedAt);
  schedulePush(key, text);
  return savedAt;
}

function schedulePush(key: string, text: string): void {
  const existing = timers.get(key);
  if (existing) clearTimeout(existing);
  timers.set(
    key,
    setTimeout(async () => {
      timers.delete(key);
      const ok = await pushDraft(key, text);
      if (typeof window !== "undefined") {
        window.dispatchEvent(
          new CustomEvent(DRAFT_PUSHED_EVENT, { detail: { key, ok } })
        );
      }
    }, PUSH_DELAY_MS)
  );
}

async function pushDraft(key: string, text: string): Promise<boolean> {
  try {
    await api.put(`/api/drafts/${encodeURIComponent(key)}`, { text });
    return true;
  } catch {
    return false; // offline or backend asleep — the local copy stays and syncs later
  }
}

export function clearDraft(key: string): void {
  const store = storage();
  if (store) {
    try {
      store.removeItem(PREFIX + key);
    } catch {
      /* ignore */
    }
  }
  const pending = timers.get(key);
  if (pending) {
    clearTimeout(pending);
    timers.delete(key);
  }
  void api.delete(`/api/drafts/${encodeURIComponent(key)}`).catch(() => {});
}

interface ServerDraft {
  key: string;
  text: string;
  updated_ms: number;
}

function localKeys(store: Storage): string[] {
  const keys: string[] = [];
  for (let i = 0; i < store.length; i += 1) {
    const full = store.key(i);
    if (full?.startsWith(PREFIX)) keys.push(full.slice(PREFIX.length));
  }
  return keys;
}

/**
 * Merge drafts from other devices: pull anything newer than the local copy,
 * push local copies the server doesn't know yet (created while offline), and
 * let open editors know a draft arrived after they mounted.
 */
export async function syncDrafts(): Promise<void> {
  const store = storage();
  if (!store) return;

  let serverDrafts: ServerDraft[];
  try {
    const resp = await api.get<{ drafts: ServerDraft[] }>("/api/drafts");
    serverDrafts = resp.drafts;
  } catch {
    return; // offline — local drafts keep working
  }

  let changed = false;
  const known = new Set<string>();

  for (const remote of serverDrafts) {
    known.add(remote.key);
    const local = loadDraft(remote.key);
    if (!local || remote.updated_ms > local.savedAt) {
      writeLocal(remote.key, remote.text, remote.updated_ms);
      changed = true;
    } else if (local.savedAt > remote.updated_ms) {
      void pushDraft(remote.key, local.text);
    }
  }

  for (const key of localKeys(store)) {
    if (known.has(key)) continue;
    const local = loadDraft(key);
    if (local) void pushDraft(key, local.text);
  }

  if (changed) {
    window.dispatchEvent(new CustomEvent(SYNC_EVENT));
  }
}

/** Notified when drafts arrived from another device. Returns unsubscribe. */
export function onDraftsSynced(handler: () => void): () => void {
  if (typeof window === "undefined") return () => {};
  window.addEventListener(SYNC_EVENT, handler);
  return () => window.removeEventListener(SYNC_EVENT, handler);
}

export function timeAgo(timestamp: number): string {
  const seconds = Math.max(0, Math.round((Date.now() - timestamp) / 1000));
  if (seconds < 45) return "just now";
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.round(minutes / 60);
  if (hours < 24) return `${hours} hr${hours === 1 ? "" : "s"} ago`;
  const days = Math.round(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}
