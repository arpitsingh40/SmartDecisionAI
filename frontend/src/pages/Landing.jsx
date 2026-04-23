import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles, BarChart3, Scale, ShieldCheck, Zap, Share2, Layers } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import HeroDemoCard from '@/components/landing/HeroDemoCard';
import { fadeUp, stagger } from '@/lib/motion';

const Value = ({ icon: Icon, title, desc, testid }) => (
  <motion.div variants={fadeUp} data-testid={testid}>
    <Card className="h-full rounded-2xl border border-border/70 bg-card/60 p-6 shadow-[var(--shadow-1)] transition-shadow hover:shadow-[var(--shadow-2)]">
      <div className="grid h-10 w-10 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
        <Icon className="h-5 w-5" />
      </div>
      <h3 className="mt-4 text-base font-semibold tracking-tight">{title}</h3>
      <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{desc}</p>
    </Card>
  </motion.div>
);

const Step = ({ n, title, desc }) => (
  <div className="relative rounded-2xl border border-border/70 bg-card/40 p-6">
    <div className="absolute -top-3 left-6 rounded-full bg-primary px-3 py-0.5 text-xs font-semibold text-primary-foreground">
      {n}
    </div>
    <h4 className="mt-2 text-base font-semibold">{title}</h4>
    <p className="mt-1 text-sm text-muted-foreground">{desc}</p>
  </div>
);

