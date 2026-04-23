import React, { useMemo, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { RotateCcw, TrendingUp, TrendingDown, Minus, Zap, Sparkles } from 'lucide-react';
import { motion } from 'framer-motion';
import ScoreBarChart from '@/components/results/ScoreBarChart';
import { normalizeWeights, scoreAndRank } from '@/lib/scoring';

/**
 * Fully client-side What-if:
 * - Sliders adjust factor weights
 * - Scores recompute INSTANTLY (no AI call)
 * - Sensitivity note: detects if best option flipped vs original weights
 */
const WhatIfPanel = ({ options, factorsInput, bestId }) => {
  const safeFactors = Array.isArray(factorsInput) ? factorsInput : [];
  const [weights, setWeights] = useState(() => safeFactors.map((f) => ({ ...f, weight: Number(f.weight) || 0 })));

  const recomputed = useMemo(() => scoreAndRank(options, weights), [options, weights]);
  const originalRanked = useMemo(() => scoreAndRank(options, safeFactors), [options, safeFactors]);

  const newBestId = recomputed[0]?.id;
  const originalBestId = originalRanked[0]?.id || bestId;

  const flipped = newBestId && originalBestId && newBestId !== originalBestId;

  const deltas = useMemo(() => {
    const map = {};
    originalRanked.forEach((o) => {
      const cur = recomputed.find((x) => x.id === o.id);
      if (cur) map[o.id] = cur.computed_score - o.computed_score;
    });
    return map;
  }, [recomputed, originalRanked]);

  const setWeight = (i, v) =>
    setWeights((prev) => prev.map((f, idx) => (idx === i ? { ...f, weight: v } : f)));

  const reset = () => setWeights(safeFactors.map((f) => ({ ...f, weight: Number(f.weight) || 0 })));

  const normalized = normalizeWeights(weights);

  if (!safeFactors.length) {
    return (
      <Card className="rounded-2xl border-border/70 bg-card/60 p-8 text-center" data-testid="whatif-no-factors">
        <Sparkles className="mx-auto mb-3 h-6 w-6 text-muted-foreground" />
        <p className="text-sm text-muted-foreground">This decision has no weighted factors. What‑if requires factors from the wizard’s priorities step.</p>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12" data-testid="results-whatif-panel">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6 lg:col-span-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold">Adjust your priorities</h3>
            <p className="text-xs text-muted-foreground">Scores recompute instantly — no AI call needed.</p>
          </div>
          <Button variant="ghost" size="sm" onClick={reset} className="gap-1.5" data-testid="whatif-reset-button">
            <RotateCcw className="h-3.5 w-3.5" /> Reset
          </Button>
        </div>
        <div className="mt-5 space-y-3">
          {weights.map((f, i) => (
            <div key={f.name} className="rounded-xl border border-border/60 bg-background/40 p-3">
              <div className="flex items-center justify-between">
                <div className="min-w-0">
                  <div className="text-sm font-medium">{f.name}</div>
                  <div className="text-[11px] text-muted-foreground">
                    {Math.round((normalized[i]?.norm || 0) * 100)}% of total
                  </div>
                </div>
                <div className="shrink-0 rounded-full bg-primary/15 px-2.5 py-0.5 text-sm font-semibold text-primary tabular-nums">
                  {Number(f.weight) || 0}
                </div>
              </div>
              <Slider
                className="mt-3"
                min={0}
                max={100}
                step={5}
                value={[Number(f.weight) || 0]}
                onValueChange={(arr) => setWeight(i, arr[0])}
                data-testid={`whatif-weight-slider-${i}`}
              />
            </div>
          ))}
        </div>
      </Card>

      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6 lg:col-span-7" data-testid="whatif-live-scores-card">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold">Live scores</h3>
            <p className="text-xs text-muted-foreground">Sensitivity to the weights you care about.</p>
          </div>
          {flipped && (
            <Badge className="rounded-full bg-amber-500/15 text-amber-600 dark:text-amber-400" variant="secondary">
              <Zap className="mr-1 h-3 w-3" /> Best option flipped
            </Badge>
          )}
        </div>

        <div className="mt-4">
          <ScoreBarChart options={recomputed} bestId={newBestId} />
        </div>

        <div className="mt-4 space-y-2">
          {recomputed.map((o) => {
            const d = deltas[o.id] ?? 0;
            const color = d > 0 ? 'text-emerald-500' : d < 0 ? 'text-rose-500' : 'text-muted-foreground';
            const Icon = d > 0 ? TrendingUp : d < 0 ? TrendingDown : Minus;
            return (
              <motion.div
                key={o.id}
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 px-3 py-2"
                data-testid={`whatif-score-${o.id}`}
              >
                <div className="min-w-0 flex-1 truncate text-sm">{o.title}</div>
                <div className="text-sm font-semibold tabular-nums">{o.computed_score}</div>
                <div className={`inline-flex w-16 items-center justify-end gap-1 text-right text-xs tabular-nums ${color}`}>
                  <Icon className="h-3 w-3" />
                  <span>{d > 0 ? `+${d}` : d}</span>
                </div>
              </motion.div>
            );
          })}
        </div>

        <div
          className={`mt-4 rounded-lg border px-3 py-2 text-xs leading-relaxed ${
            flipped
              ? 'border-amber-500/40 bg-amber-500/5 text-amber-700 dark:text-amber-300'
              : 'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400'
          }`}
          data-testid="whatif-sensitivity-note"
        >
          {flipped
            ? `Changing your weights flips the best option — your decision is sensitive to “${weights.map((w) => w.name).join(', ')}”.`
            : `The recommendation is stable across your current weight tweaks — robust decision.`}
        </div>
      </Card>
    </div>
  );
};

export default WhatIfPanel;
