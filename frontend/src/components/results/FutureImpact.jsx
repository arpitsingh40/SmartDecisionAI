import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CalendarDays, CalendarRange, Trophy } from 'lucide-react';

const FutureImpact = ({ options, bestId }) => {
  if (!options?.length) return null;
  return (
    <div className="space-y-4" data-testid="results-future-impact">
      {options.map((o) => {
        const fi = o.future_impact || {};
        if (!fi.one_year && !fi.five_year) return null;
        const isBest = o.id === bestId;
        return (
          <Card
            key={o.id}
            className={`rounded-2xl border p-5 sm:p-6 ${
              isBest ? 'border-primary/40 bg-primary/5 ring-1 ring-primary/20' : 'border-border/70 bg-card/60'
            }`}
            data-testid={`future-card-${o.id}`}
          >
            <div className="mb-3 flex items-center gap-2">
              {isBest && <Trophy className="h-4 w-4 text-primary" />}
              <h4 className="text-sm font-semibold sm:text-base">{o.title}</h4>
              {o.is_do_nothing && (
                <Badge variant="secondary" className="rounded-full text-[10px]">do nothing</Badge>
              )}
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              <Block icon={CalendarDays} label="In 1 year" text={fi.one_year} />
              <Block icon={CalendarRange} label="In 5 years" text={fi.five_year} />
            </div>
          </Card>
        );
      })}
    </div>
  );
};

const Block = ({ icon: Icon, label, text }) => (
  <div className="rounded-xl border border-border/60 bg-background/40 p-3">
    <div className="flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
      <Icon className="h-3.5 w-3.5" />
      {label}
    </div>
    <div className="mt-1.5 text-sm leading-relaxed">{text || '—'}</div>
  </div>
);

export default FutureImpact;
