"use client";

import { useState, useEffect } from "react";
import { AlertTriangle, X, BarChart3 } from "lucide-react";
import { getApiUsage } from "@/lib/api";

const SERVICE_LABELS = {
  telegram: "Telegram",
  youtube: "YouTube",
  twitter: "Twitter/X",
  yfinance: "Market Data",
  gemini: "Gemini AI",
};

export default function ApiLimitBanner() {
  const [usage, setUsage] = useState(null);
  const [dismissed, setDismissed] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    const fetchUsage = () => {
      getApiUsage()
        .then(setUsage)
        .catch(() => {});
    };
    fetchUsage();
    const interval = setInterval(fetchUsage, 30000); // refresh every 30s
    return () => clearInterval(interval);
  }, []);

  if (!usage || dismissed) return null;

  // Check if any service is blocked or near limit (>80%)
  const services = Object.entries(SERVICE_LABELS);
  const blockedServices = services.filter(
    ([key]) => usage[key]?.blocked
  );
  const warningServices = services.filter(
    ([key]) => {
      const svc = usage[key];
      return svc && !svc.blocked && svc.percent_used >= 80;
    }
  );

  const hasBlocked = blockedServices.length > 0;
  const hasWarning = warningServices.length > 0;

  // Show nothing if everything is fine
  if (!hasBlocked && !hasWarning && !showDetails) return null;

  return (
    <div className="space-y-2">
      {/* Blocked banner */}
      {hasBlocked && (
        <div className="flex items-start gap-3 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400">
          <AlertTriangle className="w-5 h-5 mt-0.5 shrink-0" />
          <div className="flex-1 text-sm">
            <p className="font-semibold">
              API Limit Reached
            </p>
            <p className="text-red-400/80 mt-0.5">
              {blockedServices.map(([, label]) => label).join(", ")}{" "}
              {blockedServices.length === 1 ? "has" : "have"} hit the free-tier daily limit.
              Data fetching is paused to avoid charges.
              Please contact the developer or wait until tomorrow for limits to reset.
            </p>
          </div>
          <button onClick={() => setDismissed(true)} className="text-red-400/50 hover:text-red-400">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Warning banner */}
      {hasWarning && !hasBlocked && (
        <div className="flex items-start gap-3 p-3 rounded-lg bg-amber-500/10 border border-amber-500/30 text-amber-400">
          <AlertTriangle className="w-5 h-5 mt-0.5 shrink-0" />
          <div className="flex-1 text-sm">
            <p className="font-semibold">API Usage Warning</p>
            <p className="text-amber-400/80 mt-0.5">
              {warningServices.map(([, label]) => label).join(", ")}{" "}
              {warningServices.length === 1 ? "is" : "are"} approaching the daily free-tier limit.
            </p>
          </div>
          <button onClick={() => setDismissed(true)} className="text-amber-400/50 hover:text-amber-400">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Usage details toggle */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="flex items-center gap-1.5 text-xs text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
      >
        <BarChart3 className="w-3.5 h-3.5" />
        {showDetails ? "Hide" : "Show"} API Usage
      </button>

      {/* Usage details panel */}
      {showDetails && (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {services.map(([key, label]) => {
            const svc = usage[key];
            if (!svc) return null;
            return (
              <div
                key={key}
                className={`p-3 rounded-lg border text-sm ${
                  svc.blocked
                    ? "bg-red-500/5 border-red-500/30"
                    : svc.percent_used >= 80
                    ? "bg-amber-500/5 border-amber-500/30"
                    : "bg-[var(--card-bg)] border-[var(--card-border)]"
                }`}
              >
                <div className="font-medium text-xs mb-1">{label}</div>
                <div className="text-lg font-bold">
                  {svc.used}
                  <span className="text-xs font-normal text-[var(--muted)]">
                    /{svc.limit}
                  </span>
                </div>
                {/* Progress bar */}
                <div className="mt-1.5 h-1.5 rounded-full bg-[var(--card-border)] overflow-hidden">
                  <div
                    className={`h-full rounded-full transition-all ${
                      svc.blocked
                        ? "bg-red-500"
                        : svc.percent_used >= 80
                        ? "bg-amber-500"
                        : "bg-green-500"
                    }`}
                    style={{ width: `${Math.min(100, svc.percent_used)}%` }}
                  />
                </div>
                <div className="text-xs text-[var(--muted)] mt-1">
                  {svc.blocked ? "BLOCKED" : `${svc.remaining} left`}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
