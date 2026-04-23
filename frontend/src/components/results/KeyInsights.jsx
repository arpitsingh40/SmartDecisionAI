import React from 'react';
import { Card } from '@/components/ui/card';
import { Lightbulb } from 'lucide-react';
import { motion } from 'framer-motion';
import { stagger, fadeUp } from '@/lib/motion';

const KeyInsights = ({ insights }) => {
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-key-insights">
      <div className="mb-4 flex items-center gap-2">
        <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
          <Lightbulb className="h-4 w-4" />
        </span>
        <div>
          <h3 className="text-base font-semibold">Key insights</h3>
          <p className="text-xs text-muted-foreground">The signals that drove the AI’s recommendation.</p>
        </div>
      </div>
      <motion.ul
        initial="initial"
        animate="animate"
        variants={stagger(0.05)}
        className="grid gap-2 sm:grid-cols-2"
      >
        {insights.map((text, i) => (
          <motion.li
            key={i}
            variants={fadeUp}
            className="flex items-start gap-2.5 rounded-xl border border-border/60 bg-background/40 p-3 text-sm leading-relaxed"
          >
            <span className="mt-[3px] grid h-5 w-5 shrink-0 place-items-center rounded-md bg-primary/15 text-[11px] font-bold text-primary">
              {i + 1}
            </span>
            <span>{text}</span>
          </motion.li>
        ))}
      </motion.ul>
    </Card>
  );
};

export default KeyInsights;
