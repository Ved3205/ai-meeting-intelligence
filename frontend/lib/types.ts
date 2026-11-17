export type Meeting = {
  meeting_id: string;
  title: string | null;
  filename: string | null;
  language: string | null;
  total_chunks: number;
  duration: number;
  uploaded_at: string | null;
};

export type MeetingList = { total: number; meetings: Meeting[] };

export type TranscriptSegment = {
  chunk_index: number;
  start_time: number;
  end_time: number;
  text: string;
};

export type Transcript = { meeting_id: string; segments: TranscriptSegment[] };

export type ActionItem = {
  description: string;
  owner: string | null;
  deadline: string | null;
};

export type Summary = {
  meeting_id: string;
  title: string;
  summary: string;
  keywords: string[];
  action_items: ActionItem[];
  chunk_count: number;
  elapsed_time: number;
};

export type SourceChunk = {
  chunk_id: string;
  meeting_id: string;
  chunk_index: number;
  text: string;
  start_time: number;
  end_time: number;
  duration: number;
  keywords: string[];
  title: string | null;
  filename: string | null;
};

export type QueryAnswer = {
  meeting_id: string | null;
  answer: string;
  confidence: number;
  retrieved_chunks: SourceChunk[];
};

export type JobStatus = "queued" | "processing" | "completed" | "failed";

export type Job = {
  job_id: string;
  status: JobStatus;
  stage: string | null;
  filename: string;
  meeting_id: string | null;
  title: string | null;
  total_chunks: number;
  elapsed_time: number;
  errors: string[];
  warnings: string[];
  created_at: string;
};
