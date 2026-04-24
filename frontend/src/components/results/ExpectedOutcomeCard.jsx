import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { DollarSign, PiggyBank, Clock, Sparkles } from 'lucide-react';

const MoneyRow = ({ label, range, icon: Icon, tone = 'emerald' }) => {
  if (!range) return null;
  const has = range.realistic_low || range.realistic_high || range.best_case;
  if (!has) return null;
  const toneClass =
    tone === 'emerald'
      ? 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 ring-emerald-500/30'
      : 'bg-sky-500/10 text-sky-600 dark:text-sky-400 ring-sky-500/30';
  return (
    <div className="rounded-xl border border-border/60 bg-background/40 p-4">
      <div className="flex items-center gap-2">
        <span className={`grid h-8 w-8 place-items-center rounded-lg ring-1 ${toneClass}`}>
          <Icon className="h-4 w-4" />
        </span>
        <div className="text-[11px] uppercase tracking-widest text-muted-foreground">{label}</div>
      </div>
      <div className="mt-3 grid grid-cols-3 gap-2 text-center">
        <Col label="Realistic low" value={range.realistic_low} />
        <Col label="Realistic high" value={range.realistic_high} />
        <Col label="Best case" value={range.best_case} emphasize />
      </div>
      {range.note && (
        <div className="mt-3 rounded-lg border border-border/60 bg-background/40 p-2 text-[11px] text-muted-foreground">
          {range.note}
        </div>
      )}
    </div>
  );
};

const Col = ({ label, value, emphasize }) => (
  <div className="rounded-lg border border-border/60 bg-background/40 p-2">
    <div className="text-[10px] uppercase tracking-widest text-muted-foreground">{label}</div>
    <div className={`mt-0.5 text-sm tabular-nums ${emphasize ? 'font-semibold text-primary' : 'font-medium'}`}>
      {value || '—'}
    </div>
  </div>
);

const ExpectedOutcomeCard = ({ outcome }) => {
  if (!outcome) return null;
  const anyMoney = outcome.revenue_increase || outcome.cost_savings;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-expected-outcome">
      <div className="mb-3 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
          <Sparkles className="h-4 w-4" />
        </span>
        <div>
          <h3 className="text-base font-semibold">Expected outcome</h3>
          <p className="text-xs text-muted-foreground">Quantified impact of the best decision.</p>
        </div>
      </div>
      <div className="space-y-3">
        <MoneyRow label="Revenue increase" range={outcome.revenue_increase} icon={DollarSign} tone="emerald" />
        <MoneyRow label="Cost savings" range={outcome.cost_savings} icon={PiggyBank} tone="sky" />
        {outcome.time_saved && (
          <div className="flex items-center justify-between rounded-xl border border-border/60 bg-background/40 p-3">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-primary" />
              <div className="text-sm font-medium">Time saved</div>
            </div>
            <Badge variant="secondary" className="rounded-full">
              {outcome.time_saved}
            </Badge>
          </div>
        )}
        {Array.isArray(outcome.non_financial) && outcome.non_financial.length > 0 && (
          <div className="rounded-xl border border-border/60 bg-background/40 p-3">
            <div className="text-[11px] uppercase tracking-widest text-muted-foreground">Non‑financial wins</div>
            <ul className="mt-2 space-y-1.5 text-sm">
              {outcome.non_financial.map((x, i) => (
                <li key={i} className="flex items-start gap-2">
                  <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary/60" />
                  <span>{x}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {!anyMoney && (!outcome.time_saved) && (
          <div className="rounded-lg border border-dashed border-border/60 bg-background/40 p-3 text-center text-xs text-muted-foreground">
            No quantified outcome provided.
          </div>
        )}
      </div>
    </Card>
  );
};

export default ExpectedOutcomeCard;
