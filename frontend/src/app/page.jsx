"use client";

import Link from "next/link";
import { TrendingUp, Play, ArrowRight, Menu, X } from "lucide-react";
import { useState } from "react";

export default function LandingPage() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950">
      <div className="relative min-h-screen flex flex-col">
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
                <Link
                  href="/dashboard?demo=true"
                  className="text-gray-300 hover:text-white transition-colors"
                >
                  Demo
                </Link>
                <Link
                  href="/login"
                  className="px-4 py-2 bg-white/10 backdrop-blur-sm text-white font-medium rounded-lg border border-white/20 hover:bg-white/20 transition-all duration-200"
                >
                  Sign In
                </Link>
              </div>

              {/* Mobile menu button */}
              <div className="md:hidden">
                <button
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="p-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
                >
                  {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {/* Mobile Navigation */}
            {mobileMenuOpen && (
              <div className="md:hidden py-4 space-y-2 border-t border-white/10">
                <Link
                  href="/about"
                  className="block px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  About
                </Link>
                <Link
                  href="/dashboard?demo=true"
                  className="block px-4 py-2 text-gray-300 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Demo
                </Link>
                <Link
                  href="/login"
                  className="block px-4 py-2 bg-white/10 backdrop-blur-sm text-white font-medium rounded-lg border border-white/20 hover:bg-white/20 transition-all duration-200"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign In
                </Link>
              </div>
            )}
          </div>
        </nav>

        {/* Hero Section */}
        <main className="flex-1 flex items-center justify-center px-4 py-12 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto text-center">

            <div className="space-y-8">
              {/* Main Content */}
              <div className="space-y-4">
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white">
                  Crowd
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-cyan-400">
                    Pulse
                  </span>
                </h1>
                <p className="text-xl sm:text-2xl text-gray-300 max-w-3xl mx-auto">
                  Track real-time sentiment from Telegram, YouTube, Twitter & Reddit. 
                  Get contrarian signals powered by AI-driven Hinglish analysis.
                </p>
              </div>

              {/* CTA Buttons */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <Link
                  href="/dashboard?demo=true"
                  className="group relative px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transform hover:-translate-y-1 transition-all duration-200 flex items-center gap-3 text-lg"
                >
                  <Play className="w-5 h-5" />
                  Try Demo
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </Link>
                
                <Link
                  href="/login"
                  className="px-8 py-4 bg-white/10 backdrop-blur-sm text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-200 flex items-center gap-3 text-lg"
                >
                  Get Started
                  <ArrowRight className="w-5 h-5" />
                </Link>
              </div>

              {/* Features */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16 max-w-5xl mx-auto">
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                  <TrendingUp className="w-8 h-8 text-blue-400 mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Real-time Analysis</h3>
                  <p className="text-gray-300">Live sentiment tracking from multiple social platforms</p>
                </div>
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                  <TrendingUp className="w-8 h-8 text-blue-400 mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">AI-Powered Insights</h3>
                  <p className="text-gray-300">FinBERT analysis optimized for Hinglish market chatter</p>
                </div>
                <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                  <TrendingUp className="w-8 h-8 text-blue-400 mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Contrarian Signals</h3>
                  <p className="text-gray-300">Identify divergence opportunities with confidence scoring</p>
                </div>
              </div>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-black/20 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="text-center text-gray-400">
              <p>&copy; helvinmg. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}
