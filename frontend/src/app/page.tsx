"use client";

import {
  ArrowRight,
  BrainCircuit,
  CheckCircle2,
  ChevronRight,
  Droplets,
  Fish,
  Gauge,
  LayoutDashboard,
  Leaf,
  LogIn,
  LogOut,
  MessageCircle,
  CircleDot,
  X,
  Mic,
  Send,
  Settings2,
  ShieldCheck,
  Square,
  Sparkles,
  Waves,
} from "lucide-react";
import {
  useEffect,
  useRef,
  useState,
} from "react";

import OceanBackground from "../components/OceanBackground";
import { AquaAIDrawer, AquaAIButton } from "@/components/ai/aqua-ai-drawer";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

type User = {
  id: string;
  email: string;
  full_name: string | null;
  onboarding_status: string;
  farm_count: number;
};

type ChatSource = {
  source_file: string;
  page: number;
  chunk_index: number;
  similarity: number;
};

type ChatPrediction = {
  status: string;
  current_biomass_kg: number | null;
  missing_for_forecast: string[];
  message: string | null;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  intent?: string | null;
  extraction?: Record<string, unknown> | null;
  prediction?: ChatPrediction | null;
  sources?: ChatSource[];
};

type ChatResponse = {
  answer: string;
  model: string;
  mode: string;
  conversation_id: string;
};


function intentLabel(
  intent: string | null | undefined,
): string {

  const labels: Record<string, string> = {
    farm_data: "Farm data",
    parameter_update: "Parameter update",
    knowledge: "Knowledge",
    farm_advice: "Farm advice",
    prediction: "Prediction",
    general_chat: "General chat",
    context_lookup: "Farm memory",
  };

  return (
    labels[intent ?? ""] ??
    (intent
      ? intent.replaceAll("_", " ")
      : "Assistant")
  );
}


function fieldLabel(
  field: string,
): string {

  const labels: Record<string, string> = {
    species: "Species",
    pond_area: "Pond area",
    pond_area_unit: "Area unit",
    pond_volume_m3: "Pond volume",
    stocking_count: "Stocking count",
    average_weight_g: "Average weight",
    survival_rate_percent: "Survival rate",
    temperature_c: "Temperature",
    ph: "pH",
    dissolved_oxygen_mg_l:
      "Dissolved oxygen",
    salinity_ppt: "Salinity",
    feed_kg_per_day:
      "Feed / day",
  };

  return (
    labels[field] ??
    field.replaceAll("_", " ")
  );
}


function fieldValue(
  field: string,
  value: unknown,
  extraction:
    Record<string, unknown>,
): string {

  if (
    field === "stocking_count" &&
    typeof value === "number"
  ) {
    return value.toLocaleString();
  }

  if (
    field === "pond_area" &&
    extraction.pond_area_unit
  ) {
    return `${value} ${extraction.pond_area_unit}`;
  }

  if (
    field ===
      "survival_rate_percent"
  ) {
    return `${value}%`;
  }

  if (
    field === "temperature_c"
  ) {
    return `${value} °C`;
  }

  if (
    field === "average_weight_g"
  ) {
    return `${value} g`;
  }

  if (
    field ===
      "dissolved_oxygen_mg_l"
  ) {
    return `${value} mg/L`;
  }

  if (field === "salinity_ppt") {
    return `${value} ppt`;
  }

  if (
    field ===
      "feed_kg_per_day"
  ) {
    return `${value} kg/day`;
  }

  return String(value);
}


