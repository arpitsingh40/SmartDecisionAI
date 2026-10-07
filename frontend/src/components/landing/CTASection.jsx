import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '../ui/button';
import { ArrowRight } from 'lucide-react';
import { api } from '../../lib/api';

// Final call-to-action band prompting signup.
export default function CTASection() {
  const navigate = useNavigate();
  const [credits, setCredits] = useState(null);
  useEffect(() => { api.get('/config').then(r => setCredits(r.data?.signup_credits)).catch(() => {}); }, []);

  return (
    <section className="relative py-28 sm:py-36 bg-background overflow-hidden">
      <div className="absolute inset-0 pointer-events-none"
        style={{ background: 'radial-gradient(ellipse at 50% 50%, hsl(var(--accent)/0.06) 0%, transparent 70%)' }} />
      <div className="relative max-w-2xl mx-auto px-6 sm:px-10 text-center">
        <div className="inline-flex items-center gap-2 text-[11px] tracking-[0.26em] uppercase text-accent font-semibold mb-5">
          <span className="h-px w-8 bg-accent" />
          Start today
        </div>
        <h2 className="font-display text-4xl sm:text-5xl text-text tracking-tight leading-[1.1]">
          Your idea is enough.<br />
          <span className="text-accent">It builds the rest</span>.
        </h2>
        <p className="mt-5 text-base text-muted max-w-md mx-auto">
          Describe it once. Approve the mission. Watch the company get built — then run it from one screen.
        </p>
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Button onClick={() => navigate('/auth?next=/app/build')}
            className="rounded-xl h-12 px-8 text-base bg-accent hover:bg-accent/90 text-white">
            Build my company
            <ArrowRight size={16} className="ml-2" />
          </Button>
          <Button onClick={() => navigate('/auth')} variant="outline" className="rounded-xl h-12 px-8 text-base">
            Sign in
          </Button>
        </div>
        <p className="mt-4 text-xs text-muted">
          {credits ? `${credits} free credits on signup. ` : 'Free credits on signup. '}No credit card required.
        </p>
      </div>
    </section>
  );
}
