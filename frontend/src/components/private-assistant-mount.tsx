"use client";

import dynamic from "next/dynamic";

import { usePrivateGate } from "@/lib/private-area";

/**
 * Loads the assistant only when the private area is open.
 *
 * The dynamic import matters: until the password is entered the assistant's
 * code is a separate chunk that is never requested, so the published site does
 * not even fetch it on load — and locally it still honours the same lock.
 */
const AssistantPanel = dynamic(
  () => import("@/components/assistant-panel").then((m) => m.AssistantPanel),
  { ssr: false },
);

export function PrivateAssistantMount() {
  const gate = usePrivateGate();
  // `loading` counts as locked: a password-configured server must never flash
  // the drawer before the status call answers.
  if (gate.locked || gate.loading) return null;
  return <AssistantPanel />;
}
