import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Sparkles, RotateCcw, Wand2, Zap, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { motion } from 'framer-motion';

const WhatIfPanel = ({ decision, answers, onRun, loading, currentResult, originalResult }) => {
  const [mutated, setMutated] = useState(() => JSON.parse(JSON.stringify(answers || [])));
  const [autoRun, setAutoRun] = useState(false);
  const debounceRef = useRef(null);

  const setAt = (i, value) => {
    setMutated((arr) => {
      const copy = [...arr];
      copy[i] = { ...copy[i], answer: value };
      return copy;
    });
  };

  // Debounced auto re-run when enabled
  useEffect(() => {
    if (!autoRun) return;
    if (loading) return;
    // only run if something actually changed
    const changed = JSON.stringify(mutated) !== JSON.stringify(answers);
    if (!changed) return;
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      onRun(mutated);
    }, 1200);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mutated, autoRun]);

  const deltas = useMemo(() => {
    if (!currentResult || !originalResult) return {};
    const map = {};
    (currentResult.options || []).forEach((o) => {
      const orig = (originalResult.options || []).find((x) => x.title === o.title);
      if (orig) {
        map[o.title] = {
          delta: o.score - orig.score,
          original: orig.score,
          current: o.score,
        };
      }
    });
    return map;
  }, [currentResult, originalResult]);

  // Sensitivity = the answer whose change correlates most with best-option-change (heuristic label)
  const sensitivityNote = useMemo(() => {
    if (!currentResult || !originalResult) return null;
    // Compare best_option_id to detect if the optimal choice flipped
    if (currentResult.best_option_id !== originalResult.best_option_id) {
      const newBest = (currentResult.options || []).find((o) => o.id === currentResult.best_option_id);
      const oldBest = (originalResult.options || []).find((o) => o.id === originalResult.best_option_id);
      return {
        kind: 'flip',
        text: `The best option flipped: from “${oldBest?.title || '—'}” to “${newBest?.title || '—'}”.`,
      };
    }
    const bigSwings = Object.entries(deltas).filter(([, v]) => Math.abs(v.delta) >= 10);
    if (bigSwings.length) {
      return {
        kind: 'swing',
        text: `${bigSwings.length} option(s) moved by 10+ points. The ranking is sensitive to your recent changes.`,
      };
    }
    if (Object.keys(deltas).length) {
      return {
        kind: 'stable',
        text: 'Scores are stable within a few points. Your decision is robust to small input changes.',
      };
    }
    return null;
  }, [currentResult, originalResult, deltas]);

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12" data-testid="results-whatif-panel">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6 lg:col-span-7">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-semibold">Adjust your answers</h3>
            <p className="text-xs text-muted-foreground">Tweak values and re‑analyze. Turn on Live mode to auto‑rerun after changes.</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 rounded-full border border-border/60 bg-background/40 px-3 py-1.5 text-xs">
              <Zap className="h-3.5 w-3.5" /> Live
              <Switch checked={autoRun} onCheckedChange={setAutoRun} data-testid="whatif-live-toggle" />
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMutated(JSON.parse(JSON.stringify(answers || [])))}
              className="gap-1.5"
              data-testid="whatif-reset-button"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Reset
            </Button>
            <Button
              onClick={() => onRun(mutated)}
              disabled={loading}
              className="gap-2"
              data-testid="whatif-run-button"
            >
              {loading ? <Wand2 className="h-4 w-4 animate-pulse" /> : <Sparkles className="h-4 w-4" />}
              {loading ? 'Running…' : 'Re‑analyze'}
            </Button>
          </div>
        </div>
        <div className="mt-5 space-y-4">
          {(mutated || []).map((a, i) => (
            <div key={i} className="rounded-xl border border-border/60 bg-background/40 p-4">
              <div className="mb-2 text-sm font-medium">{a.question}</div>
              <WhatIfInput answer={a} onChange={(v) => setAt(i, v)} />
            </div>
          ))}
        </div>
      </Card>

      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6 lg:col-span-5">
        <div className="flex items-center justify-between">
          <h3 className="text-base font-semibold">Live scores</h3>
          {typeof currentResult?.confidence === 'number' && (
            <Badge variant="secondary" className="rounded-full">
              Confidence {currentResult.confidence}%
            </Badge>
          )}
        </div>
        <p className="mt-1 text-xs text-muted-foreground">Differences vs your original analysis.</p>
        <div className="mt-4 space-y-2">
          {(currentResult?.options || []).map((o) => {
            const d = deltas[o.title]?.delta ?? 0;
            const color = d > 0 ? 'text-emerald-500' : d < 0 ? 'text-rose-500' : 'text-muted-foreground';
            const Icon = d > 0 ? TrendingUp : d < 0 ? TrendingDown : Minus;
            return (
              <motion.div
                key={o.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 px-3 py-2"
                data-testid={`whatif-score-${o.id}`}
              >
                <div className="min-w-0 flex-1 truncate text-sm">{o.title}</div>
                <div className="text-sm font-semibold tabular-nums">{o.score}</div>
                <div className={`inline-flex w-16 items-center justify-end gap-1 text-right text-xs tabular-nums ${color}`}>
                  <Icon className="h-3 w-3" />
                  <span>{d > 0 ? `+${d}` : d}</span>
                </div>
              </motion.div>
            );
          })}
        </div>
        {sensitivityNote && (
          <div
            className={`mt-4 rounded-lg border px-3 py-2 text-xs leading-relaxed ${
              sensitivityNote.kind === 'flip'
                ? 'border-amber-500/40 bg-amber-500/5 text-amber-700 dark:text-amber-300'
                : sensitivityNote.kind === 'swing'
                ? 'border-primary/40 bg-primary/5 text-foreground/90'
                : 'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400'
            }`}
            data-testid="whatif-sensitivity-note"
          >
            {sensitivityNote.text}
          </div>
        )}
      </Card>
    </div>
  );
};

const WhatIfInput = ({ answer, onChange }) => {
  const { type, answer: v } = answer;
  if (type === 'slider' || typeof v === 'number') {
    return (
      <div>
        <div className="mb-2 text-sm tabular-nums text-primary">{Number(v)}</div>
        <Slider
          min={0}
          max={10}
          step={1}
          value={[Number(v) || 0]}
          onValueChange={(arr) => onChange(arr[0])}
        />
      </div>
    );
  }
  if (type === 'multi_choice' && Array.isArray(v)) {
    return (
      <Input value={v.join(', ')} onChange={(e) => onChange(e.target.value.split(',').map((s) => s.trim()).filter(Boolean))} />
    );
  }
  return <Input value={String(v ?? '')} onChange={(e) => onChange(e.target.value)} />;
};

export default WhatIfPanel;
