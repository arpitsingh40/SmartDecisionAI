import React from 'react';
import { Card } from '@/components/ui/card';
import { NotebookPen } from 'lucide-react';

const AssumptionsCard = ({ assumptions }) => {
  if (!Array.isArray(assumptions) || assumptions.length === 0) return null;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5" data-testid="results-assumptions">
      <div className="flex items-center gap-2 text-sm font-semibold">
        <NotebookPen className="h-4 w-4 text-primary" /> Assumptions we made
      </div>
      <ul className="mt-3 space-y-1.5 text-sm">
        {assumptions.map((a, i) => (
          <li key={i} className="flex items-start gap-2 text-muted-foreground">
            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary/60" />
            <span>{a}</span>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-[11px] text-muted-foreground">
        These filled in missing details. Correct them in What‑if to sharpen the recommendation.
      </p>
    </Card>
  );
};

export default AssumptionsCard;
