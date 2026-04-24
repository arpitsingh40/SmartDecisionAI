import React from 'react';
import KeyReasons from '@/components/results/KeyReasons';
import ExpectedOutcomeCard from '@/components/results/ExpectedOutcomeCard';
import RiskAnalysisCard from '@/components/results/RiskAnalysisCard';
import KPIsCard from '@/components/results/KPIsCard';
import AutomationCard from '@/components/results/AutomationCard';
import MonetizationCard from '@/components/results/MonetizationCard';
import Scorecard from '@/components/results/Scorecard';
import ExecutionPlanCard from '@/components/results/ExecutionPlanCard';
import PlanBCard from '@/components/results/PlanBCard';

const ExecuteDashboard = ({ result, best }) => {
  if (!result) return null;
  return (
    <div className="grid grid-cols-1 gap-6 lg:grid-cols-12" data-testid="results-execute-dashboard">
      <div className="space-y-6 lg:col-span-8">
        <KeyReasons reasons={result.key_reasons || []} />
        <ExpectedOutcomeCard outcome={result.expected_outcome} />
        <RiskAnalysisCard risks={result.risks || []} />
        {result.execution_plan && <ExecutionPlanCard plan={result.execution_plan} best={best} />}
        <AutomationCard ideas={result.automation_layer || []} />
        <KPIsCard kpis={result.kpis || []} />
        <MonetizationCard monetization={result.monetization} />
      </div>
      <div className="space-y-4 lg:col-span-4">
        <Scorecard scorecard={result.scorecard} />
        {result.plan_b && <PlanBCard planB={result.plan_b} trigger={result.plan_b_trigger} />}
      </div>
    </div>
  );
};

export default ExecuteDashboard;
