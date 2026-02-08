"use client";

import { AlertTriangle } from "lucide-react";

export default function DisclaimerBanner() {
  return (
    <div className="flex items-center gap-2 rounded-lg border border-yellow-500/30 bg-yellow-500/5 px-4 py-2 text-sm text-yellow-300">
      <AlertTriangle className="w-4 h-4 shrink-0" />
      <span>
        Educational analytics only. This platform does <strong>not</strong>{" "}
        provide investment advice, buy/sell recommendations, or trading signals.
      </span>
    </div>
  );
}
