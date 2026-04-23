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
  const [includePlan, setIncludePlan] = useState(true);
  const [includeInsights, setIncludeInsights] = useState(true);
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
      const ensure = (h = 40) => {
        if (y + h > 790) {
          doc.addPage();
          y = margin;
        }
      };

      // Header
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(18);
      doc.text('Smart Decision AI — Report', margin, y);
      y += 22;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      doc.setTextColor(110);
      doc.text(new Date().toLocaleString(), margin, y);
      y += 20;
      doc.setTextColor(0);
      doc.setDrawColor(220);
      doc.line(margin, y, pageW - margin, y);
      y += 16;

      const { result } = data;

      // Goal
      if (result.goal) {
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Goal', margin, y); y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(11);
        const gl = wrap(result.goal, pageW - margin * 2);
        doc.text(gl, margin, y); y += gl.length * 14 + 6;
      }

      // Decision
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.text('Decision', margin, y);
      y += 14;
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(11);
      const decLines = wrap(data.decision, pageW - margin * 2);
      doc.text(decLines, margin, y);
      y += decLines.length * 14 + 10;

      // Best option
      const best = (result.options || []).find((o) => o.id === result.best_option_id) || result.options?.[0];
      if (best) {
        ensure(120);
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
        const summary = `Score: ${best.score}/100   Risk: ${best.risk_level}   Confidence: ${result.confidence}%`;
        doc.text(summary, margin, y);
        y += 14;
        if (typeof best.success_probability === 'number' || best.time_to_result) {
          doc.text(`Success probability: ${best.success_probability ?? '-'}%   Time to result: ${best.time_to_result || '-'}`, margin, y); y += 14;
        }
        if (best.expected_return) {
          doc.text(`Expected return: ${best.expected_return}`, margin, y); y += 14;
        }
        doc.setTextColor(0);
        y += 4;
      }

      if (includeInsights && Array.isArray(result.key_insights) && result.key_insights.length) {
        ensure(60);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Key insights', margin, y); y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        for (const [i, ins] of result.key_insights.entries()) {
          const il = wrap(`${i + 1}. ${ins}`, pageW - margin * 2);
          ensure(il.length * 13 + 6);
          doc.text(il, margin, y);
          y += il.length * 13 + 3;
        }
        y += 6;
      }

      if (includeReasoning && result.reasoning) {
        ensure(60);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Reasoning', margin, y);
        y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        const rl = wrap(result.reasoning, pageW - margin * 2);
        doc.text(rl, margin, y);
        y += rl.length * 13 + 10;
      }

      // Options
      const ranked = [...(result.options || [])].sort((a, b) => b.score - a.score);
      ensure(40);
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(11);
      doc.text('All options (ranked)', margin, y);
      y += 14;

      for (const o of ranked) {
        ensure(80);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text(`${o.title} — ${o.score}/100`, margin, y);
        y += 13;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(9);
        doc.setTextColor(110);
        const metaLine = `Risk: ${o.risk_level}${typeof o.success_probability === 'number' ? '   Success: ' + o.success_probability + '%' : ''}${o.time_to_result ? '   Time: ' + o.time_to_result : ''}${o.expected_return ? '   Return: ' + o.expected_return : ''}`;
        const ml = wrap(metaLine, pageW - margin * 2);
        doc.text(ml, margin, y); y += ml.length * 12;
        doc.setTextColor(0);
        const dl = wrap(o.description, pageW - margin * 2);
        ensure(dl.length * 12 + 4);
        doc.text(dl, margin, y);
        y += dl.length * 12 + 4;

        if (includePros) {
          doc.setFont('helvetica', 'bold');
          doc.text('Pros:', margin, y); y += 12;
          doc.setFont('helvetica', 'normal');
          for (const p of (o.pros || [])) {
            const pl = wrap('• ' + p, pageW - margin * 2 - 10);
            ensure(pl.length * 11);
            doc.text(pl, margin + 10, y); y += pl.length * 11;
          }
          doc.setFont('helvetica', 'bold');
          doc.text('Cons:', margin, y); y += 12;
          doc.setFont('helvetica', 'normal');
          for (const c of (o.cons || [])) {
            const cl = wrap('• ' + c, pageW - margin * 2 - 10);
            ensure(cl.length * 11);
            doc.text(cl, margin + 10, y); y += cl.length * 11;
          }
        }
        doc.setTextColor(110);
        doc.setFontSize(9);
        const stl = wrap('Short-term: ' + (o.short_term_outcome || '-'), pageW - margin * 2);
        ensure(stl.length * 11);
        doc.text(stl, margin, y); y += stl.length * 11;
        const lt = wrap('Long-term: ' + (o.long_term_outcome || '-'), pageW - margin * 2);
        ensure(lt.length * 11);
        doc.text(lt, margin, y); y += lt.length * 11;
        if (o.why_not) {
          const wn = wrap('Why not: ' + o.why_not, pageW - margin * 2);
          ensure(wn.length * 11);
          doc.text(wn, margin, y); y += wn.length * 11;
        }
        y += 6;
        doc.setTextColor(0);
      }

      // Execution plan
      if (includePlan && result.execution_plan) {
        const ep = result.execution_plan;
        ensure(80);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Execution plan — ' + (ep.title || ''), margin, y); y += 14;
        if (ep.total_timeline) {
          doc.setFont('helvetica', 'normal');
          doc.setFontSize(10);
          doc.setTextColor(110);
          doc.text('Total timeline: ' + ep.total_timeline, margin, y); y += 14;
          doc.setTextColor(0);
        }
        for (const s of ep.steps || []) {
          const title = `${s.step || '-'}. ${s.action}`;
          const tl = wrap(title, pageW - margin * 2);
          ensure(tl.length * 13 + 24);
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.text(tl, margin, y); y += tl.length * 13;
          doc.setFont('helvetica', 'normal');
          doc.setTextColor(110);
          doc.setFontSize(9);
          const meta = `  Timeline: ${s.timeline || '-'}   Priority: ${s.priority || '-'}${s.est_cost ? '   Cost: ' + s.est_cost : ''}${s.est_benefit ? '   Benefit: ' + s.est_benefit : ''}`;
          const mm = wrap(meta, pageW - margin * 2);
          doc.text(mm, margin, y); y += mm.length * 11 + 4;
          doc.setTextColor(0);
        }
        if (ep.short_term_plan) {
          const sl = wrap('Quick wins: ' + ep.short_term_plan, pageW - margin * 2);
          ensure(sl.length * 13 + 4);
          doc.setFontSize(10);
          doc.text(sl, margin, y); y += sl.length * 13 + 4;
        }
        if (ep.moderate_benefits) {
          const ml = wrap('Moderate benefits: ' + ep.moderate_benefits, pageW - margin * 2);
          ensure(ml.length * 13 + 4);
          doc.text(ml, margin, y); y += ml.length * 13 + 8;
        }
      }

      // Plan B
      if (result.plan_b) {
        ensure(60);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Plan B', margin, y); y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        const pb = wrap(result.plan_b, pageW - margin * 2);
        doc.text(pb, margin, y); y += pb.length * 13 + 4;
        if (result.plan_b_trigger) {
          doc.setTextColor(110);
          const tr = wrap('Trigger: ' + result.plan_b_trigger, pageW - margin * 2);
          ensure(tr.length * 12);
          doc.text(tr, margin, y); y += tr.length * 12 + 6;
          doc.setTextColor(0);
        }
      }

      if (includeAnswers && Array.isArray(data.answers) && data.answers.length) {
        ensure(40);
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.text('Your answers', margin, y); y += 14;
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        for (const a of data.answers) {
          const ql = wrap('Q: ' + a.question, pageW - margin * 2);
          ensure(ql.length * 13);
          doc.text(ql, margin, y); y += ql.length * 13;
          const al = wrap('A: ' + (Array.isArray(a.answer) ? a.answer.join(', ') : String(a.answer ?? '')), pageW - margin * 2);
          ensure(al.length * 13 + 6);
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
            <Checkbox checked={includeInsights} onCheckedChange={(v) => setIncludeInsights(!!v)} />
            <span className="text-sm">Include key insights</span>
          </label>
          <label className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 p-3">
            <Checkbox checked={includePros} onCheckedChange={(v) => setIncludePros(!!v)} />
            <span className="text-sm">Include pros and cons</span>
          </label>
          <label className="flex items-center gap-3 rounded-lg border border-border/60 bg-background/40 p-3">
            <Checkbox checked={includePlan} onCheckedChange={(v) => setIncludePlan(!!v)} />
            <span className="text-sm">Include execution plan</span>
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
