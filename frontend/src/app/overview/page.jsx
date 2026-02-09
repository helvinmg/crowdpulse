"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import AuthGuard from "@/components/AuthGuard";
import { ArrowLeft, TrendingUp, TrendingDown, Activity, BarChart3, Users, ShieldCheck } from "lucide-react";
import {
  LineChart, Line, BarChart, Bar, AreaChart, Area,
  PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { getOverview, getIndexSummary } from "@/lib/api";
import { cn, directionColor } from "@/lib/utils";

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) {
      return <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-3 text-xs text-red-400">Error: {this.state.error.message}</div>;
    }
    return this.props.children;
  }
}
function Safe({ children }) { return <ErrorBoundary>{children}</ErrorBoundary>; }

// --- Stat Card ---
function StatCard({ icon: Icon, label, value, sub, color = "text-brand-500" }) {
  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4 space-y-1">
      <div className="flex items-center gap-2 text-xs text-[var(--muted)]">
        <Icon className="w-3.5 h-3.5" />
        {label}
      </div>
      <div className={cn("text-2xl font-bold", color)}>{value}</div>
      {sub && <div className="text-xs text-[var(--muted)]">{sub}</div>}
    </div>
  );
}

// --- Direction Pie ---
function DirectionPie({ data }) {
  const COLORS = { hype: "#ef4444", panic: "#3b82f6", neutral: "#a3a3a3" };
  const pieData = [
    { name: "Hype", value: data.hype },
    { name: "Panic", value: data.panic },
    { name: "Neutral", value: data.neutral },
  ];
  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4">
      <h3 className="text-sm font-semibold mb-3">Signal Direction Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label={({ name, value }) => `${name}: ${value}`}>
            {pieData.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name.toLowerCase()]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: "#141414", border: "1px solid #262626", borderRadius: 8, fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

// --- Sentiment Pie ---
function SentimentPie({ data }) {
  const COLORS = { Positive: "#22c55e", Negative: "#ef4444", Neutral: "#a3a3a3" };
  const total = data.positive + data.negative + data.neutral;
  const pieData = [
    { name: "Positive", value: data.positive },
    { name: "Negative", value: data.negative },
    { name: "Neutral", value: data.neutral },
  ];
  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4">
      <h3 className="text-sm font-semibold mb-3">Sentiment Distribution ({total.toLocaleString()} posts)</h3>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={pieData} cx="50%" cy="50%" innerRadius={50} outerRadius={80} dataKey="value" label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}>
            {pieData.map((entry) => (
              <Cell key={entry.name} fill={COLORS[entry.name]} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ backgroundColor: "#141414", border: "1px solid #262626", borderRadius: 8, fontSize: 12 }} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}

// --- Index Timeseries Chart ---
function IndexDivergenceChart({ data }) {
  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4">
      <h3 className="text-sm font-semibold mb-3">Nifty 50 - Average Divergence Over Time</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
          <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#737373" }} />
          <YAxis tick={{ fontSize: 11, fill: "#737373" }} />
          <Tooltip contentStyle={{ backgroundColor: "#141414", border: "1px solid #262626", borderRadius: 8, fontSize: 12 }} />
          <Area type="monotone" dataKey="avg_divergence" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.15} strokeWidth={2} name="Avg Divergence" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

// --- Volume + Velocity Chart ---
function IndexVolumeVelocityChart({ data }) {
  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4">
      <h3 className="text-sm font-semibold mb-3">Nifty 50 - Discussion Volume & Avg Velocity</h3>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
          <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#737373" }} />
          <YAxis yAxisId="left" tick={{ fontSize: 11, fill: "#737373" }} />
          <YAxis yAxisId="right" orientation="right" domain={[0, 100]} tick={{ fontSize: 11, fill: "#737373" }} />
          <Tooltip contentStyle={{ backgroundColor: "#141414", border: "1px solid #262626", borderRadius: 8, fontSize: 12 }} />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Bar yAxisId="left" dataKey="total_volume" fill="#22c55e" fillOpacity={0.5} name="Volume" />
          <Line yAxisId="right" type="monotone" dataKey="avg_velocity" stroke="#f59e0b" strokeWidth={2} dot={false} name="Avg Velocity" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

// --- Top Movers Table ---
function TopMovers({ title, icon: Icon, stocks, color }) {
  if (!stocks || stocks.length === 0) return null;
  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] overflow-hidden">
      <div className="px-4 py-3 border-b border-[var(--card-border)] flex items-center gap-2">
        <Icon className={cn("w-4 h-4", color)} />
        <h3 className="text-sm font-semibold">{title}</h3>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-xs text-[var(--muted)] border-b border-[var(--card-border)]">
            <th className="px-4 py-2">Symbol</th>
            <th className="px-4 py-2">Divergence</th>
            <th className="px-4 py-2">Velocity</th>
            <th className="px-4 py-2">Volume</th>
            <th className="px-4 py-2">Confidence</th>
          </tr>
        </thead>
        <tbody>
          {stocks.map((s) => (
            <tr key={s.symbol} className="border-b border-[var(--card-border)] hover:bg-white/5">
              <td className="px-4 py-2 font-medium">{s.symbol}</td>
              <td className={cn("px-4 py-2 font-semibold", color)}>{s.divergence_score?.toFixed(2)}</td>
              <td className="px-4 py-2">{s.sentiment_velocity?.toFixed(1)}</td>
              <td className="px-4 py-2">{s.discussion_volume}</td>
              <td className="px-4 py-2">{s.confidence_score ? `${(s.confidence_score * 100).toFixed(0)}%` : "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// --- Full Overview Table ---
function FullOverviewTable({ stocks, onSelect }) {
  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] overflow-hidden">
      <div className="px-4 py-3 border-b border-[var(--card-border)]">
        <h2 className="text-sm font-semibold">All Nifty 50 Stocks</h2>
      </div>
      {stocks.length === 0 ? (
        <div className="p-8 text-center text-sm text-[var(--muted)]">No signal data available.</div>
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
                  onClick={() => onSelect(s.symbol)}
                  className="border-b border-[var(--card-border)] hover:bg-white/5 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-2 font-medium">{s.symbol}</td>
                  <td className={cn("px-4 py-2 font-semibold uppercase", directionColor(s.divergence_direction))}>
                    {s.divergence_direction}
                  </td>
                  <td className="px-4 py-2">{s.divergence_score?.toFixed(2) ?? "-"}</td>
                  <td className="px-4 py-2">{s.sentiment_velocity?.toFixed(1) ?? "-"}</td>
                  <td className="px-4 py-2">{s.discussion_volume ?? "-"}</td>
                  <td className="px-4 py-2">{s.confidence_score ? `${(s.confidence_score * 100).toFixed(0)}%` : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// --- Main Page ---
export default function OverviewPageWrapper() {
  return (
    <AuthGuard>
      <OverviewPage />
    </AuthGuard>
  );
}

function OverviewPage() {
  const [stocks, setStocks] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshKey, setRefreshKey] = useState(0);
  
  // Get mode and date range from URL parameters
  const [mode, setMode] = useState("test");
  const [dateRange, setDateRange] = useState({ hours: 168, start: null, end: null });

  // Parse URL parameters on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    const urlMode = urlParams.get('mode') || 'test';
    const urlHours = parseInt(urlParams.get('hours')) || 168;
    const urlStart = urlParams.get('start');
    const urlEnd = urlParams.get('end');
    
    setMode(urlMode);
    setDateRange({ hours: urlHours, start: urlStart, end: urlEnd });
  }, []);

  // Listen for refresh events from dashboard
  useEffect(() => {
    const handleRefresh = (event) => {
      // If the event includes mode and dateRange data, update them
      if (event.detail) {
        setMode(event.detail.mode || mode);
        setDateRange(event.detail.dateRange || dateRange);
      }
      setRefreshKey(prev => prev + 1);
    };

    // Listen for custom refresh event
    window.addEventListener('refreshOverview', handleRefresh);
    
    // Check URL parameter for refresh trigger
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('refresh') === 'true') {
      handleRefresh();
      // Clean up URL parameter
      window.history.replaceState({}, '', window.location.pathname);
    }

    return () => {
      window.removeEventListener('refreshOverview', handleRefresh);
    };
  }, [mode, dateRange]);

  useEffect(() => {
    setLoading(true);
    // Use dynamic mode and date range from URL parameters
    Promise.all([getOverview(mode), getIndexSummary(dateRange.hours, dateRange, mode)])
      .then(([ov, idx]) => {
        setStocks(ov.stocks || []);
        setSummary(idx);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [refreshKey, mode, dateRange]);

  const timeseriesData = (summary?.index_timeseries || []).map((d) => ({
    ...d,
    time: d.timestamp.slice(5, 13).replace("T", " ") + "h",
  }));

  const handleSelect = (symbol) => {
    window.location.href = `/?symbol=${symbol}`;
  };

  return (
    <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-4">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2 text-sm text-[var(--muted)] hover:text-[var(--foreground)] transition-colors">
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
        </div>
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold tracking-tight flex items-center gap-2">
            <Activity className="w-6 h-6 text-brand-500" />
            Nifty 50 Overview
          </h1>
          <div className="flex items-center gap-2 text-xs text-[var(--muted)] bg-[var(--card)] px-3 py-1 rounded-lg border border-[var(--card-border)]">
            <span className="capitalize">{mode}</span>
            <span>•</span>
            <span>{dateRange.hours}h</span>
            {dateRange.start && <span>• Custom Range</span>}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-sm text-[var(--muted)] py-20 animate-pulse">Loading index data...</div>
      ) : (
        <>
          {/* Stat Cards */}
          {summary && (
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              <StatCard icon={BarChart3} label="Stocks Tracked" value={summary.index_stats.stocks_tracked} />
              <StatCard icon={Activity} label="Avg Divergence" value={summary.index_stats.avg_divergence.toFixed(2)} color={summary.index_stats.avg_divergence > 0 ? "text-red-400" : summary.index_stats.avg_divergence < 0 ? "text-blue-400" : "text-neutral-400"} />
              <StatCard icon={TrendingUp} label="Avg Velocity" value={summary.index_stats.avg_velocity.toFixed(1)} sub="50 = baseline" />
              <StatCard icon={Users} label="Total Volume" value={summary.index_stats.total_volume.toLocaleString()} sub="discussion posts" />
              <StatCard icon={ShieldCheck} label="Avg Confidence" value={`${(summary.index_stats.avg_confidence * 100).toFixed(0)}%`} />
            </div>
          )}

          {/* Pie Charts */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Safe><DirectionPie data={summary.direction_distribution} /></Safe>
              <Safe><SentimentPie data={summary.sentiment_distribution} /></Safe>
            </div>
          )}

          {/* Index Timeseries */}
          {timeseriesData.length > 0 && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Safe><IndexDivergenceChart data={timeseriesData} /></Safe>
              <Safe><IndexVolumeVelocityChart data={timeseriesData} /></Safe>
            </div>
          )}

          {/* Top Movers */}
          {summary && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Safe><TopMovers title="Top Hype Signals" icon={TrendingUp} stocks={summary.top_hype} color="text-red-400" /></Safe>
              <Safe><TopMovers title="Top Panic Signals" icon={TrendingDown} stocks={summary.top_panic} color="text-blue-400" /></Safe>
            </div>
          )}

          {/* Full Table */}
          <Safe><FullOverviewTable stocks={stocks} onSelect={handleSelect} /></Safe>
        </>
      )}
    </main>
  );
}
