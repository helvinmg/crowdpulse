"use client";

import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { getSentimentTimeseries, getDivergenceLatest } from "@/lib/api";

export default function SentimentScoreChart({ symbol, dateRange, mode }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    console.log("[SentimentScoreChart] useEffect:", { symbol, dateRange, mode });
    console.log("[SentimentScoreChart] getSentimentTimeseries function:", typeof getSentimentTimeseries);
    setLoading(true);
    const hours = dateRange?.hours || 24;
    getSentimentTimeseries(symbol, hours, dateRange, mode)
      .then((res) => {
        console.log("[SentimentScoreChart] API response:", res);
        const grouped = {};

        res.data.forEach((p) => {
          const hour = p.timestamp.slice(0, 13);
          if (!grouped[hour]) grouped[hour] = { pos: [], neg: [], neu: [] };
          if (p.label === "positive") grouped[hour].pos.push(p.score);
          else if (p.label === "negative") grouped[hour].neg.push(p.score);
          else grouped[hour].neu.push(p.score);
        });

        const chartData = Object.entries(grouped).map(([hour, vals]) => ({
          time: (dateRange?.hours || 24) > 24 ? hour.slice(5, 13).replace("T", " ") + "h" : hour.slice(11) + ":00",
          positive: vals.pos.length ? +(vals.pos.reduce((a, b) => a + b, 0) / vals.pos.length).toFixed(3) : 0,
          negative: vals.neg.length ? +(vals.neg.reduce((a, b) => a + b, 0) / vals.neg.length).toFixed(3) : 0,
          neutral: vals.neu.length ? +(vals.neu.reduce((a, b) => a + b, 0) / vals.neu.length).toFixed(3) : 0,
        }));

        console.log("[SentimentScoreChart] chartData:", chartData);
        setData(chartData);
      })
      .catch((err) => {
        console.error("[SentimentScoreChart] API error:", err);
        setData([]);
      })
      .finally(() => setLoading(false));
  }, [symbol, dateRange, mode]);

  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4">
      <h3 className="text-sm font-semibold mb-4">
        Sentiment Score — {symbol}
      </h3>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-sm text-[var(--muted)] animate-pulse">
          Loading chart...
        </div>
      ) : data.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-sm text-[var(--muted)]">
          No sentiment data available. Run the pipeline to populate.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
            <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#737373" }} />
            <YAxis domain={[0, 1]} tick={{ fontSize: 11, fill: "#737373" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#141414",
                border: "1px solid #262626",
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Line type="monotone" dataKey="positive" stroke="#22c55e" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="negative" stroke="#ef4444" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="neutral" stroke="#a3a3a3" strokeWidth={1.5} dot={false} strokeDasharray="4 4" />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
