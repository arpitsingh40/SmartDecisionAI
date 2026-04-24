import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import {
  Trophy, ArrowLeft, Save, FileDown, Sparkles, ShieldAlert,
  TrendingUp, Scale, Zap, BarChart3, Users, Swords,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { toast } from 'sonner';
import { saveDecision, getDecision, getGuestId, revertDebate } from '@/lib/api';
import { scoreAndRank, confidenceLevel } from '@/lib/scoring';
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
import BiasAlerts from '@/components/results/BiasAlerts';
import AssumptionsCard from '@/components/results/AssumptionsCard';
import EvaluationMatrix from '@/components/results/EvaluationMatrix';
import RiskScenarios from '@/components/results/RiskScenarios';
import FutureImpact from '@/components/results/FutureImpact';
import ExecuteDashboard from '@/components/results/ExecuteDashboard';
import Scorecard from '@/components/results/Scorecard';
import BoardroomPanel from '@/components/results/BoardroomPanel';
import DebatePanel from '@/components/debate/DebatePanel';
import DebateDialog from '@/components/debate/DebateDialog';

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
  const [savedId, setSavedId] = useState(id || null);
  const [exportOpen, setExportOpen] = useState(false);
  const [debateOpen, setDebateOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

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
            debate_history: doc.debate_history || [],
          });
          setSavedId(doc.id);
        } else {
          const cached = sessionStorage.getItem('sda_current_result');
          if (!cached) {
            navigate('/wizard');
            return;
          }
          const parsed = JSON.parse(cached);
          setState({ ...parsed, debate_history: parsed.debate_history || [] });
        }
      } catch (e) {
        setError(e?.response?.data?.detail || e?.message || 'Failed to load decision');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [id, navigate]);

  // The ACTIVE result for all tabs: latest debate turn's refined_result if any,
  // otherwise the original. This ensures Overview/Boardroom/Execute/etc.
  // all show the user's most recent refinement.
  const debateHistory = state?.debate_history || [];
  const latestTurn = debateHistory[debateHistory.length - 1];
  const originalResult = state?.result;
  const result = latestTurn?.refined_result || originalResult;
  const isRefined = !!latestTurn;

  const factorsInput = result?.factors_input || originalResult?.factors_input || [];
  const rawOptions = result?.options || [];

  // Client-side computed ranking using user weights (fallback to AI score if no factors)
  const ranked = useMemo(() => {
    if (factorsInput.length > 0) return scoreAndRank(rawOptions, factorsInput);
    return [...rawOptions].sort((a, b) => (b.score || 0) - (a.score || 0))
      .map((o, i) => ({ ...o, computed_score: o.score, computed_rank: i + 1 }));
  }, [rawOptions, factorsInput]);

  const bestId = ranked[0]?.id || result?.best_option_id;
  const best = ranked.find((o) => o.id === bestId) || ranked[0];
  const confLvl = confidenceLevel(result?.confidence);

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

  // --- Debate handlers ---
  const openDebate = () => {
    if (!savedId) {
      toast.info('Save the decision first to challenge it.');
      return;
    }
    setDebateOpen(true);
  };

  const handleTurnCompleted = (turn) => {
    // Append the new turn optimistically so UI updates immediately.
    setState((prev) => {
      if (!prev) return prev;
      const next = { ...prev, debate_history: [...(prev.debate_history || []), turn] };
      return next;
    });
    setActiveTab('debate');
  };

  const handleRevertToTurn = async (turnId) => {
    if (!savedId) return;
    try {
      const guest_id = getGuestId();
      await revertDebate(savedId, turnId, guest_id);
      // Refresh from server to stay authoritative.
      const doc = await getDecision(savedId, guest_id);
      setState((prev) => ({
        ...(prev || {}),
        id: doc.id,
        title: doc.title,
        decision: doc.decision,
        answers: doc.answers || [],
        result: doc.result,
        debate_history: doc.debate_history || [],
      }));
      toast.success('Reverted');
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Revert failed');
    }
  };

  const handleRevertToOriginal = () => handleRevertToTurn(null);

  if (loading) {
    return (
      <section className="mx-auto w-full max-w-6xl px-4 pb-16 pt-8 sm:px-6 lg:px-8" data-testid="results-loading">
        <div className="mb-6 h-6 w-40 rounded shimmer" />
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
          <div className="lg:col-span-8 space-y-4">
            <div className="h-48 rounded-2xl shimmer" />
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
          <Button
            variant="outline"
            className="gap-2"
            onClick={openDebate}
            disabled={!savedId}
            data-testid="results-challenge-button"
          >
            <Swords className="h-4 w-4" />
            Challenge
          </Button>
          <Button variant="secondary" className="gap-2" onClick={handleSave} disabled={!!savedId} data-testid="results-save-decision-button">
            <Save className="h-4 w-4" />
            {savedId ? 'Saved' : 'Save'}
          </Button>
          <Button className="gap-2" onClick={() => setExportOpen(true)} data-testid="results-export-pdf-button">
            <FileDown className="h-4 w-4" /> Export PDF
          </Button>
        </div>
      </div>

      {/* Refined banner — signals the active result is a user-refined version */}
      {isRefined && (
        <div
          className="mb-5 flex flex-wrap items-center gap-2 rounded-xl border border-primary/30 bg-primary/5 px-4 py-2.5 text-xs"
          data-testid="results-refined-banner"
        >
          <Sparkles className="h-3.5 w-3.5 text-primary" />
          <span className="text-foreground/90">
            Showing <span className="font-semibold">Refinement #{debateHistory.length}</span> —
            the most recent refinement from the debate.
          </span>
          <span className="mx-1 h-3 w-px bg-border" />
          <button
            type="button"
            onClick={() => setActiveTab('debate')}
            className="font-medium text-primary underline-offset-2 hover:underline"
            data-testid="results-refined-banner-open-debate"
          >
            Open Debate tab
          </button>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-6 flex flex-wrap">
          <TabsTrigger value="overview" data-testid="results-tab-overview">Overview</TabsTrigger>
          <TabsTrigger value="boardroom" data-testid="results-tab-boardroom">
            <Users className="mr-1.5 h-3.5 w-3.5" />
            Boardroom
          </TabsTrigger>
          <TabsTrigger value="debate" data-testid="results-tab-debate">
            <Swords className="mr-1.5 h-3.5 w-3.5" />
            Debate{debateHistory.length > 0 ? ` (${debateHistory.length})` : ''}
          </TabsTrigger>
          <TabsTrigger value="execute" data-testid="results-tab-execute">Execute</TabsTrigger>
          <TabsTrigger value="evaluation" data-testid="results-tab-evaluation">Evaluation</TabsTrigger>
          <TabsTrigger value="risk" data-testid="results-tab-risk">Scenarios</TabsTrigger>
          <TabsTrigger value="future" data-testid="results-tab-future">Future</TabsTrigger>
          <TabsTrigger value="compare" data-testid="results-tab-compare">Compare</TabsTrigger>
          <TabsTrigger value="whatif" data-testid="results-tab-whatif">What-if</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
            <div className="space-y-6 lg:col-span-8">
              {best && <BestOptionHero best={best} reasoning={result?.reasoning} confidence={result?.confidence} />}

              {Array.isArray(result?.bias_flags) && result.bias_flags.length > 0 && (
                <BiasAlerts flags={result.bias_flags} />
              )}

              {Array.isArray(result?.key_insights) && result.key_insights.length > 0 && (
                <KeyInsights insights={result.key_insights} />
              )}

              <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-score-chart">
                <div className="mb-3 flex items-center justify-between">
                  <div>
                    <h3 className="text-base font-semibold">Score breakdown</h3>
                    <p className="text-xs text-muted-foreground">
                      {factorsInput.length > 0
                        ? 'Weighted scores from your priorities × AI ratings.'
                        : 'AI scores reflect overall fit.'}
                    </p>
                  </div>
                  <Badge variant="secondary" className="rounded-full">
                    {ranked.length} options
                  </Badge>
                </div>
                <ScoreBarChart options={ranked} bestId={bestId} />
              </Card>

              <div className="space-y-3" data-testid="results-ranked-options">
                <h3 className="text-base font-semibold">All options (ranked)</h3>
                {ranked.map((o, i) => (
                  <OptionCard key={o.id} option={o} rank={i + 1} isBest={o.id === bestId} />
                ))}
              </div>
            </div>

            {/* Right rail */}
            <div className="space-y-4 lg:col-span-4">
              {result?.scorecard && (
                <Scorecard scorecard={result.scorecard} />
              )}

              <Card className="rounded-2xl border-border/70 bg-card/60 p-5" data-testid="results-confidence-meter">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs uppercase tracking-wider text-muted-foreground">Confidence</div>
                    <div className="mt-1 font-display text-3xl font-semibold tabular-nums">
                      {result?.confidence ?? 0}<span className="text-base text-muted-foreground">%</span>
                    </div>
                  </div>
                  <Badge
                    variant="secondary"
                    className={`rounded-full ${
                      confLvl.tone === 'emerald' ? 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400' :
                      confLvl.tone === 'amber' ? 'bg-amber-500/15 text-amber-600 dark:text-amber-400' :
                      'bg-rose-500/15 text-rose-600 dark:text-rose-400'
                    }`}
                    data-testid="results-confidence-level"
                  >
                    {confLvl.label}
                  </Badge>
                </div>
                <Progress value={result?.confidence ?? 0} className="mt-4 h-2" />
                <p className="mt-3 text-xs text-muted-foreground">
                  How decisive the AI is given your inputs.
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

              {Array.isArray(result?.assumptions) && result.assumptions.length > 0 && (
                <AssumptionsCard assumptions={result.assumptions} />
              )}

              {result?.plan_b && (
                <PlanBCard planB={result.plan_b} trigger={result.plan_b_trigger} />
              )}

              <Card className="rounded-2xl border-border/70 bg-card/60 p-5">
                <div className="text-xs uppercase tracking-wider text-muted-foreground">Quick stats</div>
                <div className="mt-3 grid grid-cols-3 gap-3 text-center">
                  <Stat label="Options" value={ranked.length} icon={TrendingUp} />
                  <Stat label="Top score" value={best?.computed_score ?? best?.score ?? '-'} icon={Trophy} />
                  <Stat label="Risk" value={best?.risk_level ?? '-'} icon={ShieldAlert} />
                </div>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="execute">
          <ExecuteDashboard result={result} best={best} />
        </TabsContent>

        <TabsContent value="boardroom">
          <BoardroomPanel
            agentPerspectives={result?.agent_perspectives || []}
            debate={result?.debate || null}
          />
        </TabsContent>

        <TabsContent value="debate">
          <DebatePanel
            debateHistory={debateHistory}
            onChallenge={openDebate}
            onRevert={handleRevertToTurn}
            onRevertToOriginal={debateHistory.length > 0 ? handleRevertToOriginal : null}
          />
        </TabsContent>

        <TabsContent value="evaluation">
          {factorsInput.length > 0 ? (
            <EvaluationMatrix options={ranked} factors={factorsInput} bestId={bestId} />
          ) : (
            <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-pros-cons-table">
              <h3 className="mb-3 text-base font-semibold">Pros & Cons comparison</h3>
              <ProsConsTable options={ranked} />
            </Card>
          )}
        </TabsContent>

        <TabsContent value="risk">
          <RiskScenarios options={ranked} bestId={bestId} />
        </TabsContent>

        <TabsContent value="future">
          <FutureImpact options={ranked} bestId={bestId} />
        </TabsContent>

        <TabsContent value="compare">
          <CompareView options={ranked} bestId={bestId} />
        </TabsContent>

        <TabsContent value="whatif">
          <WhatIfPanel
            options={rawOptions}
            factorsInput={factorsInput}
            bestId={bestId}
          />
        </TabsContent>
      </Tabs>

      <ExportDialog
        open={exportOpen}
        onOpenChange={setExportOpen}
        data={{ ...state, result: { ...result, ranked } }}
      />

      <DebateDialog
        open={debateOpen}
        onOpenChange={setDebateOpen}
        decisionId={savedId}
        onTurnCompleted={handleTurnCompleted}
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
