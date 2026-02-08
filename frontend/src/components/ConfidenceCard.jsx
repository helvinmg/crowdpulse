"use client";

import { useEffect, useState } from "react";
import { ShieldCheck } from "lucide-react";
import { getDivergenceLatest } from "@/lib/api";
import { cn, confidenceLabel, directionColor, directionBg } from "@/lib/utils";

export default function ConfidenceCard({ symbol }) {
  const [signal, setSignal] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    getDivergenceLatest(symbol)
      .then((res) => setSignal(res.signal))
      .catch(() => setSignal(null))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) {
    return (
      <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4 animate-pulse h-24 w-full md:w-72" />
    );
  }

  if (!signal) {
    return (
      <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4 text-sm text-[var(--muted)] w-full md:w-72">
        No signal data for {symbol}
      </div>
    );
  }

  const conf = signal.confidence_score ?? 0;
  const dir = signal.divergence_direction ?? "neutral";

  return (
    <div
      className={cn(
        "rounded-lg border p-4 w-full md:w-72 space-y-2",
        directionBg(dir)
      )}
    >
      <div className="flex items-center gap-2 text-sm font-medium">
        <ShieldCheck className="w-4 h-4" />
        <span>Confidence: {confidenceLabel(conf)} ({(conf * 100).toFixed(0)}%)</span>
      </div>
      <div className="flex items-center gap-2 text-xs">
        <span className="text-[var(--muted)]">Direction:</span>
        <span className={cn("font-semibold uppercase", directionColor(dir))}>
          {dir}
        </span>
      </div>
      <div className="text-xs text-[var(--muted)]">
        Volume: {signal.discussion_volume ?? "—"} posts
      </div>
    </div>
  );
}
