import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
});

const GUEST_KEY = 'sda_guest_id';

export async function ensureGuestSession() {
  const cached = localStorage.getItem(GUEST_KEY);
  if (cached) return cached;
  const { data } = await api.post('/guest/session');
  localStorage.setItem(GUEST_KEY, data.guest_id);
  return data.guest_id;
}

export function getGuestId() {
  return localStorage.getItem(GUEST_KEY);
}

export async function fetchFollowUps(decision) {
  const { data } = await api.post('/decisions/followups', { decision });
  return data;
}

export async function analyzeDecision(decision, answers, onProgress) {
  // Start async job
  const { data: start } = await api.post('/decisions/analyze/start', { decision, answers });
  const jobId = start.job_id;
  const deadline = Date.now() + 150000; // 150s hard cap
  let delay = 1200;
  while (Date.now() < deadline) {
    await new Promise((r) => setTimeout(r, delay));
    try {
      const { data } = await api.get(`/decisions/analyze/status/${jobId}`);
      if (onProgress) onProgress(data);
      if (data.status === 'completed') return data.result;
      if (data.status === 'failed') {
        const err = new Error(data.error || 'Analysis failed');
        err.response = { data: { detail: data.error } };
        throw err;
      }
    } catch (e) {
      if (e?.response?.status === 404) {
        throw new Error('Job not found');
      }
      // transient network error — keep polling
      if (e.message && e.message.includes('Analysis failed')) throw e;
    }
    delay = Math.min(delay + 300, 2500);
  }
  throw new Error('Analysis timed out (please try again)');
}

export async function saveDecision({ guest_id, title, decision, answers, result }) {
  const { data } = await api.post('/decisions', { guest_id, title, decision, answers, result });
  return data;
}

export async function listDecisions(guestId) {
  const { data } = await api.get('/decisions', { params: { guest_id: guestId } });
  return data;
}

export async function getDecision(id, guestId) {
  const { data } = await api.get(`/decisions/${id}`, { params: { guest_id: guestId } });
  return data;
}

export async function deleteDecision(id, guestId) {
  const { data } = await api.delete(`/decisions/${id}`, { params: { guest_id: guestId } });
  return data;
}
