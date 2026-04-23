import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Sparkles, Brain, ListChecks, Gauge } from 'lucide-react';

const PHRASES = [
  { icon: Brain, text: 'Weighing tradeoffs against your priorities…' },
  { icon: ListChecks, text: 'Generating 3–5 tailored options…' },
  { icon: Gauge, text: 'Scoring risks and outcomes…' },
  { icon: Sparkles, text: 'Finalizing the recommendation…' },
];

const AnalysisLoading = () => {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx((i) => (i + 1) % PHRASES.length), 1400);
    return () => clearInterval(t);
  }, []);
  const Cur = PHRASES[idx].icon;
  return (
    <Card
      className="rounded-2xl border-border/70 bg-card/60 p-8 backdrop-blur"
      data-testid="analysis-loading-state"
    >
      <div className="flex items-center gap-3 text-sm">
        <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary/15 text-primary">
          <Cur className="h-4 w-4" />
        </span>
        <span className="font-medium">{PHRASES[idx].text}</span>
      </div>
      <div className="mt-6 space-y-3">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="h-10 rounded-lg shimmer" />
        ))}
      </div>
      <div className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
        <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-primary" />
        <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-primary" style={{ animationDelay: '0.2s' }} />
        <span className="pulse-dot h-1.5 w-1.5 rounded-full bg-primary" style={{ animationDelay: '0.4s' }} />
        <span className="ml-2">This typically takes 10–30 seconds</span>
      </div>
    </Card>
  );
};

export default AnalysisLoading;
