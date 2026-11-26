"use client";

import { Check, Pencil, Tag, Trash2, X } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { CategoryBadge } from "@/components/meetings/category-controls";
import { Button } from "@/components/ui/button";
import { Card, CardBody, CardHeader, CardTitle } from "@/components/ui/card";
import { PageHeader } from "@/components/ui/page-header";
import { EmptyState } from "@/components/ui/states";
import {
  CATEGORY_TINTS,
  createCategory,
  deleteCategory,
  renameCategory,
  useCategories,
  type Category,
} from "@/lib/categories";
import { cn } from "@/lib/format";

function Swatches({ value, onChange }: { value: number; onChange: (n: number) => void }) {
  return (
    <div className="flex gap-1.5" role="radiogroup" aria-label="Colour">
      {CATEGORY_TINTS.map((tint, i) => (
        <button
          key={i}
          type="button"
          role="radio"
          aria-checked={value === i}
          aria-label={`Colour ${i + 1}`}
          onClick={() => onChange(i)}
          className={cn(
            "flex size-7 items-center justify-center rounded-full",
            tint,
            value === i && "ring-2 ring-primary ring-offset-2 ring-offset-card",
          )}
        >
          {value === i && <Check className="size-3.5" />}
        </button>
      ))}
    </div>
  );
}

function CategoryRow({ category, count }: { category: Category; count: number }) {
  const [editing, setEditing] = useState(false);
  const [name, setName] = useState(category.name);
  const [confirm, setConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function save() {
    const problem = renameCategory(category.id, name);
    setError(problem);
    if (!problem) setEditing(false);
  }

  return (
    <li className="flex flex-wrap items-center gap-3 px-5 py-3.5">
      <div className="min-w-0 flex-1">
        {editing ? (
          <div>
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && save()}
              aria-label="Category name"
              className="h-9 w-full max-w-xs rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-primary"
            />
            {error && <p className="mt-1 text-xs text-danger">{error}</p>}
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <CategoryBadge category={category} />
            <Link
              href={`/meetings?category=${category.id}`}
              className="text-sm text-muted-foreground hover:text-primary hover:underline"
            >
              {count} {count === 1 ? "meeting" : "meetings"}
            </Link>
          </div>
        )}
      </div>

      {editing ? (
        <div className="flex gap-2">
          <Button size="sm" onClick={save}>
            Save
          </Button>
          <Button
            size="sm"
            variant="secondary"
            onClick={() => {
              setEditing(false);
              setName(category.name);
              setError(null);
            }}
          >
            Cancel
          </Button>
        </div>
      ) : confirm ? (
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Delete? Meetings stay, just uncategorized.</span>
          <Button size="sm" variant="danger" onClick={() => deleteCategory(category.id)}>
            Delete
          </Button>
          <Button size="sm" variant="secondary" onClick={() => setConfirm(false)}>
            <X className="size-4" />
            <span className="sr-only">Cancel</span>
          </Button>
        </div>
      ) : (
        <div className="flex gap-1">
          <Button size="sm" variant="ghost" onClick={() => setEditing(true)} aria-label={`Rename ${category.name}`}>
            <Pencil className="size-4" />
          </Button>
          <Button size="sm" variant="ghost" onClick={() => setConfirm(true)} aria-label={`Delete ${category.name}`}>
            <Trash2 className="size-4" />
          </Button>
        </div>
      )}
    </li>
  );
}

export default function CategoriesPage() {
  const { categories, countIn } = useCategories();
  const [name, setName] = useState("");
  const [color, setColor] = useState(0);
  const [error, setError] = useState<string | null>(null);

  function add(e: React.FormEvent) {
    e.preventDefault();
    const problem = createCategory(name, color);
    setError(problem);
    if (!problem) {
      setName("");
      setColor((color + 1) % CATEGORY_TINTS.length);
    }
  }

  return (
    <>
      <PageHeader
        title="Categories"
        description="Group meetings by team or topic, such as HR, Marketing or Engineering."
      />

      <Card className="mb-6">
        <CardBody>
          <form onSubmit={add} className="flex flex-wrap items-end gap-4">
            <div className="min-w-[14rem] flex-1">
              <label htmlFor="cat-name" className="mb-1.5 block text-sm font-medium">
                New category
              </label>
              <input
                id="cat-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. HR"
                maxLength={40}
                className="h-10 w-full rounded-lg border border-border bg-background px-3 text-sm outline-none focus:border-primary"
              />
            </div>
            <Swatches value={color} onChange={setColor} />
            <Button type="submit">Create</Button>
          </form>
          {error && <p className="mt-2 text-sm text-danger">{error}</p>}
        </CardBody>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Your categories</CardTitle>
        </CardHeader>
        {categories.length === 0 ? (
          <EmptyState
            icon={Tag}
            title="No categories yet"
            description="Create one above, then assign meetings to it from the meetings list or a meeting page."
          />
        ) : (
          <ul className="divide-y divide-border">
            {categories.map((c) => (
              <CategoryRow key={c.id} category={c} count={countIn(c.id)} />
            ))}
          </ul>
        )}
      </Card>
      <p className="mt-3 text-xs text-muted-foreground">
        Categories are saved in this browser for now, so they are not shared with other people or devices.
      </p>
    </>
  );
}
