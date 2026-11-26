"use client";

import Link from "next/link";
import { assignMeeting, CATEGORY_TINTS, useCategories, type Category } from "@/lib/categories";
import { cn } from "@/lib/format";

export function CategoryBadge({ category, className }: { category: Category; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        CATEGORY_TINTS[category.color % CATEGORY_TINTS.length],
        className,
      )}
    >
      {category.name}
    </span>
  );
}

export function CategorySelect({ meetingId, className }: { meetingId: string; className?: string }) {
  const { categories, categoryOf } = useCategories();
  const current = categoryOf(meetingId);

  if (categories.length === 0) {
    return (
      <Link href="/categories" className={cn("text-xs font-medium text-primary hover:underline", className)}>
        Create a category
      </Link>
    );
  }

  return (
    <select
      value={current?.id ?? ""}
      onChange={(e) => assignMeeting(meetingId, e.target.value || null)}
      aria-label="Category"
      className={cn(
        "h-8 rounded-lg border border-border bg-card px-2 text-xs outline-none focus:border-primary",
        className,
      )}
    >
      <option value="">Uncategorized</option>
      {categories.map((c) => (
        <option key={c.id} value={c.id}>
          {c.name}
        </option>
      ))}
    </select>
  );
}
