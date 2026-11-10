// Local draft persistence for work-in-progress answers and code.
// Drafts live in localStorage under `draft:<key>` as { text, savedAt } so the
// user never loses typing when switching questions or reloading the page.
// (Submitted work is already stored server-side; this is for unsaved edits.)

export interface Draft {
  text: string;
  savedAt: number;
}

const PREFIX = "draft:";

export function loadDraft(key: string): Draft | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem(PREFIX + key);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as Partial<Draft>;
    if (typeof parsed?.text !== "string") return null;
    return { text: parsed.text, savedAt: Number(parsed.savedAt) || 0 };
  } catch {
    return null;
  }
}

export function saveDraft(key: string, text: string): number {
  const savedAt = Date.now();
  if (typeof window !== "undefined") {
    try {
      window.localStorage.setItem(PREFIX + key, JSON.stringify({ text, savedAt }));
    } catch {
      // Storage full or unavailable — drafts are best-effort only.
    }
  }
  return savedAt;
}

export function clearDraft(key: string): void {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(PREFIX + key);
  } catch {
    // ignore
  }
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
