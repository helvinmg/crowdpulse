"use client";

import { ChevronDown } from "lucide-react";

const NIFTY_50 = [
  "NIFTY",
  "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
  "HINDUNILVR", "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK",
  "LT", "AXISBANK", "ASIANPAINT", "MARUTI", "HCLTECH",
  "SUNPHARMA", "TATAMOTORS", "BAJFINANCE", "WIPRO", "TITAN",
  "ULTRACEMCO", "NESTLEIND", "POWERGRID", "NTPC", "TECHM",
  "TATASTEEL", "M&M", "BAJAJFINSV", "INDUSINDBK", "ONGC",
  "JSWSTEEL", "ADANIENT", "ADANIPORTS", "COALINDIA", "GRASIM",
  "CIPLA", "BPCL", "DRREDDY", "EICHERMOT", "DIVISLAB",
  "SBILIFE", "BRITANNIA", "HEROMOTOCO", "APOLLOHOSP", "TATACONSUM",
  "HINDALCO", "BAJAJ-AUTO", "HDFCLIFE", "LTIM", "SHRIRAMFIN",
];

export default function StockSelector({ selected, onSelect }) {
  return (
    <div className="relative">
      <select
        value={selected}
        onChange={(e) => onSelect(e.target.value)}
        className="appearance-none rounded-lg border border-[var(--card-border)] bg-[var(--card)] px-4 py-2 pr-10 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-brand-500"
      >
        {NIFTY_50.map((s) => (
          <option key={s} value={s}>
            {s}
          </option>
        ))}
      </select>
      <ChevronDown className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--muted)]" />
    </div>
  );
}
