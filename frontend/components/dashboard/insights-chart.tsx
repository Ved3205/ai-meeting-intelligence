"use client";

import { BarChart3 } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { EmptyState, Skeleton } from "@/components/ui/states";
import type { Meeting } from "@/lib/types";

const DAYS = 14;

function dayKey(d: Date) {
  return `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}`;
}

// hours of recording indexed on each of the last 14 days
function buildSeries(meetings: Meeting[]) {
  const today = new Date();
  const days = Array.from({ length: DAYS }, (_, i) => {
    const d = new Date(today);
    d.setDate(today.getDate() - (DAYS - 1 - i));
    return {
      key: dayKey(d),
      label: d.toLocaleDateString(undefined, { day: "numeric", month: "short" }),
      hours: 0,
    };
  });
  const byKey = new Map(days.map((d) => [d.key, d]));
  for (const m of meetings) {
    if (!m.uploaded_at) continue;
    const slot = byKey.get(dayKey(new Date(m.uploaded_at)));
    if (slot) slot.hours += m.duration / 3600;
  }
  return days.map((d) => ({ label: d.label, hours: Number(d.hours.toFixed(2)) }));
}

const tick = { fontSize: 11, fill: "var(--muted-foreground)" };

export function InsightsChart({ meetings, loading }: { meetings: Meeting[]; loading: boolean }) {
  const series = buildSeries(meetings);
  const hasData = series.some((p) => p.hours > 0);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Meeting insights</CardTitle>
        <p className="mt-0.5 text-xs text-muted-foreground">Hours indexed, last {DAYS} days</p>
      </CardHeader>
      <CardBody>
        {loading ? (
          <Skeleton className="h-60" />
        ) : !hasData ? (
          <EmptyState
            icon={BarChart3}
            title="Nothing indexed recently"
            description="Meetings you upload will show up here."
          />
        ) : (
          <div className="h-60" role="img" aria-label="Hours of meetings indexed per day">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={series} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="hoursFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--primary)" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="var(--primary)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid vertical={false} stroke="var(--border)" />
                <XAxis dataKey="label" tickLine={false} axisLine={false} tick={tick} interval="preserveStartEnd" />
                <YAxis tickLine={false} axisLine={false} tick={tick} allowDecimals />
                <Tooltip
                  formatter={(v) => [`${v} hrs`, "Indexed"]}
                  contentStyle={{
                    background: "var(--card)",
                    border: "1px solid var(--border)",
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                />
                <Area type="monotone" dataKey="hours" stroke="var(--primary)" strokeWidth={2} fill="url(#hoursFill)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardBody>
    </Card>
  );
}
