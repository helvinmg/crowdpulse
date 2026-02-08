"use client";

import { Activity } from "lucide-react";

export default function Header() {
  return (
    <header className="flex items-center gap-3 pb-4 border-b border-[var(--card-border)]">
      <Activity className="w-8 h-8 text-brand-500" />
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Crowd Pulse</h1>
        <p className="text-sm text-[var(--muted)]">
          Hinglish sentiment analysis &amp; contrarian signals — Nifty 50
        </p>
      </div>
    </header>
  );
}
