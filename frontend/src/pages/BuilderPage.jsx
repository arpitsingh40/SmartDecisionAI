import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { TopBar } from '../components/TopBar';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { toast } from 'sonner';
import {
  Loader2, Rocket, Sparkles, Building2, Users, Wifi, Play, CheckCircle2,
  ArrowRight, Target, Wallet, ShieldCheck, Gauge, Hammer,
} from 'lucide-react';

const STEPS = ['Idea', 'Questions', 'Mission', 'Company', 'Tools', 'Launch'];

const STAGE_INDEX = {
  not_started: 0, clarify: 1, review_mission: 2, review_org: 3, connect_tools: 4, launched: 5,
};

const inr = (v) => new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(v || 0);

const titleCase = (s) => String(s || '').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

function StepRail({ stage }) {
  const idx = STAGE_INDEX[stage] ?? 0;
  return (
    <div className="flex flex-wrap items-center gap-1.5" data-testid="builder-steps">
      {STEPS.map((s, i) => (
        <span key={s}
          className={`inline-flex items-center gap-1.5 text-[11px] rounded-full px-2.5 py-1 border ${i === idx ? 'border-accent/40 bg-accent/10 text-accent font-medium' : i < idx ? 'border-hairline bg-surface-2 text-muted' : 'border-hairline text-muted/60'}`}>
          <span className="font-mono-plex">{i + 1}</span>{s}
        </span>
      ))}
    </div>
  );
}

function Field({ label, children }) {
  return (
    <div>
      <p className="text-[11px] uppercase tracking-wide text-muted mb-1.5">{label}</p>
      {children}
    </div>
  );
}

