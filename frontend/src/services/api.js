/**
 * Frontend API Service client for Multi-Agent Lead Generation System.
 */

// Relative by default so requests go through the Vite dev-server proxy
// (same-origin, no CORS). Set VITE_API_BASE to call a backend directly.
const API_BASE = import.meta.env.VITE_API_BASE || "/api";

export async function fetchStats() {
  const res = await fetch(`${API_BASE}/stats`);
  if (!res.ok) throw new Error("Failed to load dashboard statistics");
  return res.json();
}

export async function fetchLeads(params = {}) {
  const query = new URLSearchParams();
  if (params.category) query.append("category", params.category);
  if (params.status) query.append("status", params.status);
  if (params.review_status) query.append("review_status", params.review_status);
  if (params.search) query.append("search", params.search);

  const res = await fetch(`${API_BASE}/leads?${query.toString()}`);
  if (!res.ok) throw new Error("Failed to load leads");
  return res.json();
}

export async function fetchLeadDetail(leadId) {
  const res = await fetch(`${API_BASE}/leads/${leadId}`);
  if (!res.ok) throw new Error("Failed to load lead details");
  return res.json();
}

export async function updateLeadReview(leadId, reviewStatus, notes = null) {
  const res = await fetch(`${API_BASE}/leads/${leadId}/review`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ review_status: reviewStatus, notes }),
  });
  if (!res.ok) throw new Error("Failed to update lead review decision");
  return res.json();
}

export async function updateLead(leadId, data) {
  const res = await fetch(`${API_BASE}/leads/${leadId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update lead");
  return res.json();
}

export async function deleteLead(leadId) {
  const res = await fetch(`${API_BASE}/leads/${leadId}`, {
    method: "DELETE",
  });
  if (!res.ok) throw new Error("Failed to delete lead");
  return res.json();
}

export async function triggerPipelineRun(config = {}, sync = false) {
  const res = await fetch(`${API_BASE}/pipeline/run?sync=${sync}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      category: config.category || "Restaurants",
      location: config.location || "Downtown, CA",
      max_leads: config.max_leads || 5,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Pipeline trigger failed" }));
    throw new Error(err.detail || "Pipeline run failed");
  }
  return res.json();
}

export async function fetchPipelineStatus() {
  const res = await fetch(`${API_BASE}/pipeline/status`);
  if (!res.ok) return { is_running: false };
  return res.json();
}

export async function fetchSchedulerStatus() {
  const res = await fetch(`${API_BASE}/pipeline/scheduler`);
  if (!res.ok) throw new Error("Failed to load scheduler configuration");
  return res.json();
}

export async function updateSchedulerConfig(intervalHours, enabled = true) {
  const res = await fetch(`${API_BASE}/pipeline/scheduler`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ interval_hours: intervalHours, enabled }),
  });
  if (!res.ok) throw new Error("Failed to update scheduler");
  return res.json();
}

export function getPrototypeRenderUrl(leadId) {
  return `${API_BASE}/websites/${leadId}/render`;
}
