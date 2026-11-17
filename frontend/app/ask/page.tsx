"use client";

import { useSearchParams } from "next/navigation";
import { Suspense } from "react";
import { Chat } from "@/components/chat/chat";
import { Card } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";

function AskView() {
  const question = useSearchParams().get("q") ?? undefined;
  return (
    <Card className="h-[calc(100vh-15rem)] min-h-[28rem] overflow-hidden">
      <Chat initialQuestion={question} />
    </Card>
  );
}

export default function AskPage() {
  return (
    <>
      <PageHeader title="Ask AI" description="Ask a question across all of your meetings." />
      <Suspense>
        <AskView />
      </Suspense>
    </>
  );
}
