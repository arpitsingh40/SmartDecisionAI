import React from 'react';
import { Card } from '@/components/ui/card';
import { AlertTriangle, ArrowRight } from 'lucide-react';

const PlanBCard = ({ planB, trigger }) => {
  return (
    <Card className="rounded-2xl border-amber-500/30 bg-amber-500/5 p-5" data-testid="results-plan-b">
      <div className="flex items-center gap-2 text-sm font-semibold text-amber-600 dark:text-amber-400">
        <AlertTriangle className="h-4 w-4" /> Plan B
      </div>
      <p className="mt-2 text-sm leading-relaxed text-foreground/90">{planB}</p>
      {trigger && (
        <div className="mt-3 flex items-start gap-1.5 rounded-lg border border-border/60 bg-background/40 p-3 text-xs text-muted-foreground">
          <ArrowRight className="mt-0.5 h-3 w-3 shrink-0" />
          <div>
            <span className="text-foreground/80">Trigger: </span>
            {trigger}
          </div>
        </div>
      )}
    </Card>
  );
};

export default PlanBCard;
