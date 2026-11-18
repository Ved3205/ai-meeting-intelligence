import { CloudUpload } from "lucide-react";
import Link from "next/link";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/states";
import { formatDate, formatDuration } from "@/lib/format";
import type { Meeting } from "@/lib/types";

export function ActivityList({ meetings, loading }: { meetings: Meeting[]; loading: boolean }) {
  const recent = [...meetings]
    .filter((m) => m.uploaded_at)
    .sort((a, b) => (b.uploaded_at ?? "").localeCompare(a.uploaded_at ?? ""))
    .slice(0, 4);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent activity</CardTitle>
      </CardHeader>
      {loading ? (
        <div className="space-y-3 p-5">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-10" />
          ))}
        </div>
      ) : recent.length === 0 ? (
        <p className="p-5 text-sm text-muted-foreground">Uploads will be listed here.</p>
      ) : (
        <ul className="divide-y divide-border">
          {recent.map((m) => (
            <li key={m.meeting_id}>
              <Link
                href={`/meeting?id=${m.meeting_id}`}
                className="flex items-start gap-3 px-5 py-3 transition-colors hover:bg-muted/60"
              >
                <span className="mt-0.5 flex size-8 shrink-0 items-center justify-center rounded-lg bg-success-soft text-success">
                  <CloudUpload className="size-4" />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-medium">Meeting indexed</span>
                  <span className="block truncate text-xs text-muted-foreground">
                    {m.title ?? m.filename ?? "Untitled"}
                  </span>
                  <span className="block text-xs text-muted-foreground">
                    {formatDate(m.uploaded_at)} · {formatDuration(m.duration)}
                  </span>
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}
