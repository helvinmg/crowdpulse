import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatNumber(n) {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toString();
}

export function directionColor(direction) {
  switch (direction) {
    case "hype":
      return "text-red-500";
    case "panic":
      return "text-blue-500";
    default:
      return "text-neutral-400";
  }
}

export function directionBg(direction) {
  switch (direction) {
    case "hype":
      return "bg-red-500/10 border-red-500/30";
    case "panic":
      return "bg-blue-500/10 border-blue-500/30";
    default:
      return "bg-neutral-500/10 border-neutral-500/30";
  }
}

export function confidenceLabel(score) {
  if (score >= 0.7) return "High";
  if (score >= 0.4) return "Medium";
  return "Low";
}
