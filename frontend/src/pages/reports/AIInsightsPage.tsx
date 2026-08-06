import PageHeader from "../../components/ui/PageHeader";
import ForecastSection from "../../components/ai/ForecastSection";
import AnomalyList from "../../components/ai/AnomalyList";
import ChurnRiskTable from "../../components/ai/ChurnRiskTable";
import InsightNarrative from "../../components/ai/InsightNarrative";
import ChatPanel from "../../components/ai/ChatPanel";

export default function AIInsightsPage() {
  return (
    <div>
      <PageHeader
        title="AI Insights"
        description="AI-generated business intelligence: forecast, alerts, churn risk, narrative and Q&A"
      />
      <div className="grid grid-cols-1 gap-6">
        <section id="insight-narrative" aria-label="AI narrative">
          <InsightNarrative />
        </section>
        <section id="forecast-section" aria-label="Demand forecast">
          <ForecastSection />
        </section>
        <section id="anomalies-section" aria-label="Anomaly alerts">
          <AnomalyList />
        </section>
        <section id="churn-section" aria-label="Customer churn risk">
          <ChurnRiskTable />
        </section>
        <section id="chat-section" aria-label="Conversational Q&A">
          <ChatPanel />
        </section>
      </div>
    </div>
  );
}
