import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell, LabelList,
} from 'recharts';

const ScoreBarChart = ({ options, bestId }) => {
  const data = [...(options || [])]
    .sort((a, b) => (a.computed_score ?? a.score) - (b.computed_score ?? b.score))
    .map((o) => ({
      name: (o.title || '').length > 28 ? o.title.slice(0, 26) + '…' : o.title,
      score: Math.round(o.computed_score ?? o.score ?? 0),
      id: o.id,
      is_do_nothing: o.is_do_nothing,
    }));

  const primary = 'hsl(var(--primary))';
  const muted = 'hsl(var(--muted-foreground))';
  const border = 'hsl(var(--border))';

  const height = Math.max(200, data.length * 52);

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 8, right: 40, left: 8, bottom: 8 }}
        >
          <CartesianGrid stroke={border} strokeOpacity={0.35} horizontal={false} />
          <XAxis
            type="number"
            domain={[0, 100]}
            tick={{ fill: muted, fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="name"
            tick={{ fill: muted, fontSize: 11 }}
            width={180}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            cursor={{ fill: 'hsl(var(--muted) / 0.35)' }}
            contentStyle={{
              background: 'hsl(var(--popover))',
              border: `1px solid hsl(var(--border))`,
              borderRadius: 8,
              color: 'hsl(var(--popover-foreground))',
              fontSize: 12,
              boxShadow: 'var(--shadow-2)',
            }}
            formatter={(v) => [v, 'Score']}
          />
          <Bar dataKey="score" radius={[0, 8, 8, 0]} animationDuration={600}>
            {data.map((d) => (
              <Cell
                key={d.id}
                fill={d.id === bestId ? primary : 'hsl(var(--chart-2))'}
                fillOpacity={d.id === bestId ? 1 : d.is_do_nothing ? 0.45 : 0.6}
              />
            ))}
            <LabelList dataKey="score" position="right" style={{ fill: muted, fontSize: 11 }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ScoreBarChart;
