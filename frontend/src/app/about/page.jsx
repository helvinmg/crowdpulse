"use client";

import Link from "next/link";
import { ArrowLeft, TrendingUp, MessageCircle, Youtube, Twitter, Globe, Shield, Zap, BarChart3, Users, Target, Key } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950">
      <div className="relative min-h-screen">
        {/* Header */}
        <header className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <Link
                href="/"
                className="p-2 rounded-lg border border-white/20 bg-white/10 text-white hover:bg-white/20 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <h1 className="text-2xl font-bold text-white">About Crowd Pulse</h1>
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="max-w-4xl mx-auto px-4 py-12 space-y-12">
          {/* Hero Section */}
          <div className="text-center space-y-6">
            <div className="inline-flex items-center gap-2 mb-4">
              <TrendingUp className="w-8 h-8 text-blue-400" />
              <h2 className="text-4xl font-bold text-white">Crowd Pulse</h2>
            </div>
            <p className="text-xl text-gray-300 max-w-3xl mx-auto">
              Your smart companion for Indian stock market insights. We analyze what thousands of investors are saying 
              about Nifty 50 stocks across social media and give you contrarian signals.
            </p>
          </div>

          {/* How It Works */}
          <section className="space-y-6">
            <h3 className="text-2xl font-bold text-white flex items-center gap-3">
              <Zap className="w-6 h-6 text-yellow-400" />
              How It Works
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
                  <MessageCircle className="w-6 h-6 text-blue-400" />
                </div>
                <h4 className="text-lg font-semibold text-white mb-2">Collect Chatter</h4>
                <p className="text-gray-300 text-sm">
                  We gather real-time discussions from Telegram, YouTube, Twitter, and Reddit about Indian stocks.
                </p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
                  <BarChart3 className="w-6 h-6 text-blue-400" />
                </div>
                <h4 className="text-lg font-semibold text-white mb-2">Analyze Sentiment</h4>
                <p className="text-gray-300 text-sm">
                  Our AI understands Hinglish (Hindi + English) conversations and determines if people are bullish or bearish.
                </p>
              </div>
              <div className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10">
                <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-4">
                  <Target className="w-6 h-6 text-green-400" />
                </div>
                <h4 className="text-lg font-semibold text-white mb-2">Find Opportunities</h4>
                <p className="text-gray-300 text-sm">
                  We identify when sentiment diverges from market action - potential contrarian trading opportunities.
                </p>
              </div>
            </div>
          </section>

          {/* Why Connect Your Accounts */}
          <section className="space-y-8">
            <h3 className="text-2xl font-bold text-white flex items-center gap-3">
              <Users className="w-6 h-6 text-blue-400" />
              Why Connect Your Social Accounts?
            </h3>
            
            <div className="bg-gradient-to-r from-blue-600/20 to-blue-600/10 border border-blue-500/30 rounded-xl p-6">
              <p className="text-gray-300 mb-6">
                Connecting your social accounts gives you access to real-time, personalized market intelligence. 
                Here's why each platform matters:
              </p>
              
              <div className="space-y-6">
                {/* Telegram */}
                <div className="flex gap-4">
                  <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <MessageCircle className="w-5 h-5 text-blue-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-2">Telegram Channels</h4>
                    <p className="text-gray-300 text-sm mb-2">
                      Telegram is where serious Indian traders share detailed analysis and stock tips. Many professional analysts 
                      and experienced investors run private channels with high-quality discussions.
                    </p>
                    <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
                      <p className="text-blue-300 text-sm font-medium mb-1">🎯 Advantage:</p>
                      <p className="text-gray-300 text-xs">
                        Get early signals from expert traders before they become mainstream. Telegram discussions often 
                        lead market movements by hours or days.
                      </p>
                    </div>
                  </div>
                </div>

                {/* YouTube */}
                <div className="flex gap-4">
                  <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Youtube className="w-5 h-5 text-red-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-2">YouTube Comments</h4>
                    <p className="text-gray-300 text-sm mb-2">
                      Popular finance YouTubers get thousands of comments on their stock analysis videos. These comments contain 
                      valuable insights from retail investors across India.
                    </p>
                    <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
                      <p className="text-red-300 text-sm font-medium mb-1">🎯 Advantage:</p>
                      <p className="text-gray-300 text-xs">
                        Tap into the sentiment of millions of retail investors. YouTube comments often reflect 
                        broader market psychology and emerging trends.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Twitter/X */}
                <div className="flex gap-4">
                  <div className="w-10 h-10 bg-sky-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Twitter className="w-5 h-5 text-sky-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-2">Twitter/X Discussions</h4>
                    <p className="text-gray-300 text-sm mb-2">
                      Twitter is where news breaks and traders share quick thoughts. Many market influencers and financial 
                      journalists post real-time commentary on stock movements.
                    </p>
                    <div className="bg-sky-500/10 border border-sky-500/30 rounded-lg p-3">
                      <p className="text-sky-300 text-sm font-medium mb-1">🎯 Advantage:</p>
                      <p className="text-gray-300 text-xs">
                        Capture breaking news and instant market reactions. Twitter often provides the fastest 
                        signals about market-moving events.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Reddit */}
                <div className="flex gap-4">
                  <div className="w-10 h-10 bg-orange-500/20 rounded-lg flex items-center justify-center flex-shrink-0">
                    <Globe className="w-5 h-5 text-orange-400" />
                  </div>
                  <div className="flex-1">
                    <h4 className="text-lg font-semibold text-white mb-2">Reddit Communities</h4>
                    <p className="text-gray-300 text-sm mb-2">
                      Reddit communities like r/IndianStreetBets and r/IndianStockMarket are where retail investors 
                      share honest opinions, detailed analysis, and sometimes contrarian views.
                    </p>
                    <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3">
                      <p className="text-orange-300 text-sm font-medium mb-1">🎯 Advantage:</p>
                      <p className="text-gray-300 text-xs">
                        Access diverse perspectives from thousands of investors. Reddit discussions often contain 
                        detailed fundamental analysis and long-term thinking.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* Why Use Your Own API Keys */}
          <section className="space-y-6">
            <h3 className="text-2xl font-bold text-white flex items-center gap-3">
              <Key className="w-6 h-6 text-yellow-400" />
              Why Use Your Own API Keys?
            </h3>
            
            <div className="bg-gradient-to-r from-yellow-600/20 to-amber-600/20 border border-yellow-500/30 rounded-xl p-6">
              <p className="text-gray-300 mb-6">
                During onboarding, you can optionally provide your own API credentials for Twitter and Reddit, 
                while Telegram requires your own credentials for security. Here's why using your own keys matters:
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                  <h4 className="text-yellow-300 font-semibold mb-2">Higher Rate Limits</h4>
                  <p className="text-gray-300 text-sm">
                    Shared API keys hit rate limits quickly when multiple users are active. 
                    Your own keys give you dedicated quota - typically 10x more requests per day.
                  </p>
                </div>
                
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                  <h4 className="text-yellow-300 font-semibold mb-2">Better Reliability</h4>
                  <p className="text-gray-300 text-sm">
                    When shared keys hit limits, your data stops flowing. Personal keys ensure 
                    continuous, uninterrupted access to real-time market discussions.
                  </p>
                </div>
                
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                  <h4 className="text-yellow-300 font-semibold mb-2">Faster Updates</h4>
                  <p className="text-gray-300 text-sm">
                    With higher limits, we can fetch data more frequently. Get sentiment updates 
                    every few minutes instead of hourly with shared keys.
                  </p>
                </div>
                
                <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4">
                  <h4 className="text-yellow-300 font-semibold mb-2">Privacy & Security</h4>
                  <p className="text-gray-300 text-sm">
                    Your API usage stays separate from other users. For Telegram, you must use 
                    your own session - we never store or share your login credentials.
                  </p>
                </div>
              </div>
              
              <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <p className="text-blue-300 text-sm">
                  <strong>How to get API keys:</strong>
                </p>
                <ul className="text-blue-300 text-sm mt-2 space-y-1 list-disc list-inside">
                  <li><strong>Telegram:</strong> Get API ID and Hash from <a href="https://my.telegram.org/apps" target="_blank" rel="noopener" className="underline">my.telegram.org/apps</a> (required for private channels)</li>
                  <li><strong>Twitter:</strong> Get Bearer Token from <a href="https://developer.twitter.com" target="_blank" rel="noopener" className="underline">developer.twitter.com</a> (optional, improves results)</li>
                  <li><strong>Reddit:</strong> Create app at <a href="https://reddit.com/prefs/apps" target="_blank" rel="noopener" className="underline">reddit.com/prefs/apps</a> (optional, improves results)</li>
                </ul>
                <p className="text-blue-300 text-sm mt-2">
                  It takes just 5 minutes and dramatically improves your Crowd Pulse experience.
                </p>
              </div>
            </div>
          </section>

          {/* Privacy & Security */}
          <section className="space-y-6">
            <h3 className="text-2xl font-bold text-white flex items-center gap-3">
              <Shield className="w-6 h-6 text-green-400" />
              Your Privacy & Security
            </h3>
            <div className="bg-green-500/10 border border-green-500/30 rounded-xl p-6">
              <div className="space-y-4 text-gray-300">
                <p>• We only read public discussions - never your private messages</p>
                <p>• Your account credentials are encrypted and stored securely</p>
                <p>• We never post anything to your accounts - read-only access only</p>
                <p>• You can disconnect your accounts at any time</p>
                <p>• We analyze discussions anonymously - no personal data is shared</p>
              </div>
            </div>
          </section>

          {/* CTA */}
          <section className="text-center space-y-6">
            <h3 className="text-2xl font-bold text-white">Ready to Get Smarter Insights?</h3>
            <p className="text-gray-300 max-w-2xl mx-auto">
              Join thousands of investors using Crowd Pulse to make data-driven decisions. 
              Start with our demo or create an account to unlock real-time analysis.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/dashboard?demo=true"
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-500 text-white font-semibold rounded-xl hover:shadow-lg transform hover:-translate-y-1 transition-all duration-200"
              >
                Try Demo
              </Link>
              <Link
                href="/login"
                className="px-6 py-3 bg-white/10 backdrop-blur-sm text-white font-semibold rounded-xl border border-white/20 hover:bg-white/20 transition-all duration-200"
              >
                Get Started
              </Link>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-black/20 backdrop-blur-sm mt-12">
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
