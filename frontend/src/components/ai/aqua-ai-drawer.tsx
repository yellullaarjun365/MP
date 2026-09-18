"use client";



/*
 * AquaLife browser voice recording helpers.
 *
 * The browser determines which MediaRecorder MIME type is supported.
 * We never blindly claim that arbitrary bytes are audio/webm.
 */
const getAquaLifeRecordingMimeType = (): string => {
  if (
    typeof MediaRecorder === "undefined" ||
    typeof MediaRecorder.isTypeSupported !== "function"
  ) {
    return "";
  }

  const candidates = [
    "audio/webm;codecs=opus",
    "audio/webm",
    "audio/ogg;codecs=opus",
    "audio/ogg",
  ];

  for (const type of candidates) {
    try {
      if (MediaRecorder.isTypeSupported(type)) {
        return type;
      }
    } catch {
      // Try the next format.
    }
  }

  return "";
};

const getAquaLifeAudioExtension = (mimeType: string): string => {
  const type = (mimeType || "").toLowerCase();

  if (type.includes("ogg")) {
    return "ogg";
  }

  return "webm";
};
import {
  BrainCircuit,
  Loader2,
  Mic,
  Send,
  Sparkles,
  Square,
  X,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL ??
  "http://127.0.0.1:8000";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

type AquaAIDrawerProps = {
  open: boolean;
  onClose: () => void;
};

export function AquaAIDrawer({
  open,
  onClose,
}: AquaAIDrawerProps) {
  const [input, setInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
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
    useRef<ReturnType<typeof setInterval> | null>(null);

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Hi, I'm Aqua AI. Ask me about aquaculture, water quality, production, feeding, ponds, or your farm.",
    },
  ]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages, chatLoading]);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();

      if (recordingTimerRef.current) {
        clearInterval(recordingTimerRef.current);
        recordingTimerRef.current = null;
      }

      const recorder = mediaRecorderRef.current;

      if (
        recorder &&
        recorder.state !== "inactive"
      ) {
        recorder.stop();
      }

      recorder?.stream
        .getTracks()
        .forEach((track) => track.stop());

      mediaRecorderRef.current = null;
    };
  }, []);

  async function transcribeVoice(audioBlob: Blob) {
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
      formData.append("file", file);
      formData.append("language", "auto");

      const response = await fetch(
        `${API_URL}/api/v1/voice/transcribe`,
        {
          method: "POST",
          body: formData,
        },
      );

      const data =
        (await response.json()) as {
          text?: string;
          detail?: string;
        };

      if (!response.ok) {
        throw new Error(
          data.detail ??
            `Voice transcription failed: ${response.status}`,
        );
      }

      const transcript =
        data.text?.trim() ?? "";

      if (!transcript) {
        throw new Error(
          "No speech was detected in the recording.",
        );
      }

      setInput(transcript);
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
      clearInterval(recordingTimerRef.current);
      recordingTimerRef.current = null;
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
      !navigator.mediaDevices?.getUserMedia ||
      typeof MediaRecorder === "undefined"
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
        await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
          },
        });

      let mimeType = "";

      if (
        MediaRecorder.isTypeSupported(
          "audio/webm;codecs=opus",
        )
      ) {
        mimeType = "audio/webm;codecs=opus";
      } else if (
        MediaRecorder.isTypeSupported(
          "audio/webm",
        )
      ) {
        mimeType = "audio/webm";
      }

      const recorder = mimeType
        ? new MediaRecorder(
            stream,
            { mimeType },
          )
        : new MediaRecorder(
        stream,
        {
          mimeType: getAquaLifeRecordingMimeType(),
        },
      );

      audioChunksRef.current = [];
      discardRecordingRef.current = false;

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(
            event.data,
          );
        }
      };

      recorder.onerror = () => {
        clearRecordingTimer();

        stream
          .getTracks()
          .forEach((track) => track.stop());

        mediaRecorderRef.current = null;
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
          .forEach((track) => track.stop());

        mediaRecorderRef.current = null;
        setRecording(false);

        const cancelled =
          discardRecordingRef.current;

        setRecordingSeconds(0);

        if (cancelled) {
          audioChunksRef.current = [];
          return;
        }

        const audioBlob = new Blob(
          audioChunksRef.current,
          {
            type:
              mimeType ||
              "audio/webm",
          },
        );

        audioChunksRef.current = [];

        if (audioBlob.size > 0) {
          await transcribeVoice(
            audioBlob,
          );
        }
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250);

      setRecordingSeconds(0);
      setRecording(true);

      recordingTimerRef.current =
        setInterval(() => {
          setRecordingSeconds(
            (current) => {
              const next = current + 1;

              if (next >= 60) {
                window.setTimeout(
                  () => stopRecording(),
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
      setRecordingSeconds(0);

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            error instanceof Error
              ? error.message
              : "Unable to access your microphone.",
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
    discardRecordingRef.current = true;
    clearRecordingTimer();

    const recorder =
      mediaRecorderRef.current;

    if (
      recorder &&
      recorder.state !== "inactive"
    ) {
      recorder.stop();
    } else {
      setRecording(false);
      setRecordingSeconds(0);
      audioChunksRef.current = [];
    }
  }

  async function sendMessage() {
    const text = input.trim();

    if (!text || chatLoading) {
      return;
    }

    setInput("");

    setMessages((current) => [
      ...current,
      {
        role: "user",
        content: text,
      },
    ]);

    setChatLoading(true);

    const controller = new AbortController();
    abortRef.current = controller;

    try {
      const response = await fetch(
        `${API_URL}/api/v1/public/ai/chat/stream`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Accept: "text/event-stream",
          },
          body: JSON.stringify({
            message: text,
          }),
          signal: controller.signal,
        },
      );

      if (!response.ok) {
        throw new Error(
          `Aqua AI request failed: ${response.status}`,
        );
      }

      if (!response.body) {
        throw new Error("Aqua AI returned no stream.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";
      let answer = "";
      let assistantCreated = false;

      while (true) {
        const { value, done } =
          await reader.read();

        if (done) {
          break;
        }

        buffer += decoder.decode(
          value,
          { stream: true },
        );

        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const event of events) {
          const dataLine = event
            .split("\n")
            .find((line) =>
              line.startsWith("data:"),
            );

          if (!dataLine) {
            continue;
          }

          const raw = dataLine
            .slice(5)
            .trim();

          if (!raw) {
            continue;
          }

          const payload = JSON.parse(raw) as {
            type?: string;
            content?: string;
            detail?: string;
          };

          if (payload.type === "token") {
            answer += payload.content ?? "";

            setMessages((current) => {
              if (!assistantCreated) {
                assistantCreated = true;

                return [
                  ...current,
                  {
                    role: "assistant",
                    content: answer,
                  },
                ];
              }

              return current.map(
                (message, index) => {
                  if (
                    index === current.length - 1 &&
                    message.role === "assistant"
                  ) {
                    return {
                      ...message,
                      content: answer,
                    };
                  }

                  return message;
                },
              );
            });
          }

          if (payload.type === "error") {
            throw new Error(
              payload.detail ??
                "Aqua AI could not answer.",
            );
          }
        }
      }

      if (!answer && !assistantCreated) {
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content:
              "I could not generate a response.",
          },
        ]);
      }
    } catch (error) {
      if (
        error instanceof DOMException &&
        error.name === "AbortError"
      ) {
        return;
      }

      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content:
            "Aqua AI is temporarily unavailable. Please try again.",
        },
      ]);
    } finally {
      abortRef.current = null;
      setChatLoading(false);
    }
  }

  if (!open) {
    return null;
  }

  return (
    <>
      <div
        className="fixed inset-0 z-40 bg-black/30 backdrop-blur-[2px] lg:hidden"
        onClick={onClose}
        aria-hidden="true"
      />

      <aside
        className={[
          "fixed right-4 top-20 z-50",
          "flex h-[min(760px,calc(100vh-104px))]",
          "w-[min(430px,calc(100vw-32px))]",
          "flex-col overflow-hidden",
          "rounded-3xl border border-border",
          "bg-background/95 shadow-2xl",
          "backdrop-blur-2xl",
        ].join(" ")}
        aria-label="Aqua AI assistant"
      >
        <div className="flex items-center justify-between border-b border-border px-5 py-4">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-foreground text-background">
              <BrainCircuit className="h-5 w-5" />
            </div>

            <div>
              <p className="text-sm font-semibold">
                Aqua AI
              </p>

              <p className="text-[10px] text-muted-foreground">
                Aquaculture intelligence
              </p>
            </div>
          </div>

          <div className="flex items-center gap-1">
            <Sparkles className="mr-2 h-4 w-4 text-muted-foreground" />

            <button
              type="button"
              onClick={onClose}
              className="flex h-9 w-9 items-center justify-center rounded-xl text-muted-foreground transition hover:bg-muted hover:text-foreground"
              aria-label="Close Aqua AI"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-4 py-5">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={[
                  "flex gap-3",
                  message.role === "user"
                    ? "justify-end"
                    : "justify-start",
                ].join(" ")}
              >
                {message.role === "assistant" && (
                  <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-muted">
                    <BrainCircuit className="h-4 w-4" />
                  </div>
                )}

                <div
                  className={[
                    "max-w-[82%] rounded-2xl px-4 py-3",
                    "text-xs leading-6",
                    message.role === "user"
                      ? "bg-foreground text-background"
                      : "bg-muted",
                  ].join(" ")}
                >
                  {message.content}
                </div>
              </div>
            ))}

            {chatLoading && (
              <div className="flex gap-3">
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-muted">
                  <BrainCircuit className="h-4 w-4" />
                </div>

                <div className="flex items-center gap-2 rounded-2xl bg-muted px-4 py-3 text-xs text-muted-foreground">
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  Aqua AI is thinking...
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="border-t border-border p-4">

          {recording && (
            <div className="mb-3 rounded-2xl border border-border bg-background p-3">

              <div className="flex items-center justify-between gap-3">

                <div className="flex items-center gap-2">
                  <span className="relative flex h-3 w-3">
                    <span className="absolute h-3 w-3 animate-ping rounded-full bg-foreground/40" />
                    <span className="relative h-3 w-3 rounded-full bg-foreground" />
                  </span>

                  <span className="text-xs font-semibold">
                    Recording...
                  </span>
                </div>

                <span className="font-mono text-xs font-semibold tabular-nums">
                  {String(
                    Math.floor(
                      recordingSeconds / 60,
                    ),
                  ).padStart(2, "0")}
                  :
                  {String(
                    recordingSeconds % 60,
                  ).padStart(2, "0")}
                  <span className="ml-1 text-muted-foreground">
                    / 01:00
                  </span>
                </span>

              </div>

              <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-foreground transition-[width] duration-1000 ease-linear"
                  style={{
                    width: `${Math.min(
                      100,
                      (recordingSeconds / 60) * 100,
                    )}%`,
                  }}
                />
              </div>

              <div className="mt-3 flex items-center justify-between gap-2">

                <button
                  type="button"
                  onClick={cancelRecording}
                  className="rounded-xl border border-border px-3 py-2 text-xs font-semibold transition hover:bg-muted"
                >
                  Cancel
                </button>

                <button
                  type="button"
                  onClick={stopRecording}
                  className="flex items-center gap-2 rounded-xl bg-foreground px-3 py-2 text-xs font-semibold text-background transition hover:opacity-90"
                >
                  <Square className="h-3.5 w-3.5" />
                  Stop & transcribe
                </button>

              </div>

            </div>
          )}

          {voiceLoading && (
            <div className="mb-3 rounded-xl border border-border bg-muted/30 px-3 py-2 text-[10px] text-muted-foreground">
              Transcribing your voice...
            </div>
          )}

          <div className="flex items-center gap-2 rounded-2xl border border-border bg-muted/20 p-2">

            <input
              value={input}
              onChange={(event) =>
                setInput(event.target.value)
              }
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void sendMessage();
                }
              }}
              disabled={
                recording ||
                voiceLoading
              }
              placeholder={
                recording
                  ? "Listening..."
                  : voiceLoading
                    ? "Transcribing..."
                    : "Ask Aqua AI..."
              }
              className="h-10 min-w-0 flex-1 bg-transparent px-2 text-xs outline-none placeholder:text-muted-foreground disabled:opacity-60"
            />

            <button
              type="button"
              onClick={
                recording
                  ? stopRecording
                  : startRecording
              }
              disabled={
                chatLoading ||
                voiceLoading
              }
              className={[
                "flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border transition",
                recording
                  ? "border-foreground bg-foreground text-background"
                  : "border-border bg-transparent text-foreground",
                chatLoading || voiceLoading
                  ? "opacity-40"
                  : "hover:bg-muted",
              ].join(" ")}
              aria-label={
                recording
                  ? "Stop recording"
                  : "Start voice recording"
              }
              title={
                recording
                  ? "Stop recording"
                  : "Speak to Aqua AI"
              }
            >
              {recording ? (
                <Square className="h-4 w-4" />
              ) : (
                <Mic className="h-4 w-4" />
              )}
            </button>

            <button
              type="button"
              onClick={() => void sendMessage()}
              disabled={
                !input.trim() ||
                chatLoading ||
                recording ||
                voiceLoading
              }
              className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-foreground text-background transition hover:opacity-90 disabled:opacity-40"
              aria-label="Send message"
            >
              <Send className="h-4 w-4" />
            </button>

          </div>

          <p className="mt-2 px-1 text-[9px] text-muted-foreground">
            Speak or type your question. Voice input is transcribed locally through AquaLife's voice service.
          </p>
        </div>
      </aside>
    </>
  );
}

export function AquaAIButton({
  onClick,
}: {
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "fixed bottom-5 right-5 z-40",
        "flex h-14 w-14 items-center justify-center",
        "rounded-2xl border border-border",
        "bg-foreground text-background",
        "shadow-xl shadow-black/20",
        "transition hover:-translate-y-0.5 hover:shadow-2xl",
      ].join(" ")}
      aria-label="Open Aqua AI"
      title="Open Aqua AI"
    >
      <BrainCircuit className="h-6 w-6" />
    </button>
  );
}