const Landing = () => {
  return (
    <div data-testid="landing-page">
      {/* HERO */}
      <section className="relative overflow-hidden">
        <div className="hero-glow pointer-events-none absolute inset-0 -z-10" />
        <div className="mx-auto grid w-full max-w-6xl items-center gap-10 px-4 py-16 sm:px-6 lg:grid-cols-12 lg:gap-12 lg:px-8 lg:py-24">
          <motion.div
            initial="initial"
            animate="animate"
            variants={stagger(0.08)}
            className="lg:col-span-7"
          >
            <motion.div variants={fadeUp}>
              <Badge variant="secondary" className="rounded-full px-3 py-1 text-xs">
                <Sparkles className="mr-1.5 h-3 w-3" />
                AI-guided decisions, made simple
              </Badge>
            </motion.div>
            <motion.h1
              variants={fadeUp}
              className="font-display mt-5 text-4xl font-semibold tracking-tight sm:text-5xl lg:text-6xl"
              data-testid="landing-hero-title"
            >
              Make better decisions,
              <br />
              <span className="text-primary">with clarity.</span>
            </motion.h1>
            <motion.p
              variants={fadeUp}
              className="mt-5 max-w-xl text-base leading-relaxed text-muted-foreground sm:text-lg"
            >
              A premium decision coach for students and early‑career professionals. Answer a few guided questions and receive ranked options, pros and cons, risks, and a confident recommendation — in under a minute.
            </motion.p>
            <motion.div variants={fadeUp} className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/wizard" data-testid="landing-hero-cta-link">
                <Button size="lg" className="h-11 gap-2 px-5" data-testid="landing-hero-cta-button">
                  Start a decision <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link to="/saved" data-testid="landing-secondary-cta-link">
                <Button
                  variant="ghost"
                  size="lg"
                  className="h-11 px-4"
                  data-testid="landing-secondary-cta-button"
                >
                  View saved decisions
                </Button>
              </Link>
            </motion.div>
            <motion.div variants={fadeUp} className="mt-6 flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
              <span className="inline-flex items-center gap-1.5">
                <ShieldCheck className="h-3.5 w-3.5" /> No sign-up required
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Zap className="h-3.5 w-3.5" /> Results in ~30 seconds
              </span>
              <span className="inline-flex items-center gap-1.5">
                <Layers className="h-3.5 w-3.5" /> Compare, save, export
              </span>
            </motion.div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 16, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1], delay: 0.15 }}
            className="lg:col-span-5"
          >
            <HeroDemoCard />
          </motion.div>
        </div>
      </section>

      {/* VALUE PROPS */}
      <section className="border-t border-border/60 bg-background/60">
        <div className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mb-10 max-w-2xl">
            <h2 className="text-xl font-semibold tracking-tight sm:text-2xl">
              Built for the decisions that matter most
            </h2>
            <p className="mt-2 text-sm text-muted-foreground sm:text-base">
              From grad school to job offers to relocations, Smart Decision AI turns messy choices into a clear, ranked plan.
            </p>
          </div>
          <motion.div
            initial="initial"
            whileInView="animate"
            viewport={{ once: true, amount: 0.2 }}
            variants={stagger(0.06)}
            className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3"
          >
            <Value
              icon={Scale}
              title="Structured tradeoffs"
              desc="Get 3–5 concrete options with pros, cons, risk level, and short/long term outcomes — not generic advice."
              testid="value-prop-1"
            />
            <Value
              icon={BarChart3}
              title="Scored & ranked"
              desc="Each option is scored 0–100 with a confidence meter so you can see why the best pick wins."
              testid="value-prop-2"
            />
            <Value
              icon={Share2}
              title="Save, compare, export"
              desc="Revisit decisions anytime, compare side‑by‑side, and export a clean PDF for your records."
              testid="value-prop-3"
            />
          </motion.div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="border-t border-border/60">
        <div className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="mb-10 max-w-2xl">
            <h2 className="text-xl font-semibold tracking-tight sm:text-2xl">How it works</h2>
            <p className="mt-2 text-sm text-muted-foreground sm:text-base">
              A focused, 3‑step flow designed to feel calm and intelligent.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <Step n="1" title="Describe your decision" desc="One sentence is enough. The AI will ask smart follow‑ups tailored to your situation." />
            <Step n="2" title="Answer guided questions" desc="Sliders, multi‑choice, and text inputs — one question at a time, never overwhelming." />
            <Step n="3" title="See your ranked options" desc="A best recommendation, ranked alternatives, a confidence meter, and what‑if controls to explore." />
          </div>
        </div>
      </section>

      {/* TESTIMONIAL / SOCIAL PROOF */}
      <section className="border-t border-border/60 bg-background/60">
        <div className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <div className="grid gap-6 md:grid-cols-2">
            <Card className="rounded-2xl border-border/70 bg-card/60 p-6">
              <p className="text-sm leading-relaxed">
                “I was stuck between two job offers for weeks. Twenty minutes in Smart Decision AI gave me a ranked plan I actually trusted.”
              </p>
              <p className="mt-4 text-xs text-muted-foreground">
                — Priya K., Software Engineer
              </p>
            </Card>
            <Card className="rounded-2xl border-border/70 bg-card/60 p-6">
              <p className="text-sm leading-relaxed">
                “It asked the right questions I hadn’t even thought to ask myself. The what‑if panel is a game changer.”
              </p>
              <p className="mt-4 text-xs text-muted-foreground">
                — Marco D., Masters Applicant
              </p>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA BAND */}
      <section className="border-t border-border/60">
        <div className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 lg:px-8">
          <Card className="rounded-3xl border-border/70 bg-card/60 p-8 sm:p-10 text-center">
            <h3 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
              Clarity is one decision away.
            </h3>
            <p className="mx-auto mt-3 max-w-xl text-sm text-muted-foreground sm:text-base">
              Start your first decision — it’s free, guest‑friendly, and takes less than a minute to see results.
            </p>
            <div className="mt-6 flex items-center justify-center gap-3">
              <Link to="/wizard" data-testid="landing-cta-band-link">
                <Button size="lg" className="h-11 gap-2 px-5" data-testid="landing-cta-band-button">
                  Try Smart Decision AI <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
            </div>
          </Card>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="border-t border-border/60">
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-4 py-6 text-xs text-muted-foreground sm:px-6 lg:px-8">
          <span>© {new Date().getFullYear()} Smart Decision AI</span>
          <span className="inline-flex items-center gap-1.5">
            <Sparkles className="h-3.5 w-3.5" /> Powered by Claude Sonnet 4.5
          </span>
        </div>
      </footer>
    </div>
  );
};

export default Landing;
