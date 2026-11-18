import { Card, CardBody } from "@/components/ui/card";
import { cn } from "@/lib/format";

const ENDPOINTS = [
  { method: "POST", path: "/api/v1/uploads", text: "Upload and index a meeting" },
  { method: "POST", path: "/api/v1/query", text: "Ask across all meetings" },
  { method: "POST", path: "/api/v1/meetings/{id}/summary", text: "Generate a summary" },
  { method: "GET", path: "/api/v1/meetings", text: "List indexed meetings" },
];

export function EndpointStrip() {
  return (
    <Card>
      <CardBody>
        <p className="mb-3 text-sm font-semibold">API endpoints powering this app</p>
        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
          {ENDPOINTS.map((e) => (
            <div key={e.path} className="min-w-0 rounded-lg border border-border bg-muted/50 p-3">
              <div className="flex items-center gap-2">
                <span
                  className={cn(
                    "rounded px-1.5 py-0.5 text-[10px] font-bold",
                    e.method === "GET" ? "bg-muted text-muted-foreground" : "bg-primary-soft text-primary",
                  )}
                >
                  {e.method}
                </span>
                <code className="truncate text-xs font-medium">{e.path}</code>
              </div>
              <p className="mt-1.5 text-xs text-muted-foreground">{e.text}</p>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
