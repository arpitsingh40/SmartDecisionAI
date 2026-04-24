import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

const severityTone = {
  High: { text: 'text-rose-500', bg: 'bg-rose-500/10', ring: 'ring-rose-500/30' },
  Medium: { text: 'text-amber-500', bg: 'bg-amber-500/10', ring: 'ring-amber-500/30' },
  Low: { text: 'text-emerald-500', bg: 'bg-emerald-500/10', ring: 'ring-emerald-500/30' },
};

const probIcon = { High: ShieldAlert, Medium: Shield, Low: ShieldCheck };

const RiskAnalysisCard = ({ risks }) => {
  if (!Array.isArray(risks) || risks.length === 0) return null;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-risk-analysis">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div>
          <h3 className="text-base font-semibold">Risk analysis</h3>
          <p className="text-xs text-muted-foreground">Top risks with severity, likelihood, and mitigation.</p>
        </div>
        <Badge variant="secondary" className="rounded-full">
          {risks.length} risks
        </Badge>
      </div>
      <div className="space-y-2">
        {risks.map((r, i) => {
          const sv = severityTone[r.severity] || severityTone.Medium;
          const ProbI = probIcon[r.probability] || Shield;
          return (
            <div key={i} className="rounded-xl border border-border/60 bg-background/40 p-4" data-testid={`risk-item-${i}`}>
              <div className="flex flex-wrap items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold">{r.risk}</div>
                  <div className="mt-0.5 flex flex-wrap items-center gap-2 text-xs">
                    <span className={`inline-flex items-center gap-1 rounded-full px-2 py-0.5 ring-1 ${sv.bg} ${sv.text} ${sv.ring}`}>
                      Severity: {r.severity}
                    </span>
                    <span className="inline-flex items-center gap-1 text-muted-foreground">
                      <ProbI className="h-3 w-3" />
                      Probability: {r.probability}
                    </span>
                  </div>
                </div>
              </div>
              <div className="mt-3 rounded-lg border border-border/60 bg-background/40 p-3">
                <div className="text-[10px] uppercase tracking-widest text-muted-foreground">Mitigation</div>
                <div className="mt-1 text-sm leading-relaxed">{r.mitigation}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Card>
  );
};

export default RiskAnalysisCard;
