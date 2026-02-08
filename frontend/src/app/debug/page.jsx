"use client";

import { useEffect, useState } from "react";
import { getSentimentTimeseries } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function DebugPage() {
  const auth = useAuth();
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log("[Debug] auth:", auth);
    
    const token = localStorage.getItem('crowdpulse_token');
    console.log("[Debug] token in localStorage:", token);
    
    getSentimentTimeseries("RELIANCE", 24, null, "test")
      .then((data) => {
        console.log("[Debug] API success:", data);
        setResult(data);
      })
      .catch((err) => {
        console.error("[Debug] API error:", err);
        setError(err.message);
      });
  }, []);

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-4">Debug Page</h1>
      
      <div className="space-y-4">
        <div>
          <h2 className="font-semibold">Auth Status:</h2>
          <pre className="bg-gray-100 p-2 rounded">
            {JSON.stringify({ user: auth?.user, token: !!auth?.token }, null, 2)}
          </pre>
        </div>
        
        <div>
          <h2 className="font-semibold">API Result:</h2>
          {result && (
            <pre className="bg-gray-100 p-2 rounded overflow-auto max-h-64">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </div>
        
        <div>
          <h2 className="font-semibold">Error:</h2>
          {error && (
            <pre className="bg-red-100 p-2 rounded">
              {error}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}
