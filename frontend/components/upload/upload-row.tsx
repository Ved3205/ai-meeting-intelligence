"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, FileVideo, RotateCcw, X, XCircle } from "lucide-react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Spinner } from "@/components/ui/states";
import { api } from "@/lib/api";
import { beep } from "@/lib/beep";
import { cn, formatSize } from "@/lib/format";
import type { Job } from "@/lib/types";

const STEPS = ["Upload", "Audio", "Transcribe", "Chunk", "Embed", "Index"];

const STAGE_INDEX: Record<string, number> = {
  extracting_audio: 1,
  transcribing: 2,
  chunking: 3,
  embedding: 4,
  indexing: 5,
};

const STAGE_TEXT: Record<string, string> = {
  extracting_audio: "Extracting audio",
  transcribing: "Transcribing speech",
  chunking: "Splitting the transcript",
  embedding: "Creating embeddings",
  indexing: "Saving to the index",
};

function activeStep(job: Job | undefined) {
  if (!job) return 0;
  if (job.status === "completed") return STEPS.length;
  if (job.status === "processing" && job.stage) return STAGE_INDEX[job.stage] ?? 1;
  return 0;
}

function statusText(job: Job | undefined, uploadError: string | null) {
  if (uploadError) return "Upload failed";
  if (!job) return "Uploading file";
  if (job.status === "queued") return "Waiting for earlier uploads";
  if (job.status === "processing") return STAGE_TEXT[job.stage ?? ""] ?? "Processing";
  if (job.status === "completed") return "Ready";
  return "Processing failed";
}

export function UploadRow({
  file,
  onRemove,
  onRetry,
}: {
  file: File;
  onRemove: () => void;
  onRetry: () => void;
}) {
  const queryClient = useQueryClient();
  const [jobId, setJobId] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;
    api
      .startUpload(file)
      .then((job) => setJobId(job.job_id))
      .catch((err: Error) => setUploadError(err.message));
  }, [file]);

  const { data: job } = useQuery({
    queryKey: ["upload", jobId],
    queryFn: () => api.getUpload(jobId!),
    enabled: !!jobId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === "completed" || status === "failed" ? false : 2500;
    },
  });

  const done = job?.status === "completed";
  const failed = !!uploadError || job?.status === "failed";
  const step = activeStep(job);

  useEffect(() => {
    if (done) {
      queryClient.invalidateQueries({ queryKey: ["meetings"] });
      beep(880);
    }
  }, [done, queryClient]);

  useEffect(() => {
    if (failed) beep(330, 260);
  }, [failed]);

  const errors = uploadError ? [uploadError] : (job?.errors ?? []);

  return (
    <Card className="p-4">
      <div className="flex items-start gap-3">
        <div className="flex size-10 shrink-0 items-center justify-center rounded-lg bg-primary-soft text-primary">
          <FileVideo className="size-5" />
        </div>

        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <p className="truncate text-sm font-medium">{file.name}</p>
            <span className="text-xs text-muted-foreground">{formatSize(file.size)}</span>
          </div>

          <div className="mt-1.5 flex items-center gap-2 text-sm">
            {done ? (
              <CheckCircle2 className="size-4 text-success" />
            ) : failed ? (
              <XCircle className="size-4 text-danger" />
            ) : (
              <Spinner className="text-primary" />
            )}
            <span className={cn(failed && "text-danger")}>{statusText(job, uploadError)}</span>
          </div>

          <div className="mt-3 grid grid-cols-6 gap-1.5" aria-hidden>
            {STEPS.map((label, i) => (
              <div key={label}>
                <div
                  className={cn(
                    "h-1.5 rounded-full",
                    failed && i === step
                      ? "bg-danger"
                      : i < step
                        ? "bg-primary"
                        : i === step && !done
                          ? "animate-pulse bg-primary/50"
                          : "bg-muted",
                  )}
                />
                <p className="mt-1 hidden text-[11px] text-muted-foreground sm:block">{label}</p>
              </div>
            ))}
          </div>

          {failed && errors.length > 0 && (
            <ul className="mt-3 space-y-1 text-sm text-danger">
              {errors.map((e, i) => (
                <li key={i}>{e}</li>
              ))}
            </ul>
          )}

          {done && (
            <div className="mt-3 flex flex-wrap items-center gap-3">
              <Badge tone="success">{job.total_chunks} chunks indexed</Badge>
              {job.meeting_id && (
                <Link
                  href={`/meeting?id=${job.meeting_id}`}
                  className="text-sm font-medium text-primary hover:underline"
                >
                  Open meeting
                </Link>
              )}
            </div>
          )}
        </div>

        <div className="flex shrink-0 gap-1">
          {failed && (
            <Button variant="ghost" size="sm" onClick={onRetry} aria-label="Try again">
              <RotateCcw className="size-4" />
            </Button>
          )}
          {(done || failed) && (
            <Button variant="ghost" size="sm" onClick={onRemove} aria-label="Remove">
              <X className="size-4" />
            </Button>
          )}
        </div>
      </div>
    </Card>
  );
}
