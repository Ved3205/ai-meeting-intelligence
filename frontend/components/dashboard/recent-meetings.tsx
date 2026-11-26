import { Upload, Video } from "lucide-react";
import Link from "next/link";
import { CategoryBadge } from "@/components/meetings/category-controls";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, ListSkeleton } from "@/components/ui/states";
import { useCategories } from "@/lib/categories";
import { formatDate, formatDuration } from "@/lib/format";
import type { Meeting } from "@/lib/types";

export function RecentMeetings({ meetings, loading }: { meetings: Meeting[]; loading: boolean }) {
  const { categoryOf } = useCategories();
  const recent = [...meetings]
    .sort((a, b) => (b.uploaded_at ?? "").localeCompare(a.uploaded_at ?? ""))
    .slice(0, 5);

  return (
    <Card className="h-full">
      <CardHeader className="flex items-center justify-between">
        <CardTitle>Recent meetings</CardTitle>
        {meetings.length > 0 && (
          <Link href="/meetings" className="text-sm font-medium text-primary hover:underline">
            View all
          </Link>
        )}
      </CardHeader>
      {loading ? (
        <ListSkeleton rows={4} />
      ) : recent.length === 0 ? (
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
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-border text-left text-xs text-muted-foreground">
                <th className="px-5 py-2.5 font-medium">Meeting</th>
                <th className="px-3 py-2.5 font-medium">Date</th>
                <th className="px-3 py-2.5 font-medium">Duration</th>
                <th className="px-3 py-2.5 font-medium">Category</th>
                <th className="px-5 py-2.5 font-medium">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {recent.map((m) => (
                <tr key={m.meeting_id} className="transition-colors hover:bg-muted/60">
                  <td className="max-w-[16rem] px-5 py-3">
                    <Link href={`/meeting?id=${m.meeting_id}`} className="block truncate font-medium hover:text-primary">
                      {m.title ?? "Untitled meeting"}
                    </Link>
                  </td>
                  <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">{formatDate(m.uploaded_at)}</td>
                  <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">{formatDuration(m.duration)}</td>
                  <td className="px-3 py-3">
                    {categoryOf(m.meeting_id) ? (
                      <CategoryBadge category={categoryOf(m.meeting_id)!} />
                    ) : (
                      <span className="text-muted-foreground">-</span>
                    )}
                  </td>
                  <td className="px-5 py-3">
                    <Badge tone="success">Indexed</Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </Card>
  );
}
