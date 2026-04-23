import React, { useMemo, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Sparkles, RotateCcw, Wand2 } from 'lucide-react';
import { motion } from 'framer-motion';

const WhatIfPanel = ({ decision, answers, onRun, loading, currentResult, originalResult }) => {
  const [mutated, setMutated] = useState(() => JSON.parse(JSON.stringify(answers || [])));

  const setAt = (i, value) => {
    setMutated((arr) => {
      const copy = [...arr];
      copy[i] = { ...copy[i], answer: value };
      return copy;
    });
  };

  const deltas = useMemo(() => {
    if (!currentResult || !originalResult) return {};
    const map = {};
    (currentResult.options || []).forEach((o) => {
      const orig = (originalResult.options || []).find((x) => x.title === o.title);
      if (orig) map[o.title] = o.score - orig.score;
    });
    return map;
  }, [currentResult, originalResult]);

  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12" data-testid="results-whatif-panel">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6 lg:col-span-7">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold">Adjust your answers</h3>
            <p className="text-xs text-muted-foreground">Tweak values and re‑run the AI to see how scores change.</p>
          </div>
          <div className="flex items-center gap-2">
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
        <h3 className="text-base font-semibold">Live scores</h3>
        <p className="mt-1 text-xs text-muted-foreground">Differences vs your original analysis.</p>
        <div className="mt-4 space-y-3">
          {(currentResult?.options || []).map((o) => {
            const d = deltas[o.title] ?? 0;
            const color = d > 0 ? 'text-emerald-500' : d < 0 ? 'text-rose-500' : 'text-muted-foreground';
            return (
              <motion.div
                key={o.id}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 px-3 py-2"
              >
                <div className="min-w-0 flex-1 truncate text-sm">{o.title}</div>
                <div className="text-sm font-semibold tabular-nums">{o.score}</div>
                <div className={`w-12 text-right text-xs tabular-nums ${color}`}>
                  {d > 0 ? `+${d}` : d}
                </div>
              </motion.div>
            );
          })}
        </div>
        <div className="mt-4 flex items-center gap-2">
          <Badge variant="secondary" className="rounded-full">
            Confidence {currentResult?.confidence ?? 0}%
          </Badge>
        </div>
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
