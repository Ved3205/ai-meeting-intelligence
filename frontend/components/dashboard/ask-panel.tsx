"use client";

import { MessageSquare, Minus, X } from "lucide-react";
import { useState } from "react";
import { Chat } from "@/components/chat/chat";

export function AskPanel() {
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-20 flex h-12 items-center gap-2 rounded-full bg-primary px-5 text-sm font-medium text-white shadow-lg transition-colors hover:bg-primary-hover"
      >
        <MessageSquare className="size-4" />
        Ask a question
      </button>
    );
  }

  return (
    <div className="fixed inset-x-3 bottom-3 z-20 flex h-[32rem] max-h-[80vh] flex-col overflow-hidden rounded-xl border border-border bg-card shadow-xl sm:inset-x-auto sm:bottom-6 sm:right-6 sm:w-[24rem]">
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <h2 className="text-sm font-semibold">Ask a question</h2>
        <div className="flex gap-1">
          <button onClick={() => setOpen(false)} aria-label="Minimize" className="rounded p-1 text-muted-foreground hover:bg-muted">
            <Minus className="size-4" />
          </button>
          <button onClick={() => setOpen(false)} aria-label="Close" className="rounded p-1 text-muted-foreground hover:bg-muted">
            <X className="size-4" />
          </button>
        </div>
      </div>
      <div className="min-h-0 flex-1">
        <Chat />
      </div>
    </div>
  );
}
