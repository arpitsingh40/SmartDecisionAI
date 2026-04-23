import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import { ArrowLeft, ArrowRight, Sparkles, Wand2, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Checkbox } from '@/components/ui/checkbox';
import { Slider } from '@/components/ui/slider';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { toast } from 'sonner';
import {
  fetchFollowUps,
  analyzeDecision,
  saveDecision,
  getGuestId,
  ensureGuestSession,
} from '@/lib/api';
import { stepVariants } from '@/lib/motion';
import AnalysisLoading from '@/components/wizard/AnalysisLoading';

const Wizard = () => {
  const navigate = useNavigate();
  const [phase, setPhase] = useState('decision'); // 'decision' | 'loading-qs' | 'questions' | 'review' | 'analyzing'
  const [decision, setDecision] = useState('');
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({}); // qid -> value
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState(null);

  useEffect(() => {
    ensureGuestSession().catch(() => {});
  }, []);

  const totalSteps = 1 + questions.length + 1; // decision + questions + review
  const currentStepNum = phase === 'decision' ? 1 : phase === 'questions' ? 2 + stepIndex : totalSteps;
  const progressPct = Math.round((currentStepNum / totalSteps) * 100);

  const handleBeginFollowUps = async () => {
    if (decision.trim().length < 6) {
      toast.error('Please describe your decision in a bit more detail.');
      return;
    }
    setPhase('loading-qs');
    setError(null);
    try {
      const data = await fetchFollowUps(decision.trim());
      const qs = (data?.questions || []).map((q) => ({
        ...q,
        options: q.options || null,
      }));
      setQuestions(qs);
      // initialize defaults
      const defaults = {};
      qs.forEach((q) => {
        if (q.type === 'slider') defaults[q.id] = Math.round(((q.min ?? 0) + (q.max ?? 10)) / 2);
        if (q.type === 'multi_choice') defaults[q.id] = [];
        if (q.type === 'single_choice') defaults[q.id] = null;
        if (q.type === 'text') defaults[q.id] = '';
      });
      setAnswers(defaults);
      setStepIndex(0);
      setPhase('questions');
    } catch (e) {
      const msg = e?.response?.data?.detail || e.message || 'Failed to load questions';
      setError(msg);
      setPhase('decision');
      toast.error(msg);
    }
  };

  const currentQ = questions[stepIndex];

  const validCurrent = useMemo(() => {
    if (!currentQ) return true;
    const v = answers[currentQ.id];
    if (currentQ.type === 'text') return (v || '').trim().length > 0;
    if (currentQ.type === 'single_choice') return !!v;
    if (currentQ.type === 'multi_choice') return Array.isArray(v) && v.length > 0;
    if (currentQ.type === 'slider') return typeof v === 'number';
    return true;
  }, [currentQ, answers]);

  const next = () => {
    if (!validCurrent) return;
    if (stepIndex < questions.length - 1) setStepIndex((i) => i + 1);
    else setPhase('review');
  };
  const back = () => {
    if (phase === 'review') {
      setPhase('questions');
      setStepIndex(questions.length - 1);
      return;
    }
    if (stepIndex > 0) setStepIndex((i) => i - 1);
    else setPhase('decision');
  };

  const setAnswer = (qid, v) => setAnswers((a) => ({ ...a, [qid]: v }));

  const runAnalysis = async () => {
    setPhase('analyzing');
    try {
      const normAnswers = questions.map((q) => ({
        question: q.question,
        type: q.type,
        answer: answers[q.id],
      }));
      const result = await analyzeDecision(decision, normAnswers);
      // auto-save to localStorage AND backend
      const guest_id = getGuestId();
      const title = decision.length > 60 ? decision.slice(0, 57) + '…' : decision;
      try {
        const saved = await saveDecision({
          guest_id,
          title,
          decision,
          answers: normAnswers,
          result,
        });
        sessionStorage.setItem(
          'sda_current_result',
          JSON.stringify({ id: saved.id, title, decision, answers: normAnswers, result })
        );
        navigate('/results?id=' + saved.id);
      } catch (e) {
        sessionStorage.setItem(
          'sda_current_result',
          JSON.stringify({ title, decision, answers: normAnswers, result })
        );
        navigate('/results');
      }
    } catch (e) {
      const msg = e?.response?.data?.detail || e.message || 'Analysis failed';
      toast.error(msg);
      setPhase('review');
    }
  };

  return (
    <section className="mx-auto w-full max-w-2xl px-4 pb-16 pt-8 sm:px-6" data-testid="wizard-page">
      {/* Progress */}
      <div className="mb-8" data-testid="wizard-progress">
        <div className="mb-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>Step {currentStepNum} of {totalSteps}</span>
          <span className="tabular-nums">{progressPct}%</span>
        </div>
        <Progress value={progressPct} className="h-1.5" />
      </div>

      <AnimatePresence mode="wait">
        {phase === 'decision' && (
          <motion.div key="decision" variants={stepVariants} initial="initial" animate="animate" exit="exit">
            <Card className="rounded-2xl border-border/70 bg-card/60 p-6 shadow-[var(--shadow-1)] backdrop-blur sm:p-8">
              <Badge variant="secondary" className="rounded-full">
                <Sparkles className="mr-1.5 h-3 w-3" /> Let’s get specific
              </Badge>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
                What decision are you making?
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">
                One sentence is enough. Include the options you’re weighing if you have any.
              </p>
              <Textarea
                data-testid="wizard-decision-statement-textarea"
                value={decision}
                onChange={(e) => setDecision(e.target.value.slice(0, 500))}
                placeholder="e.g. Should I accept the offer at Stripe or pursue a Master's at CMU?"
                className="mt-5 min-h-[120px] resize-none bg-background/60 text-base"
              />
              <div className="mt-2 text-right text-xs text-muted-foreground">
                {decision.length} / 500
              </div>
              <div className="mt-5 flex items-center justify-end gap-3">
                <Button
                  onClick={handleBeginFollowUps}
                  disabled={decision.trim().length < 6}
                  size="lg"
                  className="gap-2"
                  data-testid="wizard-begin-button"
                >
                  Continue <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
              {error && <p className="mt-3 text-sm text-destructive">{error}</p>}
            </Card>
          </motion.div>
        )}

        {phase === 'loading-qs' && (
          <motion.div key="loading-qs" variants={stepVariants} initial="initial" animate="animate" exit="exit">
            <Card className="rounded-2xl border-border/70 bg-card/60 p-8" data-testid="wizard-loading-questions">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Wand2 className="h-4 w-4 animate-pulse text-primary" />
                Crafting smart follow‑up questions…
              </div>
              <div className="mt-6 space-y-3">
                {Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="h-12 rounded-lg shimmer" />
                ))}
              </div>
            </Card>
          </motion.div>
        )}

        {phase === 'questions' && currentQ && (
          <motion.div
            key={`q-${currentQ.id}`}
            variants={stepVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            <Card className="rounded-2xl border-border/70 bg-card/60 p-6 shadow-[var(--shadow-1)] backdrop-blur sm:p-8">
              <div className="flex items-center justify-between text-xs">
                <span className="font-medium text-primary">
                  Question {stepIndex + 1} of {questions.length}
                </span>
                <span className="text-muted-foreground uppercase tracking-wider">
                  {currentQ.type.replace('_', ' ')}
                </span>
              </div>
              <h2 className="mt-3 text-xl font-semibold leading-snug tracking-tight sm:text-2xl">
                {currentQ.question}
              </h2>
              {currentQ.help_text && (
                <p className="mt-1.5 text-sm text-muted-foreground">{currentQ.help_text}</p>
              )}
              <div className="mt-6">
                <QuestionInput q={currentQ} value={answers[currentQ.id]} onChange={(v) => setAnswer(currentQ.id, v)} />
              </div>
              <div className="mt-8 flex items-center justify-between">
                <Button
                  variant="ghost"
                  onClick={back}
                  className="gap-2"
                  data-testid="wizard-back-button"
                >
                  <ArrowLeft className="h-4 w-4" /> Back
                </Button>
                <Button
                  onClick={next}
                  disabled={!validCurrent}
                  size="lg"
                  className="gap-2"
                  data-testid="wizard-next-button"
                >
                  {stepIndex === questions.length - 1 ? 'Review' : 'Next'} <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          </motion.div>
        )}

        {phase === 'review' && (
          <motion.div key="review" variants={stepVariants} initial="initial" animate="animate" exit="exit">
            <Card className="rounded-2xl border-border/70 bg-card/60 p-6 shadow-[var(--shadow-1)] backdrop-blur sm:p-8" data-testid="wizard-review-card">
              <Badge variant="secondary" className="rounded-full">
                <Check className="mr-1.5 h-3 w-3" /> Review
              </Badge>
              <h2 className="mt-3 text-2xl font-semibold tracking-tight sm:text-3xl">
                Ready for the analysis?
              </h2>
              <p className="mt-2 text-sm text-muted-foreground">
                Quick review of your answers. You can edit any of them before running the AI.
              </p>
              <div className="mt-6 rounded-xl border border-border/70 bg-background/40 p-4">
                <div className="text-[11px] uppercase tracking-wider text-muted-foreground">Decision</div>
                <div className="mt-1 text-sm">{decision}</div>
              </div>
              <div className="mt-4 space-y-2">
                {questions.map((q, i) => (
                  <div
                    key={q.id}
                    className="flex items-start justify-between gap-3 rounded-lg border border-border/60 bg-background/40 px-4 py-3"
                  >
                    <div className="min-w-0">
                      <div className="truncate text-sm font-medium">{q.question}</div>
                      <div className="mt-0.5 text-xs text-muted-foreground">
                        {formatAnswer(q, answers[q.id])}
                      </div>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setPhase('questions');
                        setStepIndex(i);
                      }}
                      data-testid={`wizard-review-edit-${i}`}
                    >
                      Edit
                    </Button>
                  </div>
                ))}
              </div>
              <Separator className="my-6" />
              <div className="flex flex-col-reverse items-stretch justify-between gap-3 sm:flex-row sm:items-center">
                <Button variant="ghost" onClick={back} className="gap-2" data-testid="wizard-review-back-button">
                  <ArrowLeft className="h-4 w-4" /> Back
                </Button>
                <Button
                  size="lg"
                  onClick={runAnalysis}
                  className="gap-2"
                  data-testid="wizard-review-submit-button"
                >
                  Run AI analysis <Sparkles className="h-4 w-4" />
                </Button>
              </div>
            </Card>
          </motion.div>
        )}

        {phase === 'analyzing' && (
          <motion.div key="analyzing" variants={stepVariants} initial="initial" animate="animate" exit="exit">
            <AnalysisLoading />
          </motion.div>
        )}
      </AnimatePresence>
    </section>
  );
};

