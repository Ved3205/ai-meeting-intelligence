"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api";
import { cn } from "@/lib/format";

export function HealthStatus() {
  const { isSuccess, isPending } = useQuery({
    queryKey: ["health"],
    queryFn: api.health,
    refetchInterval: 30_000,
  });

  const label = isPending ? "Checking" : isSuccess ? "Backend online" : "Backend offline";

  return (
    <div className="flex items-center gap-2 text-xs font-medium text-muted-foreground">
      <span className="relative flex size-2">
        {isSuccess && (
          <span className="absolute inline-flex size-full animate-ping rounded-full bg-success opacity-40" />
        )}
        <span
          className={cn(
            "relative inline-flex size-2 rounded-full",
            isPending ? "bg-warning" : isSuccess ? "bg-success" : "bg-danger",
          )}
        />
      </span>
      {label}
    </div>
  );
}
