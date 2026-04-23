import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { ChevronDown, ChevronUp, Check, Shield, TrendingUp, Clock, CheckCircle2, XCircle, Trophy } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const riskColor = (r) =>
  r === 'Low' ? 'text-emerald-500' : r === 'Medium' ? 'text-amber-500' : 'text-rose-500';

const OptionCard = ({ option, rank, isBest }) => {
  const [open, setOpen] = useState(isBest || rank === 1);
  return (
    <Card
      className={`overflow-hidden rounded-2xl border p-0 transition-shadow ${
        isBest ? 'border-primary/40 bg-primary/5 ring-1 ring-primary/20' : 'border-border/70 bg-card/60'
      }`}
      data-testid={`option-card-${option.id}`}
    >
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-4 px-5 py-4 text-left"
      >
        <div className={`grid h-9 w-9 shrink-0 place-items-center rounded-full ${
          isBest ? 'bg-primary text-primary-foreground' : 'bg-secondary text-foreground'
        }`}>
          {isBest ? <Trophy className="h-4 w-4" /> : <span className="text-xs font-semibold">{rank}</span>}
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <div className="truncate text-sm font-semibold sm:text-base">{option.title}</div>
            {isBest && (
              <Badge className="rounded-full bg-primary/15 text-primary" variant="secondary">
                Best
              </Badge>
            )}
          </div>
          <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
            <span className={`inline-flex items-center gap-1 ${riskColor(option.risk_level)}`}>
              <Shield className="h-3 w-3" /> {option.risk_level}
            </span>
            <span className="inline-flex items-center gap-1">
              <Clock className="h-3 w-3" /> short‑term
            </span>
            <span className="inline-flex items-center gap-1">
              <TrendingUp className="h-3 w-3" /> long‑term
            </span>
          </div>
          <div className="mt-2 flex items-center gap-3">
            <Progress value={option.score} className="h-1.5 flex-1" />
            <span className="w-10 shrink-0 text-right text-sm font-semibold tabular-nums">{option.score}</span>
          </div>
        </div>
        <div className="shrink-0">
          {open ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </div>
      </button>
      <AnimatePresence initial={false}>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            <div className="border-t border-border/60 px-5 py-4 text-sm">
              <p className="text-muted-foreground">{option.description}</p>
              <div className="mt-4 grid gap-4 sm:grid-cols-2">
                <div>
                  <div className="mb-2 inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-emerald-500">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Pros
                  </div>
                  <ul className="space-y-1.5 text-sm">
                    {option.pros?.map((p, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <Check className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-500" />
                        <span>{p}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="mb-2 inline-flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wider text-rose-500">
                    <XCircle className="h-3.5 w-3.5" /> Cons
                  </div>
                  <ul className="space-y-1.5 text-sm">
                    {option.cons?.map((c, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-rose-500" />
                        <span>{c}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
              <div className="mt-5 grid gap-3 sm:grid-cols-2">
                <div className="rounded-lg border border-border/60 bg-background/40 p-3">
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Short‑term (weeks–months)</div>
                  <div className="mt-1 text-sm">{option.short_term_outcome}</div>
                </div>
                <div className="rounded-lg border border-border/60 bg-background/40 p-3">
                  <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Long‑term (1–3 yrs)</div>
                  <div className="mt-1 text-sm">{option.long_term_outcome}</div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export default OptionCard;
