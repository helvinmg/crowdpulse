const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

function _dateParams(dateRange) {
  if (!dateRange) return "";
  const { start, end } = dateRange;
  let params = "";
  if (start) params += `&start=${start}`;
  if (end) params += `&end=${end}`;
  return params;
}

async function fetchJSON(path) {
  try {
    const url = `${API_URL}${path}`;
    console.log("[CrowdPulse] fetch:", url);
    
    // Get auth token
    const token = typeof window !== 'undefined' ? localStorage.getItem('crowdpulse_token') : null;
    console.log("[CrowdPulse] token present:", !!token);
    const headers = { 
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` })
    };
    console.log("[CrowdPulse] headers:", headers);
    
    const res = await fetch(url, { 
      cache: "no-store",
      headers 
    });
    console.log("[CrowdPulse] response status:", res.status, res.statusText);
    if (!res.ok) {
      console.error("[CrowdPulse] API error:", res.status, res.statusText, url);
      throw new Error(`API error: ${res.status} ${res.statusText}`);
    }
    const data = await res.json();
    console.log("[CrowdPulse] response data:", data);
    return data;
  } catch (err) {
    console.error("[CrowdPulse] fetch failed:", path, err.message);
    throw err;
  }
}

// Sentiment endpoints
export const getSentimentLatest = (symbol, hours = 24, dateRange = null, mode = null) =>
  fetchJSON(`/sentiment/latest/${symbol}?hours=${hours}${_dateParams(dateRange)}${mode ? `&mode=${mode}` : ''}`);

export const getSentimentTimeseries = (symbol, hours = 24, dateRange = null, mode = null) => {
  const path = `/sentiment/timeseries/${symbol}?hours=${hours}${_dateParams(dateRange)}${mode ? `&mode=${mode}` : ''}`;
  console.log("[getSentimentTimeseries] calling:", path);
  return fetchJSON(path);
};

export const getDiscussionVolume = (symbol, hours = 24, dateRange = null, mode = null) =>
  fetchJSON(`/sentiment/volume/${symbol}?hours=${hours}${_dateParams(dateRange)}${mode ? `&mode=${mode}` : ''}`);

// Divergence endpoints
export const getDivergenceLatest = (symbol, mode = null) =>
  fetchJSON(`/divergence/latest/${symbol}${mode ? `?mode=${mode}` : ''}`);

export const getDivergenceTimeseries = (symbol, hours = 72, dateRange = null, mode = null) =>
  fetchJSON(`/divergence/timeseries/${symbol}?hours=${hours}${_dateParams(dateRange)}${mode ? `&mode=${mode}` : ''}`);

export const getOverview = () =>
  fetchJSON("/divergence/overview");

export const getIndexSummary = (hours = 168, dateRange = null) =>
  fetchJSON(`/divergence/index-summary?hours=${hours}${_dateParams(dateRange)}`);

// Market endpoints
export const getPriceData = (symbol, days = 5) =>
  fetchJSON(`/market/price/${symbol}?days=${days}`);

// Usage & data mode endpoints
export const getApiUsage = () => fetchJSON("/usage");

export const getStats = (hours = 24, dateRange = null, mode = null) => 
  fetchJSON(`/stats?hours=${hours}${_dateParams(dateRange)}${mode ? `&mode=${mode}` : ''}`);

export const getUsageLogs = (limit = 100) => fetchJSON(`/usage/logs?limit=${limit}`);

export const getDataMode = () => fetchJSON("/data-mode");

export async function setDataMode(mode) {
  const res = await fetch(`${API_URL}/data-mode?mode=${mode}`, {
    method: "POST",
  });
  return res.json();
}

export async function triggerSeed() {
  const res = await fetch(`${API_URL}/seed`, { method: "POST" });
  return res.json();
}

// Pipeline run with SSE progress
export function runPipeline(onProgress, onDone, onError, hours = 24, dateRange = null) {
  const params = new URLSearchParams();
  params.append('hours', hours.toString());
  if (dateRange?.start) params.append('start', dateRange.start);
  if (dateRange?.end) params.append('end', dateRange.end);
  
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  
  fetch(`${API_URL}/pipeline/run?${params}`, { method: "POST", headers })
    .then((res) => {
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      function read() {
        reader.read().then(({ done, value }) => {
          if (done) {
            onDone?.();
            return;
          }
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n\n");
          buffer = lines.pop() || "";

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              try {
                const data = JSON.parse(line.slice(6));
                onProgress?.(data);
                if (data.done) {
                  onDone?.(data);
                }
              } catch {}
            }
          }
          read();
        });
      }
      read();
    })
    .catch((err) => {
      onError?.(err);
    });
}
