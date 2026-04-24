import React, { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Compass, DollarSign, ShieldAlert, Rocket, Swords, Sparkles,
  ChevronDown, ChevronUp,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Icon + tone per agent. Colors are scoped to the chip only to stay on-palette.
const AGENT_META = {
  Strategic:    { icon: Compass,     tone: 'text-primary',                chipBg: 'bg-primary/12 ring-primary/25',                    label: 'Strategic',    subtitle: 'Framing & north-star'  },
  Financial:    { icon: DollarSign,  tone: 'text-emerald-500',            chipBg: 'bg-emerald-500/15 ring-emerald-500/30',            label: 'Financial',    subtitle: 'EV, ROI, payback'      },
  Risk:         { icon: ShieldAlert, tone: 'text-rose-500',               chipBg: 'bg-rose-500/15 ring-rose-500/30',                  label: 'Risk',         subtitle: 'Failure modes, worst-case' },
  Execution:    { icon: Rocket,      tone: 'text-amber-500',              chipBg: 'bg-amber-500/15 ring-amber-500/30',                label: 'Execution',    subtitle: 'Feasibility & next steps' },
  Contrarian:   { icon: Swords,      tone: 'text-indigo-500',             chipBg: 'bg-indigo-500/15 ring-indigo-500/30',              label: 'Contrarian',   subtitle: 'Devil\u2019s advocate'  },
  Optimization: { icon: Sparkles,    tone: 'text-teal-500',               chipBg: 'bg-teal-500/15 ring-teal-500/30',                  label: 'Optimization', subtitle: 'Leverage & scale plays' },
};

// Per-agent, order-of-importance keys to render from `details` (human-readable).
const AGENT_KEYS = {
  Strategic:    ['goal_restated', 'optimize_for', 'success_metric', 'noise_filtered'],
  Financial:    ['expected_value', 'roi_pct_range', 'payback_months', 'opportunity_cost', 'money_insights'],
  Risk:         ['worst_case', 'risk_score_100', 'top_risks', 'hidden_failure_modes'],
  Execution:    ['feasibility_score_100', 'quick_start', 'time_to_first_result', 'tools', 'bottlenecks'],
  Contrarian:   ['devil_advocate_view', 'strong_objections', 'weak_assumptions', 'false_premises'],
  Optimization: ['quick_wins_to_10x', 'leverage_ideas', 'automation_opportunities', 'scale_plays'],
};

const prettifyKey = (k) =>
  k.replace(/_/g, ' ').replace(/\b\w/g, (ch) => ch.toUpperCase());

const renderValue = (val) => {
  if (val == null || val === '') return <span className="text-muted-foreground">\u2014</span>;
  if (typeof val === 'string' || typeof val === 'number' || typeof val === 'boolean') {
    return <span className="leading-relaxed">{String(val)}</span>;
  }
  if (Array.isArray(val)) {
    return (
      <ul className="mt-1 space-y-1.5">
        {val.slice(0, 6).map((item, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="mt-[7px] h-1 w-1 shrink-0 rounded-full bg-primary/60" />
            <span className="text-[13px] leading-relaxed">
              {typeof item === 'object' && item !== null
                ? (
                  <span className="space-x-1">
                    {Object.entries(item).slice(0, 4).map(([k, v]) => (
                      <span key={k} className="mr-2">
                        <span className="text-muted-foreground">{prettifyKey(k)}:</span>{' '}
                        <span className="font-medium">{String(v)}</span>
                      </span>
                    ))}
                  </span>
                )
                : String(item)}
            </span>
          </li>
        ))}
      </ul>
    );
  }
  if (typeof val === 'object') {
    return (
      <div className="mt-1 space-y-1 text-[13px]">
        {Object.entries(val).slice(0, 6).map(([k, v]) => (
          <div key={k} className="flex gap-2">
            <span className="text-muted-foreground">{prettifyKey(k)}:</span>
            <span className="font-medium">{String(v)}</span>
          </div>
        ))}
      </div>
    );
  }
  return String(val);
};

const AgentPerspectiveCard = ({ perspective, defaultOpen = false }) => {
  const [open, setOpen] = useState(!!defaultOpen);
  const meta = AGENT_META[perspective?.agent] || AGENT_META.Strategic;
  const Icon = meta.icon;
  const details = perspective?.details || {};
  const keys = (AGENT_KEYS[perspective?.agent] || Object.keys(details)).filter(
    (k) => details[k] !== undefined && details[k] !== null && details[k] !== '',
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <Card
        className="rounded-2xl border-border/70 bg-card/60 p-5"
        data-testid={`boardroom-agent-card-${(perspective?.agent || 'agent').toLowerCase()}`}
      >
        <div className="flex items-start gap-3">
          <span
            className={`grid h-10 w-10 shrink-0 place-items-center rounded-lg ring-1 ${meta.chipBg} ${meta.tone}`}
          >
            <Icon className="h-5 w-5" />
          </span>
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-center gap-2">
              <h3 className="truncate text-sm font-semibold">{meta.label} Agent</h3>
              <Badge
                variant="secondary"
                className="rounded-full bg-background/60 px-2 py-0 text-[10px] font-medium uppercase tracking-wider text-muted-foreground"
              >
                {meta.subtitle}
              </Badge>
            </div>
            <p className="mt-1.5 text-sm leading-relaxed text-foreground/90">
              {perspective?.summary || 'No summary available.'}
            </p>
          </div>
        </div>

        {keys.length > 0 && (
          <>
            <Button
              variant="ghost"
              size="sm"
              className="mt-3 h-8 w-full justify-between px-2 text-xs text-muted-foreground hover:text-foreground"
              onClick={() => setOpen((v) => !v)}
              data-testid={`boardroom-agent-toggle-${(perspective?.agent || 'agent').toLowerCase()}`}
            >
              <span>{open ? 'Hide details' : 'View details'}</span>
              {open ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5" />}
            </Button>

            <AnimatePresence initial={false}>
              {open && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="mt-2 grid gap-3 rounded-xl border border-border/60 bg-background/40 p-3">
                    {keys.map((k) => (
                      <div key={k}>
                        <div className="mb-0.5 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
                          {prettifyKey(k)}
                        </div>
                        <div className="text-sm text-foreground/90">{renderValue(details[k])}</div>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </>
        )}
      </Card>
    </motion.div>
  );
};

export default AgentPerspectiveCard;