export default function BuilderPage() {
  const navigate = useNavigate();
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [vision, setVision] = useState('');
  const [answers, setAnswers] = useState({});
  const [missionDraft, setMissionDraft] = useState(null);
  const [orgDraft, setOrgDraft] = useState(null);
  const [capabilities, setCapabilities] = useState([]);
  const [connections, setConnections] = useState(null);
  const [launchResult, setLaunchResult] = useState(null);

  const load = useCallback(async () => {
    try {
      const r = await api.get('/genesis/status');
      setStatus(r.data);
      if (r.data.stage === 'review_mission' && r.data.mission) setMissionDraft(r.data.mission);
      if (r.data.org) setOrgDraft(r.data.org);
      if (['connect_tools', 'launched'].includes(r.data.stage)) {
        api.get('/genesis/connect').then((c) => setConnections(c.data?.connections || [])).catch(() => {});
      }
    } catch (_) {
      toast.error('Could not load your builder session.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const run = async (fn, errMsg) => {
    setBusy(true);
    try { return await fn(); }
    catch (e) { toast.error(e?.response?.data?.detail || errMsg); return null; }
    finally { setBusy(false); }
  };

  const start = () => run(async () => {
    const r = await api.post('/genesis/start', { vision: vision.trim() });
    setStatus((s) => ({ ...(s || {}), stage: r.data.stage, twin: r.data.twin, questions: r.data.questions }));
    setAnswers({});
  }, 'Could not read your idea. Try again.');

  const submitAnswers = () => run(async () => {
    const r = await api.post('/genesis/answer', { answers });
    setMissionDraft(r.data.mission);
    setStatus((s) => ({ ...s, stage: r.data.stage, mission: r.data.mission }));
  }, 'Could not shape your mission. Try again.');

  const approveMission = () => run(async () => {
    const m = missionDraft || {};
    const priorities = Array.isArray(m.priorities)
      ? m.priorities
      : String(m.priorities || '').split('\n').map((p) => p.trim()).filter(Boolean);
    const r = await api.post('/genesis/approve-mission', {
      mission: m,
      north_star: m.north_star || '',
      target: m.target || '',
      deadline: m.deadline || '',
      priorities,
      decision_rules: m.decision_rules || '',
    });
    setOrgDraft(r.data.organization || { divisions: [], culture: [] });
    setCapabilities(r.data.capabilities_needed || []);
    setStatus((s) => ({ ...s, stage: r.data.stage }));
  }, 'Could not design your organization. Try again.');

  const approveOrg = () => run(async () => {
    const r = await api.post('/genesis/approve-org', {
      divisions: orgDraft?.divisions || [],
      culture: orgDraft?.culture || [],
    });
    setStatus((s) => ({
      ...s, stage: r.data.stage, org_id: r.data.org_id,
      executives: r.data.executives || [],
    }));
    if (r.data.capabilities_needed) setCapabilities(r.data.capabilities_needed);
    api.get('/genesis/connect').then((c) => setConnections(c.data?.connections || [])).catch(() => {});
    toast.success(`${r.data.org_name} created — ${r.data.executives_created} executives on board.`);
  }, 'Could not create your company. Try again.');

  const connectTool = async (toolkit) => {
    try {
      const r = await api.post('/execution/connections/connect', {
        toolkit, redirect_uri: window.location.origin + '/app/build',
      });
      if (r.data?.auth_url) window.open(r.data.auth_url, '_blank');
      setTimeout(() => api.get('/genesis/connect').then((c) => setConnections(c.data?.connections || [])).catch(() => {}), 5000);
    } catch (_) {
      toast.error('Could not start the connection flow.');
    }
  };

  const launch = () => run(async () => {
    const r = await api.post('/genesis/launch');
    setLaunchResult(r.data);
    setStatus((s) => ({ ...s, stage: r.data.stage, tasks_generated: r.data.tasks_generated }));
  }, 'Could not launch your company. Try again.');

  if (loading) {
    return (
      <div className="min-h-screen"><TopBar />
        <div className="max-w-3xl mx-auto px-4 py-10 space-y-4">
          <div className="h-8 w-56 animate-pulse rounded-md bg-surface-2" />
          <div className="h-32 animate-pulse rounded-2xl bg-surface-2" />
        </div>
      </div>
    );
  }

  const stage = status?.stage || 'not_started';
  const twin = status?.twin || {};
  const questions = status?.questions || [];
  const executives = status?.executives || [];
  const orgExecCount = (orgDraft?.divisions || []).reduce((n, d) => n + (d.executives?.length || 0), 0);

  return (
    <div className="min-h-screen">
      <TopBar />
      <main data-testid="builder-page" className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        <div className="flex flex-col gap-3">
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center justify-center w-9 h-9 rounded-xl bg-text text-background">
              <Hammer size={17} strokeWidth={1.75} />
            </span>
            <div>
              <h1 className="font-display text-2xl leading-tight">Build your company</h1>
              <p className="text-sm text-muted">Type an idea. Get a company.</p>
            </div>
          </div>
          <StepRail stage={stage} />
        </div>

        {stage === 'not_started' && (
          <section className="rounded-2xl border border-hairline bg-surface p-6 space-y-4" data-testid="builder-step-idea">
            <div className="space-y-1.5">
              <h2 className="font-display text-xl">What do you want to build?</h2>
              <p className="text-sm text-muted leading-relaxed">
                One or two sentences is enough. The engine extracts your situation, asks what it needs,
                then designs the mission and the company around it.
              </p>
            </div>
            <Textarea
              data-testid="builder-vision-input"
              value={vision}
              onChange={(e) => setVision(e.target.value)}
              rows={5}
              placeholder="I want to build India's largest rooftop solar company for housing societies. 3 people, ₹20L saved up, no sales team yet."
              className="text-[15px] resize-none rounded-xl"
            />
            <div className="flex items-center justify-between gap-3">
              <span className="text-[11px] text-muted">{vision.trim().length}/5000</span>
              <Button data-testid="builder-start-btn" onClick={start} disabled={busy || vision.trim().length < 10}
                className="rounded-xl bg-accent hover:bg-accent/90 text-white">
                {busy ? <Loader2 size={15} className="animate-spin mr-2" /> : <Sparkles size={15} className="mr-2" />}
                Read my idea
              </Button>
            </div>
          </section>
        )}

        {stage === 'clarify' && (
          <section className="space-y-5" data-testid="builder-step-clarify">
            <div className="rounded-2xl border border-hairline bg-surface p-5 space-y-3" data-testid="builder-twin">
              <p className="text-[11px] uppercase tracking-wide text-muted">What I extracted</p>
              <div className="flex flex-wrap gap-1.5">
                {[
                  twin.industry && `Industry: ${twin.industry}`,
                  twin.stage && `Stage: ${twin.stage}`,
                  twin.team_size > 0 && `Team: ${twin.team_size}`,
                  twin.runway_months > 0 && `Runway: ${twin.runway_months} months`,
                  twin.current_arr > 0 && `ARR: ${inr(twin.current_arr)}`,
                ].filter(Boolean).map((t) => (
                  <span key={t} className="text-xs rounded-full border border-hairline bg-surface-2 px-2.5 py-1 text-muted">{t}</span>
                ))}
              </div>
              {twin.constraints?.length > 0 && (
                <p className="text-xs text-muted leading-relaxed"><span className="text-text">Constraints:</span> {twin.constraints.join(' · ')}</p>
              )}
              {twin.strategic_forks?.length > 0 && (
                <p className="text-xs text-muted leading-relaxed"><span className="text-text">Forks:</span> {twin.strategic_forks.join(' · ')}</p>
              )}
            </div>

            <div className="rounded-2xl border border-hairline bg-surface p-6 space-y-5">
              <div className="space-y-1">
                <h2 className="font-display text-xl">{questions.length} questions before I design the company</h2>
                <p className="text-sm text-muted">Answer in your own words. Short is fine.</p>
              </div>
              {questions.map((q, i) => (
                <Field key={i} label={`${i + 1}. ${q}`}>
                  <Textarea
                    data-testid={`builder-question-${i}`}
                    value={answers[String(i)] || ''}
                    onChange={(e) => setAnswers((a) => ({ ...a, [String(i)]: e.target.value }))}
                    rows={2}
                    className="text-sm resize-none rounded-xl"
                    placeholder="Your answer"
                  />
                </Field>
              ))}
              <Button data-testid="builder-answers-submit" onClick={submitAnswers} disabled={busy}
                className="rounded-xl w-full sm:w-auto">
                {busy ? <Loader2 size={15} className="animate-spin mr-2" /> : <ArrowRight size={15} className="mr-2" />}
                Shape my mission
              </Button>
            </div>
          </section>
        )}

        {stage === 'review_mission' && missionDraft && (
          <section className="rounded-2xl border border-hairline bg-surface p-6 space-y-5" data-testid="builder-step-mission">
            <div className="space-y-1">
              <p className="text-[11px] uppercase tracking-wide text-muted">Step 3 · Your mission</p>
              <h2 className="font-display text-xl">Edit anything. This becomes your North Star.</h2>
            </div>
            <Field label="Mission">
              <Textarea data-testid="builder-mission-text" rows={2} className="text-sm resize-none rounded-xl"
                value={missionDraft.mission || ''}
                onChange={(e) => setMissionDraft((m) => ({ ...m, mission: e.target.value }))} />
            </Field>
            <Field label="North star (10-year outcome)">
              <Input data-testid="builder-north-star" className="rounded-xl text-sm"
                value={missionDraft.north_star || ''}
                onChange={(e) => setMissionDraft((m) => ({ ...m, north_star: e.target.value }))} />
            </Field>
            <div className="grid sm:grid-cols-2 gap-4">
              <Field label="Target (number)">
                <Input data-testid="builder-target" className="rounded-xl text-sm"
                  value={missionDraft.target || ''}
                  onChange={(e) => setMissionDraft((m) => ({ ...m, target: e.target.value }))} />
              </Field>
              <Field label="Deadline">
                <Input data-testid="builder-deadline" className="rounded-xl text-sm"
                  value={missionDraft.deadline || ''}
                  onChange={(e) => setMissionDraft((m) => ({ ...m, deadline: e.target.value }))} />
              </Field>
            </div>
            <Field label="Priorities (one per line)">
              <Textarea data-testid="builder-priorities" rows={4} className="text-sm resize-none rounded-xl"
                value={Array.isArray(missionDraft.priorities) ? missionDraft.priorities.join('\n') : (missionDraft.priorities || '')}
                onChange={(e) => setMissionDraft((m) => ({ ...m, priorities: e.target.value.split('\n') }))} />
            </Field>
            <Field label="Decision rules">
              <Textarea data-testid="builder-rules" rows={3} className="text-sm resize-none rounded-xl"
                value={missionDraft.decision_rules || ''}
                onChange={(e) => setMissionDraft((m) => ({ ...m, decision_rules: e.target.value }))} />
            </Field>
            <Button data-testid="builder-approve-mission" onClick={approveMission} disabled={busy}
              className="rounded-xl bg-accent hover:bg-accent/90 text-white">
              {busy ? <Loader2 size={15} className="animate-spin mr-2" /> : <Building2 size={15} className="mr-2" />}
              Design my company
            </Button>
          </section>
        )}

        {stage === 'review_org' && orgDraft && (
          <section className="space-y-5" data-testid="builder-step-org">
            <div className="space-y-1">
              <p className="text-[11px] uppercase tracking-wide text-muted">Step 4 · Your organization</p>
              <h2 className="font-display text-xl">
                {(orgDraft.divisions || []).length} divisions · {orgExecCount} executives
              </h2>
              <p className="text-sm text-muted">Every executive starts at L3 — they recommend, you approve.</p>
            </div>

            {(orgDraft.divisions || []).map((d, di) => (
              <div key={di} className="rounded-2xl border border-hairline bg-surface p-5 space-y-4" data-testid={`builder-division-${di}`}>
                <div className="flex items-center gap-2">
                  <Building2 size={15} className="text-accent" />
                  <h3 className="font-display text-lg">{d.name}</h3>
                  <span className="text-[11px] text-muted rounded-full border border-hairline px-2 py-0.5">{titleCase(d.function)}</span>
                </div>
                {(d.executives || []).map((ex, ei) => (
                  <div key={ei} className="rounded-xl border border-hairline bg-surface-2/50 p-4 space-y-2" data-testid={`builder-exec-${di}-${ei}`}>
                    <div className="flex flex-wrap items-center gap-2">
                      <Users size={13} className="text-muted" />
                      <span className="text-sm font-medium">{ex.role}</span>
                      {ex.spending_limit_inr > 0 && (
                        <span className="inline-flex items-center gap-1 text-[11px] text-muted"><Wallet size={11} /> {inr(ex.spending_limit_inr)} limit</span>
                      )}
                    </div>
                    {ex.mission && <p className="text-xs text-muted leading-relaxed">{ex.mission}</p>}
                    {ex.kpis?.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {ex.kpis.map((k, ki) => (
                          <span key={ki} className="text-[11px] rounded-full border border-hairline px-2 py-0.5 text-muted">
                            {k.name}: {k.target}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ))}

            {(orgDraft.culture || []).length > 0 && (
              <div className="rounded-2xl border border-hairline bg-surface p-5 space-y-3" data-testid="builder-culture">
                <p className="text-[11px] uppercase tracking-wide text-muted flex items-center gap-1.5"><ShieldCheck size={12} /> Culture principles</p>
                {(orgDraft.culture || []).map((p, i) => (
                  <div key={i} className="text-xs leading-relaxed">
                    <span className="text-text font-medium">{p.statement}</span>
                    {p.heuristic && <span className="text-muted"> — {p.heuristic}</span>}
                  </div>
                ))}
              </div>
            )}

            {orgExecCount === 0 && (
              <p className="text-sm text-amber-600" data-testid="builder-org-empty">
                The design came back empty. Press "Design my company" again to retry.
              </p>
            )}
            <Button data-testid="builder-approve-org" onClick={approveOrg} disabled={busy || orgExecCount === 0}
              className="rounded-xl bg-accent hover:bg-accent/90 text-white">
              {busy ? <Loader2 size={15} className="animate-spin mr-2" /> : <Rocket size={15} className="mr-2" />}
              Create my company
            </Button>
          </section>
        )}

        {stage === 'connect_tools' && (
          <section className="space-y-5" data-testid="builder-step-tools">
            <div className="rounded-2xl border border-accent/20 bg-accent/[0.03] p-5 flex items-center gap-3">
              <CheckCircle2 size={18} className="text-accent shrink-0" />
              <div>
                <p className="text-sm font-medium">{executives.length || status?.executives_created || 0} executives created</p>
                <p className="text-xs text-muted">Connect the tools they should work through — or launch without and tasks wait in your manual queue.</p>
              </div>
            </div>

            {(capabilities || []).length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {(capabilities || []).slice(0, 8).map((c, i) => (
                  <span key={i} className="text-[11px] rounded-full border border-hairline bg-surface px-2.5 py-1 text-muted" title={c.why}>
                    {titleCase(c.capability)}
                  </span>
                ))}
              </div>
            )}

            <div className="rounded-2xl border border-hairline bg-surface p-5 space-y-3" data-testid="builder-connections">
              <p className="text-[11px] uppercase tracking-wide text-muted flex items-center gap-1.5"><Wifi size={12} /> Tools</p>
              {(connections || []).length === 0 && <p className="text-sm text-muted">No required tools for this business yet.</p>}
              {(connections || []).map((c) => (
                <div key={c.toolkit} className="flex items-center justify-between gap-3 py-1.5">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className={`w-2 h-2 rounded-full shrink-0 ${c.status === 'connected' ? 'bg-emerald-500' : c.status === 'builtin' ? 'bg-accent' : 'bg-muted/40'}`} />
                    <span className="text-sm truncate">{titleCase(c.toolkit)}</span>
                    {c.needed && <span className="text-[10px] text-muted/70 shrink-0">needed</span>}
                  </div>
                  {c.status === 'connected'
                    ? <span className="text-[11px] text-emerald-600 shrink-0">Connected</span>
                    : c.status === 'builtin'
                      ? <span className="text-[11px] text-accent shrink-0" title={c.note || ''}>Built in</span>
                      : <Button size="sm" variant="outline" className="rounded-lg h-7 px-2.5 text-xs"
                          data-testid={`builder-connect-${c.toolkit}`} onClick={() => connectTool(c.toolkit)}>Connect</Button>}
                </div>
              ))}
            </div>

            <Button data-testid="builder-launch-btn" onClick={launch} disabled={busy}
              className="rounded-xl bg-accent hover:bg-accent/90 text-white">
              {busy ? <Loader2 size={15} className="animate-spin mr-2" /> : <Play size={15} className="mr-2" />}
              Launch first-week tasks
            </Button>
          </section>
        )}

        {stage === 'launched' && (
          <section className="rounded-2xl border border-hairline bg-surface p-6 space-y-5" data-testid="builder-launched">
            <div className="space-y-2">
              <span className="inline-flex items-center justify-center w-10 h-10 rounded-2xl bg-accent/10 text-accent">
                <Rocket size={18} />
              </span>
              <h2 className="font-display text-xl">Your company is live.</h2>
              <p className="text-sm text-muted leading-relaxed">
                {launchResult?.tasks_generated || status?.tasks_generated || 0} first-week tasks are waiting for your approval.
                Nothing executes until you approve it — that is your authority gradient.
              </p>
            </div>
            <div className="grid sm:grid-cols-3 gap-3">
              {[
                { icon: Gauge, label: 'Mission Control', sub: 'Approve tasks, watch outcomes', to: '/app/mission-control' },
                { icon: Wifi, label: 'Business OS', sub: 'Run cycles, connect tools', to: '/app/business-os' },
                { icon: Target, label: 'Record Room', sub: 'Every action, audited', to: '/app/record-room' },
              ].map((c) => (
                <button key={c.label} onClick={() => navigate(c.to)}
                  className="rounded-xl border border-hairline bg-surface-2/50 p-4 text-left hover:border-accent/30 transition-colors">
                  <c.icon size={15} className="text-accent" />
                  <p className="text-sm font-medium mt-2">{c.label}</p>
                  <p className="text-[11px] text-muted mt-0.5">{c.sub}</p>
                </button>
              ))}
            </div>
            <Button variant="outline" className="rounded-xl" onClick={() => navigate('/app')}>
              Back to home <ArrowRight size={14} className="ml-2" />
            </Button>
          </section>
        )}

        {['not_started', 'clarify', 'review_mission', 'review_org', 'connect_tools', 'launched'].indexOf(stage) === -1 && (
          <section className="rounded-2xl border border-hairline bg-surface p-6">
            <p className="text-sm text-muted">Session stage "{stage}" — <button className="text-accent hover:underline" onClick={load}>reload</button>.</p>
          </section>
        )}
      </main>
    </div>
  );
}
