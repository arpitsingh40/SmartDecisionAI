import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  ChevronDown, ChevronUp, Check, Shield, TrendingUp, Clock,
  CheckCircle2, XCircle, Trophy, Target, DollarSign, MapPin, Gauge,
  Users, History as HistoryIcon,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const riskColor = (r) =>
  r === 'Low' ? 'text-emerald-500' : r === 'Medium' ? 'text-amber-500' : 'text-rose-500';

const Stat = ({ icon: Icon, label, value }) => {
  if (value == null || value === '' || value === undefined) return null;
  return (
    <div className="rounded-lg border border-border/60 bg-background/40 p-2.5">
      <div className="flex items-center gap-1.5 text-[10px] uppercase tracking-widest text-muted-foreground">
        <Icon className="h-3 w-3" />
        {label}
      </div>
      <div className="mt-0.5 text-sm leading-snug">{value}</div>
    </div>
  );
};

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
          <div className="mt-1 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
            <span className={`inline-flex items-center gap-1 ${riskColor(option.risk_level)}`}>
              <Shield className="h-3 w-3" /> {option.risk_level}
            </span>
            {typeof option.success_probability === 'number' && (
              <span className="inline-flex items-center gap-1">
                <Target className="h-3 w-3" /> {option.success_probability}% success
              </span>
            )}
            {option.time_to_result && (
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3 w-3" /> {option.time_to_result}
              </span>
            )}
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

              {/* Extended stats grid */}
              <div className="mt-4 grid grid-cols-2 gap-2 sm:grid-cols-3">
                <Stat icon={Target} label="Success" value={typeof option.success_probability === 'number' ? `${option.success_probability}%` : null} />
                <Stat icon={TrendingUp} label="Expected return" value={option.expected_return} />
                <Stat icon={Clock} label="Time to result" value={option.time_to_result} />
                <Stat icon={Gauge} label="Easiness" value={typeof option.easiness === 'number' ? `${option.easiness}/100` : null} />
                <Stat icon={DollarSign} label="Cost : reward" value={option.financial_ratio} />
                <Stat icon={MapPin} label="Geography" value={option.geography} />
                <Stat icon={Users} label="Support" value={option.support} />
                <Stat icon={HistoryIcon} label="Track record" value={option.history} />
              </div>

              <div className="mt-5 grid gap-4 sm:grid-cols-2">
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

              {option.why_not && !isBest && (
                <div className="mt-5 rounded-lg border border-amber-500/30 bg-amber-500/5 p-3">
                  <div className="text-[11px] uppercase tracking-wider text-amber-600 dark:text-amber-400">Why not this one?</div>
                  <div className="mt-1 text-sm">{option.why_not}</div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </Card>
  );
};

export default OptionCard;
