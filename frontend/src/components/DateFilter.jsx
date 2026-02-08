"use client";

import { useState, useEffect } from "react";
import { Calendar, ChevronDown } from "lucide-react";

const PRESETS = [
  { label: "Today", hours: 24 },
  { label: "Yesterday", hours: 48, offset: 24 },
  { label: "3 Days", hours: 72 },
  { label: "7 Days", hours: 168 },
];

export default function DateFilter({ value, onChange }) {
  const [open, setOpen] = useState(false);
  const [customStart, setCustomStart] = useState("");
  const [customEnd, setCustomEnd] = useState("");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const today = new Date().toISOString().slice(0, 10);
    const weekAgo = new Date(Date.now() - 7 * 86400000).toISOString().slice(0, 10);
    setCustomStart(weekAgo);
    setCustomEnd(today);
  }, []);

  const activeLabel = value?.label || "7 Days";

  const handlePreset = (preset) => {
    if (preset.label === "Yesterday") {
      const now = new Date();
      const yStart = new Date(now);
      yStart.setDate(yStart.getDate() - 1);
      yStart.setHours(0, 0, 0, 0);
      const yEnd = new Date(now);
      yEnd.setDate(yEnd.getDate() - 1);
      yEnd.setHours(23, 59, 59, 999);
      onChange({
        label: "Yesterday",
        hours: 24,
        start: yStart.toISOString(),
        end: yEnd.toISOString(),
      });
    } else {
      onChange({
        label: preset.label,
        hours: preset.hours,
        start: null,
        end: null,
      });
    }
    setOpen(false);
  };

  const handleCustom = () => {
    onChange({
      label: `${customStart} → ${customEnd}`,
      hours: 168,
      start: new Date(customStart + "T00:00:00").toISOString(),
      end: new Date(customEnd + "T23:59:59").toISOString(),
    });
    setOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium
          bg-[var(--card)] border border-[var(--card-border)] text-[var(--foreground)]
          hover:border-[var(--foreground)]/20 transition-all"
      >
        <Calendar className="w-3.5 h-3.5 text-[var(--muted)]" />
        {activeLabel}
        <ChevronDown className="w-3 h-3 text-[var(--muted)]" />
      </button>

      {open && (
        <div className="absolute top-full mt-1 right-0 z-50 w-64 rounded-lg border border-[var(--card-border)] bg-[var(--card)] shadow-xl p-3 space-y-2">
          {/* Presets */}
          <div className="grid grid-cols-2 gap-1.5">
            {PRESETS.map((p) => (
              <button
                key={p.label}
                onClick={() => handlePreset(p)}
                className={`px-2.5 py-1.5 rounded text-xs font-medium transition-all
                  ${activeLabel === p.label
                    ? "bg-brand-500/20 text-brand-500 border border-brand-500/30"
                    : "bg-white/5 text-[var(--muted)] hover:text-[var(--foreground)] border border-transparent hover:border-[var(--card-border)]"
                  }`}
              >
                {p.label}
              </button>
            ))}
          </div>

          {/* Custom range */}
          <div className="border-t border-[var(--card-border)] pt-2 space-y-1.5">
            <div className="text-[10px] uppercase tracking-wider text-[var(--muted)] font-semibold">
              Custom Range
            </div>
            <div className="flex gap-1.5">
              <input
                type="date"
                value={customStart}
                onChange={(e) => setCustomStart(e.target.value)}
                className="flex-1 px-2 py-1 rounded text-xs bg-white/5 border border-[var(--card-border)]
                  text-[var(--foreground)] outline-none focus:border-brand-500/50"
              />
              <input
                type="date"
                value={customEnd}
                onChange={(e) => setCustomEnd(e.target.value)}
                className="flex-1 px-2 py-1 rounded text-xs bg-white/5 border border-[var(--card-border)]
                  text-[var(--foreground)] outline-none focus:border-brand-500/50"
              />
            </div>
            <button
              onClick={handleCustom}
              className="w-full px-2 py-1.5 rounded text-xs font-medium bg-brand-500/15 text-brand-500
                hover:bg-brand-500/25 transition-all border border-brand-500/20"
            >
              Apply
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
