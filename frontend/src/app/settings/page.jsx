"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import AuthGuard from "@/components/AuthGuard";
import { useAuth, authHeaders } from "@/lib/auth";
import {
  MessageCircle,
  Youtube,
  Twitter,
  ArrowLeft,
  Save,
  Check,
  Loader2,
  Plus,
  X,
  Shield,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function SettingsPage() {
  return (
    <AuthGuard>
      <SettingsContent />
    </AuthGuard>
  );
}

function SettingsContent() {
  const { token, user } = useAuth();
  const router = useRouter();
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState("");
  const [error, setError] = useState("");

  // Editable state
  const [tgChannels, setTgChannels] = useState([""]);
  const [ytVideoIds, setYtVideoIds] = useState([""]);
  const [twQueries, setTwQueries] = useState([""]);
  const [rdSubreddits, setRdSubreddits] = useState([""]);

  const headers = {
    "Content-Type": "application/json",
    ...authHeaders(token),
  };

  useEffect(() => {
    if (!token) {
      setError("Please log in to view settings");
      setLoading(false);
      return;
    }
    
    fetch(`${API_URL}/onboarding/config`, { headers: authHeaders(token) })
      .then((r) => {
        if (!r.ok) {
          if (r.status === 401) {
            setError("Please log in again");
            return;
          }
          throw new Error(`HTTP ${r.status}`);
        }
        return r.json();
      })
      .then((data) => {
        if (data) {
          setConfig(data);
          if (data.telegram?.channels?.length)
            setTgChannels(data.telegram.channels);
          if (data.youtube?.video_ids?.length)
            setYtVideoIds(data.youtube.video_ids);
          if (data.twitter?.queries?.length) setTwQueries(data.twitter.queries);
          if (data.reddit?.subreddits?.length) setRdSubreddits(data.reddit.subreddits);
        }
      })
      .catch((error) => {
        console.error("Settings config error:", error);
        setError("Failed to load config. Please try logging out and back in.");
      })
      .finally(() => setLoading(false));
  }, [token]);

  const saveSection = async (section) => {
    setSaving(true);
    setSaved("");
    setError("");
    try {
      let url, body;
      if (section === "telegram") {
        url = `${API_URL}/onboarding/telegram/channels`;
        body = JSON.stringify(tgChannels.filter((c) => c.trim()));
      } else if (section === "youtube") {
        url = `${API_URL}/onboarding/youtube`;
        body = JSON.stringify({
          video_ids: ytVideoIds.filter((v) => v.trim()),
        });
      } else if (section === "twitter") {
        url = `${API_URL}/onboarding/twitter`;
        body = JSON.stringify({
          queries: twQueries.filter((q) => q.trim()),
        });
      } else if (section === "reddit") {
        url = `${API_URL}/onboarding/reddit`;
        body = JSON.stringify({
          subreddits: rdSubreddits.filter((s) => s.trim()),
        });
      }
      const res = await fetch(url, { method: "POST", headers, body });
      if (!res.ok) throw new Error("Save failed");
      setSaved(section);
      setTimeout(() => setSaved(""), 2000);
    } catch (err) {
      setError(err.message);
    }
    setSaving(false);
  };

  const addItem = (list, setList) => setList([...list, ""]);
  const removeItem = (list, setList, idx) =>
    setList(list.filter((_, i) => i !== idx));
  const updateItem = (list, setList, idx, val) =>
    setList(list.map((v, i) => (i === idx ? val : v)));

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-neutral-950">
        <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />
      </div>
    );
  }

  return (
    <main className="max-w-2xl mx-auto px-4 py-8 space-y-6">
      <div className="flex items-center gap-3">
        <Link
          href="/"
          className="p-2 rounded-lg border border-neutral-800 bg-neutral-900 text-neutral-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" />
        </Link>
        <h1 className="text-xl font-bold text-white">Settings</h1>
      </div>

      {error && (
        <div className="p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Telegram */}
      <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <MessageCircle className="w-5 h-5 text-blue-400" />
            <h2 className="font-semibold text-white">Telegram Channels</h2>
          </div>
          {config?.telegram?.validated && (
            <span className="flex items-center gap-1 text-xs text-green-400">
              <Shield className="w-3 h-3" /> Connected
            </span>
          )}
        </div>
        {tgChannels.map((ch, i) => (
          <div key={i} className="flex gap-2">
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
        <div className="flex items-center justify-between">
          <button
            onClick={() => addItem(tgChannels, setTgChannels)}
            className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <Plus className="w-3 h-3" /> Add channel
          </button>
          <button
            onClick={() => saveSection("telegram")}
            disabled={saving}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white text-sm rounded-lg flex items-center gap-1.5 transition"
          >
            {saved === "telegram" ? (
              <><Check className="w-3.5 h-3.5" /> Saved</>
            ) : (
              <><Save className="w-3.5 h-3.5" /> Save</>
            )}
          </button>
        </div>
      </section>

      {/* YouTube */}
      <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Youtube className="w-5 h-5 text-red-500" />
          <h2 className="font-semibold text-white">YouTube Video IDs</h2>
        </div>
        {ytVideoIds.map((vid, i) => (
          <div key={i} className="flex gap-2">
            <input
              placeholder="e.g. dQw4w9WgXcQ"
              value={vid}
              onChange={(e) =>
                updateItem(ytVideoIds, setYtVideoIds, i, e.target.value)
              }
              className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
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
        <div className="flex items-center justify-between">
          <button
            onClick={() => addItem(ytVideoIds, setYtVideoIds)}
            className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <Plus className="w-3 h-3" /> Add video
          </button>
          <button
            onClick={() => saveSection("youtube")}
            disabled={saving}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white text-sm rounded-lg flex items-center gap-1.5 transition"
          >
            {saved === "youtube" ? (
              <><Check className="w-3.5 h-3.5" /> Saved</>
            ) : (
              <><Save className="w-3.5 h-3.5" /> Save</>
            )}
          </button>
        </div>
      </section>

      {/* Twitter */}
      <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <Twitter className="w-5 h-5 text-sky-400" />
          <h2 className="font-semibold text-white">Twitter / X Queries</h2>
        </div>
        {twQueries.map((q, i) => (
          <div key={i} className="flex gap-2">
            <input
              placeholder="e.g. #Nifty50"
              value={q}
              onChange={(e) =>
                updateItem(twQueries, setTwQueries, i, e.target.value)
              }
              className="flex-1 px-3 py-2 bg-neutral-800 border border-neutral-700 rounded-lg text-white text-sm placeholder-neutral-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
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
        <div className="flex items-center justify-between">
          <button
            onClick={() => addItem(twQueries, setTwQueries)}
            className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <Plus className="w-3 h-3" /> Add query
          </button>
          <button
            onClick={() => saveSection("twitter")}
            disabled={saving}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white text-sm rounded-lg flex items-center gap-1.5 transition"
          >
            {saved === "twitter" ? (
              <><Check className="w-3.5 h-3.5" /> Saved</>
            ) : (
              <><Save className="w-3.5 h-3.5" /> Save</>
            )}
          </button>
        </div>
      </section>

      {/* Reddit */}
      <section className="bg-neutral-900 border border-neutral-800 rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3">
          <svg className="w-5 h-5 text-orange-500" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 0 1-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 0 1 .042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 0 1 4.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 0 1 .14-.197.35.35 0 0 1 .238-.042l2.906.617a1.214 1.214 0 0 1 1.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 0 0-.231.094.33.33 0 0 0 0 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 0 0 .029-.463.33.33 0 0 0-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 0 0-.232-.095z"/>
          </svg>
          <h2 className="font-semibold text-white">Reddit Subreddits</h2>
        </div>
        {rdSubreddits.map((sub, i) => (
          <div key={i} className="flex gap-2">
            <div className="flex-1 flex items-center bg-neutral-800 border border-neutral-700 rounded-lg overflow-hidden">
              <span className="pl-3 text-neutral-500 text-sm">r/</span>
              <input
                placeholder="e.g. IndianStreetBets"
                value={sub}
                onChange={(e) =>
                  updateItem(rdSubreddits, setRdSubreddits, i, e.target.value)
                }
                className="flex-1 px-2 py-2 bg-transparent text-white text-sm placeholder-neutral-500 focus:outline-none"
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
        <div className="flex items-center justify-between">
          <button
            onClick={() => addItem(rdSubreddits, setRdSubreddits)}
            className="text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
          >
            <Plus className="w-3 h-3" /> Add subreddit
          </button>
          <button
            onClick={() => saveSection("reddit")}
            disabled={saving}
            className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 disabled:bg-neutral-700 text-white text-sm rounded-lg flex items-center gap-1.5 transition"
          >
            {saved === "reddit" ? (
              <><Check className="w-3.5 h-3.5" /> Saved</>
            ) : (
              <><Save className="w-3.5 h-3.5" /> Save</>
            )}
          </button>
        </div>
      </section>

      <p className="text-xs text-neutral-500 text-center">
        Leave fields empty to use default hardcoded channels/queries.
      </p>
    </main>
  );
}
