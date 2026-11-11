/**
 * Client-side login gate for a statically exported site (GitHub Pages).
 *
 * Honest limits, by design: there is no server to authenticate against on a
 * static host, so this gate runs in the browser. It keeps out visitors who
 * don't know the credentials, but a determined technical reader of the public
 * bundle could bypass it. The practice data behind it is public research
 * content anyway — no personal data is stored. The plaintext password is
 * NEVER committed: only this salted one-way SHA-256 hash is.
 */

export const AUTH_KEY = "sdet-gym-auth";

/**
 * sha256("sdet-gym-v1:<username>:<password>") — hex.
 * Double-clicking security theater would be pretending otherwise.
 */
export const AUTH_TOKEN =
  "c85e4b23455aeaee349c8e0a57347644f7c99ebb134d72a5284a864f9ee39166";

/** Verify username + password against the committed hash (Web Crypto). */
export async function verifyCredentials(username: string, password: string): Promise<boolean> {
  try {
    const data = new TextEncoder().encode(`sdet-gym-v1:${username}:${password}`);
    const digest = await crypto.subtle.digest("SHA-256", data);
    const hex = Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
    return hex === AUTH_TOKEN;
  } catch {
    return false;
  }
}

/** True when the current browser holds a valid session token. */
export function hasValidSession(): boolean {
  try {
    return localStorage.getItem(AUTH_KEY) === AUTH_TOKEN;
  } catch {
    return false;
  }
}
