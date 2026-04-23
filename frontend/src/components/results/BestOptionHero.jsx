import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  Trophy, ShieldAlert, TrendingUp, Clock, Target, DollarSign, MapPin, Gauge, Sparkles,
} from 'lucide-react';
import { motion } from 'framer-motion';

const BestOptionHero = ({ best, reasoning, confidence }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card
        className="relative overflow-hidden rounded-2xl border-t-2 border-t-primary/60 bg-card/60 p-6 shadow-[var(--shadow-2)] backdrop-blur sm:p-8"
        data-testid="results-best-option-card"
      >
        <div className="pointer-events-none absolute -right-20 -top-20 h-56 w-56 rounded-full bg-primary/15 blur-3xl" />
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="min-w-0">
            <Badge className="rounded-full bg-primary/15 text-primary" variant="secondary">
              <Trophy className="mr-1.5 h-3 w-3" /> Best recommendation
            </Badge>
            <h2 className="font-display mt-3 text-2xl font-semibold tracking-tight sm:text-3xl" data-testid="results-best-option-title">
              {best.title}
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted-foreground sm:text-base">
              {best.description}
            </p>
          </div>
          <div className="min-w-[120px] rounded-xl border border-border/70 bg-background/50 p-4 text-center">
            <div className="text-[10px] uppercase tracking-widest text-muted-foreground">Score</div>
            <div className="font-display text-4xl font-semibold tabular-nums" data-testid="results-best-option-score">
              {best.computed_score ?? best.score}
            </div>
            <div className="mt-2 text-[10px] uppercase tracking-widest text-muted-foreground">/ 100</div>
          </div>
        </div>

        <div className="mt-4">
          <Progress value={best.computed_score ?? best.score} className="h-2" />
        </div>

        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Info icon={ShieldAlert} label="Risk" value={best.risk_level} />
          <Info icon={Target} label="Success probability" value={typeof best.success_probability === 'number' ? `${best.success_probability}%` : '—'} />
          <Info icon={Clock} label="Time to result" value={best.time_to_result || '—'} />
          <Info icon={TrendingUp} label="Expected return" value={best.expected_return || '—'} />
          {best.financial_ratio && <Info icon={DollarSign} label="Cost:reward" value={best.financial_ratio} />}
          {best.geography && <Info icon={MapPin} label="Geography" value={best.geography} />}
          {typeof best.easiness === 'number' && <Info icon={Gauge} label="Easiness" value={`${best.easiness}/100`} />}
          {typeof confidence === 'number' && <Info icon={Sparkles} label="Confidence" value={`${confidence}%`} />}
        </div>
      </Card>
    </motion.div>
  );
};

const Info = ({ icon: Icon, label, value }) => (
  <div className="rounded-xl border border-border/60 bg-background/40 p-3">
    <div className="flex items-center gap-2 text-[11px] uppercase tracking-widest text-muted-foreground">
      <Icon className="h-3.5 w-3.5" />
      {label}
    </div>
    <div className="mt-1 line-clamp-2 text-sm leading-snug">{value}</div>
  </div>
);

export default BestOptionHero;
