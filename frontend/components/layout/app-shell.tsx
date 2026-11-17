"use client";

import { ExternalLink, LayoutDashboard, MessageSquare, Mic, Search, Upload, Video } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import { API_URL } from "@/lib/api";
import { cn } from "@/lib/format";
import { HealthStatus } from "./health-status";
import { ThemeToggle } from "./theme-toggle";

const nav = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/upload", label: "Upload", icon: Upload },
  { href: "/meetings", label: "Meetings", icon: Video },
  { href: "/ask", label: "Ask AI", icon: MessageSquare },
];

function isActive(pathname: string, href: string) {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

function Brand() {
  return (
    <Link href="/" className="flex items-center gap-2.5 whitespace-nowrap text-sm font-semibold">
      <span className="flex size-8 items-center justify-center rounded-lg bg-primary text-white shadow-card">
        <Mic className="size-4" />
      </span>
      Meeting Intelligence
    </Link>
  );
}

function AskTrigger() {
  const router = useRouter();

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        router.push("/ask");
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [router]);

  return (
    <Link
      href="/ask"
      className="flex h-9 w-full max-w-sm items-center gap-2 rounded-lg border border-border bg-card px-3 text-sm text-muted-foreground shadow-card transition-colors hover:border-primary/50"
    >
      <Search className="size-4" />
      <span className="flex-1 truncate">Ask about your meetings</span>
      <kbd className="hidden rounded border border-border bg-muted px-1.5 py-0.5 text-[11px] font-medium sm:block">
        Ctrl K
      </kbd>
    </Link>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen md:flex">
      <aside className="sticky top-0 hidden h-screen w-60 shrink-0 flex-col border-r border-border p-4 md:flex">
        <div className="px-2 py-2">
          <Brand />
        </div>
        <p className="mb-2 mt-7 px-3 text-[11px] font-medium uppercase tracking-wider text-muted-foreground">
          Menu
        </p>
        <nav className="flex flex-col gap-0.5">
          {nav.map(({ href, label, icon: Icon }) => {
            const active = isActive(pathname, href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                  active
                    ? "bg-card text-foreground shadow-card ring-1 ring-border"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
              >
                <Icon className={cn("size-4", active && "text-primary")} />
                {label}
              </Link>
            );
          })}
        </nav>
        <a
          href={`${API_URL}/docs`}
          target="_blank"
          rel="noreferrer"
          className="mt-auto flex items-center gap-2 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-muted hover:text-foreground"
        >
          <ExternalLink className="size-4" />
          API docs
        </a>
      </aside>

      <div className="min-w-0 flex-1">
        <header className="sticky top-0 z-10 border-b border-border bg-background/85 backdrop-blur">
          <div className="flex h-14 items-center gap-3 px-4 md:px-8">
            <div className="md:hidden">
              <Brand />
            </div>
            <div className="ml-auto flex items-center justify-end gap-3 md:ml-0 md:w-full md:justify-between">
              <div className="hidden w-full md:block">
                <AskTrigger />
              </div>
              <div className="flex shrink-0 items-center gap-3">
                <div className="hidden rounded-full border border-border bg-card px-3 py-1.5 sm:block">
                  <HealthStatus />
                </div>
                <ThemeToggle />
              </div>
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-3 pb-2 md:hidden">
            {nav.map(({ href, label, icon: Icon }) => (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex shrink-0 items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium",
                  isActive(pathname, href)
                    ? "bg-primary-soft text-primary"
                    : "text-muted-foreground",
                )}
              >
                <Icon className="size-4" />
                {label}
              </Link>
            ))}
          </nav>
        </header>
        <main className="mx-auto w-full max-w-5xl px-4 py-8 md:px-8">
          <div key={pathname} className="page-enter">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}
