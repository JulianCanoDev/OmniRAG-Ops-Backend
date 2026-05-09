"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { useAuth } from "@/contexts/auth-context";
import {
  LayoutDashboard,
  Database,
  Upload,
  LogOut,
  Brain,
} from "lucide-react";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/collections", label: "Collections", icon: Database },
  { href: "/ingest", label: "Ingest", icon: Upload },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuth();

  if (pathname === "/login") return null;

  return (
    <aside className="flex h-screen w-64 flex-col border-r border-border bg-sidebar-background">
      <div className="flex items-center gap-2 border-b border-border px-6 py-5">
        <Brain className="h-6 w-6 text-primary" />
        <span className="text-lg font-semibold tracking-tight">
          OmniRAG-Ops
        </span>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-sidebar-accent text-sidebar-accent-foreground"
                  : "text-sidebar-foreground hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border p-4">
        {user && (
          <p className="mb-2 truncate text-xs text-sidebar-foreground/60">
            {user.email}
          </p>
        )}
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-sm"
          onClick={logout}
        >
          <LogOut className="h-4 w-4" />
          Sign Out
        </Button>
      </div>
    </aside>
  );
}
