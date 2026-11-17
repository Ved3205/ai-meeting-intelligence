"use client";

import { Search, Upload, Video } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { MeetingRow } from "@/components/meetings/meeting-row";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyState, ErrorNote, ListSkeleton } from "@/components/ui/states";
import { useMeetings } from "@/lib/hooks";
import type { Meeting } from "@/lib/types";

const SORTS = {
  newest: { label: "Newest first", fn: (a: Meeting, b: Meeting) => (b.uploaded_at ?? "").localeCompare(a.uploaded_at ?? "") },
  oldest: { label: "Oldest first", fn: (a: Meeting, b: Meeting) => (a.uploaded_at ?? "").localeCompare(b.uploaded_at ?? "") },
  longest: { label: "Longest first", fn: (a: Meeting, b: Meeting) => b.duration - a.duration },
  name: { label: "Name A-Z", fn: (a: Meeting, b: Meeting) => (a.title ?? "").localeCompare(b.title ?? "") },
};

type SortKey = keyof typeof SORTS;

export default function MeetingsPage() {
  const { data, isPending, error } = useMeetings();
  const [search, setSearch] = useState("");
  const [sort, setSort] = useState<SortKey>("newest");

  const term = search.trim().toLowerCase();
  const meetings = (data?.meetings ?? [])
    .filter((m) => `${m.title ?? ""} ${m.filename ?? ""}`.toLowerCase().includes(term))
    .sort(SORTS[sort].fn);

  return (
    <>
      <PageHeader
        title="Meetings"
        description={data ? `${data.total} indexed ${data.total === 1 ? "meeting" : "meetings"}` : "Every meeting that has been uploaded and indexed."}
        action={
          <Link href="/upload">
            <Button>
              <Upload className="size-4" />
              Upload meeting
            </Button>
          </Link>
        }
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by title or file name"
            aria-label="Search meetings"
            className="h-10 w-full rounded-lg border border-border bg-card pl-9 pr-3 text-sm outline-none transition-colors focus:border-primary"
          />
        </div>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          aria-label="Sort meetings"
          className="h-10 rounded-lg border border-border bg-card px-3 text-sm outline-none focus:border-primary"
        >
          {Object.entries(SORTS).map(([key, { label }]) => (
            <option key={key} value={key}>
              {label}
            </option>
          ))}
        </select>
      </div>

      {error && <ErrorNote message={error.message} className="mb-4" />}

      <Card>
        {isPending ? (
          <ListSkeleton rows={4} />
        ) : meetings.length === 0 ? (
          <EmptyState
            icon={term ? Search : Video}
            title={term ? "No meetings match your search" : "No meetings yet"}
            description={term ? "Try a different word." : "Upload a recording to get started."}
          />
        ) : (
          <div className="divide-y divide-border">
            {meetings.map((m) => (
              <MeetingRow key={m.meeting_id} meeting={m} />
            ))}
          </div>
        )}
      </Card>
    </>
  );
}
