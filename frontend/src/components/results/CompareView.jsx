import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { Trophy, CheckCircle2, XCircle } from 'lucide-react';

const CompareView = ({ options, bestId }) => {
  const [selected, setSelected] = useState(() => options.slice(0, Math.min(3, options.length)).map((o) => o.id));

  const toggle = (id) => {
    setSelected((s) => {
      if (s.includes(id)) return s.filter((x) => x !== id);
      if (s.length >= 3) return s;
      return [...s, id];
    });
  };

  const picked = options.filter((o) => selected.includes(o.id));

  return (
    <div className="space-y-6" data-testid="results-compare-mode">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6">
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h3 className="text-base font-semibold">Pick up to 3 options to compare</h3>
            <p className="text-xs text-muted-foreground">{selected.length} selected · max 3</p>
          </div>
        </div>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
          {options.map((o) => {
            const isSel = selected.includes(o.id);
            const isBest = o.id === bestId;
            return (
              <label
                key={o.id}
                className={`flex cursor-pointer items-start gap-2 rounded-xl border px-3 py-2.5 text-sm transition-colors ${
                  isSel ? 'border-primary/50 bg-primary/5 ring-1 ring-primary/30' : 'border-border/70 bg-background/40'
                }`}
              >
                <Checkbox checked={isSel} onCheckedChange={() => toggle(o.id)} />
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="truncate font-medium">{o.title}</span>
                    {isBest && <Badge className="rounded-full bg-primary/15 text-primary" variant="secondary">Best</Badge>}
                  </div>
                  <div className="text-xs text-muted-foreground">Score {o.score} · Risk {o.risk_level}</div>
                </div>
              </label>
            );
          })}
        </div>
      </Card>

      <div className={`grid gap-4 ${picked.length <= 1 ? 'grid-cols-1' : picked.length === 2 ? 'grid-cols-1 md:grid-cols-2' : 'grid-cols-1 md:grid-cols-3'}`}>
        {picked.map((o) => (
          <Card key={o.id} className={`rounded-2xl border p-5 ${o.id === bestId ? 'border-primary/40 bg-primary/5' : 'border-border/70 bg-card/60'}`} data-testid={`compare-col-${o.id}`}>
            <div className="flex items-start justify-between">
              <div>
                {o.id === bestId && (
                  <Badge className="mb-2 rounded-full bg-primary/15 text-primary" variant="secondary">
                    <Trophy className="mr-1 h-3 w-3" /> Best
                  </Badge>
                )}
                <h4 className="text-sm font-semibold sm:text-base">{o.title}</h4>
              </div>
              <div className="text-right">
                <div className="text-[10px] uppercase tracking-widest text-muted-foreground">Score</div>
                <div className="text-2xl font-semibold tabular-nums">{o.score}</div>
              </div>
            </div>
            <p className="mt-2 text-xs text-muted-foreground">{o.description}</p>

            <div className="mt-4 grid grid-cols-2 gap-2 text-[11px]">
              <div className="rounded-md border border-border/60 bg-background/40 p-2">
                <div className="uppercase tracking-widest text-muted-foreground">Risk</div>
                <div className="mt-0.5 text-sm">{o.risk_level}</div>
              </div>
              <div className="rounded-md border border-border/60 bg-background/40 p-2">
                <div className="uppercase tracking-widest text-muted-foreground">Short‑term</div>
                <div className="mt-0.5 line-clamp-2 text-sm">{o.short_term_outcome}</div>
              </div>
            </div>

            <div className="mt-4">
              <div className="mb-1 inline-flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wider text-emerald-500">
                <CheckCircle2 className="h-3 w-3" /> Pros
              </div>
              <ul className="space-y-1 text-xs">
                {o.pros.map((p, i) => <li key={i} className="flex gap-1.5"><span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-emerald-500" />{p}</li>)}
              </ul>
            </div>
            <div className="mt-3">
              <div className="mb-1 inline-flex items-center gap-1 text-[11px] font-semibold uppercase tracking-wider text-rose-500">
                <XCircle className="h-3 w-3" /> Cons
              </div>
              <ul className="space-y-1 text-xs">
                {o.cons.map((p, i) => <li key={i} className="flex gap-1.5"><span className="mt-1 h-1 w-1 shrink-0 rounded-full bg-rose-500" />{p}</li>)}
              </ul>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default CompareView;
