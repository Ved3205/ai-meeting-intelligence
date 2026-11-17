import { cn } from "@/lib/format";

const TINTS = [
  "bg-indigo-100 text-indigo-700 dark:bg-indigo-950 dark:text-indigo-300",
  "bg-sky-100 text-sky-700 dark:bg-sky-950 dark:text-sky-300",
  "bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  "bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
  "bg-rose-100 text-rose-700 dark:bg-rose-950 dark:text-rose-300",
  "bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300",
];

function hash(value: string) {
  let h = 0;
  for (const ch of value) h = (h * 31 + ch.charCodeAt(0)) >>> 0;
  return h;
}

export function MeetingTile({
  id,
  title,
  size = "md",
}: {
  id: string;
  title: string | null;
  size?: "md" | "lg";
}) {
  const letter = (title ?? "M").trim().charAt(0).toUpperCase() || "M";
  return (
    <div
      className={cn(
        "flex shrink-0 items-center justify-center font-semibold",
        size === "lg" ? "size-14 rounded-xl text-xl" : "size-10 rounded-lg text-sm",
        TINTS[hash(id) % TINTS.length],
      )}
    >
      {letter}
    </div>
  );
}
