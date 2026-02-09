"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import AuthGuard from "@/components/AuthGuard";
import { ArrowLeft, Activity, CheckCircle, XCircle, AlertTriangle } from "lucide-react";
import { getApiUsage, getUsageLogs } from "@/lib/api";

const SERVICE_COLORS = {
  telegram: "text-blue-400",
  youtube: "text-red-400",
  twitter: "text-sky-400",
  yfinance: "text-green-400",
  gemini: "text-purple-400",
};

const STATUS_ICONS = {
  success: <CheckCircle className="w-3.5 h-3.5 text-green-400" />,
  blocked: <XCircle className="w-3.5 h-3.5 text-red-400" />,
  error: <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />,
};

function UsageBar({ service, used, limit, blocked }) {
  const pct = limit > 0 ? Math.min(100, (used / limit) * 100) : 0;
  const color = blocked ? "bg-red-500" : pct > 80 ? "bg-amber-500" : "bg-brand-500";

  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4 space-y-2">
      <div className="flex items-center justify-between">
        <span className={`text-sm font-semibold capitalize ${SERVICE_COLORS[service] || "text-[var(--foreground)]"}`}>
          {service}
        </span>
        <span className="text-xs text-[var(--muted)]">
          {used} / {limit} {blocked && <span className="text-red-400 font-semibold ml-1">BLOCKED</span>}
        </span>
      </div>
      <div className="h-2 rounded-full bg-[var(--card-border)] overflow-hidden">
        <div className={`h-full rounded-full transition-all ${color}`} style={{ width: `${pct}%` }} />
      </div>
      <div className="text-xs text-[var(--muted)]">
        {limit - used > 0 ? `${limit - used} remaining` : "Limit reached"} &middot; {pct.toFixed(0)}% used
      </div>
    </div>
  );
}

export default function UsagePageWrapper() {
  return (
    <AuthGuard>
      <UsagePage />
    </AuthGuard>
  );
}

function UsagePage() {
  const [summary, setSummary] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.all([getApiUsage(), getUsageLogs(200)])
      .then(([usage, logsRes]) => {
        setSummary(usage);
        setLogs(logsRes.logs || []);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const services = summary
    ? Object.entries(summary).filter(([k]) => k !== "date" && k !== "any_blocked")
    : [];

  return (
    <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-4">
        <Link href="/" className="flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--foreground)] transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
        <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
          <Activity className="w-6 h-6 text-brand-500" />
          API Usage & Consumption Log
        </h1>
      </div>

      {loading ? (
        <div className="text-center text-sm text-[var(--muted)] py-20 animate-pulse">Loading usage data...</div>
      ) : (
        <>
          {/* Usage bars */}
          {services.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {services.map(([service, data]) => (
                <UsageBar
                  key={service}
                  service={service}
                  used={data.used}
                  limit={data.limit}
                  blocked={data.blocked}
                />
              ))}
            </div>
          )}

          {summary?.date && (
            <div className="text-xs text-[var(--muted)]">Usage for: {summary.date}</div>
          )}

          {/* Logs table */}
          <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] overflow-hidden">
            <div className="px-4 py-3 border-b border-[var(--card-border)]">
              <h2 className="text-sm font-semibold">Recent API Calls ({logs.length})</h2>
            </div>
            {logs.length === 0 ? (
              <div className="p-8 text-center text-sm text-[var(--muted)]">
                No API usage logs yet. Switch to Live Mode and click Fetch Latest to start making real API calls.
              </div>
            ) : (
              <div className="overflow-x-auto max-h-[600px] overflow-y-auto">
                <table className="w-full text-sm">
                  <thead className="sticky top-0 bg-[var(--card)]">
                    <tr className="text-left text-xs text-[var(--muted)] border-b border-[var(--card-border)]">
                      <th className="px-4 py-2">Time</th>
                      <th className="px-4 py-2">Service</th>
                      <th className="px-4 py-2">Status</th>
                      <th className="px-4 py-2">Endpoint</th>
                      <th className="px-4 py-2">Records</th>
                      <th className="px-4 py-2">Response</th>
                      <th className="px-4 py-2">Daily Usage</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.map((log) => (
                      <tr key={log.id} className="border-b border-[var(--card-border)] hover:bg-white/5">
                        <td className="px-4 py-2 text-xs text-[var(--muted)] whitespace-nowrap">
                          {log.called_at ? new Date(log.called_at).toLocaleString() : "-"}
                        </td>
                        <td className={`px-4 py-2 font-medium capitalize ${SERVICE_COLORS[log.service] || ""}`}>
                          {log.service}
                        </td>
                        <td className="px-4 py-2">
                          <span className={`inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full ${
                            log.status === "success" ? "bg-green-500/10 text-green-400" :
                            log.status === "blocked" ? "bg-red-500/10 text-red-400" :
                            "bg-amber-500/10 text-amber-400"
                          }`}>
                            {log.status}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-xs text-[var(--muted)] max-w-[200px] truncate">
                          {log.endpoint || "-"}
                        </td>
                        <td className="px-4 py-2">{log.records_fetched || "-"}</td>
                        <td className="px-4 py-2 text-xs">
                          {log.response_time_ms ? `${log.response_time_ms.toFixed(0)}ms` : "-"}
                        </td>
                        <td className="px-4 py-2 text-xs text-[var(--muted)]">
                          {log.daily_count != null ? `${log.daily_count}/${log.daily_limit}` : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </main>
  );
}
