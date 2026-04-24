import React from 'react';
import { Card } from '@/components/ui/card';
import { Users } from 'lucide-react';
import AgentPerspectiveCard from './AgentPerspectiveCard';
import DebatePanel from './DebatePanel';

// Preferred display order for the panel.
const AGENT_ORDER = [
  'Strategic',
  'Financial',
  'Risk',
  'Execution',
  'Contrarian',
  'Optimization',
];

const BoardroomPanel = ({ agentPerspectives, debate }) => {
  const perspectives = Array.isArray(agentPerspectives) ? agentPerspectives : [];

  const sorted = [...perspectives].sort((a, b) => {
    const ia = AGENT_ORDER.indexOf(a?.agent);
    const ib = AGENT_ORDER.indexOf(b?.agent);
    return (ia === -1 ? 999 : ia) - (ib === -1 ? 999 : ib);
  });

  if (sorted.length === 0 && !debate) {
    return (
      <Card
        className="rounded-2xl border-border/70 bg-card/60 p-6 text-sm text-muted-foreground"
        data-testid="boardroom-empty"
      >
        <div className="flex items-center gap-2">
          <Users className="h-4 w-4 text-primary" />
          <span className="font-medium text-foreground">Boardroom not available</span>
        </div>
        <p className="mt-1.5">
          This decision was analyzed with the single-analyst engine (legacy fallback).
          New analyses will show the full 6-agent panel and their debate here.
        </p>
      </Card>
    );
  }

  return (
    <div className="space-y-5" data-testid="boardroom-panel">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6">
        <div className="flex items-center gap-3">
          <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
            <Users className="h-4 w-4" />
          </span>
          <div className="min-w-0">
            <h2 className="text-base font-semibold sm:text-lg">The Boardroom</h2>
            <p className="mt-0.5 text-xs text-muted-foreground sm:text-sm">
              Six specialist agents independently analyzed your decision.
              Below are their verdicts, and where they disagreed.
            </p>
          </div>
        </div>
      </Card>

      {sorted.length > 0 && (
        <div
          className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3"
          data-testid="boardroom-agents-grid"
        >
          {sorted.map((p, i) => (
            <AgentPerspectiveCard
              key={`${p?.agent || i}-${i}`}
              perspective={p}
            />
          ))}
        </div>
      )}

      <DebatePanel debate={debate} />
    </div>
  );
};

export default BoardroomPanel;
