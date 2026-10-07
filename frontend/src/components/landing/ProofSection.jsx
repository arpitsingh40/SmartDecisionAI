import { ShieldCheck, Wallet, History, CheckCircle2 } from 'lucide-react';

// Honest trust rails — each maps to a working surface, not a testimonial.
const RAILS = [
  {
    icon: ShieldCheck,
    title: 'L3 by default',
    desc: 'Every executive starts recommend-only. Nothing happens until you approve it — the approval queue is the product, not a setting.',
  },
  {
    icon: Wallet,
    title: 'Budget caps + kill switch',
    desc: 'Spend is capped per org per month. One switch stops every agent, immediately — the founder override is real and tested.',
  },
  {
    icon: History,
    title: 'The Record Room',
    desc: 'Every decision, execution, tool call and task event is audited. You can read your company history like a database.',
  },
  {
    icon: CheckCircle2,
    title: 'Honest by design',
    desc: 'Outcomes are evidence-backed or marked manual. No invented verifications, no fake agents, no "12 tools connected" when none are.',
  },
];

// Trust section that replaces fabricated testimonials until real outcomes exist.
export default function ProofSection() {
  return (
    <section id="proof" className="relative py-28 sm:py-36 bg-surface overflow-hidden">
      <div className="max-w-4xl mx-auto px-6 sm:px-10 text-center">
        <span className="inline-flex items-center gap-2 text-[11px] tracking-[0.26em] uppercase text-accent font-semibold mb-5">
          <span className="h-px w-8 bg-accent" />
          Proof, not promises
        </span>
        <h2 className="font-display text-4xl sm:text-5xl text-text tracking-tight mb-4">
          Nothing executes on vibes.
        </h2>
        <p className="text-sm text-muted max-w-md mx-auto mb-12">
          These are the rails the company runs on. The first cohort's outcome ledger will be published here —
          we will not fake a quote before it exists.
        </p>

        <div className="grid sm:grid-cols-2 gap-5 text-left">
          {RAILS.map((r) => {
            const Icon = r.icon;
            return (
              <div key={r.title} className="rounded-3xl border border-hairline bg-surface-2 p-6">
                <div className="w-10 h-10 rounded-xl bg-surface border border-hairline flex items-center justify-center mb-4">
                  <Icon size={18} strokeWidth={1.5} className="text-accent" />
                </div>
                <h3 className="font-display text-lg text-text mb-1.5">{r.title}</h3>
                <p className="text-sm text-muted leading-relaxed">{r.desc}</p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
