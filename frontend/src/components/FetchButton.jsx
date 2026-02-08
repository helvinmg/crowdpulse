"use client";

import { useState } from "react";
import { RefreshCw, Check, AlertCircle } from "lucide-react";
import { runPipeline } from "@/lib/api";

const STEP_ICONS = {
  start: "[START]",
  telegram: "[TG]",
  youtube: "[YT]",
  twitter: "[X]",
  reddit: "[RD]",
  market: "[MKT]",
  scoring: "[NLP]",
  signals: "[SIG]",
  done: "[OK]",
  error: "[ERR]",
};

export default function FetchButton({ onComplete, dateRange }) {
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [steps, setSteps] = useState([]);
  const [currentMsg, setCurrentMsg] = useState("");
  const [error, setError] = useState(null);
  const [showLog, setShowLog] = useState(false);

  const handleFetch = () => {
    setRunning(true);
    setProgress(0);
    setSteps([]);
    setCurrentMsg("Starting pipeline...");
    setError(null);
    setShowLog(true);

    const hours = dateRange?.hours || 24;
    runPipeline(
      (data) => {
        setProgress(data.progress);
        setCurrentMsg(data.message);
        setSteps((prev) => [
          ...prev,
          { step: data.step, message: data.message, progress: data.progress },
        ]);
      },
      (data) => {
        setRunning(false);
        setProgress(100);
        setCurrentMsg(data?.message || "Pipeline complete!");
        onComplete?.();
      },
      (err) => {
        setRunning(false);
        setError(err?.message || "Pipeline failed");
        setCurrentMsg("Pipeline failed");
      },
      hours,
      dateRange
    );
  };

  return (
    <div className="space-y-2">
      {/* Button row */}
      <div className="flex items-center gap-3">
        <button
          onClick={handleFetch}
          disabled={running}
          className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold
            transition-all duration-200 border
            ${running
              ? "bg-brand-500/10 text-brand-500 border-brand-500/30 cursor-wait"
              : "bg-brand-500/15 text-brand-500 border-brand-500/30 hover:bg-brand-500/25"
            }`}
        >
          {running ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : progress === 100 && !error ? (
            <Check className="w-4 h-4" />
          ) : error ? (
            <AlertCircle className="w-4 h-4 text-red-400" />
          ) : (
            <RefreshCw className="w-4 h-4" />
          )}
          {running ? "Fetching..." : "Fetch Latest"}
        </button>

        {/* Inline progress */}
        {(running || steps.length > 0) && (
          <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
            <span>{currentMsg}</span>
            {running && (
              <button
                onClick={() => setShowLog(!showLog)}
                className="underline hover:text-[var(--foreground)]"
              >
                {showLog ? "hide" : "show"} log
              </button>
            )}
          </div>
        )}
      </div>

      {/* Progress bar */}
      {(running || progress > 0) && (
        <div className="h-1.5 rounded-full bg-[var(--card-border)] overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              error ? "bg-red-500" : progress === 100 ? "bg-green-500" : "bg-brand-500"
            }`}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Step log */}
      {showLog && steps.length > 0 && (
        <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-3 max-h-48 overflow-y-auto">
          <div className="space-y-1">
            {steps.map((s, i) => (
              <div key={i} className="flex items-center gap-2 text-xs">
                <span>{STEP_ICONS[s.step] || "⏳"}</span>
                <span className="text-[var(--muted)]">{s.progress}%</span>
                <span className="text-[var(--foreground)]">{s.message}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
