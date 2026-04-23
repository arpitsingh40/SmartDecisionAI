import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { Trash2, Sparkles, Trophy, ArrowRight, Inbox } from 'lucide-react';
import { listDecisions, deleteDecision, getGuestId } from '@/lib/api';
import { toast } from 'sonner';
import { stagger, fadeUp } from '@/lib/motion';

const formatDate = (d) => {
  try {
    const dt = new Date(d);
    return dt.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
};

const SavedDecisions = () => {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    try {
      const guestId = getGuestId();
      const data = await listDecisions(guestId);
      setItems(data);
    } catch (e) {
      toast.error('Failed to load saved decisions');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  const onDelete = async (id) => {
    try {
      const guestId = getGuestId();
      await deleteDecision(id, guestId);
      setItems((xs) => xs.filter((x) => x.id !== id));
      toast.success('Deleted');
    } catch {
      toast.error('Delete failed');
    }
  };

  return (
    <section className="mx-auto w-full max-w-6xl px-4 pb-16 pt-8 sm:px-6 lg:px-8" data-testid="saved-decisions-page">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
        <div>
          <div className="text-xs uppercase tracking-wider text-muted-foreground">Library</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight sm:text-3xl">Saved decisions</h1>
        </div>
        <Link to="/wizard">
          <Button className="gap-2" data-testid="saved-new-decision-button">
            <Sparkles className="h-4 w-4" /> New decision
          </Button>
        </Link>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-36 rounded-2xl shimmer" />
          ))}
        </div>
      ) : items.length === 0 ? (
        <Card className="mx-auto max-w-xl rounded-2xl border-border/70 bg-card/60 p-10 text-center" data-testid="saved-decisions-empty-state">
          <div className="mx-auto grid h-12 w-12 place-items-center rounded-full bg-primary/15 text-primary">
            <Inbox className="h-5 w-5" />
          </div>
          <h2 className="mt-4 text-lg font-semibold">No decisions yet</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Run your first analysis and it will automatically appear here.
          </p>
          <Link to="/wizard" className="mt-5 inline-block">
            <Button className="gap-2" data-testid="saved-empty-cta-button">
              Start a decision <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
        </Card>
      ) : (
        <motion.div
          initial="initial"
          animate="animate"
          variants={stagger(0.05)}
          className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
          data-testid="saved-decisions-list"
        >
          {items.map((item) => (
            <motion.div key={item.id} variants={fadeUp}>
              <Card className="h-full rounded-2xl border-border/70 bg-card/60 p-5 transition-shadow hover:shadow-[var(--shadow-2)]">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{formatDate(item.created_at)}</span>
                  <Badge variant="secondary" className="rounded-full">
                    Confidence {item.confidence ?? 0}%
                  </Badge>
                </div>
                <h3 className="mt-2 line-clamp-2 text-sm font-semibold sm:text-base">{item.title}</h3>
                <div className="mt-3 rounded-lg border border-border/60 bg-background/40 p-3">
                  <div className="inline-flex items-center gap-1 text-[11px] uppercase tracking-widest text-muted-foreground">
                    <Trophy className="h-3 w-3" /> Best option
                  </div>
                  <div className="mt-1 line-clamp-2 text-sm font-medium">{item.best_option_title || '—'}</div>
                  <div className="mt-2 flex items-center gap-2">
                    <Progress value={item.best_option_score ?? 0} className="h-1.5 flex-1" />
                    <span className="w-10 text-right text-xs font-semibold tabular-nums">{item.best_option_score ?? '-'}</span>
                  </div>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <Link to={`/saved/${item.id}`}>
                    <Button variant="secondary" size="sm" className="gap-1.5" data-testid="saved-decision-open-button">
                      Open <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  </Link>
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="ghost" size="icon" aria-label="Delete" data-testid="saved-decision-delete-button">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Delete this decision?</AlertDialogTitle>
                        <AlertDialogDescription>
                          This will permanently remove “{item.title}” from your library.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel data-testid="saved-decision-delete-cancel">Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={() => onDelete(item.id)} data-testid="saved-decision-delete-confirm">
                          Delete
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                </div>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      )}
    </section>
  );
};

export default SavedDecisions;
