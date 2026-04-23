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

export async function analyzeDecision(decision, answers) {
  const { data } = await api.post('/decisions/analyze', { decision, answers });
  return data;
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
