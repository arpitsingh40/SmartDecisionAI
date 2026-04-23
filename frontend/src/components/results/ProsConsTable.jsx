import React from 'react';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { CheckCircle2, XCircle } from 'lucide-react';

const ProsConsTable = ({ options }) => {
  const maxItems = Math.max(...options.map((o) => Math.max(o.pros.length, o.cons.length)), 3);
  return (
    <div className="overflow-x-auto" data-testid="results-pros-cons-table">
      <Table className="min-w-full text-sm">
        <TableHeader>
          <TableRow>
            <TableHead className="w-48 sticky left-0 bg-card/60 backdrop-blur">Option</TableHead>
            <TableHead>
              <span className="inline-flex items-center gap-1.5 text-emerald-500">
                <CheckCircle2 className="h-3.5 w-3.5" /> Pros
              </span>
            </TableHead>
            <TableHead>
              <span className="inline-flex items-center gap-1.5 text-rose-500">
                <XCircle className="h-3.5 w-3.5" /> Cons
              </span>
            </TableHead>
            <TableHead className="w-20 text-right">Score</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {options.map((o) => (
            <TableRow key={o.id}>
              <TableCell className="sticky left-0 bg-card/60 font-medium backdrop-blur">
                <div className="truncate" title={o.title}>{o.title}</div>
                <div className="mt-0.5 text-xs text-muted-foreground">Risk: {o.risk_level}</div>
              </TableCell>
              <TableCell>
                <ul className="space-y-1">
                  {o.pros.map((p, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-emerald-500" />
                      <span>{p}</span>
                    </li>
                  ))}
                </ul>
              </TableCell>
              <TableCell>
                <ul className="space-y-1">
                  {o.cons.map((c, i) => (
                    <li key={i} className="flex items-start gap-1.5">
                      <span className="mt-1 h-1.5 w-1.5 shrink-0 rounded-full bg-rose-500" />
                      <span>{c}</span>
                    </li>
                  ))}
                </ul>
              </TableCell>
              <TableCell className="text-right tabular-nums">
                <span className="text-base font-semibold">{o.score}</span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
};

export default ProsConsTable;
