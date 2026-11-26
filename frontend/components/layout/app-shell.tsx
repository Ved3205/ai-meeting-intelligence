"use client";

import {
  BookOpen,
  CheckSquare,
  LayoutDashboard,
  MessageSquare,
  Mic,
  Search,
  Tag,
  Upload,
  Video,
} from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { API_URL } from "@/lib/api";
import { cn } from "@/lib/format";
import { HealthStatus } from "./health-status";
import { ThemeToggle } from "./theme-toggle";

type NavItem = { href: string; label: string; icon: React.ElementType; external?: boolean };

const groups: { label?: string; items: NavItem[] }[] = [
  { items: [{ href: "/", label: "Dashboard", icon: LayoutDashboard }] },
  {
    label: "Meetings",
    items: [
      { href: "/meetings", label: "All Meetings", icon: Video },
      { href: "/categories", label: "Categories", icon: Tag },
      { href: "/upload", label: "Upload & Index", icon: Upload },
    ],
  },
  {
    label: "Intelligence",
    items: [
      { href: "/ask", label: "Ask a Question", icon: MessageSquare },
      { href: "/action-items", label: "Action Items", icon: CheckSquare },
    ],
  },
  {
    label: "Developers",
    items: [{ href: `${API_URL}/docs`, label: "API Docs", icon: BookOpen, external: true }],
  },
];

const allItems = groups.flatMap((g) => g.items);
const internalItems = allItems.filter((i) => !i.external);

// longest matching path wins, so /meetings/abc still highlights All Meetings
function activeHref(pathname: string) {
  const hits = internalItems.filter((i) => (i.href === "/" ? pathname === "/" : pathname.startsWith(i.href)));
  return hits.sort((a, b) => b.href.length - a.href.length)[0]?.href ?? "";
}

function Brand() {
  return (
    <Link href="/" className="flex items-center gap-2.5 whitespace-nowrap text-[15px] font-semibold text-white">
      <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-white">
        <Mic className="size-4" />
      </span>
      Meeting Intelligence
    </Link>
  );
}

function SearchBox() {
  const router = useRouter();
  const [term, setTerm] = useState("");

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        document.getElementById("global-search")?.focus();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, []);

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        router.push(term.trim() ? `/meetings?q=${encodeURIComponent(term.trim())}` : "/meetings");
      }}
      className="relative w-full max-w-md"
    >
      <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <input
        id="global-search"
        value={term}
        onChange={(e) => setTerm(e.target.value)}
        placeholder="Search meetings"
        aria-label="Search meetings"
        className="h-9 w-full rounded-lg border border-border bg-card pl-9 pr-14 text-sm outline-none transition-colors focus:border-primary"
      />
      <kbd className="pointer-events-none absolute right-2 top-1/2 hidden -translate-y-1/2 rounded border border-border bg-muted px-1.5 py-0.5 text-[11px] font-medium text-muted-foreground sm:block">
        Ctrl K
      </kbd>
    </form>
  );
}

function NavLink({ item, active }: { item: NavItem; active: boolean }) {
  const { href, label, icon: Icon, external } = item;
  const cls = cn(
    "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
    active ? "bg-primary text-white" : "text-slate-400 hover:bg-white/5 hover:text-white",
  );
  if (external) {
    return (
      <a href={href} target="_blank" rel="noreferrer" className={cls}>
        <Icon className="size-4" />
        {label}
      </a>
    );
  }
  return (
    <Link href={href} className={cls} aria-current={active ? "page" : undefined}>
      <Icon className="size-4" />
      {label}
    </Link>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const current = activeHref(pathname);

  return (
    <div className="min-h-screen md:flex">
      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col bg-sidebar p-4 md:flex">
        <div className="px-2 py-2">
          <Brand />
        </div>
        <nav className="mt-6 flex flex-1 flex-col gap-5 overflow-y-auto">
          {groups.map((g, i) => (
            <div key={i}>
              {g.label && (
                <p className="mb-1.5 px-3 text-[11px] font-medium uppercase tracking-wider text-slate-500">
                  {g.label}
                </p>
              )}
              <div className="flex flex-col gap-0.5">
                {g.items.map((item) => (
                  <NavLink key={item.href} item={item} active={item.href === current} />
                ))}
              </div>
            </div>
          ))}
        </nav>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-10 border-b border-border bg-background/90 backdrop-blur">
          <div className="flex h-14 items-center gap-3 px-4 md:px-8">
            <Link href="/" className="md:hidden" aria-label="Home">
              <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-white">
                <Mic className="size-4" />
              </span>
            </Link>
            <SearchBox />
            <div className="ml-auto flex shrink-0 items-center gap-3">
              <div className="hidden rounded-full border border-border bg-card px-3 py-1.5 sm:block">
                <HealthStatus />
              </div>
              <ThemeToggle />
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-3 pb-2 md:hidden">
            {internalItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex shrink-0 items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium",
                  item.href === current ? "bg-primary-soft text-primary" : "text-muted-foreground",
                )}
              >
                <item.icon className="size-4" />
                {item.label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto w-full max-w-6xl px-4 py-8 md:px-8">
          <div key={pathname} className="page-enter">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
