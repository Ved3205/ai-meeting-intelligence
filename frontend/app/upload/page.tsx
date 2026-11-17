"use client";

import { UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { UploadRow } from "@/components/upload/upload-row";
import { PageHeader } from "@/components/ui/page-header";
import { ErrorNote } from "@/components/ui/states";
import { cn, VIDEO_EXTENSIONS, validateVideo } from "@/lib/format";

type Item = { id: number; file: File };

export default function UploadPage() {
  const [items, setItems] = useState<Item[]>([]);
  const [rejected, setRejected] = useState<string[]>([]);
  const [dragging, setDragging] = useState(false);
  const nextId = useRef(0);

  function addFiles(list: FileList | null) {
    if (!list) return;
    const accepted: Item[] = [];
    const errors: string[] = [];
    for (const file of Array.from(list)) {
      const problem = validateVideo(file);
      if (problem) errors.push(`${file.name}: ${problem}`);
      else accepted.push({ id: nextId.current++, file });
    }
    setRejected(errors);
    setItems((prev) => [...prev, ...accepted]);
  }

  function remove(id: number) {
    setItems((prev) => prev.filter((i) => i.id !== id));
  }

  function retry(id: number) {
    setItems((prev) => prev.map((i) => (i.id === id ? { ...i, id: nextId.current++ } : i)));
  }

  return (
    <>
      <PageHeader
        title="Upload"
        description="Add a meeting recording. It is transcribed and indexed so you can search it."
      />

      <label
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          addFiles(e.dataTransfer.files);
        }}
        className={cn(
          "flex cursor-pointer flex-col items-center rounded-xl border-2 border-dashed px-6 py-12 text-center transition-colors",
          dragging ? "border-primary bg-primary-soft" : "border-border bg-card hover:border-primary",
        )}
      >
        <div className="mb-3 flex size-12 items-center justify-center rounded-full bg-primary-soft text-primary">
          <UploadCloud className="size-6" />
        </div>
        <p className="text-sm font-medium">Drop videos here or click to browse</p>
        <p className="mt-1 text-xs text-muted-foreground">
          {VIDEO_EXTENSIONS.join(", ")} up to 500 MB each
        </p>
        <input
          type="file"
          multiple
          accept={VIDEO_EXTENSIONS.join(",")}
          className="sr-only"
          onChange={(e) => {
            addFiles(e.target.files);
            e.target.value = "";
          }}
        />
      </label>

      {rejected.length > 0 && (
        <div className="mt-4 space-y-2">
          {rejected.map((r) => (
            <ErrorNote key={r} message={r} />
          ))}
        </div>
      )}

      {items.length > 0 && (
        <div className="mt-6 space-y-3">
          <p className="text-xs text-muted-foreground">
            Long recordings can take a few minutes. You can leave this page open while they finish.
          </p>
          {items.map((item) => (
            <UploadRow
              key={item.id}
              file={item.file}
              onRemove={() => remove(item.id)}
              onRetry={() => retry(item.id)}
            />
          ))}
        </div>
      )}
    </>
  );
}
