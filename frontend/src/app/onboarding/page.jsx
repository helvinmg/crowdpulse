"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth, authHeaders } from "@/lib/auth";
import {
  MessageCircle,
  Youtube,
  Twitter,
  ChevronRight,
  SkipForward,
  Check,
  Loader2,
  Plus,
  X,
  TrendingUp,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const STEPS = ["telegram", "youtube", "twitter", "reddit", "done"];

export default function OnboardingPage() {
  const { token, updateUser } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(0);

  // Telegram state
  const [tgApiId, setTgApiId] = useState("");
  const [tgApiHash, setTgApiHash] = useState("");
  const [tgPhone, setTgPhone] = useState("");
  const [tgCode, setTgCode] = useState("");
  const [tgCodeSent, setTgCodeSent] = useState(false);
  const [tgVerified, setTgVerified] = useState(false);
  const [tgNeeds2FA, setTgNeeds2FA] = useState(false);
  const [tgPassword, setTgPassword] = useState("");
  const [tgChannels, setTgChannels] = useState([""]);
  const [tgLoading, setTgLoading] = useState(false);

  // YouTube state
  const [ytVideoIds, setYtVideoIds] = useState([""]);

  // Twitter state
  const [twQueries, setTwQueries] = useState([""]);
  const [twBearerToken, setTwBearerToken] = useState("");
  const [twUseOwnKey, setTwUseOwnKey] = useState(false);

  // Reddit state
  const [rdSubreddits, setRdSubreddits] = useState(["IndianStreetBets", "IndianStockMarket", ""]);
  const [rdClientId, setRdClientId] = useState("");
  const [rdClientSecret, setRdClientSecret] = useState("");
  const [rdUseOwnCreds, setRdUseOwnCreds] = useState(false);

  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const headers = {
    "Content-Type": "application/json",
    ...authHeaders(token),
  };

  // ---------------------------------------------------------------------------
  // Telegram handlers
  // ---------------------------------------------------------------------------

  const sendTelegramCode = async () => {
    setError("");
    setTgLoading(true);
    try {
      const res = await fetch(`${API_URL}/onboarding/telegram/send-code`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          api_id: tgApiId,
          api_hash: tgApiHash,
          phone: tgPhone,
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to send code");
      setTgCodeSent(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setTgLoading(false);
    }
  };

  const verifyTelegramCode = async (password = null) => {
    setError("");
    setTgLoading(true);
    try {
      const body = { code: tgCode };
      if (password) body.password = password;
      const res = await fetch(`${API_URL}/onboarding/telegram/verify`, {
        method: "POST",
        headers,
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Verification failed");
      if (data.status === "needs_2fa") {
        setTgNeeds2FA(true);
      } else {
        setTgVerified(true);
        setTgNeeds2FA(false);
      }
    } catch (err) {
      if (err.message.includes("No pending") || err.message.includes("Send code first")) {
        setTgCodeSent(false);
        setTgNeeds2FA(false);
        setTgCode("");
        setTgPassword("");
        setError("Session expired. Please re-send the OTP code.");
      } else {
        setError(err.message);
      }
    } finally {
      setTgLoading(false);
    }
  };

  const submit2FAPassword = async () => {
    await verifyTelegramCode(tgPassword);
  };

  const saveTelegramChannels = async () => {
    const channels = tgChannels.filter((c) => c.trim());
    if (channels.length === 0) return;
    try {
      await fetch(`${API_URL}/onboarding/telegram/channels`, {
        method: "POST",
        headers,
        body: JSON.stringify(channels),
      });
    } catch {}
  };

  // ---------------------------------------------------------------------------
  // YouTube handler
  // ---------------------------------------------------------------------------

  const saveYouTube = async () => {
    const ids = ytVideoIds.filter((v) => v.trim());
    if (ids.length === 0) return;
    setSaving(true);
    try {
      await fetch(`${API_URL}/onboarding/youtube`, {
        method: "POST",
        headers,
        body: JSON.stringify({ video_ids: ids }),
      });
    } catch {}
    setSaving(false);
  };

  // ---------------------------------------------------------------------------
  // Twitter handler
  // ---------------------------------------------------------------------------

  const saveTwitter = async () => {
    const queries = twQueries.filter((q) => q.trim());
    if (queries.length === 0) return;
    setSaving(true);
    try {
      await fetch(`${API_URL}/onboarding/twitter`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          queries,
          bearer_token: twUseOwnKey ? twBearerToken : null,
        }),
      });
    } catch {}
    setSaving(false);
  };

  // ---------------------------------------------------------------------------
  // Reddit handler
  // ---------------------------------------------------------------------------

  const saveReddit = async () => {
    const subs = rdSubreddits.filter((s) => s.trim());
    if (subs.length === 0) return;
    setSaving(true);
    try {
      await fetch(`${API_URL}/onboarding/reddit`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          subreddits: subs,
          client_id: rdUseOwnCreds ? rdClientId : null,
          client_secret: rdUseOwnCreds ? rdClientSecret : null,
        }),
      });
    } catch {}
    setSaving(false);
  };

  // ---------------------------------------------------------------------------
  // Navigation
  // ---------------------------------------------------------------------------

  const nextStep = async () => {
    setError("");
    // Save current step data
    if (STEPS[step] === "telegram" && tgVerified) {
      await saveTelegramChannels();
    }
    if (STEPS[step] === "youtube") {
      await saveYouTube();
    }
    if (STEPS[step] === "twitter") {
      await saveTwitter();
    }
    if (STEPS[step] === "reddit") {
      await saveReddit();
    }
    setStep((s) => s + 1);
  };

  const skipStep = () => {
    setError("");
    setStep((s) => s + 1);
  };

  const finishOnboarding = async () => {
    setSaving(true);
    try {
      await fetch(`${API_URL}/onboarding/complete`, {
        method: "POST",
        headers,
      });
      updateUser({ onboarding_complete: true });
      router.push("/dashboard");
    } catch {
      setError("Failed to complete onboarding");
    }
    setSaving(false);
  };

  const skipAll = async () => {
    setSaving(true);
    try {
      await fetch(`${API_URL}/onboarding/skip`, {
        method: "POST",
        headers,
      });
      updateUser({ onboarding_complete: true });
      router.push("/dashboard");
    } catch {
      setError("Failed to skip onboarding");
    }
    setSaving(false);
  };

  // ---------------------------------------------------------------------------
  // List input helpers
  // ---------------------------------------------------------------------------

  const addItem = (list, setList) => setList([...list, ""]);
  const removeItem = (list, setList, idx) =>
    setList(list.filter((_, i) => i !== idx));
  const updateItem = (list, setList, idx, val) =>
    setList(list.map((v, i) => (i === idx ? val : v)));

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const currentStep = STEPS[step];

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-950 via-neutral-900 to-neutral-950 flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-lg">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-2">
            <TrendingUp className="w-6 h-6 text-blue-500" />
            <h1 className="text-2xl font-bold text-white">Setup Your Sources</h1>
          </div>
          <p className="text-neutral-400 text-sm">
            Connect your data sources or skip to use defaults
          </p>
        </div>

        {/* Progress */}
        <div className="flex items-center justify-center gap-2 mb-8">
          {STEPS.slice(0, -1).map((s, i) => (
            <div
              key={s}
              className={`h-1.5 w-16 rounded-full transition ${
                i < step
                  ? "bg-blue-500"
                  : i === step
                  ? "bg-blue-500/50"
                  : "bg-neutral-700"
              }`}
            />
          ))}
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="bg-neutral-900 border border-neutral-800 rounded-2xl p-8 shadow-xl">
          {/* ============================================================= */}
          {/* TELEGRAM STEP */}
          {/* ============================================================= */}
          {currentStep === "telegram" && (
            <div className="space-y-5">
              <div className="flex items-center gap-3 mb-2">
                <MessageCircle className="w-6 h-6 text-blue-400" />
                <h2 className="text-lg font-semibold text-white">
                  Connect Telegram
                </h2>
              </div>
              <p className="text-neutral-400 text-sm">
                Get API credentials from{" "}
                <a
                  href="https://my.telegram.org/apps"
                  target="_blank"
                  rel="noopener"
                  className="text-blue-400 underline"
                >
                  my.telegram.org/apps
                </a>
              </p>

              {!tgVerified ? (
                <>
                  <input
                    placeholder="API ID"
                    value={tgApiId}
                    onChange={(e) => setTgApiId(e.target.value)}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  />
                  <input
                    placeholder="API Hash"
                    value={tgApiHash}
                    onChange={(e) => setTgApiHash(e.target.value)}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  />
                  <input
                    placeholder="Phone (+91XXXXXXXXXX)"
                    value={tgPhone}
                    onChange={(e) => setTgPhone(e.target.value)}
                    className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  />

                  {!tgCodeSent ? (
                    <button
                      onClick={sendTelegramCode}
                      disabled={tgLoading || !tgApiId || !tgApiHash || !tgPhone}
                      className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white rounded-lg flex items-center justify-center gap-2 transition"
                    >
                      {tgLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        "Send OTP Code"
                      )}
                    </button>
                  ) : tgNeeds2FA ? (
                    <>
                      <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-lg text-amber-400 text-sm">
                        Your account has Two-Step Verification (2FA) enabled.
                        Enter your cloud password (set in Telegram Settings &rarr; Privacy &rarr; Two-Step Verification).
                      </div>
                      <input
                        type="password"
                        placeholder="Enter 2FA password"
                        value={tgPassword}
                        onChange={(e) => setTgPassword(e.target.value)}
                        className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                      />
                      <button
                        onClick={submit2FAPassword}
                        disabled={tgLoading || !tgPassword}
                        className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white rounded-lg flex items-center justify-center gap-2 transition"
                      >
                        {tgLoading ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          "Submit Password"
                        )}
                      </button>
                    </>
                  ) : (
                    <>
                      <input
                        placeholder="Enter OTP code"
                        value={tgCode}
                        onChange={(e) => setTgCode(e.target.value)}
                        className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                      />
                      <button
                        onClick={() => verifyTelegramCode()}
                        disabled={tgLoading || !tgCode}
                        className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white rounded-lg flex items-center justify-center gap-2 transition"
                      >
                        {tgLoading ? (
                          <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                          "Verify Code"
                        )}
                      </button>
                    </>
                  )}
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm">
                    <Check className="w-4 h-4" /> Telegram connected!
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-neutral-300 mb-2">
                      Channels to scrape (optional)
                    </label>
                    {tgChannels.map((ch, i) => (
                      <div key={i} className="flex gap-2 mb-2">
                        <input
                          placeholder="e.g. UshasAnalysis"
                          value={ch}
                          onChange={(e) =>
                            updateItem(tgChannels, setTgChannels, i, e.target.value)
                          }
                          className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                        />
                        {tgChannels.length > 1 && (
                          <button
                            onClick={() => removeItem(tgChannels, setTgChannels, i)}
                            className="p-2 text-neutral-500 hover:text-red-400"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    ))}
                    <button
                      onClick={() => addItem(tgChannels, setTgChannels)}
                      className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
                    >
                      <Plus className="w-3 h-3" /> Add channel
                    </button>
                  </div>
                </>
              )}
            </div>
          )}

          {/* ============================================================= */}
          {/* YOUTUBE STEP */}
          {/* ============================================================= */}
          {currentStep === "youtube" && (
            <div className="space-y-5">
              <div className="flex items-center gap-3 mb-2">
                <Youtube className="w-6 h-6 text-red-500" />
                <h2 className="text-lg font-semibold text-white">
                  YouTube Videos
                </h2>
              </div>
              <p className="text-neutral-400 text-sm">
                Add YouTube video IDs to scrape comments from. Find the ID in
                the URL after <code className="text-neutral-300">?v=</code>
              </p>

              {ytVideoIds.map((vid, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    placeholder="e.g. dQw4w9WgXcQ"
                    value={vid}
                    onChange={(e) =>
                      updateItem(ytVideoIds, setYtVideoIds, i, e.target.value)
                    }
                    className="flex-1 px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  />
                  {ytVideoIds.length > 1 && (
                    <button
                      onClick={() => removeItem(ytVideoIds, setYtVideoIds, i)}
                      className="p-2 text-neutral-500 hover:text-red-400"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => addItem(ytVideoIds, setYtVideoIds)}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                <Plus className="w-3 h-3" /> Add video
              </button>
            </div>
          )}

          {/* ============================================================= */}
          {/* TWITTER STEP */}
          {/* ============================================================= */}
          {currentStep === "twitter" && (
            <div className="space-y-5">
              <div className="flex items-center gap-3 mb-2">
                <Twitter className="w-6 h-6 text-sky-400" />
                <h2 className="text-lg font-semibold text-white">
                  Twitter / X Queries
                </h2>
              </div>
              <p className="text-neutral-400 text-sm">
                Add hashtags or search terms to track on Twitter/X.
              </p>

              {twQueries.map((q, i) => (
                <div key={i} className="flex gap-2">
                  <input
                    placeholder="e.g. #Nifty50"
                    value={q}
                    onChange={(e) =>
                      updateItem(twQueries, setTwQueries, i, e.target.value)
                    }
                    className="flex-1 px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                  />
                  {twQueries.length > 1 && (
                    <button
                      onClick={() => removeItem(twQueries, setTwQueries, i)}
                      className="p-2 text-neutral-500 hover:text-red-400"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => addItem(twQueries, setTwQueries)}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                <Plus className="w-3 h-3" /> Add query
              </button>

              {/* Optional API Key */}
              <div className="pt-4 border-t border-neutral-800">
                <label className="flex items-center gap-2 mb-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={twUseOwnKey}
                    onChange={(e) => setTwUseOwnKey(e.target.checked)}
                    className="w-4 h-4 rounded border-neutral-600 bg-neutral-800 text-blue-500 focus:ring-blue-500"
                  />
                  <span className="text-sm text-neutral-300">
                    Use my own Twitter API key (better results)
                  </span>
                </label>
                
                {twUseOwnKey && (
                  <div className="space-y-3">
                    <p className="text-xs text-neutral-500">
                      Get your Bearer Token from{" "}
                      <a
                        href="https://developer.twitter.com/en/portal/dashboard"
                        target="_blank"
                        rel="noopener"
                        className="text-blue-400 underline"
                      >
                        developer.twitter.com
                      </a>
                      . Using your own key gives you higher rate limits and more reliable data.
                    </p>
                    <input
                      type="password"
                      placeholder="Bearer Token (starts with AAAAA...)"
                      value={twBearerToken}
                      onChange={(e) => setTwBearerToken(e.target.value)}
                      className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ============================================================= */}
          {/* REDDIT STEP */}
          {/* ============================================================= */}
          {currentStep === "reddit" && (
            <div className="space-y-5">
              <div className="flex items-center gap-3 mb-2">
                <svg className="w-6 h-6 text-orange-500" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
                </svg>
                <h2 className="text-lg font-semibold text-white">
                  Reddit Subreddits
                </h2>
              </div>
              <p className="text-neutral-400 text-sm">
                Add subreddit names to scrape posts and comments from. Indian
                stock subreddits like <code className="text-neutral-300">IndianStreetBets</code> have
                great Hinglish discussion.
              </p>

              {rdSubreddits.map((sub, i) => (
                <div key={i} className="flex gap-2">
                  <div className="flex-1 flex items-center bg-neutral-800 border border-neutral-700 rounded-lg overflow-hidden">
                    <span className="pl-4 text-neutral-500 text-sm">r/</span>
                    <input
                      placeholder="e.g. IndianStreetBets"
                      value={sub}
                      onChange={(e) =>
                        updateItem(rdSubreddits, setRdSubreddits, i, e.target.value)
                      }
                      className="flex-1 px-2 py-2.5 bg-transparent text-white text-sm placeholder-neutral-500 focus:outline-none"
                    />
                  </div>
                  {rdSubreddits.length > 1 && (
                    <button
                      onClick={() => removeItem(rdSubreddits, setRdSubreddits, i)}
                      className="p-2 text-neutral-500 hover:text-red-400"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  )}
                </div>
              ))}
              <button
                onClick={() => addItem(rdSubreddits, setRdSubreddits)}
                className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
              >
                <Plus className="w-3 h-3" /> Add subreddit
              </button>

              {/* Optional API Credentials */}
              <div className="pt-4 border-t border-neutral-800">
                <label className="flex items-center gap-2 mb-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rdUseOwnCreds}
                    onChange={(e) => setRdUseOwnCreds(e.target.checked)}
                    className="w-4 h-4 rounded border-neutral-600 bg-neutral-800 text-blue-500 focus:ring-blue-500"
                  />
                  <span className="text-sm text-neutral-300">
                    Use my own Reddit API credentials (better results)
                  </span>
                </label>
                
                {rdUseOwnCreds && (
                  <div className="space-y-3">
                    <p className="text-xs text-neutral-500">
                      Create a "script" app at{" "}
                      <a
                        href="https://reddit.com/prefs/apps"
                        target="_blank"
                        rel="noopener"
                        className="text-blue-400 underline"
                      >
                        reddit.com/prefs/apps
                      </a>
                      . Using your own credentials gives you higher rate limits and more reliable access.
                    </p>
                    <input
                      placeholder="Client ID"
                      value={rdClientId}
                      onChange={(e) => setRdClientId(e.target.value)}
                      className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    />
                    <input
                      type="password"
                      placeholder="Client Secret"
                      value={rdClientSecret}
                      onChange={(e) => setRdClientSecret(e.target.value)}
                      className="w-full px-4 py-2.5 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ============================================================= */}
          {/* DONE STEP */}
          {/* ============================================================= */}
          {currentStep === "done" && (
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-green-500/10 rounded-full mb-2">
                <Check className="w-8 h-8 text-green-400" />
              </div>
              <h2 className="text-lg font-semibold text-white">
                You&apos;re all set!
              </h2>
              <p className="text-neutral-400 text-sm">
                Your sources are configured. You can change them anytime in
                Settings.
              </p>
              <button
                onClick={finishOnboarding}
                disabled={saving}
                className="w-full py-2.5 bg-blue-600 hover:bg-blue-500 disabled:bg-blue-600/50 text-white font-medium rounded-lg flex items-center justify-center gap-2 transition"
              >
                {saving ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  "Go to Dashboard"
                )}
              </button>
            </div>
          )}

          {/* ============================================================= */}
          {/* Navigation buttons */}
          {/* ============================================================= */}
          {currentStep !== "done" && (
            <div className="flex items-center justify-between mt-8 pt-6 border-t border-neutral-800">
              <button
                onClick={skipStep}
                className="text-sm text-neutral-400 hover:text-neutral-200 flex items-center gap-1 transition"
              >
                <SkipForward className="w-3.5 h-3.5" /> Skip
              </button>
              <button
                onClick={nextStep}
                className="px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg flex items-center gap-1.5 transition"
              >
                Next <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Skip all */}
        {currentStep !== "done" && (
          <div className="text-center mt-4">
            <button
              onClick={skipAll}
              disabled={saving}
              className="text-sm text-neutral-500 hover:text-neutral-300 transition"
            >
              Skip all — use default channels
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
