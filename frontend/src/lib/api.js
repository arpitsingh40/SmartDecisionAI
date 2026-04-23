import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

const AUTH_TOKEN_KEY = 'sda_auth_token';
const GUEST_KEY = 'sda_guest_id';

export const api = axios.create({
  baseURL: API,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
});

// Attach auth token if present
api.interceptors.request.use((config) => {
  try {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    if (token) {
      config.headers = { ...config.headers, Authorization: `Bearer ${token}` };
    }
  } catch {}
  return config;
});

// ================= Session / Guest =================
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

// ================= Auth =================
export function getAuthToken() {
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setAuthToken(token) {
  if (token) localStorage.setItem(AUTH_TOKEN_KEY, token);
  else localStorage.removeItem(AUTH_TOKEN_KEY);
}

export async function signup({ email, password, name }) {
  const { data } = await api.post('/auth/signup', { email, password, name });
  setAuthToken(data.token);
  return data.user;
}

export async function login({ email, password }) {
  const { data } = await api.post('/auth/login', { email, password });
  setAuthToken(data.token);
  return data.user;
}

export async function fetchMe() {
  const { data } = await api.get('/auth/me');
  return data;
}

export function logout() {
  setAuthToken(null);
}

// ================= AI decisions =================
export async function fetchFollowUps(decision) {
  const { data } = await api.post('/decisions/followups', { decision });
  return data;
}

export async function analyzeDecision(decision, answers, factors, onProgress) {
  const { data: start } = await api.post('/decisions/analyze/start', {
    decision,
    answers,
    factors: (factors || []).map((f) => ({ name: f.name, weight: Number(f.weight) || 0 })),
  });
  const jobId = start.job_id;
  const deadline = Date.now() + 180000; // 3 min hard cap
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
      if (e.message && e.message.includes('Analysis failed')) throw e;
    }
    delay = Math.min(delay + 300, 2500);
  }
  throw new Error('Analysis timed out (please try again)');
}

// ================= Saved decisions =================
export async function saveDecision({ guest_id, title, decision, answers, result }) {
  // Always send guest_id as a fallback; backend prefers user_id when a valid token is present.
  const body = { title, decision, answers, result };
  if (guest_id) body.guest_id = guest_id;
  const { data } = await api.post('/decisions', body);
  return data;
}

export async function listDecisions(guestId) {
  const params = {};
  if (guestId) params.guest_id = guestId;
  const { data } = await api.get('/decisions', { params });
  return data;
}

export async function getDecision(id, guestId) {
  const params = {};
  if (guestId) params.guest_id = guestId;
  const { data } = await api.get(`/decisions/${id}`, { params });
  return data;
}

export async function deleteDecision(id, guestId) {
  const params = {};
  if (guestId) params.guest_id = guestId;
  const { data } = await api.delete(`/decisions/${id}`, { params });
  return data;
}

// ================= Wizard draft (client-only) =================
const DRAFT_KEY = 'sda_wizard_draft_v1';

export function saveWizardDraft(draft) {
  try {
    localStorage.setItem(
      DRAFT_KEY,
      JSON.stringify({
        ...draft,
        ts: Date.now(),
      })
    );
  } catch {}
}

export function loadWizardDraft(maxAgeMs = 1000 * 60 * 60 * 24 * 7) {
  try {
    const raw = localStorage.getItem(DRAFT_KEY);
    if (!raw) return null;
    const obj = JSON.parse(raw);
    if (!obj || !obj.ts) return null;
    if (Date.now() - obj.ts > maxAgeMs) {
      localStorage.removeItem(DRAFT_KEY);
      return null;
    }
    return obj;
  } catch {
    return null;
  }
}

export function clearWizardDraft() {
  try {
    localStorage.removeItem(DRAFT_KEY);
  } catch {}
}
