import React from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Coins, Box, Rocket, TrendingUp } from 'lucide-react';

const Column = ({ title, items, icon: Icon }) => (
  <div className="rounded-xl border border-border/60 bg-background/40 p-4">
    <div className="flex items-center gap-2 text-sm font-semibold">
      <Icon className="h-4 w-4 text-primary" />
      {title}
    </div>
    {Array.isArray(items) && items.length ? (
      <ul className="mt-3 space-y-1.5 text-sm">
        {items.map((x, i) => (
          <li key={i} className="flex items-start gap-2">
            <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary/60" />
            <span>{x}</span>
          </li>
        ))}
      </ul>
    ) : (
      <p className="mt-2 text-xs text-muted-foreground">None suggested.</p>
    )}
  </div>
);

const MonetizationCard = ({ monetization }) => {
  if (!monetization) return null;
  const { services = [], products = [], upsells = [] } = monetization;
  if (!services.length && !products.length && !upsells.length) return null;
  return (
    <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6" data-testid="results-monetization">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
            <Coins className="h-4 w-4" />
          </span>
          <div>
            <h3 className="text-base font-semibold">Monetization triggers</h3>
            <p className="text-xs text-muted-foreground">What you can sell from this decision.</p>
          </div>
        </div>
        <Badge variant="secondary" className="rounded-full">
          {services.length + products.length + upsells.length} ideas
        </Badge>
      </div>
      <div className="grid gap-3 md:grid-cols-3">
        <Column title="Services" items={services} icon={Rocket} />
        <Column title="Products" items={products} icon={Box} />
        <Column title="Upsells" items={upsells} icon={TrendingUp} />
      </div>
    </Card>
  );
};

export default MonetizationCard;
