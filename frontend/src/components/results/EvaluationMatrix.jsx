import React, { useMemo, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Trophy } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { RotateCcw } from 'lucide-react';

const heatColor = (r) => {
  // r: 0-10. Returns tailwind-friendly HSL-ish background.
  const pct = Math.max(0, Math.min(10, r)) / 10;
  // 0 → rose/red (0 hue), 10 → emerald (~142 hue)
  const hue = Math.round(142 * pct);
  return `hsla(${hue}, 70%, 45%, ${0.15 + pct * 0.25})`;
};

const EvaluationMatrix = ({ options, factors, bestId, onRatingChange }) => {
  const [editing, setEditing] = useState(false);
  const [overrides, setOverrides] = useState({}); // { 'optId.factorName': value }

  const merged = useMemo(() => {
    if (!editing) return options;
    return options.map((o) => ({
      ...o,
      factor_ratings: {
        ...(o.factor_ratings || {}),
        ...Object.fromEntries(
          Object.entries(overrides)
            .filter(([k]) => k.startsWith(o.id + '.'))
            .map(([k, v]) => [k.split('.').slice(1).join('.'), Number(v)])
        ),
      },
    }));
  }, [editing, overrides, options]);

  const applyOverrides = () => {
    // Push overrides upstream
    if (onRatingChange) {
      Object.entries(overrides).forEach(([k, v]) => {
        const [optId, ...rest] = k.split('.');
        const factorName = rest.join('.');
        onRatingChange(optId, factorName, Number(v));
      });
    }
    setOverrides({});
    setEditing(false);
  };

  const factorList = Array.isArray(factors) ? factors : [];

  return (
    <Card className="overflow-hidden rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-evaluation-matrix">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h3 className="text-base font-semibold">Evaluation matrix</h3>
          <p className="text-xs text-muted-foreground">AI‑rated each option 0–10 on each factor. Darker green is better.</p>
        </div>
        {onRatingChange && (
          <div className="flex items-center gap-2">
            {editing ? (
              <>
                <Button variant="ghost" size="sm" onClick={() => { setOverrides({}); setEditing(false); }} className="gap-1.5" data-testid="matrix-cancel-edit">
                  <RotateCcw className="h-3 w-3" /> Cancel
                </Button>
                <Button size="sm" onClick={applyOverrides} data-testid="matrix-apply-edit">Apply</Button>
              </>
            ) : (
              <Button variant="secondary" size="sm" onClick={() => setEditing(true)} data-testid="matrix-edit-button">
                Edit ratings
              </Button>
            )}
          </div>
        )}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[600px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border/60">
              <th className="sticky left-0 bg-card/60 px-3 py-2 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground backdrop-blur">
                Option
              </th>
              {factorList.map((f) => (
                <th key={f.name} className="px-3 py-2 text-center text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  <div className="truncate" title={f.name}>{f.name}</div>
                  {typeof f.weight === 'number' && (
                    <div className="mt-0.5 text-[10px] normal-case text-muted-foreground/80">w={f.weight}</div>
                  )}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {merged.map((o) => (
              <tr key={o.id} className="border-b border-border/40" data-testid={`matrix-row-${o.id}`}>
                <td className="sticky left-0 bg-card/60 px-3 py-2 backdrop-blur">
                  <div className="flex items-center gap-2">
                    {o.id === bestId && (
                      <Trophy className="h-3.5 w-3.5 text-primary" />
                    )}
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium" title={o.title}>
                        {o.title}
                      </div>
                      {o.is_do_nothing && (
                        <Badge variant="secondary" className="mt-0.5 rounded-full text-[10px]">do nothing</Badge>
                      )}
                    </div>
                  </div>
                </td>
                {factorList.map((f) => {
                  const r = o.factor_ratings?.[f.name];
                  const key = `${o.id}.${f.name}`;
                  if (editing) {
                    return (
                      <td key={f.name} className="px-2 py-2 text-center">
                        <Input
                          type="number"
                          min={0}
                          max={10}
                          step={1}
                          className="mx-auto h-8 w-14 bg-background/60 text-center"
                          value={overrides[key] ?? (typeof r === 'number' ? r : '')}
                          onChange={(e) => setOverrides((prev) => ({ ...prev, [key]: e.target.value }))}
                          data-testid={`matrix-input-${o.id}-${f.name}`}
                        />
                      </td>
                    );
                  }
                  return (
                    <td key={f.name} className="px-2 py-2 text-center">
                      <span
                        className="inline-flex h-8 w-10 items-center justify-center rounded-lg text-sm font-semibold tabular-nums"
                        style={{ backgroundColor: typeof r === 'number' ? heatColor(r) : undefined }}
                        data-testid={`matrix-cell-${o.id}-${f.name}`}
                      >
                        {typeof r === 'number' ? r : '—'}
                      </span>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
};

export default EvaluationMatrix;
