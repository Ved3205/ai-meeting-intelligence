"use client";

import { CheckSquare, Clock, FileText, Layers, MessageSquare, Upload, Video } from "lucide-react";
import Link from "next/link";
import { ActivityList } from "@/components/dashboard/activity-list";
import { AskPanel } from "@/components/dashboard/ask-panel";
import { EndpointStrip } from "@/components/dashboard/endpoint-strip";
import { InsightsChart } from "@/components/dashboard/insights-chart";
import { RecentMeetings } from "@/components/dashboard/recent-meetings";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { ErrorNote, Skeleton } from "@/components/ui/states";
import { cn } from "@/lib/format";
import { useMeetings, useQuestionCount, useSavedSummaries } from "@/lib/hooks";

function Stat({
  icon: Icon,
  label,
  value,
  unit,
  tone,
}: {
  icon: React.ElementType;
  label: string;
  value: string;
  unit?: string;
  tone: string;
}) {
  return (
    <Card>
      <CardBody className="flex items-center gap-4 py-4">
        <div className={cn("flex size-11 items-center justify-center rounded-xl", tone)}>
          <Icon className="size-5" />
        </div>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="text-2xl font-semibold tabular-nums leading-tight">
            {value}
            {unit && <span className="ml-1 text-sm font-medium text-muted-foreground">{unit}</span>}
          </p>
        </div>
      </CardBody>
    </Card>
  );
}

const ACTIONS = [
  { href: "/upload", icon: Upload, title: "Upload meeting", text: "Add one or many recordings", tone: "bg-primary-soft text-primary" },
  { href: "/ask", icon: MessageSquare, title: "Ask a question", text: "Search across your meetings", tone: "bg-success-soft text-success" },
  { href: "/meetings", icon: FileText, title: "Generate summary", text: "Pick a meeting to summarize", tone: "bg-warning-soft text-warning" },
  { href: "/action-items", icon: CheckSquare, title: "Action items", text: "Everything assigned so far", tone: "bg-danger-soft text-danger" },
];

export default function DashboardPage() {
  const { data, isPending, error } = useMeetings();
  const meetings = data?.meetings ?? [];
  const { summaries, isPending: summariesPending } = useSavedSummaries(meetings);
  const questions = useQuestionCount();

  const hours = meetings.reduce((sum, m) => sum + m.duration, 0) / 3600;
  const actionItems = summaries.reduce((sum, s) => sum + s.action_items.length, 0);

  return (
    <>
      <PageHeader
        title="Dashboard"
        description="An overview of your meetings and insights."
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

      <div className="mb-6 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {isPending ? (
          Array.from({ length: 4 }).map((_, i) => <Skeleton key={i} className="h-[82px]" />)
        ) : (
          <>
            <Stat icon={Video} label="Total Meetings" value={String(meetings.length)} tone="bg-primary-soft text-primary" />
            <Stat icon={Clock} label="Hours Indexed" value={hours.toFixed(1)} unit="hrs" tone="bg-success-soft text-success" />
            <Stat icon={MessageSquare} label="Questions Asked" value={String(questions)} tone="bg-warning-soft text-warning" />
            <Stat
              icon={Layers}
              label="Action Items"
              value={summariesPending ? "-" : String(actionItems)}
              tone="bg-danger-soft text-danger"
            />
          </>
        )}
      </div>

      <div className="mb-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <RecentMeetings meetings={meetings} loading={isPending} />
        </div>
        <Card>
          <CardHeader>
            <CardTitle>Quick actions</CardTitle>
          </CardHeader>
          <CardBody className="grid gap-3">
            {ACTIONS.map(({ href, icon: Icon, title, text, tone }) => (
              <Link
                key={title}
                href={href}
                className="flex items-center gap-3 rounded-lg border border-border p-3 transition-colors hover:border-primary/50 hover:bg-muted/60"
              >
                <span className={cn("flex size-9 shrink-0 items-center justify-center rounded-lg", tone)}>
                  <Icon className="size-4" />
                </span>
                <span className="min-w-0">
                  <span className="block text-sm font-medium">{title}</span>
                  <span className="block truncate text-xs text-muted-foreground">{text}</span>
                </span>
              </Link>
            ))}
          </CardBody>
        </Card>
      </div>

      <div className="mb-6 grid gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <InsightsChart meetings={meetings} loading={isPending} />
        </div>
        <ActivityList meetings={meetings} loading={isPending} />
      </div>

      <EndpointStrip />
      <AskPanel />
    </>
  );
}
