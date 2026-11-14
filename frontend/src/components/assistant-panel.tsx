"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import {
  AlertTriangle,
  BookOpen,
  Loader2,
  Mic,
  Send,
  Sparkles,
  X,
} from "lucide-react";
import { api, ApiError } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Source {
  index: number;
  page: string;
  route: string;
  title: string;
  id: string;
}

interface Answer {
  answer: string;
  sources: Source[];
  model: string | null;
  degraded: boolean;
  note: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
  degraded?: boolean;
  failed?: boolean;
}

interface AssistantStatus {
  enabled: boolean;
  model: string | null;
  excerpt_count: number;
  note: string;
}

const THREAD_KEY = "sdet-assistant-thread";
const MAX_STORED_MESSAGES = 24;
const MAX_HISTORY_CHARS = 1500;

/**
 * Minimal Web Speech API types.
 *
 * `SpeechRecognition` is still not in TypeScript's DOM lib, and the prefixed
 * `webkitSpeechRecognition` is what Chrome/Edge actually expose.
 */
interface SpeechAlternative {
  transcript: string;
}

interface SpeechResult {
  readonly isFinal: boolean;
  readonly length: number;
  [index: number]: SpeechAlternative;
}

interface SpeechResultList {
  readonly length: number;
  [index: number]: SpeechResult;
}

interface SpeechResultEvent extends Event {
  readonly resultIndex: number;
  readonly results: SpeechResultList;
}

interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  abort: () => void;
  onresult: ((event: SpeechResultEvent) => void) | null;
  onerror: ((event: Event & { error?: string }) => void) | null;
  onend: (() => void) | null;
}

type SpeechRecognitionCtor = new () => SpeechRecognitionLike;

function getSpeechRecognition(): SpeechRecognitionCtor | null {
  if (typeof window === "undefined") return null;
  const scope = window as unknown as {
    SpeechRecognition?: SpeechRecognitionCtor;
    webkitSpeechRecognition?: SpeechRecognitionCtor;
  };
  return scope.SpeechRecognition ?? scope.webkitSpeechRecognition ?? null;
}

/** iOS Safari ends a "continuous" session after one phrase anyway. */
function isAppleMobile(): boolean {
  if (typeof navigator === "undefined") return false;
  return /iP(hone|ad|od)/.test(navigator.userAgent);
}

/** Join two dictation fragments without doubling spaces. */
function joinTranscript(left: string, right: string): string {
  const parts = [left.trim(), right.trim()].filter(Boolean);
  return parts.join(" ");
}

/**
 * Hydration-safe feature detection.
 *
 * The server snapshot is always `false`, the client snapshot reflects the
 * browser. Using an external store avoids a "setState inside effect" pass just
 * to learn whether dictation exists.
 */
function useSpeechSupported(): boolean {
  return useSyncExternalStore(
    () => () => {},
    () => Boolean(getSpeechRecognition()),
    () => false,
  );
}

/** MediaRecorder + getUserMedia path (Groq Whisper transcription). */
function useRecorderSupported(): boolean {
  return useSyncExternalStore(
    () => () => {},
    () =>
      typeof MediaRecorder !== "undefined" &&
      Boolean(navigator.mediaDevices?.getUserMedia),
    () => false,
  );
}

/**
 * Read the saved thread during the first render.
 *
 * Reading storage in a lazy initializer (instead of an effect) avoids a second
 * render and the "setState in effect" lint rule. The drawer is closed on first
 * paint, so the restored messages never affect the server-rendered markup.
 */
function readThread(): Message[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.sessionStorage.getItem(THREAD_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as Message[];
    return Array.isArray(parsed) ? parsed.slice(-MAX_STORED_MESSAGES) : [];
  } catch {
    return [];
  }
}