function StructuredAssistant({
  message,
}: {
  message: ChatMessage;
}) {

  const extraction =
    message.extraction ?? {};

  const fields =
    Object.entries(
      extraction,
    ).filter(
      ([field, value]) =>
        field !== "pond_area_unit" &&
        value !== null &&
        value !== undefined &&
        value !== "",
    );

  return (
    <div className="space-y-3">

      {message.intent && (
        <div className="flex items-center gap-2">

          <span className="rounded-full border border-border px-2.5 py-1 text-[9px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Intent
          </span>

          <span className="rounded-full bg-background px-2.5 py-1 text-[10px] font-semibold capitalize">
            {intentLabel(
              message.intent,
            )}
          </span>

        </div>
      )}

      {fields.length > 0 && (
        <div className="rounded-xl border border-border bg-background/60 p-3">

          <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Farm data detected
          </p>

          <div className="mt-2 grid gap-2 sm:grid-cols-2">

            {fields.map(
              ([field, value]) => (
                <div
                  key={field}
                  className="rounded-lg bg-muted/40 px-3 py-2"
                >

                  <p className="text-[9px] text-muted-foreground">
                    {fieldLabel(field)}
                  </p>

                  <p className="mt-0.5 text-[11px] font-semibold">
                    {fieldValue(
                      field,
                      value,
                      extraction,
                    )}
                  </p>

                </div>
              ),
            )}

          </div>
        </div>
      )}

      {message.content && (
        <div>

          <p className="mb-2 text-[9px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            AI explanation
          </p>

          <div className="whitespace-pre-wrap">
            {message.content}
          </div>

        </div>
      )}

      {message.prediction && (
        <div className="rounded-xl border border-border bg-background/60 p-3">

          <p className="text-[9px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
            Prediction
          </p>

          {message.prediction
            .current_biomass_kg !==
            null && (
            <div className="mt-2 rounded-lg bg-muted/40 px-3 py-3">

              <p className="text-[9px] text-muted-foreground">
                Current standing biomass
              </p>

              <p className="mt-1 text-xl font-bold">
                {
                  message.prediction
                    .current_biomass_kg
                }{" "}
                kg
              </p>

            </div>
          )}

          <div className="mt-3">

            <p className="text-[9px] text-muted-foreground">
              Future production
            </p>

            <p className="mt-1 text-[11px] font-semibold">
              Forecast model not connected yet
            </p>

            <p className="mt-1 text-[10px] leading-5 text-muted-foreground">
              {message.prediction.message}
            </p>

          </div>

          {message.prediction
            .missing_for_forecast
            .length > 0 && (
            <div className="mt-3">

              <p className="text-[9px] text-muted-foreground">
                Needed for forecast
              </p>

              <div className="mt-2 flex flex-wrap gap-1.5">

                {message.prediction
                  .missing_for_forecast
                  .map(
                    (field) => (
                      <span
                        key={field}
                        className="rounded-full border border-border px-2 py-1 text-[9px]"
                      >
                        {field.replaceAll(
                          "_",
                          " ",
                        )}
                      </span>
                    ),
                  )}

              </div>

            </div>
          )}

        </div>
      )}

      {message.sources &&
        message.sources.length > 0 && (
          <details className="rounded-xl border border-border bg-background/50">

            <summary className="cursor-pointer px-3 py-2 text-[9px] font-semibold uppercase tracking-[0.14em] text-muted-foreground">
              Sources ({message.sources.length})
            </summary>

            <div className="space-y-2 border-t border-border p-3">

              {message.sources.map(
                (
                  source,
                  index,
                ) => (
                  <div
                    key={`${source.source_file}-${source.page}-${index}`}
                    className="rounded-lg bg-muted/40 px-3 py-2"
                  >

                    <p className="text-[10px] font-semibold">
                      {source.source_file}
                    </p>

                    <p className="mt-1 text-[9px] text-muted-foreground">
                      Page {source.page}
                      {" · "}
                      Chunk{" "}
                      {source.chunk_index}
                      {" · "}
                      similarity{" "}
                      {source.similarity.toFixed(
                        3,
                      )}
                    </p>

                  </div>
                ),
              )}

            </div>
          </details>
        )}

    </div>
  );
}


