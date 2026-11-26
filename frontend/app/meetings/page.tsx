"use client";

import { Search, Upload, Video } from "lucide-react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { MeetingRow } from "@/components/meetings/meeting-row";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyState, ErrorNote, ListSkeleton } from "@/components/ui/states";
import { useCategories } from "@/lib/categories";
import { cn } from "@/lib/format";
import { useMeetings } from "@/lib/hooks";
import type { Meeting } from "@/lib/types";

const SORTS = {
  newest: { label: "Newest first", fn: (a: Meeting, b: Meeting) => (b.uploaded_at ?? "").localeCompare(a.uploaded_at ?? "") },
  oldest: { label: "Oldest first", fn: (a: Meeting, b: Meeting) => (a.uploaded_at ?? "").localeCompare(b.uploaded_at ?? "") },
  longest: { label: "Longest first", fn: (a: Meeting, b: Meeting) => b.duration - a.duration },
  name: { label: "Name A-Z", fn: (a: Meeting, b: Meeting) => (a.title ?? "").localeCompare(b.title ?? "") },
};

type SortKey = keyof typeof SORTS;

function MeetingsView() {
  const { data, isPending, error } = useMeetings();
  const [search, setSearch] = useState(useSearchParams().get("q") ?? "");
  const [sort, setSort] = useState<SortKey>("newest");
  const [category, setCategory] = useState(useSearchParams().get("category") ?? "all");
  const { categories, categoryOf } = useCategories();

  const term = search.trim().toLowerCase();
  const meetings = (data?.meetings ?? [])
    .filter((m) => `${m.title ?? ""} ${m.filename ?? ""}`.toLowerCase().includes(term))
    .filter((m) => {
      if (category === "all") return true;
      const c = categoryOf(m.meeting_id);
      return category === "none" ? !c : c?.id === category;
    })
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

      {categories.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-2" role="group" aria-label="Filter by category">
          {[{ id: "all", name: "All" }, ...categories, { id: "none", name: "Uncategorized" }].map((c) => (
            <button
              key={c.id}
              onClick={() => setCategory(c.id)}
              aria-pressed={category === c.id}
              className={cn(
                "rounded-full border px-3 py-1 text-xs font-medium transition-colors",
                category === c.id
                  ? "border-primary bg-primary-soft text-primary"
                  : "border-border text-muted-foreground hover:border-primary/50",
              )}
            >
              {c.name}
            </button>
          ))}
          <Link href="/categories" className="ml-1 text-xs font-medium text-primary hover:underline">
            Manage
          </Link>
        </div>
      )}

      {error && <ErrorNote message={error.message} className="mb-4" />}

      <Card>
        {isPending ? (
          <ListSkeleton rows={4} />
        ) : meetings.length === 0 ? (
          <EmptyState
            icon={term ? Search : Video}
            title={term || category !== "all" ? "No meetings match your filters" : "No meetings yet"}
            description={term || category !== "all" ? "Try a different word or category." : "Upload a recording to get started."}
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

export default function MeetingsPage() {
  return (
    <Suspense>
      <MeetingsView />
    </Suspense>
  );
}
