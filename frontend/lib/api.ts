import type { Job, Meeting, MeetingList, QueryAnswer, Summary, Transcript } from "./types";

export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_URL}${path}`, init);
  } catch {
    throw new ApiError(0, "Cannot reach the server. Is the backend running?");
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // keep the default message
    }
    throw new ApiError(res.status, message);
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const api = {
  health: () => request<{ status: string }>("/health"),

  listMeetings: () => request<MeetingList>("/api/v1/meetings"),
  getMeeting: (id: string) => request<Meeting>(`/api/v1/meetings/${id}`),
  getTranscript: (id: string) => request<Transcript>(`/api/v1/meetings/${id}/transcript`),
  deleteMeeting: (id: string) => request<void>(`/api/v1/meetings/${id}`, { method: "DELETE" }),

  getSummary: (id: string) => request<Summary>(`/api/v1/meetings/${id}/summary`),
  generateSummary: (id: string, refresh = false) =>
    request<Summary>(`/api/v1/meetings/${id}/summary?refresh=${refresh}`, { method: "POST" }),

  startUpload: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<Job>("/api/v1/uploads", { method: "POST", body: form });
  },
  getUpload: (jobId: string) => request<Job>(`/api/v1/uploads/${jobId}`),

  ask: (question: string, meetingId?: string) =>
    request<QueryAnswer>(
      meetingId ? `/api/v1/meetings/${meetingId}/query` : "/api/v1/query",
      json({ question }),
    ),
};
