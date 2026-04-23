import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Trophy, ArrowLeft, Save, FileDown, Sparkles, ShieldAlert,
  TrendingUp, Scale, Lightbulb, ListChecks, AlertTriangle, Zap,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { analyzeDecision, saveDecision, getDecision, getGuestId } from '@/lib/api';
import ScoreBarChart from '@/components/results/ScoreBarChart';
import OptionCard from '@/components/results/OptionCard';
import BestOptionHero from '@/components/results/BestOptionHero';
import ProsConsTable from '@/components/results/ProsConsTable';
import WhatIfPanel from '@/components/results/WhatIfPanel';
import CompareView from '@/components/results/CompareView';
import ExportDialog from '@/components/results/ExportDialog';
import KeyInsights from '@/components/results/KeyInsights';
import ExecutionPlanCard from '@/components/results/ExecutionPlanCard';
import PlanBCard from '@/components/results/PlanBCard';

const useQuery = () => {
  const { search } = useLocation();
  return useMemo(() => new URLSearchParams(search), [search]);
};

const Results = () => {
  const q = useQuery();
  const id = q.get('id');
  const navigate = useNavigate();
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [whatIfResult, setWhatIfResult] = useState(null);
  const [whatIfLoading, setWhatIfLoading] = useState(false);
  const [savedId, setSavedId] = useState(id || null);
  const [exportOpen, setExportOpen] = useState(false);
  const reportRef = useRef(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        if (id) {
          const guest_id = getGuestId();
          const doc = await getDecision(id, guest_id);
          setState({
            id: doc.id,
            title: doc.title,
            decision: doc.decision,
            answers: doc.answers || [],
            result: doc.result,
          });
          setSavedId(doc.id);
        } else {
          const cached = sessionStorage.getItem('sda_current_result');
          if (!cached) {
            navigate('/wizard');
            return;
          }
          setState(JSON.parse(cached));
        }
      } catch (e) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load decision');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id, navigate]);

  const result = whatIfResult || state?.result;
  const options = result?.options || [];
  const bestId = result?.best_option_id;
  const best = options.find((o) => o.id === bestId) || options[0];
  const ranked = [...options].sort((a, b) => b.score - a.score);

  const runWhatIf = async (updatedAnswers) => {
    setWhatIfLoading(true);
    try {
      const res = await analyzeDecision(state.decision, updatedAnswers);
      setWhatIfResult(res);
      toast.success('What-if analysis updated');
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'What-if failed');
    } finally {
      setWhatIfLoading(false);
    }
  };

  const handleSave = async () => {
    if (!state) return;
    if (savedId) {
      toast.message('Already saved to your library');
      return;
    }
    try {
      const guest_id = getGuestId();
      const title = state.title || state.decision.slice(0, 60);
      const saved = await saveDecision({
        guest_id,
        title,
        decision: state.decision,
        answers: state.answers,
        result: state.result,
      });
      setSavedId(saved.id);
      toast.success('Saved to your library');
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Save failed');
    }
  };

  if (loading) {
    return (
      <section className="mx-auto w-full max-w-6xl px-4 pb-16 pt-8 sm:px-6 lg:px-8" data-testid="results-loading">
        <div className="mb-6 h-6 w-40 rounded shimmer" />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <div className="lg:col-span-8 space-y-4">
            <div className="h-48 rounded-2xl shimmer" />
            <div className="h-28 rounded-2xl shimmer" />
            <div className="h-28 rounded-2xl shimmer" />
          </div>
          <div className="lg:col-span-4 space-y-4">
            <div className="h-64 rounded-2xl shimmer" />
          </div>
        </div>
      </section>
    );
  }

  if (error || !state) {
    const errMsg = typeof error === 'string' ? error : (error?.message || 'Missing analysis.');
    return (
      <section className="mx-auto w-full max-w-2xl px-4 pb-16 pt-8 text-center" data-testid="results-error">
        <h2 className="text-xl font-semibold">We couldn&apos;t load this decision</h2>
        <p className="mt-2 text-sm text-muted-foreground">{errMsg}</p>
        <Link to="/wizard" className="mt-6 inline-block">
          <Button>Start a new decision</Button>
        </Link>
      </section>
    );
  }

  return (
    <section className="mx-auto w-full max-w-6xl px-4 pb-16 pt-8 sm:px-6 lg:px-8" data-testid="results-page">
      {/* Header */}
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="text-xs uppercase tracking-wider text-muted-foreground">Decision</div>
          <h1 className="mt-1 truncate text-xl font-semibold tracking-tight sm:text-2xl" data-testid="results-decision-title">
            {state.decision}
          </h1>
          {result?.goal && (
            <div className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-primary/30 bg-primary/5 px-3 py-1 text-xs text-primary" data-testid="results-goal">
              <Zap className="h-3 w-3" />
              Goal: <span className="text-foreground/90">{result.goal}</span>
            </div>
          )}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <Link to="/wizard">
            <Button variant="ghost" className="gap-2" data-testid="results-back-button">
              <ArrowLeft className="h-4 w-4" /> New
            </Button>
          </Link>
          <Button variant="secondary" className="gap-2" onClick={handleSave} disabled={!!savedId} data-testid="results-save-decision-button">
            <Save className="h-4 w-4" />
            {savedId ? 'Saved' : 'Save'}
          </Button>
          <Button className="gap-2" onClick={() => setExportOpen(true)} data-testid="results-export-pdf-button">
            <FileDown className="h-4 w-4" /> Export PDF
          </Button>
        </div>
      </div>

      <Tabs defaultValue="overview">
        <TabsList className="mb-6 flex flex-wrap">
          <TabsTrigger value="overview" data-testid="results-tab-overview">Overview</TabsTrigger>
          <TabsTrigger value="plan" data-testid="results-tab-plan">Execution plan</TabsTrigger>
          <TabsTrigger value="compare" data-testid="results-tab-compare">Compare</TabsTrigger>
          <TabsTrigger value="whatif" data-testid="results-tab-whatif">What-if</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div ref={reportRef} className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            <div className="space-y-6 lg:col-span-8">
              {best && <BestOptionHero best={best} reasoning={result?.reasoning} confidence={result?.confidence} />}

              {Array.isArray(result?.key_insights) && result.key_insights.length > 0 && (
                <KeyInsights insights={result.key_insights} />
              )}

              <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-score-chart">
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-semibold">Score breakdown</h3>
                    <p className="text-xs text-muted-foreground">Higher is better. Scores reflect fit to your answers.</p>
                  </div>
                  <Badge variant="secondary" className="rounded-full">
                    {options.length} options
                  </Badge>
                </div>
                <ScoreBarChart options={options} bestId={bestId} />
              </Card>

              <div className="space-y-3" data-testid="results-ranked-options">
                <h3 className="text-base font-semibold">All options (ranked)</h3>
                {ranked.map((o, i) => (
                  <OptionCard key={o.id} option={o} rank={i + 1} isBest={o.id === bestId} />
                ))}
              </div>

              <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6">
                <h3 className="mb-3 text-base font-semibold">Pros & Cons comparison</h3>
                <ProsConsTable options={ranked} />
              </Card>
            </div>

            {/* Right rail */}
            <div className="space-y-4 lg:col-span-4">
              <Card className="rounded-2xl border-border/70 bg-card/60 p-5" data-testid="results-confidence-meter">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs uppercase tracking-wider text-muted-foreground">Confidence</div>
                    <div className="mt-1 font-display text-3xl font-semibold tabular-nums">
                      {result?.confidence ?? 0}<span className="text-base text-muted-foreground">%</span>
                    </div>
                  </div>
                  <Sparkles className="h-5 w-5 text-primary" />
                </div>
                <Progress value={result?.confidence ?? 0} className="mt-4 h-2" />
                <p className="mt-3 text-xs text-muted-foreground">
                  Confidence reflects how decisive the AI&apos;s recommendation is given your inputs.
                </p>
              </Card>

              <Card className="rounded-2xl border-border/70 bg-card/60 p-5">
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <Scale className="h-4 w-4 text-primary" /> Key rationale
                </div>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground" data-testid="results-reasoning">
                  {result?.reasoning}
                </p>
              </Card>

              {result?.plan_b && (
                <PlanBCard planB={result.plan_b} trigger={result.plan_b_trigger} />
              )}

              <Card className="rounded-2xl border-border/70 bg-card/60 p-5">
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Quick stats</div>
                <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                  <Stat label="Options" value={options.length} icon={TrendingUp} />
                  <Stat label="Top score" value={best?.score ?? '-'} icon={Trophy} />
                  <Stat label="Risk" value={best?.risk_level ?? '-'} icon={ShieldAlert} />
                </div>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="plan">
          {result?.execution_plan ? (
            <ExecutionPlanCard plan={result.execution_plan} best={best} />
          ) : (
            <Card className="rounded-2xl border-border/70 bg-card/60 p-8 text-center" data-testid="results-no-execution-plan">
              <Lightbulb className="mx-auto mb-3 h-6 w-6 text-muted-foreground" />
              <p className="text-sm text-muted-foreground">No execution plan was returned for this analysis.</p>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="compare">
          <CompareView options={ranked} bestId={bestId} />
        </TabsContent>

        <TabsContent value="whatif">
          <WhatIfPanel
            decision={state.decision}
            answers={state.answers}
            onRun={runWhatIf}
            loading={whatIfLoading}
            currentResult={result}
            originalResult={state.result}
          />
        </TabsContent>
      </Tabs>

      <ExportDialog
        open={exportOpen}
        onOpenChange={setExportOpen}
        data={{ ...state, result }}
      />
    </section>
  );
};

const Stat = ({ label, value, icon: Icon }) => (
  <div className="rounded-lg border border-border/60 bg-background/40 p-3">
    <div className="mx-auto mb-1 grid h-8 w-8 place-items-center rounded-md bg-primary/10 text-primary">
      <Icon className="h-4 w-4" />
    </div>
    <div className="text-base font-semibold tabular-nums">{value}</div>
    <div className="text-[11px] uppercase tracking-wider text-muted-foreground">{label}</div>
  </div>
);

export default Results;
