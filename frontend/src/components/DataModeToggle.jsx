"use client";

import { useState, useEffect } from "react";
import { FlaskConical, Wifi } from "lucide-react";
import { getDataMode, setDataMode } from "@/lib/api";

export default function DataModeToggle({ onModeChange, isDemo = false }) {
  const [mode, setMode] = useState("test");
  const [loading, setLoading] = useState(false);
  const [justSwitched, setJustSwitched] = useState(false);

  useEffect(() => {
    getDataMode()
      .then((res) => setMode(res.mode))
      .catch(() => {});
  }, []);

  const handleSwitch = async (newMode) => {
    if (newMode === mode || loading) return;
    setLoading(true);
    try {
      const res = await setDataMode(newMode);
      setMode(res.mode);
      onModeChange?.(res.mode);
      setJustSwitched(true);
      setTimeout(() => setJustSwitched(false), 4000);
    } catch {
      // API not reachable
    } finally {
      setLoading(false);
    }
  };

  // Don't show toggle for demo users
  if (isDemo) {
    return null;
  }

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={() => handleSwitch(mode === "live" ? "test" : "live")}
        disabled={loading}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all duration-200 ${
          mode === "live"
            ? "bg-blue-500/20 text-blue-400 border-blue-500/30"
            : "bg-[var(--card)] text-[var(--muted)] hover:text-[var(--foreground)] border-[var(--card-border)]"
        }`}
      >
        <Wifi className="w-3.5 h-3.5" />
        Live Mode
      </button>
      {justSwitched && (
        <span className="text-[10px] text-[var(--muted)] animate-pulse">
          Click Fetch Latest to load {mode === "live" ? "real" : "test"} data
        </span>
      )}
    </div>
  );
}
