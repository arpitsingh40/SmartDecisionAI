import React, { useState, useRef } from 'react';
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import {
  Swords, Loader2, HelpCircle, MessageSquareQuote, Sparkles,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { toast } from 'sonner';
import { runDebateTurn, getGuestId } from '@/lib/api';

// ---------------------------------------------------------------------------
// Compose step — textarea for the user's objection
// ---------------------------------------------------------------------------
const ComposeStep = ({ objection, setObjection, onSubmit, disabled }) => {
  const examples = [
    'Switching costs are higher than this assumes',
    "I can't commit 14 days — I only have weekends",
    'My risk tolerance is much lower than medium',
    "The $1.8k/yr savings doesn't account for my tax bracket",
  ];
  return (
    <div className="space-y-4" data-testid="debate-compose-step">
      <div>
        <Label htmlFor="debate-objection" className="text-sm font-medium">
          What's your objection?
        </Label>
        <p className="mt-1 text-xs text-muted-foreground">
          Be specific &mdash; the more concrete you are, the better the re-analysis.
        </p>
      </div>
      <Textarea
        id="debate-objection"
        value={objection}
        onChange={(e) => setObjection(e.target.value)}
        placeholder="e.g. This plan underestimates my switching costs — I've tried similar tools before and it took me months, not weeks."
        rows={5}
        className="resize-none rounded-xl border-border/70 bg-background/40 focus-visible:ring-primary"
        disabled={disabled}
        data-testid="debate-objection-textarea"
      />
      <div className="text-[11px] uppercase tracking-wider text-muted-foreground">
        Examples &mdash; click to reuse
      </div>
      <div className="flex flex-wrap gap-2">
        {examples.map((ex, i) => (
          <button
            key={i}
            type="button"
            disabled={disabled}
            onClick={() => setObjection(ex)}
            className="rounded-full border border-border/60 bg-background/40 px-3 py-1 text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground disabled:opacity-50"
            data-testid={`debate-example-${i}`}
          >
            {ex}
          </button>
        ))}
      </div>
      <DialogFooter className="gap-2">
        <Button
          onClick={onSubmit}
          disabled={disabled || objection.trim().length < 4}
          className="gap-2"
          data-testid="debate-submit-objection-button"
        >
          <Swords className="h-4 w-4" />
          Challenge the decision
        </Button>
      </DialogFooter>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Clarify step — up to 3 clarifying questions inline
// ---------------------------------------------------------------------------
const ClarifyStep = ({ extraction, onSubmit, disabled }) => {
  const questions = extraction?.clarifying_questions || [];
  const [answers, setAnswers] = useState(() =>
    Object.fromEntries(questions.map((q) => [q.id, ''])),
  );

  const update = (id, val) =>
    setAnswers((prev) => ({ ...prev, [id]: val }));

  const payload = questions.map((q) => ({
    id: q.id,
    question: q.question,
    answer: (answers[q.id] || '').trim(),
  }));
  const canSubmit = payload.every((p) => p.answer.length > 0);

  return (
    <div className="space-y-4" data-testid="debate-clarify-step">
      {Array.isArray(extraction?.concerns) && extraction.concerns.length > 0 && (
        <div className="rounded-xl border border-primary/25 bg-primary/5 p-3">
          <div className="mb-1.5 flex items-center gap-1.5 text-[11px] font-semibold uppercase tracking-wider text-primary">
            <MessageSquareQuote className="h-3.5 w-3.5" />
            We heard you
          </div>
          <ul className="space-y-1 text-sm">
            {extraction.concerns.slice(0, 4).map((c, i) => (
              <li key={i} className="flex items-start gap-2">
                <Badge variant="secondary" className="rounded-full text-[10px] uppercase">
                  {c.category || 'other'}
                </Badge>
                <span className="leading-relaxed text-foreground/90">{c.text}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div>
        <div className="flex items-center gap-1.5 text-sm font-medium">
          <HelpCircle className="h-4 w-4 text-primary" />
          Quick clarifications ({questions.length})
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          Two or three sharp answers will materially change the re-analysis.
        </p>
      </div>

      <div className="space-y-3">
        {questions.map((q, i) => (
          <div key={q.id} className="space-y-1.5">
            <Label htmlFor={`cq-${q.id}`} className="text-sm">
              <span className="mr-2 rounded-md bg-primary/15 px-1.5 py-0.5 text-[11px] font-semibold text-primary">
                {i + 1}
              </span>
              {q.question}
            </Label>
            {q.help_text && (
              <p className="text-[11px] text-muted-foreground">{q.help_text}</p>
            )}
            <Input
              id={`cq-${q.id}`}
              value={answers[q.id] || ''}
              onChange={(e) => update(q.id, e.target.value)}
              placeholder="Type a short, honest answer…"
              className="rounded-lg border-border/70 bg-background/40 focus-visible:ring-primary"
              disabled={disabled}
              data-testid={`debate-clarify-input-${i}`}
            />
          </div>
        ))}
      </div>

      <DialogFooter className="gap-2">
        <Button
          onClick={() => onSubmit(payload)}
          disabled={disabled || !canSubmit}
          className="gap-2"
          data-testid="debate-submit-clarifications-button"
        >
          <Sparkles className="h-4 w-4" />
          Re-run analysis
        </Button>
      </DialogFooter>
    </div>
  );
};

// ---------------------------------------------------------------------------
// Processing step — spinner with contextual status
// ---------------------------------------------------------------------------
const ProcessingStep = ({ statusLabel }) => (
  <div
    className="flex flex-col items-center justify-center gap-3 py-10 text-center"
    data-testid="debate-processing-step"
  >
    <Loader2 className="h-8 w-8 animate-spin text-primary" />
    <div className="text-sm font-medium">{statusLabel}</div>
    <p className="max-w-sm text-xs text-muted-foreground">
      Six specialist agents are re-evaluating with your new context. This usually takes 60 to 180 seconds.
    </p>
  </div>
);

// ---------------------------------------------------------------------------
// Main DebateDialog
// ---------------------------------------------------------------------------
const STATUS_LABELS = {
  pending: 'Extracting your concerns…',
  needs_clarification: 'Awaiting your answers…',
  refining: 'Panel is debating — 6 agents in progress…',
  completed: 'Done',
  failed: 'Failed',
};

const DebateDialog = ({ open, onOpenChange, decisionId, onTurnCompleted }) => {
  const [step, setStep] = useState('compose'); // compose | clarify | processing
  const [objection, setObjection] = useState('');
  const [extraction, setExtraction] = useState(null);
  const [statusLabel, setStatusLabel] = useState(STATUS_LABELS.pending);
  const [busy, setBusy] = useState(false);
  const clarifyResolverRef = useRef(null); // resolves onClarify promise

  const resetState = () => {
    setStep('compose');
    setObjection('');
    setExtraction(null);
    setStatusLabel(STATUS_LABELS.pending);
    setBusy(false);
    clarifyResolverRef.current = null;
  };

  const handleOpenChange = (v) => {
    if (busy && !v) return; // don't allow close mid-run
    onOpenChange?.(v);
    if (!v) setTimeout(resetState, 150);
  };

  const handleStart = async () => {
    setBusy(true);
    setStep('processing');
    setStatusLabel(STATUS_LABELS.pending);

    const guestId = getGuestId();
    try {
      const turn = await runDebateTurn({
        decisionId,
        objection,
        guestId,
        onStatus: (status, data) => {
          setStatusLabel(STATUS_LABELS[status] || `Status: ${status}`);
          if (status === 'needs_clarification' && data?.extraction) {
            setExtraction(data.extraction);
            setStep('clarify');
          } else if (status === 'refining' || status === 'pending') {
            // back to processing view
            setStep('processing');
          }
        },
        onClarify: () =>
          new Promise((resolve) => {
            clarifyResolverRef.current = resolve;
          }),
      });
      toast.success('Refined decision is ready');
      onTurnCompleted?.(turn);
      handleOpenChange(false);
    } catch (e) {
      const msg = e?.response?.data?.detail || e?.message || 'Debate failed';
      toast.error(msg);
      setBusy(false);
      setStep('compose');
    }
  };

  const handleSubmitClarifications = (answers) => {
    if (!clarifyResolverRef.current) return;
    setStep('processing');
    setStatusLabel(STATUS_LABELS.refining);
    clarifyResolverRef.current(answers);
    clarifyResolverRef.current = null;
  };

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent
        className="max-w-xl rounded-2xl border-border/70 bg-card/95 backdrop-blur"
        data-testid="debate-dialog"
      >
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 font-display text-xl">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
              <Swords className="h-4 w-4" />
            </span>
            Challenge this decision
          </DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            Tell us where the analysis is off. The panel will re-evaluate with your input.
          </DialogDescription>
        </DialogHeader>

        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.18 }}
          >
            {step === 'compose' && (
              <ComposeStep
                objection={objection}
                setObjection={setObjection}
                onSubmit={handleStart}
                disabled={busy}
              />
            )}
            {step === 'clarify' && (
              <ClarifyStep
                extraction={extraction}
                onSubmit={handleSubmitClarifications}
                disabled={busy && !clarifyResolverRef.current}
              />
            )}
            {step === 'processing' && <ProcessingStep statusLabel={statusLabel} />}
          </motion.div>
        </AnimatePresence>
      </DialogContent>
    </Dialog>
  );
};

export default DebateDialog;
