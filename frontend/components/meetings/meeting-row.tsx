import { Calendar, ChevronRight, Clock } from "lucide-react";
import Link from "next/link";
import { Badge } from "@/components/ui/badge";
import { formatDate, formatDuration } from "@/lib/format";
import type { Meeting } from "@/lib/types";
import { CategorySelect } from "./category-controls";
import { MeetingTile } from "./meeting-tile";

export function MeetingRow({ meeting }: { meeting: Meeting }) {
  return (
    <div className="group flex items-center gap-3 px-5 py-3.5 transition-colors hover:bg-muted/60">
      <Link href={`/meetings/${meeting.meeting_id}`} className="flex min-w-0 flex-1 items-center gap-4">
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
      </Link>
      <CategorySelect meetingId={meeting.meeting_id} className="hidden w-36 sm:block" />
      <Badge tone="success" className="hidden md:inline-flex">
        Indexed
      </Badge>
      <Link href={`/meetings/${meeting.meeting_id}`} aria-label="Open meeting">
        <ChevronRight className="size-4 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-0.5" />
      </Link>
    </div>
  );
}
