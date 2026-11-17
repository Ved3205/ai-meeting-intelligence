"use client";

import { ArrowRight, Clock, FileAudio, Layers, Sparkles, Upload, Video } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { MeetingRow } from "@/components/meetings/meeting-row";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyState, ErrorNote, ListSkeleton, Skeleton } from "@/components/ui/states";
import { cn, formatDuration } from "@/lib/format";
import { useMeetings } from "@/lib/hooks";

const SUGGESTIONS = ["What decisions were made?", "List the action items", "Who owns the next steps?"];

const STEPS = [
  { icon: Upload, title: "Upload", text: "Add a meeting recording." },
  { icon: FileAudio, title: "Transcribe", text: "Speech becomes searchable text." },
  { icon: Sparkles, title: "Ask", text: "Get answers with sources." },
];

function Stat({
  icon: Icon,
  label,
  value,
  tone,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  tone: string;
}) {
  return (
    <Card>
      <CardBody className="flex items-center gap-4 py-4">
        <div className={cn("flex size-10 items-center justify-center rounded-lg", tone)}>
          <Icon className="size-5" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-2xl font-semibold tabular-nums leading-tight">{value}</p>
        </div>
      </CardBody>
    </Card>
  );
}

function AskBox() {
  const router = useRouter();
  const [question, setQuestion] = useState("");

  function go(q: string) {
    const text = q.trim();
    if (text) router.push(`/ask?q=${encodeURIComponent(text)}`);
  }

  return (
    <Card className="mb-6">
      <CardBody>
        <h2 className="text-sm font-semibold">What would you like to know?</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            go(question);
          }}
          className="mt-3 flex gap-2"
        >
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your meetings"
            aria-label="Question"
            className="h-10 min-w-0 flex-1 rounded-lg border border-border bg-background px-3 text-sm outline-none transition-colors focus:border-primary"
          />
          <Button type="submit" disabled={!question.trim()}>
            Ask
            <ArrowRight className="size-4" />
          </Button>
        </form>
        <div className="mt-3 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => go(s)}
              className="rounded-full border border-border px-3 py-1 text-xs text-muted-foreground transition-colors hover:border-primary hover:text-primary"
            >
              {s}
            </button>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}

export default function DashboardPage() {
  const { data, isPending, error } = useMeetings();
  const meetings = data?.meetings ?? [];

  const totalChunks = meetings.reduce((sum, m) => sum + m.total_chunks, 0);
  const totalDuration = meetings.reduce((sum, m) => sum + m.duration, 0);

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="Your meetings, summaries and answers in one place."
        action={
          <Link href="/upload">
            <Button>
              <Upload className="size-4" />
              Upload meeting
            </Button>
          </Link>
        }
      />

      {error && <ErrorNote message={error.message} className="mb-6" />}

      <div className="mb-6 grid gap-4 sm:grid-cols-3">
        {isPending ? (
          <>
            <Skeleton className="h-[74px]" />
            <Skeleton className="h-[74px]" />
            <Skeleton className="h-[74px]" />
          </>
        ) : (
          <>
            <Stat
              icon={Video}
              label="Meetings"
              value={String(meetings.length)}
              tone="bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300"
            />
            <Stat
              icon={Layers}
              label="Indexed chunks"
              value={String(totalChunks)}
              tone="bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300"
            />
            <Stat
              icon={Clock}
              label="Total recorded"
              value={formatDuration(totalDuration)}
              tone="bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300"
            />
          </>
        )}
      </div>

      {meetings.length > 0 && <AskBox />}

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Recent meetings</CardTitle>
          {meetings.length > 0 && (
            <Link href="/meetings" className="text-sm font-medium text-primary hover:underline">
              View all
            </Link>
          )}
        </CardHeader>
        {isPending ? (
          <ListSkeleton />
        ) : meetings.length === 0 ? (
          <div>
            <EmptyState
              icon={Video}
              title="No meetings yet"
              description="Upload a recording and it will be transcribed, indexed and ready for questions."
              action={
                <Link href="/upload">
                  <Button>
                    <Upload className="size-4" />
                    Upload your first meeting
                  </Button>
                </Link>
              }
            />
            <div className="grid gap-px border-t border-border bg-border sm:grid-cols-3">
              {STEPS.map(({ icon: Icon, title, text }, i) => (
                <div key={title} className="flex items-start gap-3 bg-card p-5">
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary-soft text-primary">
                    <Icon className="size-4" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">
                      {i + 1}. {title}
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground">{text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {meetings.slice(0, 5).map((m) => (
              <MeetingRow key={m.meeting_id} meeting={m} />
            ))}
          </div>
        )}
      </Card>
    </>
  );
}