export default function HomePage() {
  const [user, setUser] = useState<User | null>(null);
  const [checkingAuth, setCheckingAuth] = useState(true);

  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState<
    string | null
  >(null);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi, I'm Aqua AI. You can ask me anything about aquaculture. You do not need to create a farm or provide farm details to start.",
    },
  ]);

  const [chatLoading, setChatLoading] = useState(false);
  const [aquaAIOpen, setAquaAIOpen] = useState(false);

  const [recording, setRecording] = useState(false);
  const [voiceLoading, setVoiceLoading] = useState(false);
  const [recordingSeconds, setRecordingSeconds] = useState(0);

  const mediaRecorderRef =
    useRef<MediaRecorder | null>(null);

  const audioChunksRef =
    useRef<Blob[]>([]);

  const discardRecordingRef =
    useRef(false);

  const recordingTimerRef =
    useRef<ReturnType<typeof setInterval> | null>(
      null,
    );

  const chatAbortControllerRef =
    useRef<AbortController | null>(null);

  useEffect(() => {
    let active = true;

    async function loadSession() {
      try {
        const response = await fetch(
          `${API_URL}/api/v1/me`,
          {
            credentials: "include",
            cache: "no-store",
          },
        );

        if (!active) {
          return;
        }

        if (response.ok) {
          const data = (await response.json()) as User;
          setUser(data);
        }
      } catch {
      } finally {
        if (active) {
          setCheckingAuth(false);
        }
      }
    }

    loadSession();

    return () => {
      active = false;
    };
  }, []);

  async function transcribeVoice(
    audioBlob: Blob,
  ) {
    setVoiceLoading(true);

    try {
      const file = new File(
        [audioBlob],
        "aqualife-voice.webm",
        {
          type:
            audioBlob.type ||
            "audio/webm",
        },
      );

      const formData = new FormData();

      formData.append(
        "file",
        file,
      );

      // Always let Whisper automatically detect
      // English, Telugu, or mixed speech.
      formData.append(
        "language",
        "auto",
      );

      const response = await fetch(
        `${API_URL}/api/v1/voice/transcribe`,
        {
          method: "POST",
          body: formData,
        },
      );

      const data =
        await response.json();

      if (!response.ok) {
        throw new Error(
          data?.detail ??
            "Voice transcription failed.",
        );
      }

      const transcript =
        String(data.text ?? "").trim();

      if (!transcript) {
        throw new Error(
          "No speech was detected.",
        );
      }

      await sendMessage(
        transcript,
      );

    } catch (error) {

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "Voice transcription failed.",
        },
      ]);

    } finally {
      setVoiceLoading(false);
    }
  }


  function clearRecordingTimer() {
    if (recordingTimerRef.current) {
      clearInterval(
        recordingTimerRef.current,
      );

      recordingTimerRef.current =
        null;
    }
  }

  async function startRecording() {

    if (
      chatLoading ||
      recording ||
      voiceLoading
    ) {
      return;
    }

    if (
      !navigator.mediaDevices?.getUserMedia
    ) {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "Your browser does not support microphone recording.",
        },
      ]);

      return;
    }

    try {

      const stream =
        await navigator.mediaDevices.getUserMedia(
          {
            audio: {
              echoCancellation: true,
              noiseSuppression: true,
              autoGainControl: true,
            },
          },
        );

      let mimeType = "";

      if (
        MediaRecorder.isTypeSupported(
          "audio/webm;codecs=opus",
        )
      ) {
        mimeType =
          "audio/webm;codecs=opus";
      } else if (
        MediaRecorder.isTypeSupported(
          "audio/webm",
        )
      ) {
        mimeType = "audio/webm";
      }

      const recorder =
        mimeType
          ? new MediaRecorder(
              stream,
              { mimeType },
            )
          : new MediaRecorder(
              stream,
            );

      audioChunksRef.current = [];
      discardRecordingRef.current =
        false;

      recorder.ondataavailable = (
        event,
      ) => {
        if (
          event.data.size > 0
        ) {
          audioChunksRef.current.push(
            event.data,
          );
        }
      };

      recorder.onerror = () => {
        clearRecordingTimer();

        stream
          .getTracks()
          .forEach((track) =>
            track.stop(),
          );

        mediaRecorderRef.current =
          null;

        setRecording(false);
        setRecordingSeconds(0);

        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content:
              "An error occurred while recording your voice.",
          },
        ]);
      };

      recorder.onstop = async () => {

        clearRecordingTimer();

        stream
          .getTracks()
          .forEach((track) =>
            track.stop(),
          );

        mediaRecorderRef.current =
          null;

        setRecording(false);

        const cancelled =
          discardRecordingRef.current;

        if (cancelled) {
          audioChunksRef.current = [];
          setRecordingSeconds(0);
          return;
        }

        const audioBlob =
          new Blob(
            audioChunksRef.current,
            {
              type:
                recorder.mimeType ||
                "audio/webm",
            },
          );

        audioChunksRef.current =
          [];

        setRecordingSeconds(0);

        if (audioBlob.size > 0) {
          await transcribeVoice(
            audioBlob,
          );
        }
      };

      mediaRecorderRef.current =
        recorder;

      recorder.start(250);

      setRecordingSeconds(0);
      setRecording(true);

      recordingTimerRef.current =
        setInterval(() => {

          setRecordingSeconds(
            (current) => {

              const next =
                current + 1;

              if (next >= 60) {

                setTimeout(
                  () => {
                    stopRecording();
                  },
                  0,
                );

                return 60;
              }

              return next;
            },
          );

        }, 1000);

    } catch (error) {

      clearRecordingTimer();

      setRecording(false);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? `Microphone error: ${error.message}`
              : "Could not access your microphone.",
        },
      ]);
    }
  }

  function stopRecording() {

    const recorder =
      mediaRecorderRef.current;

    if (
      recorder &&
      recorder.state !== "inactive"
    ) {
      recorder.stop();
    }
  }

  function cancelRecording() {

    discardRecordingRef.current =
      true;

    clearRecordingTimer();

    const recorder =
      mediaRecorderRef.current;

    if (
      recorder &&
      recorder.state !== "inactive"
    ) {
      recorder.stop();
      return;
    }

    setRecording(false);
    setRecordingSeconds(0);
    audioChunksRef.current = [];
  }


  async function sendMessage(
    textOverride?: string,
  ) {
    const text =
      (textOverride ?? input).trim();

    if (
      !text ||
      chatLoading
    ) {
      return;
    }

    setInput("");

    // Add the user message immediately.
    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: text,
      },
    ]);

    // Create the assistant message BEFORE the request.
    // This guarantees there is always a visible response
    // container while streaming.
    let assistantIndex = -1;

    setMessages((current) => {
      const next = [
        ...current,
        {
          role: "assistant" as const,
          content: "",
        },
      ];

      assistantIndex = next.length - 1;

      return next;
    });

    setChatLoading(true);

    const controller =
      new AbortController();

    chatAbortControllerRef.current =
      controller;

    let streamedAnswer = "";

    const updateAssistant =
      (content: string) => {

        setMessages((current) => {

          const next = [
            ...current,
          ];

          if (
            assistantIndex < 0 ||
            !next[assistantIndex]
          ) {
            return next;
          }

          next[assistantIndex] = {
            ...next[assistantIndex],
            content,
          };

          return next;
        });
      };

    try {

      const response =
        await fetch(
          `${API_URL}/api/v1/public/ai/chat/stream`,
          {
            method: "POST",
            headers: {
              "Content-Type":
                "application/json",
              Accept:
                "text/event-stream",
              "Cache-Control":
                "no-cache",
            },
            credentials: "include",
            signal: controller.signal,
            body: JSON.stringify({
              message: text,
              conversation_id:
                conversationId,
            }),
          },
        );

      if (
        !response.ok
      ) {
        let detail =
          `Aqua AI request failed (${response.status}).`;

        try {
          const data =
            await response.json();

          if (data?.detail) {
            detail =
              String(data.detail);
          }
        } catch {
        }

        throw new Error(detail);
      }

      if (!response.body) {
        throw new Error(
          "Aqua AI returned an empty response stream.",
        );
      }

      const reader =
        response.body.getReader();

      const decoder =
        new TextDecoder("utf-8");

      let buffer = "";
      let finished = false;

      while (!finished) {

        const {
          value,
          done,
        } = await reader.read();

        if (done) {
          break;
        }

        buffer +=
          decoder.decode(
            value,
            {
              stream: true,
            },
          );

        const events =
          buffer.split(/\r?\n\r?\n/);

        buffer =
          events.pop() ?? "";

        for (
          const event of events
        ) {

          const dataLine =
            event
              .split(/\r?\n/)
              .find(
                (line) =>
                  line.trim().startsWith(
                    "data:",
                  ),
              );

          if (!dataLine) {
            continue;
          }

          const raw =
            dataLine
              .trim()
              .slice(5)
              .trim();

          if (!raw) {
            continue;
          }

          let payload: {
            type?: string;
            content?: string;
            conversation_id?: string;
            detail?: string;
            intent?: string | null;
            extraction?:
              Record<string, unknown> | null;
            prediction?:
              ChatPrediction | null;
            sources?: ChatSource[];
          };

          try {
            payload =
              JSON.parse(raw);
          } catch {
            continue;
          }

          if (
            payload.type ===
            "meta"
          ) {

            if (
              payload.conversation_id
            ) {
              setConversationId(
                payload.conversation_id,
              );
            }

            setMessages((current) => {

              const next = [
                ...current,
              ];

              if (
                assistantIndex >= 0 &&
                next[assistantIndex]
              ) {
                next[assistantIndex] = {
                  ...next[assistantIndex],

                  intent:
                    payload.intent ??
                    null,

                  extraction:
                    payload.extraction ??
                    null,

                  prediction:
                    payload.prediction ??
                    null,
                };
              }

              return next;
            });

            continue;
          }


          if (
            payload.type ===
            "token"
          ) {

            const token =
              payload.content ?? "";

            if (!token) {
              continue;
            }

            streamedAnswer +=
              token;

            updateAssistant(
              streamedAnswer,
            );

            continue;
          }

          if (
            payload.type ===
            "sources"
          ) {

            setMessages((current) => {

              const next = [
                ...current,
              ];

              if (
                assistantIndex >= 0 &&
                next[assistantIndex]
              ) {
                next[assistantIndex] = {
                  ...next[assistantIndex],
                  sources:
                    payload.sources ??
                    [],
                };
              }

              return next;
            });

            continue;
          }

          if (
            payload.type ===
            "error"
          ) {

            throw new Error(
              payload.detail ??
                "Aqua AI stream failed.",
            );
          }

          if (
            payload.type ===
            "done"
          ) {

            finished = true;
            break;
          }
        }
      }

      // Flush any remaining decoder content.
      buffer +=
        decoder.decode();

      if (
        streamedAnswer.length === 0
      ) {

        updateAssistant(
          "Aqua AI returned no answer.",
        );
      }

      try {
        await reader.cancel();
      } catch {
      }

    } catch (error) {

      if (
        error instanceof DOMException &&
        error.name ===
          "AbortError"
      ) {

        updateAssistant(
          streamedAnswer ||
            "Generation stopped.",
        );

      } else {

        updateAssistant(
          streamedAnswer ||
            (
              error instanceof Error
                ? error.message
                : "Aqua AI is temporarily unavailable. Please try again."
            ),
        );
      }

    } finally {

      chatAbortControllerRef.current =
        null;

      setChatLoading(false);
    }
  }


  function stopGeneration() {

    const controller =
      chatAbortControllerRef.current;

    if (!controller) {
      return;
    }

    controller.abort();

    chatAbortControllerRef.current =
      null;

    setChatLoading(false);
  }


  function startNewConversation() {

    stopGeneration();

    if (mediaRecorderRef.current) {
      cancelRecording();
    }

    setConversationId(null);

    setMessages([
      {
        role: "assistant",
        content:
          "New Aqua AI conversation started. What would you like to know?",
      },
    ]);
  }

  function signIn() {
    window.location.href =
      `${API_URL}/api/v1/auth/google`;
  }

  async function logout() {
    try {
      await fetch(
        `${API_URL}/api/v1/auth/logout`,
        {
          method: "POST",
          credentials: "include",
          cache: "no-store",
        },
      );
    } finally {
      window.location.href = "/";
    }
  }

  function openFarmSetup() {
    const element =
      document.getElementById("farm-setup");

    element?.scrollIntoView({
      behavior: "smooth",
      block: "center",
    });
  }

  return (
    <main className="relative min-h-screen bg-transparent text-foreground isolation-isolate">
      <OceanBackground />


      <div className="relative z-10">
      <header className="sticky top-0 z-40 border-b border-border/70 bg-background/85 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <a
            href="#top"
            className="flex items-center gap-3"
          >
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-foreground text-background">
              <Waves className="h-5 w-5" />
            </div>

            <div>
              <p className="text-sm font-bold tracking-tight">
                AquaLife
              </p>

              <p className="text-[9px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
                Aquaculture intelligence
              </p>
            </div>
          </a>

          <nav className="hidden items-center gap-6 text-xs font-medium text-muted-foreground md:flex">
            <button
              type="button"
              onClick={() => setAquaAIOpen(true)}
              className="hover:text-foreground"
            >
              Aqua AI
            </button>

            <a href="#platform" className="hover:text-foreground">
              Platform
            </a>

            <a href="#farm-setup" className="hover:text-foreground">
              Farm setup
            </a>
          </nav>

          <div className="flex items-center gap-2">
            {checkingAuth ? (
              <div className="h-9 w-24 animate-pulse rounded-xl bg-muted" />
            ) : user ? (
              <div className="flex items-center gap-2">
                <span className="hidden text-xs font-semibold sm:inline">
                  {user.full_name ?? user.email}
                </span>

                <button
                  type="button"
                  onClick={openFarmSetup}
                  className="rounded-xl bg-foreground px-3.5 py-2 text-xs font-semibold text-background"
                >
                  {user.farm_count > 0
                    ? "Manage farms"
                    : "Set up a farm"}
                </button>
              </div>
            ) : (
              <button
                type="button"
                onClick={signIn}
                className="rounded-xl bg-foreground px-3.5 py-2 text-xs font-semibold text-background"
              >
                Sign in
              </button>
            )}
          </div>
        </div>
      </header>

      <section id="top" className="relative overflow-hidden">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-0 h-[520px] w-[760px] -translate-x-1/2 rounded-full bg-foreground/[0.035] blur-3xl" />
        </div>

        <div className="relative mx-auto flex min-h-[calc(100vh-4rem)] max-w-5xl items-center justify-center px-4 pb-16 pt-16 sm:px-6 lg:px-8 lg:pb-24 lg:pt-24">
          <div className="mx-auto max-w-3xl text-center">
            <div className="inline-flex items-center gap-2 rounded-full border border-border bg-muted/40 px-3 py-1.5 text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-foreground" />
              Built for modern aquaculture
            </div>

            <h1 className="mt-7 text-5xl font-bold tracking-[-0.05em] sm:text-6xl lg:text-7xl">
              Your aquaculture
              <span className="block text-muted-foreground">
                intelligence layer.
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-base leading-7 text-muted-foreground sm:text-lg">
              Explore AquaLife before setting anything up. Ask
              Aqua AI questions, learn about aquaculture, and only
              provide farm information when you actually need
              farm-specific intelligence.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <button
                type="button"
                onClick={() => setAquaAIOpen(true)}
                className="flex items-center gap-2 rounded-xl bg-foreground px-5 py-3 text-xs font-semibold text-background"
              >
                Ask Aqua AI
                <ArrowRight className="h-4 w-4" />
              </button>

              {!user && (
                <button
                  type="button"
                  onClick={signIn}
                  className="flex items-center gap-2 rounded-xl border border-border px-5 py-3 text-xs font-semibold"
                >
                  Continue with Google
                  <ShieldCheck className="h-4 w-4" />
                </button>
              )}
            </div>

            <div className="mt-9 flex flex-wrap gap-x-6 gap-y-3 text-[11px] text-muted-foreground">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Guest AI available
              </span>

              <span className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Farm setup optional
              </span>

              <span className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Conversation memory
              </span>
            </div>
          </div>

        </div>
      </section>

      <section
        id="platform"
        className="border-y border-border bg-muted/20"
      >
        <div className="mx-auto max-w-7xl px-4 py-14 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Platform
            </p>

            <h2 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">
              Start with knowledge. Add farm context when you need it.
            </h2>
          </div>

          <div className="mt-8 grid gap-4 md:grid-cols-3">
            <PlatformCard
              icon={BrainCircuit}
              title="Ask first"
              text="Use Aqua AI without creating a pond, farm or account."
            />

            <PlatformCard
              icon={Waves}
              title="Configure later"
              text="Add farm and pond information only when you want personalized intelligence."
            />

            <PlatformCard
              icon={Droplets}
              title="Remember conversations"
              text="Aqua AI can continue an existing conversation instead of forgetting previous messages."
            />
          </div>
        </div>
      </section>

      <section
        id="farm-setup"
        className="mx-auto max-w-7xl px-4 py-16 sm:px-6 lg:px-8 lg:py-24"
      >
        <div className="grid gap-10 lg:grid-cols-[0.8fr_1.2fr] lg:items-center">
          <div>
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-muted-foreground">
              Farm intelligence
            </p>

            <h2 className="mt-3 text-3xl font-bold tracking-tight">
              Your farm is optional.
              <span className="block text-muted-foreground">
                Your curiosity isn't.
              </span>
            </h2>

            <p className="mt-4 text-sm leading-6 text-muted-foreground">
              You can explore AquaLife as a visitor. When you want
              farm-specific recommendations, we'll collect only the
              information required for that task.
            </p>

            {!user && (
              <button
                type="button"
                onClick={signIn}
                className="mt-6 flex items-center gap-2 rounded-xl bg-foreground px-4 py-2.5 text-xs font-semibold text-background"
              >
                Sign in when you're ready
                <ArrowRight className="h-4 w-4" />
              </button>
            )}
          </div>

          <div className="rounded-3xl border border-border bg-card/65 p-5 backdrop-blur-xl shadow-sm sm:p-7">
            <div className="grid gap-3 sm:grid-cols-3">
              <SetupCard
                icon={Leaf}
                title="Farm"
                text="Name, location and production setup"
              />

              <SetupCard
                icon={Waves}
                title="Ponds"
                text="Area, depth, water source and species"
              />

              <SetupCard
                icon={Fish}
                title="Operations"
                text="Feeding, growth, health and harvest"
              />
            </div>

            <div className="mt-5 rounded-2xl border border-dashed border-border bg-muted/20 p-4">
              <div className="flex items-center gap-3">
                <MessageCircle className="h-4 w-4" />

                <div>
                  <p className="text-xs font-semibold">
                    Nothing to configure yet?
                  </p>

                  <p className="mt-1 text-[11px] leading-5 text-muted-foreground">
                    That's fine. Keep using Aqua AI and configure
                    your farm later.
                  </p>
                </div>
              </div>
            </div>

            {user && (
              <button
                type="button"
                onClick={() => {
                  window.location.href =
                    "/onboarding";
                }}
                className="mt-5 flex items-center gap-2 rounded-xl bg-foreground px-4 py-2.5 text-xs font-semibold text-background"
              >
                {user.farm_count > 0
                  ? "Open farm setup"
                  : "Set up my farm"}
                <ChevronRight className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </section>

      <AquaAIButton
        onClick={() => setAquaAIOpen(true)}
      />

      <AquaAIDrawer
        open={aquaAIOpen}
        onClose={() => setAquaAIOpen(false)}
      />

      <footer className="border-t border-border">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 px-4 py-6 text-[10px] text-muted-foreground sm:px-6 md:flex-row md:items-center md:justify-between lg:px-8">
          <span>
            AquaLife - Intelligent aquaculture platform
          </span>

          <span>
            Explore freely. Configure when needed. Predict when ready.
          </span>
        </div>
      </footer>
          </div>
</main>
  );
}

function PlatformCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Waves;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-border bg-card/65 p-5 backdrop-blur-xl">
      <Icon className="h-5 w-5" />

      <p className="mt-5 text-sm font-semibold">
        {title}
      </p>

      <p className="mt-2 text-xs leading-5 text-muted-foreground">
        {text}
      </p>
    </div>
  );
}

function SetupCard({
  icon: Icon,
  title,
  text,
}: {
  icon: typeof Waves;
  title: string;
  text: string;
}) {
  return (
    <div className="rounded-2xl border border-border p-4">
      <Icon className="h-4 w-4" />

      <p className="mt-4 text-xs font-semibold">
        {title}
      </p>

      <p className="mt-1 text-[10px] leading-5 text-muted-foreground">
        {text}
      </p>
    </div>
  );
}

