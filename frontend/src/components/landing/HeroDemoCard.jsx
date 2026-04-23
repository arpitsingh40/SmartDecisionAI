import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Check, ChevronRight, ShieldAlert } from 'lucide-react';
import { motion } from 'framer-motion';

const HeroDemoCard = () => {
  return (
    <div className="relative">
      <div className="absolute -inset-4 -z-10 rounded-[2rem] bg-primary/10 blur-2xl" />
      <Card className="glass rounded-3xl border-border/70 p-5 shadow-[var(--shadow-2)]">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Decision</div>
            <div className="mt-1 text-sm font-semibold tracking-tight">
              Should I join the AI startup?
            </div>
          </div>
          <Badge className="rounded-full bg-primary/15 text-primary" variant="secondary">
            Confidence 87%
          </Badge>
        </div>

        <div className="mt-5 space-y-3">
          {[
            { t: 'Join with 6‑month safety net', s: 88, best: true, risk: 'Medium' },
            { t: 'Counter‑offer on equity', s: 82, risk: 'Medium' },
            { t: 'Stay & negotiate AI rotation', s: 45, risk: 'Low' },
          ].map((o, i) => (
            <motion.div
              key={o.t}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 + i * 0.08, duration: 0.3 }}
              className={`rounded-xl border p-3 ${
                o.best
                  ? 'border-primary/40 bg-primary/5 ring-1 ring-primary/30'
                  : 'border-border/70 bg-card/70'
              }`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm font-medium">
                  {o.best ? (
                    <span className="grid h-5 w-5 place-items-center rounded-full bg-primary text-[10px] font-bold text-primary-foreground">
                      <Check className="h-3 w-3" />
                    </span>
                  ) : (
                    <span className="grid h-5 w-5 place-items-center rounded-full border border-border text-[10px] text-muted-foreground">
                      {i + 1}
                    </span>
                  )}
                  <span className="truncate">{o.t}</span>
                </div>
                <span className="text-xs font-semibold tabular-nums">{o.s}</span>
              </div>
              <div className="mt-2 flex items-center gap-3">
                <Progress value={o.s} className="h-1.5" />
                <span className="inline-flex items-center gap-1 text-[11px] text-muted-foreground">
                  <ShieldAlert className="h-3 w-3" />
                  {o.risk}
                </span>
              </div>
            </motion.div>
          ))}
        </div>

        <div className="mt-5 flex items-center justify-between text-xs text-muted-foreground">
          <span>Live preview</span>
          <span className="inline-flex items-center gap-1">
            See full results <ChevronRight className="h-3 w-3" />
          </span>
        </div>
      </Card>
    </div>
  );
};

export default HeroDemoCard;
