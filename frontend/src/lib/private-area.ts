"use client";

/**
 * Private area (Admiral playbook + assistant): the browser side of the gate.
 *
 * The password is sent once to POST /api/private/unlock and never stored. What
 * comes back is a short-lived token that the backend checks on every protected
 * request, so this hook is convenience — not the security boundary.
 */

import { useEffect, useState, useSyncExternalStore } from "react";

import { api, ApiError } from "@/lib/api";
import { HIDE_ADMIRAL, HIDE_ASSISTANT } from "@/lib/features";
import {
  clearPrivateToken,
  getPrivateToken,
  setPrivateToken,
  subscribePrivateToken,
} from "@/lib/private-token";

export interface UnlockResponse {
  token: string;
  expires_in: number;
}

export interface PrivateStatus {
  configured: boolean;
  unlocked: boolean;
  token_ttl_seconds: number;
}

/** True when this browser holds an unexpired token. */
export function usePrivateUnlocked(): boolean {
  return useSyncExternalStore(
    subscribePrivateToken,
    () => getPrivateToken() !== null,
    () => false,
  );
}

export async function unlockPrivateArea(password: string): Promise<void> {
  const body = await api.post<UnlockResponse>("/api/private/unlock", { password });
  if (!body?.token) {
    throw new ApiError(502, "The server did not return an access token. Try again.");
  }
  setPrivateToken(body.token);
}

export function lockPrivateArea(): void {
  clearPrivateToken();
}

/** Is the gate configured on the server, and are we already through it? */
export async function fetchPrivateStatus(): Promise<PrivateStatus> {
  return api.get<PrivateStatus>("/api/private/status");
}

export interface PrivateGateState {
  /** Render the locked prompt instead of the protected content. */
  locked: boolean;
  /** Still asking the server whether a password is configured. */
  loading: boolean;
  /** Server answer: is PRIVATE_AREA_PASSWORD set? null = not known yet. */
  configured: boolean | null;
}

/**
 * Decide whether the protected content (Admiral playbook, assistant) should be
 * behind the password prompt.
 *
 * The server is the authority: if PRIVATE_AREA_PASSWORD is unset it says so,
 * and there is nothing to unlock — that keeps a fresh clone working with no
 * setup. Set a password (locally in backend/.env, or on Render) and the same
 * UI locks in both places. The public build always prompts, because trusting
 * "no password configured" to unlock published content is the wrong default.
 */
export function usePrivateGate(): PrivateGateState {
  const unlocked = usePrivateUnlocked();
  const [configured, setConfigured] = useState<boolean | null>(null);

  useEffect(() => {
    let alive = true;
    fetchPrivateStatus()
      .then((status) => alive && setConfigured(status.configured))
      .catch(() => alive && setConfigured(null));
    return () => {
      alive = false;
    };
  }, []);

  if (HIDE_ASSISTANT || HIDE_ADMIRAL) {
    // Public build: never trust "no password configured" to unlock content.
    return { locked: !unlocked, loading: false, configured };
  }
  if (configured === null) return { locked: false, loading: true, configured };
  return { locked: configured && !unlocked, loading: false, configured };
}