const QuestionInput = ({ q, value, onChange }) => {
  if (q.type === 'text') {
    return (
      <Input
        data-testid="wizard-followup-text-input"
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Type your answer…"
        className="h-11 bg-background/60"
      />
    );
  }
  if (q.type === 'slider') {
    const min = q.min ?? 0;
    const max = q.max ?? 10;
    const step = q.step ?? 1;
    return (
      <div data-testid="wizard-preference-slider">
        <div className="mb-3 flex items-center justify-between text-xs text-muted-foreground">
          <span>{min}</span>
          <span className="rounded-full bg-primary/15 px-3 py-0.5 text-sm font-semibold text-primary">
            {value ?? min}
          </span>
          <span>{max}</span>
        </div>
        <Slider
          min={min}
          max={max}
          step={step}
          value={[value ?? min]}
          onValueChange={(arr) => onChange(arr[0])}
        />
      </div>
    );
  }
  if (q.type === 'single_choice') {
    return (
      <RadioGroup
        value={value || ''}
        onValueChange={onChange}
        className="grid gap-2 sm:grid-cols-1"
        data-testid="wizard-single-choice"
      >
        {(q.options || []).map((opt) => (
          <label
            key={opt}
            className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-sm transition-colors ${
              value === opt
                ? 'border-primary/50 bg-primary/5 ring-1 ring-primary/30'
                : 'border-border/70 bg-background/40 hover:border-border'
            }`}
          >
            <RadioGroupItem value={opt} id={opt} />
            <span>{opt}</span>
          </label>
        ))}
      </RadioGroup>
    );
  }
  if (q.type === 'multi_choice') {
    const set = new Set(value || []);
    const toggle = (opt) => {
      if (set.has(opt)) set.delete(opt);
      else set.add(opt);
      onChange(Array.from(set));
    };
    return (
      <div className="grid gap-2" data-testid="wizard-multi-choice">
        {(q.options || []).map((opt) => {
          const checked = set.has(opt);
          return (
            <label
              key={opt}
              className={`flex cursor-pointer items-center gap-3 rounded-xl border px-4 py-3 text-sm transition-colors ${
                checked ? 'border-primary/50 bg-primary/5 ring-1 ring-primary/30' : 'border-border/70 bg-background/40 hover:border-border'
              }`}
            >
              <Checkbox checked={checked} onCheckedChange={() => toggle(opt)} />
              <span>{opt}</span>
            </label>
          );
        })}
      </div>
    );
  }
  return null;
};

const formatAnswer = (q, v) => {
  if (v == null || v === '') return <span className="italic">No answer</span>;
  if (Array.isArray(v)) return v.join(', ');
  return String(v);
};

export default Wizard;
