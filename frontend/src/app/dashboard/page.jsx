"use client";

import React, { useState, useCallback, useEffect } from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { BarChart3, Activity, Settings, LogOut, Info, TrendingUp } from "lucide-react";
import AuthGuard from "@/components/AuthGuard";
import { useAuth } from "@/lib/auth";
import DataModeToggle from "@/components/DataModeToggle";
import ApiLimitBanner from "@/components/ApiLimitBanner";
import DateFilter from "@/components/DateFilter";
import FetchButton from "@/components/FetchButton";
import StockSelector from "@/components/StockSelector";
import SentimentScoreChart from "@/components/charts/SentimentScoreChart";
import SentimentVelocityChart from "@/components/charts/SentimentVelocityChart";
import DivergenceChart from "@/components/charts/DivergenceChart";
import ConfidenceCard from "@/components/ConfidenceCard";
import DisclaimerBanner from "@/components/DisclaimerBanner";
import StatsBar from "@/components/StatsBar";

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }
  static getDerivedStateFromError(error) {
    return { error };
  }
  render() {
    if (this.state.error) {
      return (
        <div className="rounded-lg border border-red-500/30 bg-red-500/5 p-3 text-xs text-red-400">
          Component error: {this.state.error.message}
        </div>
      );
    }
    return this.props.children;
  }
}

function Safe({ children }) {
  return <ErrorBoundary>{children}</ErrorBoundary>;
}

function AuthenticatedFeatures({ children }) {
  return <AuthGuard>{children}</AuthGuard>;
}

export default function Dashboard() {
  return <DashboardContent />;
}

function DashboardContent() {
  const searchParams = useSearchParams();
  const isDemo = searchParams.get('demo') === 'true';
  const auth = useAuth();
  const user = auth?.user;
  const logout = auth?.logout;
  const [selectedSymbol, setSelectedSymbol] = useState("RELIANCE");
  const [dateRange, setDateRange] = useState({ label: "7 Days", hours: 168, start: null, end: null });
  const [refreshKey, setRefreshKey] = useState(0);
  const [currentMode, setCurrentMode] = useState(isDemo ? "demo" : "test");

  const handleFetchComplete = useCallback(() => {
    const newDateRange = { label: "Today", hours: 24, start: null, end: null };
    setDateRange(newDateRange);
    setRefreshKey((k) => k + 1);
    
    // Trigger refresh for overview page if it's open with current mode and date range
    window.dispatchEvent(new CustomEvent('refreshOverview', {
      detail: { mode: currentMode, dateRange: newDateRange }
    }));
  }, [currentMode]);

  const handleModeChange = useCallback((newMode) => {
    if (newMode) {
      setCurrentMode(newMode);
      setRefreshKey((k) => k + 1);
      
      // Trigger refresh for overview page if it's open
      window.dispatchEvent(new CustomEvent('refreshOverview', {
        detail: { mode: newMode, dateRange }
      }));
    }
  }, [dateRange]);

  // Force test mode in demo mode
  useEffect(() => {
    if (isDemo) {
      import("@/lib/api").then(({ setDataMode }) => {
        setDataMode("test").catch(() => {});
      });
    }
  }, [isDemo]);

  // Sync data mode from API when logged in (not demo)
  useEffect(() => {
    if (!isDemo && user) {
      import("@/lib/api").then(({ getDataMode }) => {
        getDataMode().then((res) => setCurrentMode(res.mode ?? "live")).catch(() => {});
      });
    }
  }, [isDemo, user]);

  // Realistic delays for logged-in users in test mode only (demo stays fast)
  useEffect(() => {
    const api = import("@/lib/api").then((m) => m.setSimulateTestModeDelay);
    const enable = !isDemo && !!user && currentMode === "test";
    api.then((fn) => fn(enable));
  }, [isDemo, user, currentMode]);

  const dashboardContent = (
    <>
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-blue-400" />
              <span className="text-xl font-bold text-white">Crowd Pulse</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center gap-8">
              <Link
                href="/about"
                className="text-gray-300 hover:text-white transition-colors"
              >
                About
              </Link>
              {isDemo && (
                <Link
                  href="/dashboard?demo=true"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Demo
                </Link>
              )}
              {!isDemo && (
                <>
                  <Link
                    href="/dashboard"
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/settings"
                    className="text-gray-300 hover:text-white transition-colors"
                  >
                    Settings
                  </Link>
                </>
              )}
              {!isDemo && (
                <button
                  onClick={logout}
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Logout
                </button>
              )}
              {isDemo && (
                <Link
                  href="/login"
                  className="px-4 py-2 bg-white/10 backdrop-blur-sm text-white font-medium rounded-lg border border-white/20 hover:bg-white/20 transition-all duration-200"
                >
                  Sign In
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
      {/* Demo Mode Banner */}
      {isDemo && (
        <div className="bg-gradient-to-r from-blue-600/20 to-blue-600/10 border border-blue-500/30 rounded-xl p-4 flex items-center gap-3">
          <Info className="w-5 h-5 text-blue-400 flex-shrink-0" />
          <p className="text-blue-400/80 text-sm">You're viewing sample test data. Sign in to access real-time live data.</p>
        </div>
      )}

      <div className="flex items-center gap-3 flex-wrap">
        <Safe><FetchButton onComplete={handleFetchComplete} dateRange={dateRange} /></Safe>
        <Safe><DateFilter value={dateRange} onChange={setDateRange} /></Safe>
        <Link
          href={`/overview?mode=${currentMode}&hours=${dateRange.hours}${dateRange.start ? `&start=${dateRange.start}` : ''}${dateRange.end ? `&end=${dateRange.end}` : ''}`}
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold border border-[var(--card-border)] bg-[var(--card)] text-[var(--muted)] hover:text-[var(--foreground)] hover:border-[var(--foreground)]/20 transition-all"
        >
          <BarChart3 className="w-4 h-4" />
          Nifty 50 Overview
        </Link>
        <Link
          href="/usage"
          className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold border border-[var(--card-border)] bg-[var(--card)] text-[var(--muted)] hover:text-[var(--foreground)] hover:border-[var(--foreground)]/20 transition-all"
        >
          <Activity className="w-4 h-4" />
          API Usage
        </Link>
        {!isDemo && <Safe><DataModeToggle onModeChange={handleModeChange} isDemo={isDemo} /></Safe>}
      </div>

      {/* Stats bar shows data for current mode */}
      <Safe key={`stats-${refreshKey}`}><StatsBar dateRange={dateRange} mode={currentMode} /></Safe>

      <Safe><ApiLimitBanner /></Safe>
      <DisclaimerBanner />

      <div className="flex flex-col md:flex-row gap-4 items-start">
        <StockSelector
          selected={selectedSymbol}
          onSelect={setSelectedSymbol}
        />
        <Safe key={`conf-${refreshKey}`}><ConfidenceCard symbol={selectedSymbol} mode={currentMode} /></Safe>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Safe key={`sent-${refreshKey}`}><SentimentScoreChart symbol={selectedSymbol} dateRange={dateRange} mode={currentMode} /></Safe>
        <Safe key={`vel-${refreshKey}`}><SentimentVelocityChart symbol={selectedSymbol} dateRange={dateRange} mode={currentMode} /></Safe>
      </div>

      <Safe key={`div-${refreshKey}`}><DivergenceChart symbol={selectedSymbol} dateRange={dateRange} mode={currentMode} /></Safe>
    </main>
    </>
  );

  return dashboardContent;
}
