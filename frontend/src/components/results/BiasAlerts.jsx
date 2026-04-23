import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { AlertTriangle, Info, ShieldAlert } from 'lucide-react';

const toneClasses = {
  info: 'border-sky-500/30 bg-sky-500/5 text-sky-600 dark:text-sky-400',
  warn: 'border-amber-500/30 bg-amber-500/5 text-amber-600 dark:text-amber-400',
  high: 'border-rose-500/40 bg-rose-500/5 text-rose-600 dark:text-rose-400',
};
const Icon = { info: Info, warn: AlertTriangle, high: ShieldAlert };

const BiasAlerts = ({ flags }) => {
  if (!Array.isArray(flags) || flags.length === 0) return null;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-bias-alerts">
      <div className="mb-3 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-amber-500/15 text-amber-500 ring-1 ring-amber-500/30">
          <AlertTriangle className="h-4 w-4" />
        </span>
        <div>
          <h3 className="text-base font-semibold">Things to double‑check</h3>
          <p className="text-xs text-muted-foreground">Possible inconsistencies we spotted in your inputs.</p>
        </div>
      </div>
      <div className="space-y-2">
        {flags.map((f, i) => {
          const tone = toneClasses[f.severity] || toneClasses.warn;
          const I = Icon[f.severity] || AlertTriangle;
          return (
            <div key={i} className={`rounded-xl border p-3 text-sm ${tone}`}>
              <div className="flex items-start gap-2">
                <I className="mt-0.5 h-4 w-4 shrink-0" />
                <div className="min-w-0">
                  <div className="text-sm font-semibold text-foreground">{f.title}</div>
                  <div className="mt-0.5 text-xs text-foreground/80">{f.message}</div>
                </div>
                <Badge variant="secondary" className="ml-auto shrink-0 rounded-full text-[10px] uppercase">
                  {f.severity}
                </Badge>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default BiasAlerts;