const SUGGESTIONS: Record<string, string[]> = {
  "/round-1": [
    "Answer \"tell me about yourself\" for Round 1.",
    "What does the 60-minute flow cover?",
    "How do I use my Admiral work in the IAM scenario?",
  ],
  "/admiral-iga": [
    "Tell me about your current role at Admiral.",
    "Walk me through CIAM Stage 2 termination.",
    "How does my Admiral work map to Schwab topics?",
  ],
  "/resume": [
    "Walk me through my 300+ automated test cases.",
    "How should I explain the race condition defect?",
    "What is my honest CyberArk boundary?",
  ],
  "/scenarios": [
    "A terminated employee still has access — how do I test it?",
    "How do I investigate an access certification gap?",
  ],
  "/sql-playground": [
    "Find inactive users who still hold roles.",
    "How do I validate revoked certifications?",
  ],
};

const DEFAULT_SUGGESTIONS = [
  "How do I answer \"tell me about yourself\"?",
  "Test a leaver who still has access.",
  "Explain the difference between 401 and 403.",
  "What is on the study roadmap?",
];

function RichText({ text }: { text: string }) {
  const blocks: React.ReactNode[] = [];
  const lines = text.split("\n");
  const codeLines: string[] = [];
  let inCode = false;
  let key = 0;

  const inline = (value: string) => {
    const parts = value.split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
    return parts.map((part, index) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={`${key}-${index}`} className="font-semibold">
            {part.slice(2, -2)}
          </strong>
        );
      }
      if (part.startsWith("`") && part.endsWith("`")) {
        return (
          <code
            key={`${key}-${index}`}
            className="rounded bg-slate-100 px-1 py-0.5 font-mono text-[11px] text-slate-800 dark:bg-slate-800 dark:text-slate-200"
          >
            {part.slice(1, -1)}
          </code>
        );
      }
      return <span key={`${key}-${index}`}>{part}</span>;
    });
  };

  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.startsWith("```")) {
      if (inCode) {
        blocks.push(
          <pre
            key={`code-${key++}`}
            className="overflow-x-auto rounded-lg bg-slate-950 p-2.5 font-mono text-[11px] leading-relaxed text-slate-100"
          >
            {codeLines.join("\n")}
          </pre>,
        );
        codeLines.length = 0;
        inCode = false;
      } else {
        inCode = true;
      }
      continue;
    }
    if (inCode) {
      codeLines.push(line);
      continue;
    }
    if (!trimmed) {
      blocks.push(<div key={`gap-${key++}`} className="h-1.5" />);
      continue;
    }
    const bullet = /^[-*•]\s+/.test(trimmed);
    const numbered = /^\d+[.)]\s+/.test(trimmed);
    const heading = /^#{1,4}\s+/.test(trimmed);
    const body = trimmed
      .replace(/^#{1,4}\s+/, "")
      .replace(/^[-*•]\s+/, "");
    const lineKey = key++;
    blocks.push(
      <p
        key={`line-${lineKey}`}
        className={cn(
          "text-[13px] leading-relaxed",
          heading && "font-semibold",
          (bullet || numbered) && "pl-4 -indent-4",
        )}
      >
        {bullet ? "• " : ""}
        {inline(body)}
      </p>,
    );
  }

  if (inCode) {
    blocks.push(
      <pre
        key={`code-${key++}`}
        className="overflow-x-auto rounded-lg bg-slate-950 p-2.5 font-mono text-[11px] leading-relaxed text-slate-100"
      >
        {codeLines.join("\n")}
      </pre>,
    );
  }

  return <div className="space-y-1">{blocks}</div>;
}

