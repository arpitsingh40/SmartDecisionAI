import React, { useEffect, useMemo, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowLeft, ArrowRight, Plus, Sliders, Sparkles, Trash2, Wand2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { api } from '@/lib/api';
import { normalizeWeights, DEFAULT_FACTORS } from '@/lib/scoring';
import { toast } from 'sonner';

const PrioritiesStep = ({ decision, value, onChange, onNext, onBack }) => {
  const [loading, setLoading] = useState(false);
  const [factors, setFactors] = useState(value && value.length ? value : []);
  const [newName, setNewName] = useState('');

  useEffect(() => {
    // If no factors yet, ask AI to suggest them for THIS decision
    if (factors.length > 0) return;
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        const { data } = await api.post('/decisions/suggest-factors', { decision });
        if (cancelled) return;
        const suggested = (data.factors || []).map((f) => ({
          name: f.name,
          description: f.description,
          weight: f.default_weight ?? 50,
        }));
        setFactors(suggested.length ? suggested : DEFAULT_FACTORS.map((f) => ({ name: f.name, description: f.description, weight: f.default_weight })));
      } catch (e) {
        if (cancelled) return;
        toast.message('Using default factors (AI factor suggestion unavailable)');
        setFactors(DEFAULT_FACTORS.map((f) => ({ name: f.name, description: f.description, weight: f.default_weight })));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const totalWeight = useMemo(() => factors.reduce((s, f) => s + (Number(f.weight) || 0), 0), [factors]);
  const normalized = useMemo(() => normalizeWeights(factors), [factors]);

  const setFactorWeight = (idx, w) => {
    setFactors((prev) => prev.map((f, i) => (i === idx ? { ...f, weight: w } : f)));
  };
  const removeFactor = (idx) => setFactors((prev) => prev.filter((_, i) => i !== idx));
  const addFactor = () => {
    const n = (newName || '').trim();
    if (!n) return;
    if (factors.find((f) => f.name.toLowerCase() === n.toLowerCase())) {
      toast.error('Factor already exists');
      return;
    }
    setFactors((prev) => [...prev, { name: n, description: 'Custom factor.', weight: 50 }]);
    setNewName('');
  };

  const handleNext = () => {
    if (!factors.length) {
      toast.error('Add at least one factor to evaluate your options.');
      return;
    }
    onChange(factors);
    onNext();
  };

  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-6 shadow-[var(--shadow-1)] backdrop-blur sm:p-8" data-testid="wizard-priorities-step">
      <Badge variant="secondary" className="rounded-full">
        <Sliders className="mr-1.5 h-3 w-3" /> Your priorities
      </Badge>
      <h2 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
        What matters most to you here?
      </h2>
      <p className="mt-2 text-sm text-muted-foreground">
        I picked factors that fit this decision. Slide to weight what matters — your weights drive the scoring.
      </p>

      {loading ? (
        <div className="mt-6 space-y-3" data-testid="wizard-priorities-loading">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="h-16 rounded-xl shimmer" />
          ))}
          <div className="mt-2 flex items-center gap-2 text-sm text-muted-foreground">
            <Wand2 className="h-4 w-4 animate-pulse text-primary" />
            Picking the right factors for your decision…
          </div>
        </div>
      ) : (
        <>
          <AnimatePresence initial={false}>
            <motion.div
              layout
              className="mt-6 space-y-3"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
            >
              {factors.map((f, i) => (
                <motion.div
                  layout
                  key={f.name}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -4 }}
                  className="rounded-xl border border-border/70 bg-background/40 p-4"
                  data-testid={`wizard-priority-factor-${i}`}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <div className="text-sm font-semibold">{f.name}</div>
                      <div className="mt-0.5 text-xs text-muted-foreground">{f.description}</div>
                    </div>
                    <div className="flex shrink-0 items-center gap-2">
                      <span className="min-w-[44px] rounded-full bg-primary/15 px-2.5 py-0.5 text-center text-sm font-semibold text-primary tabular-nums">
                        {Math.round((normalized[i]?.norm || 0) * 100)}%
                      </span>
                      <Button variant="ghost" size="icon" aria-label="Remove factor" onClick={() => removeFactor(i)} data-testid={`wizard-priority-remove-${i}`}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="mt-3">
                    <Slider
                      min={0}
                      max={100}
                      step={5}
                      value={[Number(f.weight) || 0]}
                      onValueChange={(arr) => setFactorWeight(i, arr[0])}
                      data-testid={`wizard-priority-slider-${i}`}
                    />
                    <div className="mt-1 flex justify-between text-[10px] uppercase tracking-widest text-muted-foreground">
                      <span>doesn't matter</span>
                      <span>essential</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </AnimatePresence>

          <Separator className="my-5" />
          <div className="flex flex-wrap items-center gap-2">
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Add your own factor (e.g. Commute)"
              className="h-9 flex-1 bg-background/60"
              data-testid="wizard-priority-add-input"
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addFactor(); } }}
            />
            <Button variant="secondary" size="sm" className="h-9 gap-1.5" onClick={addFactor} data-testid="wizard-priority-add-button">
              <Plus className="h-3.5 w-3.5" /> Add
            </Button>
          </div>

          <div className="mt-4 rounded-lg border border-border/60 bg-background/40 p-3 text-xs text-muted-foreground">
            Raw weights: <span className="tabular-nums text-foreground/80">{totalWeight}</span>. Percentages are auto‑normalized across factors.
          </div>
        </>
      )}

      <div className="mt-8 flex items-center justify-between">
        <Button variant="ghost" onClick={onBack} className="gap-2" data-testid="wizard-priorities-back-button">
          <ArrowLeft className="h-4 w-4" /> Back
        </Button>
        <Button
          onClick={handleNext}
          disabled={loading || !factors.length}
          size="lg"
          className="gap-2"
          data-testid="wizard-priorities-next-button"
        >
          Continue <ArrowRight className="h-4 w-4" />
        </Button>
      </div>
    </Card>
  );
};

export default PrioritiesStep;
