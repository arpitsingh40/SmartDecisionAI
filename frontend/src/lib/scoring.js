/**
 * Client-side scoring engine.
 * Score = sum(weight_i × rating_i) / sum(weight_i) × 10  → normalized 0-100.
 * This is instant, deterministic, and reruns on any weight change.
 */

export const DEFAULT_FACTORS = [
  { name: 'Money', description: 'Cost, value for money, and financial return.', default_weight: 70 },
  { name: 'Growth', description: 'Personal, career, or skill growth.', default_weight: 65 },
  { name: 'Stability', description: 'Risk and predictability.', default_weight: 60 },
  { name: 'Happiness', description: 'Day-to-day satisfaction and well‑being.', default_weight: 55 },
];

export function normalizeWeights(factors) {
  const total = (factors || []).reduce((s, f) => s + (Number(f.weight) || 0), 0);
  if (total <= 0) {
    return (factors || []).map((f) => ({ ...f, norm: 1 / Math.max(1, factors.length) }));
  }
  return (factors || []).map((f) => ({ ...f, norm: (Number(f.weight) || 0) / total }));
}

/**
 * Compute a single option's weighted score 0-100.
 * Falls back to option.score if ratings are missing.
 */
export function computeOptionScore(option, factors) {
  const ratings = option?.factor_ratings || {};
  const nf = normalizeWeights(factors);
  const hasAny = nf.some((f) => typeof ratings[f.name] === 'number');
  if (!hasAny) return typeof option?.score === 'number' ? option.score : 0;
  let s = 0;
  for (const f of nf) {
    const r = Number(ratings[f.name]);
    if (!Number.isFinite(r)) continue;
    s += (f.norm || 0) * r;
  }
  // r is 0..10; normalize to 0..100
  return Math.round(Math.max(0, Math.min(100, s * 10)));
}

/**
 * Returns options with computed scores + ranking.
 */
export function scoreAndRank(options, factors) {
  const scored = (options || []).map((o) => ({
    ...o,
    computed_score: computeOptionScore(o, factors),
  }));
  // Best is highest computed_score (ties broken by original score)
  scored.sort((a, b) =>
    b.computed_score - a.computed_score || (b.score || 0) - (a.score || 0)
  );
  scored.forEach((o, i) => {
    o.computed_rank = i + 1;
  });
  return scored;
}

/**
 * Pick the best option after applying user weights. Returns the best option + id.
 */
export function pickBest(options, factors) {
  const ranked = scoreAndRank(options, factors);
  return ranked[0] || null;
}

export function confidenceLevel(confidence) {
  const c = Number(confidence) || 0;
  if (c >= 75) return { label: 'High', tone: 'emerald' };
  if (c >= 50) return { label: 'Medium', tone: 'amber' };
  return { label: 'Low', tone: 'rose' };
}
