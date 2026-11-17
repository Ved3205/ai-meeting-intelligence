import { Calendar, ChevronRight, Clock } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatDuration } from "@/lib/format";
import type { Meeting } from "@/lib/types";
import { MeetingTile } from "./meeting-tile";

export function MeetingRow({ meeting }: { meeting: Meeting }) {
  return (
    <Link
      href={`/meetings/${meeting.meeting_id}`}
      className="group flex items-center gap-4 px-5 py-3.5 transition-colors hover:bg-muted/60"
    >
      <MeetingTile id={meeting.meeting_id} title={meeting.title} />
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">{meeting.title ?? "Untitled meeting"}</p>
        <p className="mt-1 flex flex-wrap items-center gap-x-4 gap-y-0.5 text-xs text-muted-foreground">
          <span className="inline-flex items-center gap-1.5">
            <Clock className="size-3.5" />
            {formatDuration(meeting.duration)}
          </span>
          <span className="inline-flex items-center gap-1.5">
            <Calendar className="size-3.5" />
            {formatDate(meeting.uploaded_at)}
          </span>
        </p>
      </div>
      <Badge tone="success" className="hidden sm:inline-flex">
        Indexed
      </Badge>
      <ChevronRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
    </Link>
  );
}
