import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, ShieldAlert, Activity, Trophy } from 'lucide-react';

const RiskScenarios = ({ options, bestId }) => {
  if (!options?.length) return null;
  return (
    <div className="space-y-4" data-testid="results-risk-scenarios">
      {options.map((o) => {
        const s = o.scenarios || {};
        if (!s.best_case && !s.worst_case && !s.most_likely) return null;
        const isBest = o.id === bestId;
        return (
          <Card
            key={o.id}
            className={`rounded-2xl border p-5 sm:p-6 ${
              isBest ? 'border-primary/40 bg-primary/5 ring-1 ring-primary/20' : 'border-border/70 bg-card/60'
            }`}
            data-testid={`risk-card-${o.id}`}
          >
            <div className="mb-3 flex items-center gap-2">
              {isBest && <Trophy className="h-4 w-4 text-primary" />}
              <h4 className="text-sm font-semibold sm:text-base">{o.title}</h4>
              {o.is_do_nothing && (
                <Badge variant="secondary" className="rounded-full text-[10px]">do nothing</Badge>
              )}
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              <Block icon={TrendingUp} label="Best case" text={s.best_case} tone="emerald" />
              <Block icon={Activity} label="Most likely" text={s.most_likely} tone="primary" />
              <Block icon={ShieldAlert} label="Worst case" text={s.worst_case} tone="rose" />
            </div>
          </Card>
        );
      })}
    </div>
  );
};

const toneClasses = {
  emerald: 'border-emerald-500/30 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400',
  primary: 'border-primary/30 bg-primary/5 text-primary',
  rose: 'border-rose-500/30 bg-rose-500/5 text-rose-600 dark:text-rose-400',
};

const Block = ({ icon: Icon, label, text, tone }) => (
  <div className={`rounded-xl border p-3 ${toneClasses[tone]}`}>
    <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider">
      <Icon className="h-3.5 w-3.5" />
      {label}
    </div>
    <div className="mt-1.5 text-sm leading-relaxed text-foreground/90">{text || '—'}</div>
  </div>
);

export default RiskScenarios;
