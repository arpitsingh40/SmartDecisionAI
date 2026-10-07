import { MessageCircle, Target, Building2, Wifi, ShieldCheck } from 'lucide-react';

// Timeline steps for the builder story.
const STEPS = [
  {
    num: '01', icon: MessageCircle, label: 'Describe the idea',
    desc: 'One or two sentences. The engine extracts your industry, stage, constraints, fears, and the forks you are wrestling with.',
    accent: '#2F8F8A',
    detail: 'Then it asks the 3-5 questions it actually needs. It says "unknown" instead of inventing — and waits for your answer.',
  },
  {
    num: '02', icon: Target, label: 'Approve the mission',
    desc: 'A North Star, a number, a deadline, ranked priorities, and decision rules you can use without the AI.',
    accent: '#2F8F8A',
    detail: 'Everything is editable before it becomes real. This is the judgement layer — yours, not the model\'s.',
  },
  {
    num: '03', icon: Building2, label: 'The company gets built',
    desc: 'Divisions, executives with industry-specific roles, KPIs, budgets, and culture principles — created as real records, not slides.',
    accent: '#2F8F8A',
    detail: 'Every executive starts at L3: they recommend, you approve. Authority grows only when you grant it.',
  },
  {
    num: '04', icon: Wifi, label: 'It runs through your tools',
    desc: 'Connect Gmail, your CRM, your calendar. First-week tasks are generated per executive and wait in your approval queue.',
    accent: '#2F8F8A',
    detail: 'Business OS runs scheduled cycles. No tools connected? Tasks go to your honest manual queue — never a fake execution.',
  },
  {
    num: '05', icon: ShieldCheck, label: 'Proof, not vibes',
    desc: 'Every decision, action, and outcome lands in the Record Room — with spend caps and one kill switch over all of it.',
    accent: '#2F8F8A',
    detail: 'Outcomes are verified or marked manual. The audit trail is queryable, and nothing is self-reported.',
  },
];

// Vertical timeline walking through the five builder steps.
export default function HowItWorks() {
  return (
    <section id="how-it-works" className="relative py-28 sm:py-36 bg-surface overflow-x-clip">
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[1200px] h-[800px] rounded-full opacity-15"
          style={{ background: 'radial-gradient(circle at 50% 0%, hsl(var(--accent)/0.08) 0%, transparent 60%)' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 sm:px-10 lg:px-14">
        <div className="text-center max-w-2xl mx-auto mb-16 sm:mb-20">
          <span className="inline-flex items-center gap-2 text-[11px] tracking-[0.26em] uppercase text-accent font-semibold mb-5">
            <span className="h-px bg-accent w-8" />
            How it works
          </span>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-[4rem] leading-[0.95] text-text tracking-tight">
            You steer.<br />The company runs.
          </h2>
          <p className="mt-4 text-muted text-sm sm:text-base max-w-sm mx-auto">
            From one sentence to a live company — five steps
          </p>
        </div>

        <div className="relative max-w-4xl mx-auto">
          <div className="hidden sm:block absolute left-8 top-0 bottom-0 w-px bg-gradient-to-b from-accent/30 via-accent/20 to-accent/30" />
          <div className="space-y-12 sm:space-y-16">
            {STEPS.map((s) => {
              const Icon = s.icon;
              return (
                <div key={s.label} className="relative flex gap-6 sm:gap-8 items-start">
                  <div className="relative shrink-0">
                    <div className="w-16 h-16 rounded-2xl bg-surface border border-hairline flex items-center justify-center shadow-sm">
                      <Icon size={22} strokeWidth={1.5} style={{ color: s.accent }} />
                    </div>
                  </div>
                  <div className="pt-2">
                    <div className="text-[10px] tracking-[0.3em] font-semibold mb-1 text-accent">{s.num}</div>
                    <h3 className="font-display text-2xl text-text mb-2">{s.label}.</h3>
                    <p className="text-sm text-muted leading-relaxed max-w-lg">{s.desc}</p>
                    <p className="text-xs text-accent/80 leading-relaxed max-w-lg mt-2">{s.detail}</p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
