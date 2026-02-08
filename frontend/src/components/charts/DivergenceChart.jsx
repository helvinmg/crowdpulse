"use client";

import { useEffect, useState } from "react";
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts";
import { getDivergenceTimeseries } from "@/lib/api";

export default function DivergenceChart({ symbol, dateRange, mode }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const hours = dateRange?.hours || 72;
    getDivergenceTimeseries(symbol, hours, dateRange, mode)
      .then((res) => {
        const chartData = res.data.map((d) => ({
          time: d.timestamp.slice(5, 16).replace("T", " "),
          divergence: d.divergence_score ?? 0,
          confidence: d.confidence_score ? +(d.confidence_score * 100).toFixed(0) : 0,
          volume: d.discussion_volume ?? 0,
        }));
        setData(chartData);
      })
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [symbol, dateRange, mode]);

  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4">
      <h3 className="text-sm font-semibold mb-4">
        Divergence &amp; Confidence — {symbol}
      </h3>

      {loading ? (
        <div className="h-72 flex items-center justify-center text-sm text-[var(--muted)] animate-pulse">
          Loading chart...
        </div>
      ) : data.length === 0 ? (
        <div className="h-72 flex items-center justify-center text-sm text-[var(--muted)]">
          No divergence data available. Run the pipeline to populate.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
            <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#737373" }} />
            <YAxis
              yAxisId="left"
              tick={{ fontSize: 11, fill: "#737373" }}
              label={{ value: "Divergence (z)", angle: -90, position: "insideLeft", fill: "#737373", fontSize: 11 }}
            />
            <YAxis
              yAxisId="right"
              orientation="right"
              domain={[0, 100]}
              tick={{ fontSize: 11, fill: "#737373" }}
              label={{ value: "Confidence %", angle: 90, position: "insideRight", fill: "#737373", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#141414",
                border: "1px solid #262626",
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <ReferenceLine yAxisId="left" y={1.5} stroke="#ef4444" strokeDasharray="3 3" label={{ value: "Hype", fill: "#ef4444", fontSize: 10 }} />
            <ReferenceLine yAxisId="left" y={-1.5} stroke="#3b82f6" strokeDasharray="3 3" label={{ value: "Panic", fill: "#3b82f6", fontSize: 10 }} />
            <Bar yAxisId="left" dataKey="divergence" fill="#8b5cf6" fillOpacity={0.6} name="Divergence" />
            <Line yAxisId="right" type="monotone" dataKey="confidence" stroke="#22c55e" strokeWidth={2} dot={false} name="Confidence %" />
          </ComposedChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
