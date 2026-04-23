import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { motion } from 'framer-motion';
import { stagger, fadeUp } from '@/lib/motion';
import { Flag, Clock, DollarSign, Wrench, CheckCircle2, Zap } from 'lucide-react';

const priorityColor = (p) =>
  p === 'High'
    ? 'bg-rose-500/15 text-rose-500 ring-rose-500/30'
    : p === 'Medium'
    ? 'bg-amber-500/15 text-amber-500 ring-amber-500/30'
    : 'bg-emerald-500/15 text-emerald-500 ring-emerald-500/30';

const ExecutionPlanCard = ({ plan, best }) => {
  if (!plan) return null;
  return (
    <div className="space-y-5" data-testid="results-execution-plan">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div className="min-w-0">
            <Badge variant="secondary" className="rounded-full">
              <Flag className="mr-1.5 h-3 w-3" /> Execution plan
            </Badge>
            <h3 className="mt-3 text-lg font-semibold tracking-tight sm:text-xl">{plan.title}</h3>
            {best?.title && (
              <p className="mt-1 text-xs text-muted-foreground">For option: <span className="font-medium">{best.title}</span></p>
            )}
          </div>
          {plan.total_timeline && (
            <div className="rounded-xl border border-border/70 bg-background/50 px-4 py-3 text-center">
              <div className="text-[10px] uppercase tracking-widest text-muted-foreground">Total</div>
              <div className="mt-0.5 text-sm font-semibold">{plan.total_timeline}</div>
            </div>
          )}
        </div>
      </Card>

      {/* Steps timeline */}
      <motion.ol
        initial="initial"
        animate="animate"
        variants={stagger(0.06)}
        className="relative space-y-3 border-l border-border/70 pl-5"
      >
        {(plan.steps || []).map((s, i) => (
          <motion.li
            key={i}
            variants={fadeUp}
            className="relative"
            data-testid={`results-plan-step-${i}"`}
          >
            <span className="absolute -left-[26px] grid h-6 w-6 place-items-center rounded-full border border-primary/40 bg-primary/10 text-[11px] font-bold text-primary">
              {s.step || i + 1}
            </span>
            <Card className="rounded-2xl border-border/70 bg-card/60 p-4 sm:p-5">
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold sm:text-base">{s.action}</div>
                  <div className="mt-1 flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
                    {s.timeline && (
                      <span className="inline-flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {s.timeline}
                      </span>
                    )}
                    {s.priority && (
                      <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 ring-1 ${priorityColor(s.priority)}`}>
                        {s.priority}
                      </span>
                    )}
                  </div>
                </div>
                <div className="flex shrink-0 flex-col items-end gap-1 text-right text-xs">
                  {s.est_cost && (
                    <span className="inline-flex items-center gap-1 text-muted-foreground">
                      <DollarSign className="h-3 w-3" />
                      {s.est_cost}
                    </span>
                  )}
                  {s.est_benefit && (
                    <span className="inline-flex max-w-[220px] items-center gap-1 text-emerald-500">
                      <CheckCircle2 className="h-3 w-3" />
                      <span className="truncate">{s.est_benefit}</span>
                    </span>
                  )}
                </div>
              </div>
              {Array.isArray(s.tools) && s.tools.length > 0 && (
                <div className="mt-3 flex flex-wrap items-center gap-1.5">
                  <Wrench className="h-3 w-3 text-muted-foreground" />
                  {s.tools.map((t, ti) => (
                    <span key={ti} className="rounded-md border border-border/60 bg-background/40 px-1.5 py-0.5 text-[11px] text-muted-foreground">
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </Card>
          </motion.li>
        ))}
      </motion.ol>

      {/* Short-term + moderate benefits */}
      <div className="grid gap-4 sm:grid-cols-2">
        {plan.short_term_plan && (
          <Card className="rounded-2xl border-border/70 bg-card/60 p-5">
            <div className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-primary">
              <Zap className="h-3.5 w-3.5" /> Quick wins (1–2 weeks)
            </div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{plan.short_term_plan}</p>
          </Card>
        )}
        {plan.moderate_benefits && (
          <Card className="rounded-2xl border-border/70 bg-card/60 p-5">
            <div className="inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-500">
              <CheckCircle2 className="h-3.5 w-3.5" /> Moderate‑effort benefits
            </div>
            <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{plan.moderate_benefits}</p>
          </Card>
        )}
      </div>
    </div>
  );
};

export default ExecutionPlanCard;
