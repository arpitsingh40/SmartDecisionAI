import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel,
  AlertDialogAction,
} from '@/components/ui/alert-dialog';
import {
  MessageSquareQuote, Sparkles, ArrowRight, CircleCheck, CircleAlert,
  TrendingUp, Zap, Scale, Undo2, Calendar, ChevronDown, ChevronUp,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const verdictTone = {
  keep:   { label: 'Kept original', icon: CircleCheck, cls: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 ring-emerald-500/30' },
  modify: { label: 'Modified plan',  icon: Sparkles,    cls: 'bg-amber-500/15 text-amber-600 dark:text-amber-400 ring-amber-500/30' },
  change: { label: 'Changed pick',   icon: ArrowRight,  cls: 'bg-primary/15 text-primary ring-primary/30' },
};

const categoryTone = {
  risk:        'bg-rose-500/15 text-rose-600 dark:text-rose-400',
  feasibility: 'bg-amber-500/15 text-amber-600 dark:text-amber-400',
  cost:        'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400',
  time:        'bg-indigo-500/15 text-indigo-600 dark:text-indigo-400',
  personal:    'bg-teal-500/15 text-teal-600 dark:text-teal-400',
  other:       'bg-muted text-muted-foreground',
};

const ConfidenceDelta = ({ old: oldConf, new: newConf }) => {
  if (oldConf == null || newConf == null) return null;
  const delta = newConf - oldConf;
  const improved = delta > 0;
  const unchanged = delta === 0;
  const tone = unchanged
    ? 'border-border/70 bg-background/40 text-muted-foreground'
    : improved
      ? 'border-emerald-500/40 bg-emerald-500/5 text-emerald-600 dark:text-emerald-400'
      : 'border-rose-500/40 bg-rose-500/5 text-rose-600 dark:text-rose-400';

  return (
    <div
      className={`flex items-center gap-3 rounded-xl border px-4 py-3 ${tone}`}
      data-testid="debate-confidence-delta"
    >
      <TrendingUp className={`h-4 w-4 shrink-0 ${improved ? '' : 'rotate-180'}`} />
      <div className="flex-1 text-sm">
        <span className="font-semibold">
          {unchanged
            ? 'Confidence unchanged'
            : improved
              ? `Accuracy improved from ${oldConf}% → ${newConf}% after your inputs`
              : `Confidence dropped from ${oldConf}% → ${newConf}% after your inputs`}
        </span>
      </div>
      <Badge variant="secondary" className="shrink-0 rounded-full tabular-nums">
        {delta > 0 ? '+' : ''}{delta} pts
      </Badge>
    </div>
  );
};

const DebateTurnCard = ({ turn, index, isLatest, onRevert }) => {
  const [open, setOpen] = useState(!!isLatest);
  const refinement = turn?.refinement || {};
  const extraction = turn?.concern_extraction || {};
  const verdict = verdictTone[refinement.updated_decision_verdict] || verdictTone.modify;
  const VerdictIcon = verdict.icon;
  const delta = refinement.confidence_delta || {};
  const outcome = refinement.updated_outcome || {};

  const turnDate = turn?.created_at ? new Date(turn.created_at) : null;
  const timeStr = turnDate
    ? turnDate.toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
    : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: 0.03 * index }}
    >
      <Card
        className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6"
        data-testid={`debate-turn-card-${index}`}
      >
        {/* Header */}
        <div className="mb-4 flex flex-wrap items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <span className={`grid h-8 w-8 place-items-center rounded-lg ring-1 ${verdict.cls}`}>
              <VerdictIcon className="h-4 w-4" />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="text-sm font-semibold sm:text-base">
                  Refinement #{index + 1}
                </h3>
                <Badge variant="secondary" className={`rounded-full text-[10px] uppercase ring-1 ${verdict.cls}`}>
                  {verdict.label}
                </Badge>
                {isLatest && (
                  <Badge variant="secondary" className="rounded-full bg-primary/12 text-[10px] uppercase text-primary">
                    Active
                  </Badge>
                )}
              </div>
              {timeStr && (
                <div className="mt-0.5 flex items-center gap-1 text-[11px] text-muted-foreground">
                  <Calendar className="h-3 w-3" />
                  {timeStr}
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setOpen((v) => !v)}
              className="gap-1.5 text-xs"
              data-testid={`debate-turn-toggle-${index}`}
            >
              {open ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
              {open ? 'Collapse' : 'Expand'}
            </Button>
            {onRevert && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1.5 text-xs"
                    data-testid={`debate-turn-revert-${index}`}
                  >
                    <Undo2 className="h-3.5 w-3.5" />
                    Revert here
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Revert to Refinement #{index + 1}?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This will discard any refinements made after this turn.
                      Your earlier turns (before this one) stay. You can re-challenge any time.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => onRevert(turn.id)}>
                      Revert
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
          </div>
        </div>

        {/* User objection + concerns */}
        <div className="mb-4 rounded-xl border border-border/60 bg-background/40 p-4">
          <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            <MessageSquareQuote className="h-3.5 w-3.5" />
            Your objection
          </div>
          <p
            className="text-sm italic leading-relaxed text-foreground/90"
            data-testid={`debate-turn-objection-${index}`}
          >
            &ldquo;{turn?.objection}&rdquo;
          </p>
          {Array.isArray(extraction?.concerns) && extraction.concerns.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {extraction.concerns.map((c, i) => (
                <Badge
                  key={i}
                  variant="secondary"
                  className={`rounded-full text-[10px] uppercase ${categoryTone[c.category] || categoryTone.other}`}
                >
                  {c.category || 'other'}: {c.text}
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Confidence delta */}
        <ConfidenceDelta {...delta} />

        {/* Collapsible body */}
        <AnimatePresence initial={false}>
          {open && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.22 }}
              className="overflow-hidden"
            >
              <div className="mt-4 space-y-4">
                {/* What changed summary */}
                {refinement.what_changed_summary && (
                  <div
                    className="rounded-xl border border-primary/25 bg-primary/5 p-4"
                    data-testid={`debate-turn-whatchanged-${index}`}
                  >
                    <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary">
                      <Sparkles className="h-3.5 w-3.5" />
                      What changed &amp; why
                    </div>
                    <p className="text-sm leading-relaxed text-foreground/90">
                      {refinement.what_changed_summary}
                    </p>
                  </div>
                )}

                {/* Key diffs */}
                {Array.isArray(refinement.key_diffs) && refinement.key_diffs.length > 0 && (
                  <div>
                    <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      <Scale className="h-3.5 w-3.5" />
                      Key differences
                    </div>
                    <div className="grid gap-2">
                      {refinement.key_diffs.map((d, i) => (
                        <div
                          key={i}
                          className="grid grid-cols-1 gap-2 rounded-lg border border-border/60 bg-background/40 p-3 sm:grid-cols-[1fr_auto_1fr] sm:items-center"
                        >
                          <div className="text-sm">
                            <div className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">Before</div>
                            <div className="mt-0.5 text-foreground/80 line-through decoration-muted-foreground/30">
                              {d.before || '—'}
                            </div>
                          </div>
                          <ArrowRight className="hidden h-4 w-4 shrink-0 text-primary sm:inline" />
                          <div className="text-sm">
                            <div className="text-[10px] font-semibold uppercase tracking-wider text-primary">After</div>
                            <div className="mt-0.5 font-medium text-foreground">
                              {d.after || '—'}
                            </div>
                          </div>
                          <div className="col-span-full mt-1 text-[11px] text-muted-foreground sm:col-span-3">
                            {d.topic}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Updated outcome */}
                {outcome && (outcome.revenue_or_savings || outcome.probability_pct != null || outcome.timeframe) && (
                  <div
                    className="grid gap-3 rounded-xl border border-border/60 bg-background/40 p-4 sm:grid-cols-3"
                    data-testid={`debate-turn-outcome-${index}`}
                  >
                    {outcome.revenue_or_savings && (
                      <div>
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                          Revenue / savings
                        </div>
                        <div className="mt-1 text-sm font-semibold tabular-nums">
                          {outcome.revenue_or_savings}
                        </div>
                      </div>
                    )}
                    {outcome.probability_pct != null && (
                      <div>
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                          Probability
                        </div>
                        <div className="mt-1 text-sm font-semibold tabular-nums">
                          {outcome.probability_pct}%
                        </div>
                      </div>
                    )}
                    {outcome.timeframe && (
                      <div>
                        <div className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                          Timeframe
                        </div>
                        <div className="mt-1 text-sm font-semibold">{outcome.timeframe}</div>
                      </div>
                    )}
                  </div>
                )}

                {/* Strengths & weaknesses */}
                {(refinement.strengths?.length > 0 || refinement.weaknesses?.length > 0) && (
                  <div className="grid gap-3 sm:grid-cols-2">
                    {refinement.strengths?.length > 0 && (
                      <div>
                        <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-emerald-600 dark:text-emerald-400">
                          <CircleCheck className="h-3.5 w-3.5" />
                          Strengths
                        </div>
                        <ul className="space-y-1.5 text-sm">
                          {refinement.strengths.map((s, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-emerald-500/70" />
                              <span className="leading-relaxed">{s}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {refinement.weaknesses?.length > 0 && (
                      <div>
                        <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-rose-600 dark:text-rose-400">
                          <CircleAlert className="h-3.5 w-3.5" />
                          Remaining trade-offs
                        </div>
                        <ul className="space-y-1.5 text-sm">
                          {refinement.weaknesses.map((w, i) => (
                            <li key={i} className="flex items-start gap-2">
                              <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-rose-500/70" />
                              <span className="leading-relaxed">{w}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Execution adjustments */}
                {refinement.execution_adjustments?.length > 0 && (
                  <div>
                    <div className="mb-2 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      <Sparkles className="h-3.5 w-3.5" />
                      Execution adjustments
                    </div>
                    <ul className="space-y-1.5 text-sm">
                      {refinement.execution_adjustments.map((a, i) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-primary/60" />
                          <span className="leading-relaxed">{a}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* When original wins */}
                {refinement.when_original_wins && (
                  <div className="rounded-xl border border-border/60 bg-background/40 p-4">
                    <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                      <CircleAlert className="h-3.5 w-3.5" />
                      When the original decision still wins
                    </div>
                    <p className="text-sm leading-relaxed text-foreground/90">
                      {refinement.when_original_wins}
                    </p>
                  </div>
                )}

                {/* Next action 24-48h */}
                {refinement.next_action_24_48h && (
                  <div
                    className="rounded-xl border border-primary/30 bg-primary/8 p-4"
                    data-testid={`debate-turn-next-action-${index}`}
                  >
                    <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary">
                      <Zap className="h-3.5 w-3.5" />
                      Next action (24 – 48 hours)
                    </div>
                    <p className="text-sm font-medium leading-relaxed text-foreground">
                      {refinement.next_action_24_48h}
                    </p>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </Card>
    </motion.div>
  );
};

export default DebateTurnCard;
