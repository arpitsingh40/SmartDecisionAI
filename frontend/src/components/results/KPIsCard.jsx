import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, Target, Zap } from 'lucide-react';

const KPIsCard = ({ kpis }) => {
  if (!Array.isArray(kpis) || kpis.length === 0) return null;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-kpis">
      <div className="mb-3 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
          <Activity className="h-4 w-4" />
        </span>
        <div>
          <h3 className="text-base font-semibold">Live tracking metrics</h3>
          <p className="text-xs text-muted-foreground">Track these to know if execution is working.</p>
        </div>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {kpis.map((k, i) => (
          <div key={i} className="rounded-xl border border-border/60 bg-background/40 p-4" data-testid={`kpi-item-${i}`}>
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="text-sm font-semibold">{k.name}</div>
                <div className="mt-0.5 text-xs text-muted-foreground">{k.how_to_measure}</div>
              </div>
              {k.leading_indicator && (
                <Badge variant="secondary" className="rounded-full text-[10px]">
                  <Zap className="mr-1 h-3 w-3" /> Leading
                </Badge>
              )}
            </div>
            {k.target && (
              <div className="mt-3 flex items-center gap-2 rounded-lg border border-primary/30 bg-primary/5 px-2.5 py-1.5 text-xs text-primary">
                <Target className="h-3 w-3" />
                Target: <span className="font-semibold tabular-nums">{k.target}</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
};

export default KPIsCard;
