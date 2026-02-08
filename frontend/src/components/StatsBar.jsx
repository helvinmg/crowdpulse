"use client";

import { useState, useEffect } from "react";
import { MessageSquare, Youtube, Twitter, Send, Users, BarChart3, Brain } from "lucide-react";
import { getStats } from "@/lib/api";

export default function StatsBar({ dateRange, mode }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const hours = dateRange?.hours || 24;
    getStats(hours, dateRange, mode)
      .then(setStats)
      .catch(() => {});
  }, [dateRange, mode]);

  if (!stats) return null;

  const items = [
    { icon: MessageSquare, label: "Total Posts", value: stats.total_posts.toLocaleString(), color: "text-brand-500" },
    { icon: Send, label: "Telegram", value: stats.telegram_posts.toLocaleString(), color: "text-blue-400" },
    { icon: Youtube, label: "YouTube", value: stats.youtube_comments.toLocaleString(), color: "text-red-400" },
    { icon: Twitter, label: "X / Twitter", value: stats.twitter_posts.toLocaleString(), color: "text-sky-400" },
    { icon: Brain, label: "Scored", value: stats.sentiment_records.toLocaleString(), color: "text-blue-400" },
    { icon: BarChart3, label: "Signals", value: stats.divergence_signals.toLocaleString(), color: "text-green-400" },
    { icon: Users, label: "Sources", value: stats.unique_authors.toLocaleString(), color: "text-amber-400" },
  ];

  return (
    <div className="flex items-center gap-4 overflow-x-auto py-1 text-xs">
      {items.map((item) => (
        <div key={item.label} className="flex items-center gap-1.5 whitespace-nowrap">
          <item.icon className={`w-3.5 h-3.5 ${item.color}`} />
          <span className="text-[var(--muted)]">{item.label}</span>
          <span className="font-semibold">{item.value}</span>
        </div>
      ))}
      <span className="text-[10px] text-[var(--muted)] ml-auto uppercase tracking-wider">
        {stats.mode} mode
      </span>
    </div>
  );
}
