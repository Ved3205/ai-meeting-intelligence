"use client";

import { useQuery } from "@tanstack/react-query";
import { Search } from "lucide-react";
import { useState } from "react";
import { Card } from "@/components/ui/card";
import { CopyButton } from "@/components/ui/copy-button";
import { EmptyState, ErrorNote, Skeleton } from "@/components/ui/states";
import { api } from "@/lib/api";
import { formatTime } from "@/lib/format";

function Highlight({ text, term }: { text: string; term: string }) {
  if (!term) return <>{text}</>;
  const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const parts = text.split(new RegExp(`(${escaped})`, "gi"));
  return (
    <>
      {parts.map((part, i) =>
        part.toLowerCase() === term.toLowerCase() ? (
          <mark key={i} className="rounded bg-warning-soft px-0.5 text-foreground">
            {part}
          </mark>
        ) : (
          part
        ),
      )}
    </>
  );
}

export function TranscriptTab({ meetingId }: { meetingId: string }) {
  const [search, setSearch] = useState("");
  const { data, isPending, error } = useQuery({
    queryKey: ["transcript", meetingId],
    queryFn: () => api.getTranscript(meetingId),
  });

  if (isPending) return <Skeleton className="h-72" />;
  if (error) return <ErrorNote message={error.message} />;

  const term = search.trim();
  const segments = data.segments.filter((s) => s.text.toLowerCase().includes(term.toLowerCase()));
  const fullText = data.segments.map((s) => `[${formatTime(s.start_time)}] ${s.text}`).join("\n\n");

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search the transcript"
            aria-label="Search the transcript"
            className="h-10 w-full rounded-lg border border-border bg-card pl-9 pr-3 text-sm outline-none transition-colors focus:border-primary"
          />
        </div>
        <CopyButton text={fullText} label="Copy all" className="h-10 px-3" />
      </div>

      <Card>
        {segments.length === 0 ? (
          <EmptyState icon={Search} title="Nothing found" description="No part of the transcript matches your search." />
        ) : (
          <div className="divide-y divide-border">
            {segments.map((seg) => (
              <div key={seg.chunk_index} className="flex gap-4 px-5 py-4">
                <span className="w-14 shrink-0 pt-0.5 font-mono text-xs tabular-nums text-primary">
                  {formatTime(seg.start_time)}
                </span>
                <p className="text-sm leading-7">
                  <Highlight text={seg.text} term={term} />
                </p>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
