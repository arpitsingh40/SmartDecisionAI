import { Building2, Target, Zap, Hammer, ShieldCheck, History, ArrowRight } from 'lucide-react';

// Feature card content for the six builder surfaces.
const FEATURES = [
  {
    icon: Building2,
    title: 'Company Genesis',
    desc: 'Your idea becomes a digital twin, a mission, and an organization — divisions, executives with industry-specific roles, KPIs, budgets, and culture. Real records, not slides.',
    accent: '#2F8F8A',
    details: ['Vision → mission → org in one wizard', 'Executives created in the database', 'Everything editable before it is real'],
  },
  {
    icon: Target,
    title: 'Mission & North Star',
    desc: 'A number, a deadline, ranked priorities, and decision rules you can use without the AI. Every executive steers toward it — you set it.',
    accent: '#2F8F8A',
    details: ['Editable mission, target, deadline', 'Priorities ranked by you', 'Decision rules that outlive the model'],
  },
  {
    icon: Zap,
    title: 'Autonomous Ops',
    desc: 'Business OS runs scheduled cycles for your company: morning briefs, follow-ups, pipeline health, weekly strategy. Tasks execute through your connected tools.',
    accent: '#2F8F8A',
    details: ['Scheduled processes per department', 'Runs through connected tools', 'Approval queue for anything risky'],
  },
  {
    icon: Hammer,
    title: 'Capability Builder',
    desc: 'Need a landing page, a report, a workflow? The builder drafts and iterates artifacts, then deploys them through your connected tools.',
    accent: '#2F8F8A',
    details: ['Build, review, iterate', 'Deploys via your tools', 'Lives in your workspace'],
  },
  {
    icon: ShieldCheck,
    title: 'Founder Control',
    desc: 'Mission Control gives you the kill switch, the budget cap, and the approval queue. Every executive starts at L3 — they recommend, you approve.',
    accent: '#2F8F8A',
    details: ['One kill switch stops everything', 'Per-org spend caps', 'Approve, reject, or hand to manual'],
  },
  {
    icon: History,
    title: 'Record Room',
    desc: 'Every decision, execution, tool call, and verified outcome in one audit trail. Outcomes are evidence-backed or marked manual — never invented.',
    accent: '#2F8F8A',
    details: ['Every event audited', 'Free-text search', 'Verified or honestly manual'],
  },
];

// Grid of feature cards describing the six builder surfaces.
export default function FeaturesSection() {
  return (
    <section id="features" className="relative py-28 sm:py-36 bg-surface-2 overflow-x-clip">
      <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
        <div className="absolute -top-40 -right-40 w-[800px] h-[800px] rounded-full opacity-25"
          style={{ background: 'radial-gradient(circle, hsl(var(--accent)/0.08) 0%, transparent 65%)' }} />
        <div className="absolute -bottom-40 -left-40 w-[600px] h-[600px] rounded-full opacity-20"
          style={{ background: 'radial-gradient(circle, hsl(var(--accent)/0.06) 0%, transparent 60%)' }} />
      </div>

      <div className="relative max-w-7xl mx-auto px-6 sm:px-10 lg:px-14">
        <div className="text-center max-w-2xl mx-auto mb-16 sm:mb-20">
          <span className="inline-flex items-center gap-2 text-[11px] tracking-[0.26em] uppercase text-accent font-semibold mb-5">
            <span className="h-px bg-accent w-8" />
            Not a chatbot
          </span>
          <h2 className="font-display text-4xl sm:text-5xl lg:text-[4rem] leading-[0.95] text-text tracking-tight">
            An organization<br />that happens to run on AI.
          </h2>
          <p className="mt-4 text-muted text-sm max-w-md mx-auto">
            Six surfaces. One company. The AI is the means — the company is the product.
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5 sm:gap-6">
          {FEATURES.map((f) => {
            const Icon = f.icon;
            return (
              <div key={f.title}
                className="group relative bg-surface border border-hairline rounded-3xl p-7 transition-all duration-500 cursor-default overflow-hidden hover:-translate-y-1 hover:shadow-elevation-2">
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-700"
                  style={{ background: `radial-gradient(ellipse at 50% 0%, ${f.accent}10 0%, transparent 70%)` }} />
                <div className="relative">
                  <div className="w-12 h-12 rounded-xl bg-surface-2 border border-hairline flex items-center justify-center mb-5">
                    <Icon size={20} strokeWidth={1.5} style={{ color: f.accent }} />
                  </div>
                  <h3 className="font-display text-xl text-text mb-2.5">{f.title}</h3>
                  <p className="text-sm text-muted leading-relaxed">{f.desc}</p>
                  <div className="overflow-hidden max-h-0 opacity-0 group-hover:max-h-40 group-hover:opacity-100 transition-all duration-300">
                    <div className="pt-4 mt-4 border-t border-hairline space-y-2">
                      {f.details.map((d) => (
                        <div key={d} className="flex items-center gap-2 text-xs text-muted">
                          <div className="w-1 h-1 rounded-full" style={{ backgroundColor: f.accent }} />
                          {d}
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs font-medium mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    style={{ color: f.accent }}>
                    <span>Details</span>
                    <ArrowRight size={12} strokeWidth={2} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
