import { useQueries, useQuery } from "@tanstack/react-query";
import { useSyncExternalStore } from "react";
import { api, ApiError } from "./api";
import type { Meeting, Summary } from "./types";

export function useMeetings() {
  return useQuery({ queryKey: ["meetings"], queryFn: api.listMeetings });
}

// summaries that were already generated, meetings without one are skipped
export function useSavedSummaries(meetings: Meeting[]) {
  const results = useQueries({
    queries: meetings.map((m) => ({
      queryKey: ["summary", m.meeting_id],
      queryFn: async () => {
        try {
          return await api.getSummary(m.meeting_id);
        } catch (e) {
          if (e instanceof ApiError && e.status === 404) return null;
          throw e;
        }
      },
      retry: false,
    })),
  });
  const summaries = results.map((r) => r.data).filter((s): s is Summary => !!s);
  return { summaries, isPending: results.some((r) => r.isPending) };
}

const ASKED_KEY = "mi.questions";
const ASKED_EVENT = "mi:questions";

function readAsked() {
  try {
    return Number(localStorage.getItem(ASKED_KEY) ?? 0) || 0;
  } catch {
    return 0;
  }
}

export function countQuestion() {
  try {
    localStorage.setItem(ASKED_KEY, String(readAsked() + 1));
    window.dispatchEvent(new Event(ASKED_EVENT));
  } catch {
    // storage unavailable, counter just stays put
  }
}

function subscribeAsked(cb: () => void) {
  window.addEventListener(ASKED_EVENT, cb);
  window.addEventListener("storage", cb);
  return () => {
    window.removeEventListener(ASKED_EVENT, cb);
    window.removeEventListener("storage", cb);
  };
}

export function useQuestionCount() {
  return useSyncExternalStore(subscribeAsked, readAsked, () => 0);
}
