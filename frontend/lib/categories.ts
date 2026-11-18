import { useSyncExternalStore } from "react";

export type Category = { id: string; name: string; color: number };

type State = { categories: Category[]; assignments: Record<string, string> };

// tints reused by badges and the colour picker
export const CATEGORY_TINTS = [
  "bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300",
  "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300",
  "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  "bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300",
];

const KEY = "mi.categories";
const EVENT = "mi:categories";
const EMPTY: State = { categories: [], assignments: {} };

// the backend has no category field yet, so this lives in the browser
let lastRaw: string | null = null;
let lastState: State = EMPTY;

function read(): State {
  let raw: string | null = null;
  try {
    raw = localStorage.getItem(KEY);
  } catch {
    return lastState;
  }
  if (raw === lastRaw) return lastState;
  lastRaw = raw;
  try {
    const parsed = raw ? JSON.parse(raw) : null;
    lastState = parsed?.categories ? parsed : EMPTY;
  } catch {
    lastState = EMPTY;
  }
  return lastState;
}

function write(next: State) {
  try {
    localStorage.setItem(KEY, JSON.stringify(next));
  } catch {
    // storage blocked, the change is lost on reload
    lastState = next;
  }
  window.dispatchEvent(new Event(EVENT));
}

function subscribe(cb: () => void) {
  window.addEventListener(EVENT, cb);
  window.addEventListener("storage", cb);
  return () => {
    window.removeEventListener(EVENT, cb);
    window.removeEventListener("storage", cb);
  };
}

export function useCategoryState() {
  return useSyncExternalStore(subscribe, read, () => EMPTY);
}

export function useCategories() {
  const state = useCategoryState();
  const byId = new Map(state.categories.map((c) => [c.id, c]));
  return {
    categories: state.categories,
    categoryOf: (meetingId: string) => {
      const id = state.assignments[meetingId];
      return id ? byId.get(id) : undefined;
    },
    countIn: (categoryId: string) =>
      Object.values(state.assignments).filter((id) => id === categoryId).length,
  };
}

export function createCategory(name: string, color: number): string | null {
  const clean = name.trim();
  if (!clean) return "Enter a name";
  const state = read();
  if (state.categories.some((c) => c.name.toLowerCase() === clean.toLowerCase())) {
    return "A category with this name already exists";
  }
  const id = `c${Date.now().toString(36)}`;
  write({ ...state, categories: [...state.categories, { id, name: clean, color }] });
  return null;
}

export function renameCategory(id: string, name: string): string | null {
  const clean = name.trim();
  if (!clean) return "Enter a name";
  const state = read();
  if (state.categories.some((c) => c.id !== id && c.name.toLowerCase() === clean.toLowerCase())) {
    return "A category with this name already exists";
  }
  write({ ...state, categories: state.categories.map((c) => (c.id === id ? { ...c, name: clean } : c)) });
  return null;
}

export function deleteCategory(id: string) {
  const state = read();
  const assignments = Object.fromEntries(Object.entries(state.assignments).filter(([, c]) => c !== id));
  write({ categories: state.categories.filter((c) => c.id !== id), assignments });
}

export function assignMeeting(meetingId: string, categoryId: string | null) {
  const state = read();
  const assignments = { ...state.assignments };
  if (categoryId) assignments[meetingId] = categoryId;
  else delete assignments[meetingId];
  write({ ...state, assignments });
}
