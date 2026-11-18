"use client";

import { CheckSquare } from "lucide-react";
import Link from "next/link";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyState, ErrorNote, ListSkeleton } from "@/components/ui/states";
import { useMeetings, useSavedSummaries } from "@/lib/hooks";

export default function ActionItemsPage() {
  const { data, isPending, error } = useMeetings();
  const { summaries, isPending: loadingSummaries } = useSavedSummaries(data?.meetings ?? []);

  const rows = summaries.flatMap((s) =>
    s.action_items.map((a) => ({ ...a, meetingId: s.meeting_id, meetingTitle: s.title })),
  );
  const loading = isPending || loadingSummaries;

  return (
    <>
      <PageHeader title="Action Items" description="Collected from the summaries you have generated." />
      {error && <ErrorNote message={error.message} className="mb-4" />}
      <Card>
        {loading ? (
          <ListSkeleton rows={4} />
        ) : rows.length === 0 ? (
          <EmptyState
            icon={CheckSquare}
            title="No action items yet"
            description="Open a meeting and generate its summary. Action items found in it appear here."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-muted-foreground">
                  <th className="px-5 py-2.5 font-medium">Action</th>
                  <th className="px-3 py-2.5 font-medium">Owner</th>
                  <th className="px-3 py-2.5 font-medium">Deadline</th>
                  <th className="px-5 py-2.5 font-medium">Meeting</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {rows.map((r, i) => (
                  <tr key={i} className="align-top">
                    <td className="px-5 py-3">{r.description}</td>
                    <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">{r.owner ?? "-"}</td>
                    <td className="whitespace-nowrap px-3 py-3 text-muted-foreground">{r.deadline ?? "-"}</td>
                    <td className="px-5 py-3">
                      <Link href={`/meetings/${r.meetingId}`} className="font-medium text-primary hover:underline">
                        {r.meetingTitle}
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </>
  );
}
