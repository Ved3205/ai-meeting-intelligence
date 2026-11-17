"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Calendar, Clock, Globe, Layers, Trash2, Video } from "lucide-react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import { useState } from "react";
import { Chat } from "@/components/chat/chat";
import { MeetingTile } from "@/components/meetings/meeting-tile";
import { SummaryTab } from "@/components/meetings/summary-tab";
import { TranscriptTab } from "@/components/meetings/transcript-tab";
import { Button } from "@/components/ui/button";
import { Card, CardBody } from "@/components/ui/card";
import { EmptyState, ErrorNote, Skeleton } from "@/components/ui/states";
import { api, ApiError } from "@/lib/api";
import { cn, formatDate, formatDuration } from "@/lib/format";

const TABS = [
  { id: "summary", label: "Summary" },
  { id: "transcript", label: "Transcript" },
  { id: "ask", label: "Ask" },
] as const;

type TabId = (typeof TABS)[number]["id"];

function Meta({ icon: Icon, children }: { icon: React.ElementType; children: React.ReactNode }) {
  return (
    <span className="inline-flex items-center gap-1.5 text-sm text-muted-foreground">
      <Icon className="size-4" />
      {children}
    </span>
  );
}

export default function MeetingPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const queryClient = useQueryClient();
  const [tab, setTab] = useState<TabId>("summary");
  const [confirmDelete, setConfirmDelete] = useState(false);

  const { data: meeting, isPending, error } = useQuery({
    queryKey: ["meeting", id],
    queryFn: () => api.getMeeting(id),
  });

  const remove = useMutation({
    mutationFn: () => api.deleteMeeting(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      router.push("/meetings");
    },
  });

  if (isPending) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-28" />
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-64" />
      </div>
    );
  }

  if (error) {
    const missing = error instanceof ApiError && error.status === 404;
    return missing ? (
      <Card>
        <EmptyState
          icon={Video}
          title="Meeting not found"
          description="It may have been deleted."
          action={
            <Link href="/meetings">
              <Button variant="secondary">Back to meetings</Button>
            </Link>
          }
        />
      </Card>
    ) : (
      <ErrorNote message={error.message} />
    );
  }

  return (
    <>
      <Link
        href="/meetings"
        className="mb-4 inline-flex items-center gap-1.5 text-sm text-muted-foreground transition-colors hover:text-foreground"
      >
        <ArrowLeft className="size-4" />
        Meetings
      </Link>

      <Card className="mb-6">
        <CardBody className="flex flex-wrap items-start gap-5">
          <MeetingTile id={meeting.meeting_id} title={meeting.title} size="lg" />
          <div className="min-w-0 flex-1">
            <h1 className="text-xl font-semibold leading-tight">{meeting.title ?? "Untitled meeting"}</h1>
            <div className="mt-2.5 flex flex-wrap items-center gap-x-5 gap-y-1.5">
              <Meta icon={Clock}>{formatDuration(meeting.duration)}</Meta>
              <Meta icon={Calendar}>{formatDate(meeting.uploaded_at)}</Meta>
              <Meta icon={Layers}>{meeting.total_chunks} chunks</Meta>
              {meeting.language && <Meta icon={Globe}>{meeting.language.toUpperCase()}</Meta>}
            </div>
          </div>

          {confirmDelete ? (
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Delete this meeting?</span>
              <Button variant="danger" size="sm" onClick={() => remove.mutate()} disabled={remove.isPending}>
                Delete
              </Button>
              <Button variant="secondary" size="sm" onClick={() => setConfirmDelete(false)}>
                Cancel
              </Button>
            </div>
          ) : (
            <Button variant="secondary" size="sm" onClick={() => setConfirmDelete(true)}>
              <Trash2 className="size-4" />
              Delete
            </Button>
          )}
        </CardBody>
      </Card>

      {remove.error && <ErrorNote message={remove.error.message} className="mb-4" />}

      <div className="mb-5 inline-flex rounded-lg bg-muted p-1" role="tablist">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            onClick={() => setTab(t.id)}
            className={cn(
              "rounded-md px-4 py-1.5 text-sm font-medium transition-all",
              tab === t.id
                ? "bg-card text-foreground shadow-card"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "summary" && <SummaryTab meetingId={id} />}
      {tab === "transcript" && <TranscriptTab meetingId={id} />}
      {tab === "ask" && (
        <Card className="h-[34rem] overflow-hidden">
          <Chat meetingId={id} />
        </Card>
      )}
    </>
  );
}
