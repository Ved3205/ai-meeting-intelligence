"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Circle, RefreshCw, Sparkles, User } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { CopyButton } from "@/components/ui/copy-button";
import { EmptyState, ErrorNote, Skeleton, Spinner } from "@/components/ui/states";
import { api, ApiError } from "@/lib/api";
import type { Summary } from "@/lib/types";

export function SummaryTab({ meetingId }: { meetingId: string }) {
  const queryClient = useQueryClient();
  const key = ["summary", meetingId];

  const saved = useQuery({
    queryKey: key,
    queryFn: () => api.getSummary(meetingId),
  });

  const generate = useMutation({
    mutationFn: (refresh: boolean) => api.generateSummary(meetingId, refresh),
    onSuccess: (data: Summary) => queryClient.setQueryData(key, data),
  });

  if (saved.isPending) {
    return (
      <div className="space-y-4">
        <Skeleton className="h-44" />
        <Skeleton className="h-40" />
      </div>
    );
  }

  const notGenerated = saved.error instanceof ApiError && saved.error.status === 404;
  if (saved.error && !notGenerated) return <ErrorNote message={saved.error.message} />;

  if (!saved.data) {
    return (
      <Card>
        <EmptyState
          icon={Sparkles}
          title="No summary yet"
          description="Generate a summary with the key points, keywords and action items. It is saved after the first run, so you only wait once."
          action={
            <div className="space-y-3">
              <Button onClick={() => generate.mutate(false)} disabled={generate.isPending}>
                {generate.isPending ? <Spinner /> : <Sparkles className="size-4" />}
                {generate.isPending ? "Generating, this can take a moment" : "Generate summary"}
              </Button>
              {generate.error && <ErrorNote message={generate.error.message} />}
            </div>
          }
        />
      </Card>
    );
  }

  const s = saved.data;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Summary</CardTitle>
          <div className="flex items-center gap-1">
            <CopyButton text={s.summary} />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => generate.mutate(true)}
              disabled={generate.isPending}
            >
              {generate.isPending ? <Spinner /> : <RefreshCw className="size-4" />}
              Regenerate
            </Button>
          </div>
        </CardHeader>
        <CardBody>
          <p className="whitespace-pre-wrap text-[15px] leading-7">{s.summary}</p>
          {s.keywords.length > 0 && (
            <div className="mt-5 flex flex-wrap gap-2 border-t border-border pt-4">
              {s.keywords.map((k) => (
                <Badge key={k} tone="primary">
                  {k}
                </Badge>
              ))}
            </div>
          )}
          {generate.error && <ErrorNote message={generate.error.message} className="mt-4" />}
        </CardBody>
      </Card>

      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Action items</CardTitle>
          <span className="text-xs text-muted-foreground">{s.action_items.length} found</span>
        </CardHeader>
        {s.action_items.length === 0 ? (
          <CardBody className="text-sm text-muted-foreground">No action items were found in this meeting.</CardBody>
        ) : (
          <ul className="divide-y divide-border">
            {s.action_items.map((item, i) => (
              <li key={i} className="flex items-start gap-3 px-5 py-3.5">
                <Circle className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm leading-relaxed">{item.description}</p>
                  <div className="mt-1.5 flex flex-wrap gap-2">
                    <Badge>
                      <User className="mr-1 size-3" />
                      {item.owner ?? "No owner"}
                    </Badge>
                    <Badge>{item.deadline ?? "No deadline"}</Badge>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}
