import React from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  AlertDialog, AlertDialogTrigger, AlertDialogContent, AlertDialogHeader,
  AlertDialogTitle, AlertDialogDescription, AlertDialogFooter, AlertDialogCancel,
  AlertDialogAction,
} from '@/components/ui/alert-dialog';
import { Swords, Undo2, Sparkles } from 'lucide-react';
import DebateTurnCard from './DebateTurnCard';

const EmptyState = ({ onChallenge }) => (
  <Card
    className="rounded-2xl border-border/70 bg-card/60 p-8 text-center"
    data-testid="debate-empty-state"
  >
    <div className="mx-auto mb-3 grid h-12 w-12 place-items-center rounded-2xl bg-primary/12 text-primary ring-1 ring-primary/20">
      <Swords className="h-6 w-6" />
    </div>
    <h3 className="text-base font-semibold">Disagree with the recommendation?</h3>
    <p className="mx-auto mt-2 max-w-md text-sm text-muted-foreground">
      Challenge the decision. Tell the panel where it&apos;s off and the six
      agents will re-evaluate with your new context. Confidence, trade-offs,
      and the next action will all be updated.
    </p>
    {onChallenge && (
      <Button
        onClick={onChallenge}
        className="mt-4 gap-2"
        data-testid="debate-empty-challenge-button"
      >
        <Swords className="h-4 w-4" />
        Challenge this decision
      </Button>
    )}
  </Card>
);

const DebatePanel = ({ debateHistory = [], onChallenge, onRevert, onRevertToOriginal }) => {
  const turns = Array.isArray(debateHistory) ? debateHistory : [];

  if (turns.length === 0) {
    return <EmptyState onChallenge={onChallenge} />;
  }

  return (
    <div className="space-y-5" data-testid="debate-panel">
      <Card className="rounded-2xl border-border/70 bg-card/60 p-5 sm:p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="grid h-9 w-9 place-items-center rounded-lg bg-primary/12 text-primary ring-1 ring-primary/20">
              <Sparkles className="h-4 w-4" />
            </span>
            <div className="min-w-0">
              <h2 className="text-base font-semibold sm:text-lg">Debate history</h2>
              <p className="mt-0.5 text-xs text-muted-foreground sm:text-sm">
                {turns.length} refinement{turns.length === 1 ? '' : 's'} &middot; the most
                recent turn is the active decision across all tabs.
              </p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {onRevertToOriginal && (
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="outline"
                    size="sm"
                    className="gap-1.5"
                    data-testid="debate-revert-original-button"
                  >
                    <Undo2 className="h-4 w-4" />
                    Revert to original
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Discard all refinements?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This drops every refinement and restores the original
                      panel analysis. You can challenge again any time.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={onRevertToOriginal}>
                      Revert to original
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            )}
            {onChallenge && (
              <Button
                onClick={onChallenge}
                size="sm"
                className="gap-1.5"
                data-testid="debate-challenge-again-button"
              >
                <Swords className="h-4 w-4" />
                Challenge again
              </Button>
            )}
          </div>
        </div>
      </Card>

      <div className="space-y-4">
        {turns.map((turn, i) => (
          <DebateTurnCard
            key={turn?.id || i}
            turn={turn}
            index={i}
            isLatest={i === turns.length - 1}
            onRevert={onRevert}
          />
        ))}
      </div>
    </div>
  );
};

export default DebatePanel;
