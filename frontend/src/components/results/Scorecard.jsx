import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Gauge, Clock, ShieldAlert, CheckCircle2, Trophy } from 'lucide-react';

const riskTone = (r) =>
  r === 'Low' ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400' :
  r === 'High' ? 'bg-rose-500/15 text-rose-600 dark:text-rose-400' :
  'bg-amber-500/15 text-amber-600 dark:text-amber-400';

const Ring = ({ value, size = 120, stroke = 10 }) => {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.max(0, Math.min(100, Number(value) || 0));
  const dash = c * (pct / 100);
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="hsl(var(--muted))" strokeWidth={stroke} strokeOpacity={0.35} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="hsl(var(--primary))"
        strokeWidth={stroke}
        strokeDasharray={`${dash} ${c}`}
        strokeLinecap="round"
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text
        x="50%"
        y="54%"
        textAnchor="middle"
        fill="hsl(var(--foreground))"
        fontSize={size * 0.28}
        fontWeight={700}
        fontFamily="Space Grotesk, Inter, system-ui, sans-serif"
      >
        {pct}
      </text>
    </svg>
  );
};

const Scorecard = ({ scorecard }) => {
  if (!scorecard) return null;
  const { score = 0, risk_level = 'Medium', time_to_result = '—', ease_of_execution = 0, confidence = 0 } = scorecard;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-scorecard">
      <div className="mb-3 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
          <Trophy className="h-4 w-4" />
        </span>
        <div>
          <h3 className="text-base font-semibold">Execution scorecard</h3>
          <p className="text-xs text-muted-foreground">One snapshot: ship‑worthy or not?</p>
        </div>
      </div>
      <div className="grid items-center gap-4 sm:grid-cols-[auto_1fr]">
        <div className="flex justify-center">
          <Ring value={score} />
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <Tile icon={ShieldAlert} label="Risk" value={risk_level} badge={riskTone(risk_level)} />
          <Tile icon={Clock} label="Time to result" value={time_to_result} />
          <Tile icon={Gauge} label="Ease of execution" value={`${ease_of_execution}/100`} />
          <Tile icon={CheckCircle2} label="Confidence" value={`${confidence}%`} />
        </div>
      </div>
    </Card>
  );
};

const Tile = ({ icon: Icon, label, value, badge }) => (
  <div className="rounded-xl border border-border/60 bg-background/40 p-3">
    <div className="flex items-center gap-1.5 text-[11px] uppercase tracking-widest text-muted-foreground">
      <Icon className="h-3.5 w-3.5" />
      {label}
    </div>
    <div className="mt-1.5 flex items-center gap-2">
      {badge ? <Badge variant="secondary" className={`rounded-full ${badge}`}>{value}</Badge> : <span className="text-sm font-semibold">{value}</span>}
    </div>
  </div>
);

export default Scorecard;
