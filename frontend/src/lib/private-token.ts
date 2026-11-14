/**
 * Storage for the private-area token (Admiral playbook + assistant).
 *
 * The token is issued by the backend only after the password is verified, so
 * this module never holds the password and never decides on its own whether a
 * caller is allowed in. It is kept in sessionStorage: closing the tab locks the
 * private area again, and a shared machine does not inherit the unlock.
 */

const STORAGE_KEY = "sdet-gym-private-token";

const listeners = new Set<() => void>();

function readStored(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function expiryOf(token: string): number | null {
  const [raw] = token.split(".");
  const seconds = Number(raw);
  return Number.isFinite(seconds) ? seconds * 1000 : null;
}

function isUsable(token: string | null): token is string {
  if (!token) return false;
  const expiresAt = expiryOf(token);
  return expiresAt !== null && expiresAt > Date.now();
}

function notify() {
  for (const listener of listeners) listener();
}

export function getPrivateToken(): string | null {
  const stored = readStored();
  if (!isUsable(stored)) {
    if (stored) clearPrivateToken();
    return null;
  }
  return stored;
}

export function setPrivateToken(token: string): void {
  try {
    window.sessionStorage.setItem(STORAGE_KEY, token);
  } catch {
    /* storage unavailable — the unlock lasts for this page view only */
  }
  notify();
}

export function clearPrivateToken(): void {
  try {
    window.sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    /* nothing to clear */
  }
  notify();
}

export function subscribePrivateToken(listener: () => void): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

/** Milliseconds left on the current token, or 0 when locked/expired. */
export function privateTokenRemainingMs(): number {
  const token = getPrivateToken();
  if (!token) return 0;
  return Math.max(0, (expiryOf(token) ?? 0) - Date.now());
}
