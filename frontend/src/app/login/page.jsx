"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { LogIn, UserPlus, Eye, EyeOff, TrendingUp, Menu, X } from "lucide-react";

export default function LoginPage() {
  const [isSignup, setIsSignup] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { login, signup } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      let user;
      if (isSignup) {
        user = await signup(email, password, name);
      } else {
        user = await login(email, password);
      }

      if (!user.onboarding_complete) {
        router.push("/onboarding");
      } else {
        router.push("/dashboard");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950">
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-black/20 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2">
              <TrendingUp className="w-8 h-8 text-blue-400" />
              <span className="text-xl font-bold text-white">Crowd Pulse</span>
            </Link>

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
            </div>
          )}
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-md">
          {/* Logo / Brand */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center gap-2 mb-2">
              <TrendingUp className="w-8 h-8 text-blue-500" />
              <h1 className="text-3xl font-bold text-white">Crowd Pulse</h1>
            </div>
            <p className="text-neutral-400 text-sm">
              Hinglish sentiment analysis for Indian equity markets
            </p>
          </div>

          {/* Card */}
          <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-xl">
            <h2 className="text-xl font-semibold text-white mb-6">
              {isSignup ? "Create Account" : "Welcome Back"}
            </h2>

            {error && (
              <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              {isSignup && (
                <div>
                  <label className="block text-sm font-medium text-neutral-300 mb-1.5">
                    Name
                  </label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Your name"
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition"
                  />
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1.5">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  required
                  className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-300 mb-1.5">
                  Password
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder={isSignup ? "Min 6 characters" : "Enter password"}
                    required
                    minLength={isSignup ? 6 : undefined}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition pr-12"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition"
              >
                {loading ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : isSignup ? (
                  <>
                    <UserPlus className="w-4 h-4" /> Sign Up
                  </>
                ) : (
                  <>
                    <LogIn className="w-4 h-4" /> Log In
                  </>
                )}
              </button>
            </form>

            <div className="mt-6 text-center">
              <button
                onClick={() => {
                  setIsSignup(!isSignup);
                  setError("");
                }}
                className="text-sm text-neutral-400 hover:text-blue-400 transition"
              >
                {isSignup
                  ? "Already have an account? Log in"
                  : "Don't have an account? Sign up"}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
