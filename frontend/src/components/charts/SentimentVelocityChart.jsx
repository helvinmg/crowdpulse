"use client";

import { useEffect, useState } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import { getDivergenceTimeseries } from "@/lib/api";

export default function SentimentVelocityChart({ symbol, dateRange, mode }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const hours = dateRange?.hours || 72;
    getDivergenceTimeseries(symbol, hours, dateRange, mode)
      .then((res) => {
        const chartData = res.data.map((d) => ({
          time: d.timestamp.slice(5, 16).replace("T", " "),
          velocity: d.sentiment_velocity ?? 50,
        }));
        setData(chartData);
      })
      .catch(() => setData([]))
      .finally(() => setLoading(false));
  }, [symbol, dateRange, mode]);

  return (
    <div className="rounded-lg border border-[var(--card-border)] bg-[var(--card)] p-4">
      <h3 className="text-sm font-semibold mb-4">
        Sentiment Velocity — {symbol}
      </h3>

      {loading ? (
        <div className="h-64 flex items-center justify-center text-sm text-[var(--muted)] animate-pulse">
          Loading chart...
        </div>
      ) : data.length === 0 ? (
        <div className="h-64 flex items-center justify-center text-sm text-[var(--muted)]">
          No velocity data available. Run the pipeline to populate.
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#262626" />
            <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#737373" }} />
            <YAxis domain={[0, 100]} tick={{ fontSize: 11, fill: "#737373" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#141414",
                border: "1px solid #262626",
                borderRadius: 8,
                fontSize: 12,
              }}
            />
            <ReferenceLine y={50} stroke="#525252" strokeDasharray="3 3" label={{ value: "Baseline", fill: "#737373", fontSize: 10 }} />
            <Area
              type="monotone"
              dataKey="velocity"
              stroke="#f59e0b"
              fill="#f59e0b"
              fillOpacity={0.15}
              strokeWidth={2}
            />
          </AreaChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
