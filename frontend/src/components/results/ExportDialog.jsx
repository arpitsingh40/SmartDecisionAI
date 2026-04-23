import React, { useState } from 'react';
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { FileDown, Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import { jsPDF } from 'jspdf';

const ExportDialog = ({ open, onOpenChange, data }) => {
  const [includePros, setIncludePros] = useState(true);
  const [includeAnswers, setIncludeAnswers] = useState(true);
  const [includeReasoning, setIncludeReasoning] = useState(true);
  const [loading, setLoading] = useState(false);

  const generate = async () => {
    if (!data || !data.result) return;
    setLoading(true);
    try {
      const doc = new jsPDF({ unit: 'pt', format: 'a4' });
      const pageW = doc.internal.pageSize.getWidth();
      const margin = 48;
      let y = margin;

      const wrap = (text, w) => doc.splitTextToSize(String(text || ''), w);

      // Header
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(18);
      doc.text('Smart Decision AI — Report', margin, y);
      y += 22;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.setTextColor(110);
      doc.text(new Date().toLocaleString(), margin, y);
      y += 24;
      doc.setTextColor(0);
      doc.setDrawColor(220);
      doc.line(margin, y, pageW - margin, y);
      y += 18;

      // Decision
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.text('Decision', margin, y);
      y += 14;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(12);
      const decLines = wrap(data.decision, pageW - margin * 2);
      doc.text(decLines, margin, y);
      y += decLines.length * 16 + 12;

      // Best option
      const { result } = data;
      const best = (result.options || []).find((o) => o.id === result.best_option_id) || result.options?.[0];
      if (best) {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Best recommendation', margin, y);
        y += 14;
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(13);
        doc.text(best.title, margin, y);
        y += 16;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        const descLines = wrap(best.description, pageW - margin * 2);
        doc.text(descLines, margin, y);
        y += descLines.length * 13 + 6;
        doc.setTextColor(80);
        doc.text(`Score: ${best.score}/100   Risk: ${best.risk_level}   Confidence: ${result.confidence}%`, margin, y);
        y += 16;
        doc.setTextColor(0);
      }

      if (includeReasoning && result.reasoning) {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Reasoning', margin, y);
        y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        const rl = wrap(result.reasoning, pageW - margin * 2);
        doc.text(rl, margin, y);
        y += rl.length * 13 + 12;
      }

      // Options
      const ranked = [...(result.options || [])].sort((a, b) => b.score - a.score);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.text('All options (ranked)', margin, y);
      y += 14;

      for (const o of ranked) {
        if (y > 720) { doc.addPage(); y = margin; }
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text(`${o.title} — ${o.score}/100`, margin, y);
        y += 13;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(110);
        doc.text(`Risk: ${o.risk_level}`, margin, y);
        y += 12;
        doc.setTextColor(0);
        const dl = wrap(o.description, pageW - margin * 2);
        doc.text(dl, margin, y);
        y += dl.length * 12 + 4;

        if (includePros) {
          doc.setFont('helvetica', 'bold');
          doc.text('Pros:', margin, y); y += 12;
          doc.setFont('helvetica', 'normal');
          for (const p of (o.pros || [])) {
            const pl = wrap('• ' + p, pageW - margin * 2 - 10);
            if (y + pl.length * 11 > 780) { doc.addPage(); y = margin; }
            doc.text(pl, margin + 10, y); y += pl.length * 11;
          }
          doc.setFont('helvetica', 'bold');
          doc.text('Cons:', margin, y); y += 12;
          doc.setFont('helvetica', 'normal');
          for (const c of (o.cons || [])) {
            const cl = wrap('• ' + c, pageW - margin * 2 - 10);
            if (y + cl.length * 11 > 780) { doc.addPage(); y = margin; }
            doc.text(cl, margin + 10, y); y += cl.length * 11;
          }
        }
        doc.setTextColor(110);
        doc.setFontSize(9);
        const stl = wrap('Short‑term: ' + o.short_term_outcome, pageW - margin * 2);
        if (y + stl.length * 11 > 780) { doc.addPage(); y = margin; }
        doc.text(stl, margin, y); y += stl.length * 11;
        const lt = wrap('Long‑term: ' + o.long_term_outcome, pageW - margin * 2);
        if (y + lt.length * 11 > 780) { doc.addPage(); y = margin; }
        doc.text(lt, margin, y); y += lt.length * 11 + 8;
        doc.setTextColor(0);
      }

      if (includeAnswers && Array.isArray(data.answers) && data.answers.length) {
        if (y > 700) { doc.addPage(); y = margin; }
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Your answers', margin, y); y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        for (const a of data.answers) {
          if (y > 780) { doc.addPage(); y = margin; }
          const ql = wrap('Q: ' + a.question, pageW - margin * 2);
          doc.text(ql, margin, y); y += ql.length * 13;
          const al = wrap('A: ' + (Array.isArray(a.answer) ? a.answer.join(', ') : String(a.answer ?? '')), pageW - margin * 2);
          doc.text(al, margin, y); y += al.length * 13 + 6;
        }
      }

      const filename = 'decision_' + Date.now() + '.pdf';
      doc.save(filename);
      toast.success('PDF exported');
      onOpenChange(false);
    } catch (e) {
      toast.error('Export failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md" data-testid="results-export-dialog">
        <DialogHeader>
          <DialogTitle>Export PDF report</DialogTitle>
          <DialogDescription>Choose what to include in your decision report.</DialogDescription>
        </DialogHeader>
        <div className="space-y-3">
          <label className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 p-3">
            <Checkbox checked={includePros} onCheckedChange={(v) => setIncludePros(!!v)} />
            <span className="text-sm">Include pros and cons</span>
          </label>
          <label className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 p-3">
            <Checkbox checked={includeReasoning} onCheckedChange={(v) => setIncludeReasoning(!!v)} />
            <span className="text-sm">Include AI reasoning</span>
          </label>
          <label className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 p-3">
            <Checkbox checked={includeAnswers} onCheckedChange={(v) => setIncludeAnswers(!!v)} />
            <span className="text-sm">Include your answers</span>
          </label>
        </div>
        <DialogFooter>
          <Button variant="ghost" onClick={() => onOpenChange(false)} data-testid="export-cancel-button">
            Cancel
          </Button>
          <Button onClick={generate} disabled={loading} className="gap-2" data-testid="export-confirm-button">
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <FileDown className="h-4 w-4" />}
            {loading ? 'Generating…' : 'Download PDF'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

export default ExportDialog;
