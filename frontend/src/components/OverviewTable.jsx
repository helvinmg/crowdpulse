"use client";

import { useEffect, useState } from "react";
import { getOverview } from "@/lib/api";
import { cn, directionColor } from "@/lib/utils";

export default function OverviewTable({ onSelectSymbol }) {
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getOverview()
      .then((res) => setStocks(res.stocks))
      .catch(() => setStocks([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] overflow-hidden">
      <div className="px-4 py-3 border-b border-[var(--card-border)]">
        <h2 className="text-sm font-semibold">Nifty 50 Overview</h2>
      </div>

      {loading ? (
        <div className="p-8 text-center text-sm text-[var(--muted)] animate-pulse">
          Loading overview...
        </div>
      ) : stocks.length === 0 ? (
        <div className="p-8 text-center text-sm text-[var(--muted)]">
          No signal data available yet. Run the pipeline to populate.
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-[var(--muted)] border-b border-[var(--card-border)]">
                <th className="px-4 py-2">Symbol</th>
                <th className="px-4 py-2">Direction</th>
                <th className="px-4 py-2">Divergence</th>
                <th className="px-4 py-2">Velocity</th>
                <th className="px-4 py-2">Volume</th>
                <th className="px-4 py-2">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {stocks.map((s) => (
                <tr
                  key={s.symbol}
                  onClick={() => onSelectSymbol(s.symbol)}
                  className="border-b border-[var(--card-border)] hover:bg-white/5 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-2 font-medium">{s.symbol}</td>
                  <td className={cn("px-4 py-2 font-semibold uppercase", directionColor(s.divergence_direction))}>
                    {s.divergence_direction}
                  </td>
                  <td className="px-4 py-2">{s.divergence_score?.toFixed(2) ?? "—"}</td>
                  <td className="px-4 py-2">{s.sentiment_velocity?.toFixed(1) ?? "—"}</td>
                  <td className="px-4 py-2">{s.discussion_volume ?? "—"}</td>
                  <td className="px-4 py-2">{s.confidence_score ? `${(s.confidence_score * 100).toFixed(0)}%` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
