"use client";

import { useMutation } from "@tanstack/react-query";
import { ChevronDown, Quote, SendHorizontal, Sparkles } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CopyButton } from "@/components/ui/copy-button";
import { ErrorNote } from "@/components/ui/states";
import { api } from "@/lib/api";
import { countQuestion } from "@/lib/hooks";
import { formatTime } from "@/lib/format";
import type { SourceChunk } from "@/lib/types";

type Message =
  | { role: "user"; text: string }
  | { role: "assistant"; text: string; confidence: number; sources: SourceChunk[] };

const SUGGESTIONS = [
  "What decisions were made?",
  "What are the action items?",
  "Give me a short summary of the discussion.",
];

function confidenceBadge(value: number) {
  const pct = `${Math.round(value * 100)}%`;
  if (value >= 0.75) return <Badge tone="success">High confidence {pct}</Badge>;
  if (value >= 0.5) return <Badge tone="warning">Medium confidence {pct}</Badge>;
  return <Badge tone="danger">Low confidence {pct}</Badge>;
}

function Avatar() {
  return (
    <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary-soft text-primary">
      <Sparkles className="size-4" />
    </div>
  );
}

function Sources({ sources, showMeeting }: { sources: SourceChunk[]; showMeeting: boolean }) {
  if (sources.length === 0) return null;
  return (
    <details className="group mt-3 border-t border-border pt-3">
      <summary className="flex list-none items-center gap-1.5 text-xs font-medium text-muted-foreground hover:text-foreground">
        <Quote className="size-3.5" />
        {sources.length} {sources.length === 1 ? "source" : "sources"}
        <ChevronDown className="size-3.5 transition-transform group-open:rotate-180" />
      </summary>
      <ul className="mt-3 space-y-2">
        {sources.map((s) => (
          <li key={s.chunk_id} className="rounded-lg border-l-2 border-primary bg-muted/60 py-2.5 pl-3 pr-3 text-sm">
            <div className="mb-1 flex flex-wrap items-center gap-2 text-xs">
              <span className="font-mono tabular-nums text-primary">
                {formatTime(s.start_time)} - {formatTime(s.end_time)}
              </span>
              {showMeeting && (
                <Link href={`/meeting?id=${s.meeting_id}`} className="font-medium text-foreground hover:underline">
                  {s.title ?? "Meeting"}
                </Link>
              )}
            </div>
            <p className="leading-relaxed text-muted-foreground">{s.text}</p>
          </li>
        ))}
      </ul>
    </details>
  );
}

export function Chat({ meetingId, initialQuestion }: { meetingId?: string; initialQuestion?: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const sentInitial = useRef(false);

  const ask = useMutation({
    mutationFn: (question: string) => api.ask(question, meetingId),
    onSuccess: (res) => {
      countQuestion();
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: res.answer,
          confidence: res.confidence,
          sources: res.retrieved_chunks,
        },
      ]);
    },
  });

  function send(question: string) {
    const text = question.trim();
    if (!text || ask.isPending) return;
    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    ask.mutate(text);
  }

  useEffect(() => {
    if (initialQuestion && !sentInitial.current) {
      sentInitial.current = true;
      send(initialQuestion);
    }
    // only runs for the question passed in from another page
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialQuestion]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, ask.isPending]);

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div className="flex-1 space-y-6 overflow-y-auto p-5">
        {messages.length === 0 && (
          <div className="flex h-full flex-col items-center justify-center text-center">
            <div className="mb-5 flex size-16 items-center justify-center rounded-full bg-muted">
              <div className="flex size-11 items-center justify-center rounded-full bg-card text-primary shadow-card ring-1 ring-border">
                <Sparkles className="size-5" />
              </div>
            </div>
            <h3 className="text-sm font-semibold">
              {meetingId ? "Ask about this meeting" : "Ask about your meetings"}
            </h3>
            <p className="mt-1.5 max-w-sm text-sm leading-relaxed text-muted-foreground">
              Answers come from the transcript, with the exact passages and timestamps listed under each one.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="rounded-full border border-border bg-card px-3.5 py-1.5 text-sm text-muted-foreground transition-colors hover:border-primary hover:text-primary"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="flex justify-end">
              <p className="max-w-[85%] rounded-2xl rounded-br-md bg-primary px-4 py-2.5 text-sm leading-relaxed text-white dark:text-slate-950">
                {m.text}
              </p>
            </div>
          ) : (
            <div key={i} className="flex gap-3">
              <Avatar />
              <div className="min-w-0 max-w-[90%] flex-1">
                <div className="rounded-2xl rounded-tl-md border border-border bg-card px-4 py-3 shadow-card">
                  <p className="whitespace-pre-wrap text-sm leading-7">{m.text}</p>
                  <div className="mt-3 flex items-center justify-between gap-2">
                    {confidenceBadge(m.confidence)}
                    <CopyButton text={m.text} />
                  </div>
                  <Sources sources={m.sources} showMeeting={!meetingId} />
                </div>
              </div>
            </div>
          ),
        )}

        {ask.isPending && (
          <div className="flex items-center gap-3">
            <Avatar />
            <div className="flex items-center gap-1 rounded-2xl rounded-tl-md border border-border bg-card px-4 py-3.5 shadow-card" aria-label="Searching the transcript">
              {[0, 1, 2].map((n) => (
                <span
                  key={n}
                  className="typing-dot size-1.5 rounded-full bg-muted-foreground"
                  style={{ animationDelay: `${n * 0.18}s` }}
                />
              ))}
            </div>
          </div>
        )}
        {ask.error && <ErrorNote message={ask.error.message} />}
        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex gap-2 border-t border-border bg-card p-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question"
          aria-label="Question"
          className="h-10 min-w-0 flex-1 rounded-lg border border-border bg-background px-3 text-sm outline-none transition-colors focus:border-primary"
        />
        <Button type="submit" disabled={!input.trim() || ask.isPending} aria-label="Send">
          <SendHorizontal className="size-4" />
        </Button>
      </form>
    </div>
  );
}