export function AssistantPanel() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>(readThread);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState<AssistantStatus | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [listening, setListening] = useState(false);
  const [recording, setRecording] = useState(false);
  const [transcribing, setTranscribing] = useState(false);
  const [micError, setMicError] = useState<string | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const endRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognitionLike | null>(null);
  const dictationBaseRef = useRef("");
  const recorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const streamRef = useRef<MediaStream | null>(null);
  const recordTimerRef = useRef<number | null>(null);
  const cancelledRef = useRef(false);
  const speechSupported = useSpeechSupported();
  const recorderSupported = useRecorderSupported();
  const micAvailable = speechSupported || recorderSupported;

  // Persist the thread so navigating between pages never loses the interview
  // conversation. sessionStorage keeps it scoped to this tab.
  useEffect(() => {
    if (messages.length === 0) return;
    try {
      window.sessionStorage.setItem(
        THREAD_KEY,
        JSON.stringify(messages.slice(-MAX_STORED_MESSAGES)),
      );
    } catch {
      /* storage can be full or blocked */
    }
  }, [messages]);

  useEffect(() => {
    if (!open) return;
    let active = true;
    void (async () => {
      try {
        const body = await api.get<AssistantStatus>("/api/assistant/status");
        if (active) {
          setStatus(body);
          setStatusError(null);
        }
      } catch (err) {
        if (!active) return;
        setStatus(null);
        if (err instanceof ApiError && err.status === 404) {
          setStatusError("The assistant endpoint is not deployed yet. Push the backend and let Render redeploy.");
        } else {
          setStatusError("Could not reach the assistant. Check the API URL on the dashboard.");
        }
      }
    })();
    return () => {
      active = false;
    };
  }, [open]);

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.altKey && event.key.toLowerCase() === "k") {
        event.preventDefault();
        setOpen((value) => !value);
      }
      if (event.key === "Escape") setOpen(false);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const timer = window.setTimeout(() => inputRef.current?.focus(), 50);
    return () => {
      document.body.style.overflow = previous;
      window.clearTimeout(timer);
    };
  }, [open]);

  useEffect(() => {
    if (open) endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, open, busy]);

  // Closing the drawer or unmounting must release the microphone. `onstop` /
  // `onend` clear the busy flags, so these effects never call setState directly.
  function releaseRecorder(cancel: boolean) {
    if (recordTimerRef.current !== null) {
      window.clearTimeout(recordTimerRef.current);
      recordTimerRef.current = null;
    }
    if (cancel) cancelledRef.current = true;
    const recorder = recorderRef.current;
    recorderRef.current = null;
    try {
      if (recorder && recorder.state !== "inactive") recorder.stop();
      else streamRef.current?.getTracks().forEach((track) => track.stop());
    } catch {
      /* already stopped */
    }
    if (!recorder) streamRef.current = null;
  }

  useEffect(() => {
    if (open) return;
    releaseRecorder(true);
    const recognition = recognitionRef.current;
    recognitionRef.current = null;
    try {
      recognition?.abort();
    } catch {
      /* already stopped */
    }
  }, [open]);

  useEffect(() => {
    return () => {
      releaseRecorder(true);
      const recognition = recognitionRef.current;
      recognitionRef.current = null;
      try {
        recognition?.abort();
      } catch {
        /* already stopped */
      }
    };
  }, []);

  const stopBrowserDictation = (abort = false) => {
    const recognition = recognitionRef.current;
    recognitionRef.current = null;
    setListening(false);
    try {
      if (abort) recognition?.abort();
      else recognition?.stop();
    } catch {
      /* already stopped */
    }
  };

  const startBrowserDictation = () => {
    const Recognition = getSpeechRecognition();
    if (!Recognition) {
      setMicError("Voice input needs Chrome, Edge or Safari.");
      return;
    }
    if (!window.isSecureContext) {
      setMicError("Microphone needs HTTPS — open the deployed site or localhost.");
      return;
    }
    setMicError(null);
    dictationBaseRef.current = input;
    const recognition = new Recognition();
    recognition.lang = navigator.language || "en-GB";
    // Desktop Chrome handles long dictation; iOS reliably captures one phrase.
    recognition.continuous = !isAppleMobile();
    recognition.interimResults = true;
    recognition.onresult = (event) => {
      let interim = "";
      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index];
        const transcript = result[0]?.transcript ?? "";
        if (result.isFinal) {
          dictationBaseRef.current = joinTranscript(dictationBaseRef.current, transcript);
        } else {
          interim += transcript;
        }
      }
      setInput(joinTranscript(dictationBaseRef.current, interim).slice(0, 1000));
    };
    recognition.onerror = (event) => {
      const code = event.error ?? "unknown";
      // Deliberate stops (drawer closed, question sent) are not failures.
      if (code === "aborted") return;
      if (recognitionRef.current === recognition) recognitionRef.current = null;
      setListening(false);
      if (code === "not-allowed" || code === "service-not-allowed") {
        setMicError(
          "Microphone blocked. Allow mic access for this site in your browser settings.",
        );
      } else if (code === "no-speech") {
        setMicError("Didn't catch that — tap the mic and try again.");
      } else if (code === "audio-capture") {
        setMicError("No microphone found. Check your system input device and try again.");
      } else if (code === "network") {
        // Chrome/Edge send audio to a cloud speech service. VPNs, firewalls,
        // corporate proxies and some ad-blockers make this fail even when the
        // rest of the site works.
        setMicError(
          "Browser dictation is blocked here. Type the question, or switch to recording mode by reloading once the server route is deployed.",
        );
      } else if (code === "language-not-supported") {
        setMicError("This browser can't dictate in your language. Type the question instead.");
      } else {
        setMicError(`Voice input stopped (${code}). Tap the mic to try again.`);
      }
    };
    recognition.onend = () => {
      if (recognitionRef.current === recognition) recognitionRef.current = null;
      setListening(false);
    };
    try {
      recognition.start();
      recognitionRef.current = recognition;
      setListening(true);
    } catch {
      setMicError("Could not start the microphone. Close other dictation apps and try again.");
      setListening(false);
    }
  };

  const transcribeClip = async (clip: Blob) => {
    setTranscribing(true);
    const extension = clip.type.includes("mp4")
      ? "m4a"
      : clip.type.includes("ogg")
        ? "ogg"
        : "webm";
    const form = new FormData();
    form.append("file", clip, `dictation.${extension}`);
    try {
      const body = await api.postForm<{ text: string }>("/api/assistant/transcribe", form);
      const text = body.text.trim();
      if (text) {
        setInput((prev) => joinTranscript(prev, text).slice(0, 1000));
      } else {
        setMicError("No speech detected — tap the mic and speak again.");
      }
    } catch (err) {
      if (err instanceof ApiError && (err.status === 404 || err.status === 503)) {
        // Older backend or no Groq key: fall back to the browser's engine.
        startBrowserDictation();
        setMicError(
          "Server transcription is unavailable — using the browser's dictation instead.",
        );
      } else {
        setMicError(
          err instanceof ApiError
            ? err.message
            : "Could not transcribe that clip. Tap the mic and try again.",
        );
      }
    } finally {
      setTranscribing(false);
    }
  };

  const startRecording = async () => {
    setMicError(null);
    if (
      typeof MediaRecorder === "undefined" ||
      !navigator.mediaDevices?.getUserMedia
    ) {
      startBrowserDictation();
      return;
    }
    if (!window.isSecureContext) {
      setMicError("Microphone needs HTTPS — open the deployed site or localhost.");
      return;
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const candidates = [
        "audio/webm;codecs=opus",
        "audio/webm",
        "audio/mp4",
        "audio/ogg",
      ];
      const mimeType =
        candidates.find((type) => MediaRecorder.isTypeSupported?.(type)) ?? "";
      const recorder = mimeType
        ? new MediaRecorder(stream, { mimeType })
        : new MediaRecorder(stream);
      chunksRef.current = [];
      cancelledRef.current = false;
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data);
      };
      recorder.onstop = () => {
        stream.getTracks().forEach((track) => track.stop());
        if (streamRef.current === stream) streamRef.current = null;
        setRecording(false);
        if (cancelledRef.current) {
          cancelledRef.current = false;
          chunksRef.current = [];
          return;
        }
        const clip = new Blob(chunksRef.current, {
          type: recorder.mimeType || "audio/webm",
        });
        chunksRef.current = [];
        if (clip.size === 0) {
          setMicError("No audio was captured. Check your microphone and try again.");
          return;
        }
        void transcribeClip(clip);
      };
      recorder.start();
      recorderRef.current = recorder;
      streamRef.current = stream;
      setRecording(true);
      // Hard stop so a forgotten recording never uploads a huge clip.
      recordTimerRef.current = window.setTimeout(() => stopRecording(), 90_000);
    } catch (err) {
      if (err instanceof DOMException && err.name === "NotFoundError") {
        setMicError("No microphone found. Check your system input device.");
      } else if (
        err instanceof DOMException &&
        (err.name === "NotAllowedError" || err.name === "SecurityError")
      ) {
        setMicError(
          "Microphone blocked. Allow mic access for this site in your browser settings.",
        );
      } else {
        setMicError("Could not start the microphone. Close other recording apps and try again.");
      }
    }
  };

  const stopRecording = () => {
    if (recordTimerRef.current !== null) {
      window.clearTimeout(recordTimerRef.current);
      recordTimerRef.current = null;
    }
    const recorder = recorderRef.current;
    recorderRef.current = null;
    setRecording(false);
    try {
      if (recorder && recorder.state !== "inactive") recorder.stop();
      else streamRef.current?.getTracks().forEach((track) => track.stop());
    } catch {
      /* already stopped */
    }
  };

  const toggleDictation = () => {
    if (recording) {
      stopRecording();
    } else if (listening) {
      stopBrowserDictation();
    } else {
      void startRecording();
    }
  };

  const send = async (raw: string) => {
    const question = raw.trim();
    if (!question || busy) return;
    if (status && !status.enabled) return;
    if (recognitionRef.current) stopBrowserDictation(true);
    if (recorderRef.current || streamRef.current) {
      cancelledRef.current = true;
      releaseRecorder(true);
      setRecording(false);
    }

    const history = messages.slice(-8).map((message) => ({
      role: message.role,
      // Answers regularly exceed the history cap; keep the request small and
      // let the backend do the final trimming.
      content: message.content.slice(0, MAX_HISTORY_CHARS),
    }));
    setInput("");
    setBusy(true);
    setMessages((prev) => [...prev, { role: "user", content: question }]);

    try {
      const body = await api.post<Answer>("/api/assistant/ask", {
        question,
        page: pathname,
        history,
      });
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: body.answer,
          sources: body.sources,
          degraded: body.degraded,
        },
      ]);
    } catch (err) {
      let message =
        err instanceof ApiError ? err.message : "Could not reach the assistant.";
      if (err instanceof ApiError && err.status === 404) {
        message =
          "The assistant endpoint is not deployed yet. Push the backend and let Render redeploy.";
      }
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: message, failed: true },
      ]);
    } finally {
      setBusy(false);
    }
  };

  const suggestions = SUGGESTIONS[pathname] ?? DEFAULT_SUGGESTIONS;
  const disabled = status ? !status.enabled : false;

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className={cn(
          "fixed bottom-[calc(1.25rem+env(safe-area-inset-bottom))] right-5 z-40 flex items-center gap-2 rounded-full bg-gradient-to-br from-indigo-500 to-violet-600 px-4 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/30 transition hover:-translate-y-0.5 hover:shadow-xl focus:outline-none focus-visible:ring-2 focus-visible:ring-indigo-400",
          open && "hidden",
        )}
        aria-label="Open interview assistant (Alt+K)"
        title="Ask the interview assistant (Alt+K)"
      >
        <Sparkles className="h-4 w-4" />
        Ask
      </button>

      {open ? (
        <div className="fixed inset-0 z-50 flex justify-end">
          <button
            type="button"
            aria-label="Close assistant"
            className="absolute inset-0 bg-slate-950/40 backdrop-blur-[1px]"
            onClick={() => setOpen(false)}
          />

          <section
            role="dialog"
            aria-modal="true"
            aria-label="Interview assistant"
            className="relative flex h-dvh w-full max-w-md flex-col border-l border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900"
          >
            <header className="flex items-start gap-3 border-b border-slate-200 px-4 py-3 dark:border-slate-700">
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 text-white">
                <Sparkles className="h-4 w-4" />
              </span>
              <div className="min-w-0 flex-1">
                <h2 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                  Interview assistant
                </h2>
                <p className="text-[11px] leading-snug text-slate-500 dark:text-slate-400">
                  Answers come only from your repo. Groq key stays server-side.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setOpen(false)}
                className="rounded-lg p-1.5 text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100"
                aria-label="Close assistant"
              >
                <X className="h-4 w-4" />
              </button>
            </header>

            <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
              {statusError ? (
                <div className="flex items-start gap-2 rounded-xl border border-amber-300 bg-amber-50 px-3 py-2.5 text-[12px] leading-snug text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200">
                  <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                  <span>{statusError}</span>
                </div>
              ) : null}

              {status && !status.enabled ? (
                <div className="flex items-start gap-2 rounded-xl border border-amber-300 bg-amber-50 px-3 py-2.5 text-[12px] leading-snug text-amber-900 dark:border-amber-700 dark:bg-amber-950/40 dark:text-amber-200">
                  <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
                  <span>
                    {status.note} Add <code className="font-mono">GROQ_API_KEY</code> to
                    the backend environment (Render dashboard for the hosted API),
                    then restart it.
                  </span>
                </div>
              ) : null}

              {messages.length === 0 ? (
                <div className="space-y-4">
                  <div className="rounded-xl border border-slate-200 bg-slate-50 px-3.5 py-3 dark:border-slate-700 dark:bg-slate-800/60">
                    <p className="text-[13px] leading-relaxed text-slate-700 dark:text-slate-200">
                      Ask anything about the playbooks, your Admiral evidence, resume
                      answers, IAM, SQL, Java or the study plan. If the repo does not
                      cover it, the assistant says so instead of guessing.
                    </p>
                    <p className="mt-2 flex items-center gap-1.5 text-[11px] text-slate-500 dark:text-slate-400">
                      <BookOpen className="h-3 w-3" />
                      Grounded in {status ? `${status.excerpt_count} excerpts` : "your repo content"}
                      {status?.model ? ` · ${status.model}` : ""}
                    </p>
                  </div>
                  <div>
                    <p className="mb-2 text-[11px] font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                      Try one of these
                    </p>
                    <div className="flex flex-col gap-2">
                      {suggestions.map((suggestion) => (
                        <button
                          key={suggestion}
                          type="button"
                          onClick={() => void send(suggestion)}
                          disabled={disabled}
                          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-[12px] leading-snug text-slate-700 transition hover:border-indigo-300 hover:bg-indigo-50 disabled:cursor-not-allowed disabled:opacity-50 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:border-indigo-500 dark:hover:bg-indigo-950/40"
                        >
                          {suggestion}
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ) : null}

              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={cn(
                    "flex",
                    message.role === "user" ? "justify-end" : "justify-start",
                  )}
                >
                  <div
                    className={cn(
                      "max-w-[92%] rounded-xl px-3 py-2.5",
                      message.role === "user"
                        ? "bg-indigo-600 text-white"
                        : message.failed
                          ? "border border-rose-300 bg-rose-50 text-rose-900 dark:border-rose-800 dark:bg-rose-950/40 dark:text-rose-200"
                          : "border border-slate-200 bg-white text-slate-800 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100",
                    )}
                  >
                    {message.role === "user" ? (
                      <p className="whitespace-pre-wrap text-[13px] leading-relaxed">
                        {message.content}
                      </p>
                    ) : (
                      <>
                        {message.degraded ? (
                          <p className="mb-1.5 flex items-center gap-1 text-[10px] font-semibold uppercase tracking-wide text-amber-700 dark:text-amber-300">
                            <AlertTriangle className="h-3 w-3" />
                            Excerpts only — model unavailable
                          </p>
                        ) : null}
                        <RichText text={message.content} />
                        {message.sources && message.sources.length > 0 ? (
                          <div className="mt-2 flex flex-wrap gap-1.5 border-t border-slate-200 pt-2 dark:border-slate-700">
                            {message.sources.map((source) => (
                              <Link
                                key={`${source.id}-${source.index}`}
                                href={source.route}
                                title={source.title}
                                className="rounded-full bg-slate-100 px-2 py-0.5 text-[10px] font-medium text-slate-600 transition hover:bg-indigo-100 hover:text-indigo-800 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-indigo-950 dark:hover:text-indigo-200"
                              >
                                [{source.index}] {source.page}
                              </Link>
                            ))}
                          </div>
                        ) : null}
                      </>
                    )}
                  </div>
                </div>
              ))}

              {busy ? (
                <div className="flex items-center gap-2 text-[12px] text-slate-500 dark:text-slate-400">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Searching your playbook…
                </div>
              ) : null}
              <div ref={endRef} />
            </div>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                void send(input);
              }}
              className="border-t border-slate-200 px-3 py-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] dark:border-slate-700"
            >
              <div className="flex items-end gap-2">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      void send(input);
                    }
                  }}
                  rows={1}
                  maxLength={1000}
                  enterKeyHint="send"
                  placeholder={
                    transcribing
                      ? "Transcribing your question…"
                      : recording
                        ? "Recording — tap the mic to stop…"
                        : listening
                          ? "Listening — speak now…"
                          : disabled
                            ? "Assistant disabled — set GROQ_API_KEY"
                            : "Ask about any page, answer or IAM concept…"
                  }
                  disabled={disabled}
                  className="max-h-32 min-h-[38px] flex-1 resize-none rounded-lg border border-slate-300 bg-white px-2.5 py-2 text-base leading-snug text-slate-800 outline-none transition focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-100 sm:text-[13px] dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100 dark:disabled:bg-slate-800/60"
                />
                <button
                  type="button"
                  onClick={toggleDictation}
                  disabled={disabled || busy || transcribing || !micAvailable}
                  aria-pressed={recording || listening}
                  aria-label={
                    transcribing
                      ? "Transcribing question"
                      : recording
                        ? "Stop recording"
                        : listening
                          ? "Stop dictation"
                          : "Dictate question"
                  }
                  title={
                    micAvailable
                      ? transcribing
                        ? "Transcribing…"
                        : recording
                          ? "Stop recording and transcribe"
                          : "Record a question and transcribe it"
                      : "Voice input needs a microphone and a modern browser"
                  }
                  className={cn(
                    "flex h-11 w-11 shrink-0 items-center justify-center rounded-lg border transition disabled:cursor-not-allowed disabled:opacity-40 sm:h-[38px] sm:w-[38px]",
                    recording || listening
                      ? "animate-pulse border-rose-500 bg-rose-500 text-white"
                      : "border-slate-300 bg-white text-slate-600 hover:border-indigo-400 hover:text-indigo-600 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-indigo-500 dark:hover:text-indigo-300",
                  )}
                >
                  {transcribing ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Mic className="h-4 w-4" />
                  )}
                </button>
                <button
                  type="submit"
                  disabled={busy || disabled || !input.trim()}
                  className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-indigo-600 text-white transition hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50 sm:h-[38px] sm:w-[38px]"
                  aria-label="Send question"
                >
                  {busy ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="h-4 w-4" />
                  )}
                </button>
              </div>
              {micError ? (
                <p role="alert" className="mt-1.5 text-[10px] leading-snug text-rose-600 dark:text-rose-400">
                  {micError}
                </p>
              ) : null}
              <p className="mt-1.5 text-[10px] text-slate-400 dark:text-slate-500">
                Enter to send · Shift+Enter for a new line · Mic records and transcribes · Alt+K toggles this panel
              </p>
            </form>
          </section>
        </div>
      ) : null}
    </>
  );
}
