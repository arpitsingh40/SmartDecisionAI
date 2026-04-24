import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MessageSquareQuote, Scale, Handshake } from 'lucide-react';
import { motion } from 'framer-motion';
import { stagger, fadeUp } from '@/lib/motion';

const DebatePanel = ({ debate }) => {
  const conflicts = Array.isArray(debate?.conflicts) ? debate.conflicts : [];
  const tradeOffs = Array.isArray(debate?.trade_offs) ? debate.trade_offs : [];
  const convergence = debate?.convergence || '';

  const nothingToShow =
    conflicts.length === 0 && tradeOffs.length === 0 && !convergence;

  if (nothingToShow) return null;

  return (
    <div className="space-y-4" data-testid="boardroom-debate-panel">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6">
        <div className="mb-4 flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
            <MessageSquareQuote className="h-4 w-4" />
          </span>
          <div>
            <h3 className="text-base font-semibold">Boardroom debate</h3>
            <p className="text-xs text-muted-foreground">
              Where agents disagreed &mdash; and how the synthesizer resolved it.
            </p>
          </div>
        </div>

        {conflicts.length > 0 ? (
          <motion.ol
            initial="initial"
            animate="animate"
            variants={stagger(0.06)}
            className="space-y-3"
          >
            {conflicts.map((c, i) => (
              <motion.li
                key={i}
                variants={fadeUp}
                className="rounded-xl border border-border/60 bg-background/40 p-4"
                data-testid={`boardroom-conflict-${i}`}
              >
                <div className="flex flex-wrap items-center gap-2">
                  <Badge
                    variant="secondary"
                    className="rounded-full bg-primary/10 text-primary"
                  >
                    Conflict #{i + 1}
                  </Badge>
                  <h4 className="text-sm font-semibold">{c?.topic || 'Disagreement'}</h4>
                </div>

                {Array.isArray(c?.views) && c.views.length > 0 && (
                  <div className="mt-3 grid gap-2 sm:grid-cols-2">
                    {c.views.map((v, j) => (
                      <div
                        key={j}
                        className="rounded-lg border border-border/60 bg-card/50 p-3 text-sm"
                      >
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                          {v?.agent || 'Agent'}
                        </div>
                        <div className="mt-1 text-sm leading-relaxed text-foreground/90">
                          {v?.view || ''}
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {c?.resolution && (
                  <div className="mt-3 rounded-lg border border-primary/25 bg-primary/5 p-3 text-sm">
                    <div className="mb-1 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary">
                      <Handshake className="h-3.5 w-3.5" />
                      Resolution
                    </div>
                    <p className="leading-relaxed text-foreground/90">{c.resolution}</p>
                  </div>
                )}
              </motion.li>
            ))}
          </motion.ol>
        ) : (
          <p className="text-sm text-muted-foreground">
            No significant disagreements surfaced. The panel converged quickly.
          </p>
        )}
      </Card>

      {(tradeOffs.length > 0 || convergence) && (
        <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6">
          <div className="grid gap-5 sm:grid-cols-2 sm:gap-6">
            {tradeOffs.length > 0 && (
              <div data-testid="boardroom-trade-offs">
                <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                  <Scale className="h-3.5 w-3.5" />
                  Trade-offs acknowledged
                </div>
                <ul className="space-y-2 text-sm">
                  {tradeOffs.slice(0, 6).map((t, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-primary/60" />
                      <span className="leading-relaxed">{t}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {convergence && (
              <div data-testid="boardroom-convergence">
                <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary">
                  <Handshake className="h-3.5 w-3.5" />
                  Where the panel converged
                </div>
                <p className="rounded-lg border border-primary/25 bg-primary/5 p-3 text-sm leading-relaxed text-foreground/90">
                  {convergence}
                </p>
              </div>
            )}
          </div>
        </Card>
      )}
    </div>
  );
};

export default DebatePanel;
