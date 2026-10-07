import { MessageCircle, Building2, Rocket } from 'lucide-react';

// Frames mirror the real builder wizard at /app/build.
const SCREENS = [
  {
    icon: MessageCircle,
    label: 'Step 1 · Idea',
    desc: 'One or two sentences. The engine reads your situation and asks the questions it actually needs.',
    lines: ['What do you want to build?', 'I want to build India\'s largest rooftop solar company for housing societies. 3 people, ₹20L saved up, no sales team yet.', '[ Read my idea ]', 'Then:', '2 questions before I design the company', 'Who is your first customer?', 'What is your monthly burn?'],
  },
  {
    icon: Building2,
    label: 'Step 4 · Your organization',
    desc: 'Divisions, executives, KPIs and budgets — generated for your industry, every executive at L3.',
    lines: ['2 divisions · 5 executives', 'Sales — VP Housing Society Sales', '₹1,00,000 limit · Signed: 10 societies', 'Delivery — Head of Installation', '₹50,000 limit · On-time: 95%', 'Culture: Owner mindset', 'Every executive starts at L3. They recommend, you approve.'],
  },
  {
    icon: Rocket,
    label: 'Step 6 · Launched',
    desc: 'First-week tasks wait in your approval queue. Nothing runs until you approve it.',
    lines: ['Your company is live.', '9 first-week tasks awaiting approval', 'Mission Control — approve, reject, watch outcomes', 'Budget caps on · Kill switch armed', 'Record Room — everything audited', 'No connected tool? Honest manual queue.'],
  },
];

// Section showcasing the three real surfaces of the builder flow.
export default function DemoSection() {
  return (
    <section id="demo" className="relative py-28 sm:py-36 bg-surface-2 overflow-hidden">
      <div className="max-w-6xl mx-auto px-6 sm:px-10 lg:px-14">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <span className="inline-flex items-center gap-2 text-[11px] tracking-[0.26em] uppercase text-accent font-semibold mb-5">
            <span className="h-px bg-accent w-8" />
            See it in action
          </span>
          <h2 className="font-display text-4xl sm:text-5xl text-text tracking-tight">
            From one sentence to a company.
          </h2>
          <p className="mt-4 text-sm text-muted max-w-md mx-auto">
            The real flow inside the product. No mockups, no fake agents.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {SCREENS.map((s) => {
            const Icon = s.icon;
            return (
              <div key={s.label} className="bg-surface rounded-2xl border border-hairline overflow-hidden shadow-elevation-1">
                <div className="flex items-center gap-2 px-4 py-2.5 bg-surface-2 border-b border-hairline">
                  <div className="flex gap-1.5">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-300/60" />
                    <div className="w-2.5 h-2.5 rounded-full bg-amber-300/60" />
                    <div className="w-2.5 h-2.5 rounded-full bg-emerald-300/60" />
                  </div>
                  <span className="text-[10px] text-muted ml-2">{s.label}</span>
                </div>
                <div className="p-5 space-y-2.5">
                  <div className="flex items-center gap-2 mb-3">
                    <Icon size={16} strokeWidth={1.5} className="text-accent" />
                    <span className="text-sm font-medium text-text">{s.label}</span>
                  </div>
                  <p className="text-xs text-muted leading-relaxed mb-3">{s.desc}</p>
                  <div className="space-y-1.5">
                    {s.lines.map((line, i) => (
                      <div key={i} className={`text-[11px] ${i % 4 === 0 ? 'text-text font-medium pt-1' : 'text-muted'}`}>
                        {line}
                      </div>
                    ))}
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
