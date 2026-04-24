import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Zap, Wand2, PlugZap } from 'lucide-react';

const AutomationCard = ({ ideas }) => {
  if (!Array.isArray(ideas) || ideas.length === 0) return null;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-automation-layer">
      <div className="mb-3 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
          <Zap className="h-4 w-4" />
        </span>
        <div>
          <h3 className="text-base font-semibold">Automation &amp; integration</h3>
          <p className="text-xs text-muted-foreground">Reduce manual work — prefer plug‑and‑play.</p>
        </div>
      </div>
      <div className="grid gap-2 sm:grid-cols-2">
        {ideas.map((a, i) => (
          <div key={i} className="rounded-xl border border-border/60 bg-background/40 p-4" data-testid={`automation-item-${i}`}>
            <div className="flex items-start justify-between gap-2">
              <div className="min-w-0">
                <div className="text-sm font-semibold">{a.area}</div>
                {Array.isArray(a.tools) && a.tools.length > 0 && (
                  <div className="mt-1.5 flex flex-wrap gap-1">
                    {a.tools.map((t, ti) => (
                      <span key={ti} className="rounded-md border border-border/60 bg-background/40 px-1.5 py-0.5 text-[11px] text-muted-foreground">
                        {t}
                      </span>
                    ))}
                  </div>
                )}
              </div>
              {a.plug_and_play && (
                <Badge variant="secondary" className="rounded-full text-[10px]">
                  <PlugZap className="mr-1 h-3 w-3" /> No‑code
                </Badge>
              )}
            </div>
            <div className="mt-3 flex items-start gap-1.5 text-xs text-muted-foreground">
              <Wand2 className="mt-0.5 h-3 w-3 shrink-0" />
              <span>{a.how_it_helps}</span>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
};

export default AutomationCard;
