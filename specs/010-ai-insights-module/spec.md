# Feature Specification: AI Insights Module

**Feature Branch**: `010-ai-insights-module`

**Created**: 2026-08-05

**Status**: Draft

**Input**: User description: "implement ai module"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - AI-Generated Business Insights (Priority: P1)

The business owner opens the AI Insights dashboard and sees an automatically written plain-language summary of what is happening in the business: today's operations status (milk loaded vs delivered, cash collected, pending items), revenue trend for the selected period, top-performing routes, notable increases or declines, and any items needing attention. The summary reads like a brief report written by a business analyst, so the owner can understand the state of the business at a glance without manually cross-referencing reports.

**Why this priority**: This is the headline value of the AI dashboard — it converts scattered reports into one actionable narrative. It is also the most independently valuable slice: it works as soon as report data exists.

**Independent Test**: Can be fully tested by seeding a known set of sessions, deliveries, and payments for a period, then verifying the AI Insights page produces a narrative that references the seeded totals, top routes, and flagged items.

**Acceptance Scenarios**:

1. **Given** the system has today's delivery sessions and a month of payment history, **When** the owner opens the AI Insights dashboard, **Then** the page shows a written summary that includes total milk delivered, total cash collected, revenue trend direction, and the top route by volume.
2. **Given** there is a session from a previous day that was never closed, **When** the AI summary is generated, **Then** the summary explicitly calls out the unclosed session as an item needing attention.
3. **Given** the AI assistant service is temporarily unavailable, **When** the owner opens the dashboard, **Then** the page still shows all statistical insights (numbers, forecasts, alerts) with a clear note that AI-written explanations are unavailable.

---

### User Story 2 - Demand Forecasting (Priority: P1)

The owner wants to know how much milk to procure from suppliers. On the AI Insights dashboard they select a route (or view the whole business) and see a forecast of expected daily delivery demand for the next 7 days, together with the expected total. The forecast is derived from the customer's historical delivery volumes and shows a plausible range, not just a single number, so the owner can plan procurement with confidence.

**Why this priority**: Milk procurement is a daily, high-cost decision. Forecasting is one of the most valuable AI capabilities for this business and is independent of the narrative summary.

**Independent Test**: Can be fully tested by recording several weeks of known daily delivery quantities for a route, then verifying the forecast returns 7 daily values that are consistent with (and derived from) the recorded history, with a total and a range.

**Acceptance Scenarios**:

1. **Given** a route has 4+ weeks of historical daily delivery records, **When** the owner views the 7-day demand forecast for that route, **Then** the forecast shows a predicted quantity for each of the next 7 days, an expected total, and a low–high range for the period.
2. **Given** a route is new with fewer than 2 weeks of history, **When** the owner views its forecast, **Then** the system shows the available historical average with a clear message that there is insufficient history for a full forecast.
3. **Given** the owner changes the forecast period from 7 days to a different horizon, **When** the forecast refreshes, **Then** the number of forecast days matches the selected horizon.

---

### User Story 3 - Anomaly and Exception Alerts (Priority: P2)

The system continuously reviews operations and automatically flags anomalies: delivery volumes well below what subscriptions expected, sessions that failed reconciliation, sessions left unclosed from previous days, customers whose consumption suddenly dropped, and unusually large payments. Each alert shows severity (high/medium/low), what was expected vs what actually happened, and a suggested action. This lets the owner catch problems the same day instead of discovering them weeks later.

**Why this priority**: Anomaly detection converts raw discrepancies into prioritized action items. It is P2 because the narrative summary (P1) already surfaces the most critical flags, while this story provides the complete, filterable alert list.

**Independent Test**: Can be fully tested by creating a session with a known reconciliation shortage, an unclosed session from yesterday, and a customer with a sudden consumption drop, then verifying each appears as an alert with correct severity and expected-vs-actual figures.

**Acceptance Scenarios**:

1. **Given** a delivery session has a reconciliation shortage above the configured tolerance, **When** the owner views the anomaly alerts, **Then** the session appears as a high-severity alert showing the expected vs actual quantity.
2. **Given** a session from a previous day was never closed, **When** alerts are generated, **Then** it appears with medium severity and a suggested action to close or investigate the session.
3. **Given** a customer's consumption in the last 7 days dropped more than 25% below the prior 3-week average, **When** alerts are generated, **Then** the customer appears with a low-to-medium severity alert about the consumption drop.
4. **Given** no anomalies exist, **When** the owner views the alerts section, **Then** it shows a clear "no anomalies detected" state rather than an error.

---

### User Story 4 - Customer Churn Risk (Priority: P2)

The owner wants to identify customers who may stop taking milk so they can intervene early. The dashboard shows a risk list where each customer has a risk score (0–100), a risk level, the factors that contributed (e.g., declining consumption, repeated delivery exceptions, recent non-deliveries, overdue payments), and a suggested action such as reaching out to the customer.

**Why this priority**: Retaining customers is directly tied to revenue. This story is P2 because it relies on historical consumption and delivery data that the earlier stories also use, and it is independently testable with seeded customer histories.

**Independent Test**: Can be fully tested by creating customers with differing histories (steady consumption vs sharply declining consumption, one with repeated exceptions and missed deliveries, one with a long-overdue balance), then verifying the risk list ranks them with scores and factors consistent with their history.

**Acceptance Scenarios**:

1. **Given** a customer's consumption declined more than 25% over the last month, **When** the owner views the churn-risk list, **Then** that customer appears with a high risk level and "declining consumption" listed as a factor.
2. **Given** a customer has several delivery exceptions and missed deliveries in the last month, **When** the risk list is generated, **Then** their risk score is elevated and those factors are listed.
3. **Given** a customer has an outstanding balance over 60 days old, **When** the risk list is generated, **Then** the overdue balance is listed as a contributing factor.
4. **Given** a customer has steady consumption and current payments, **When** the risk list is generated, **Then** they appear with a low risk level.

---

### User Story 5 - Conversational Q&A (Priority: P3)

The owner asks questions about their business in plain language — for example, "Which route collected the most cash this month?" or "Which customers have the highest outstanding balance?" — and receives a natural-language answer that references the data and time range used. The assistant answers only from the business data available in the system and clearly states when it cannot answer a question.

**Why this priority**: Conversational access is the most convenient but least essential slice — the information is already available through reports and the other AI stories. It is P3 because it is a value-add on top of the first four stories.

**Independent Test**: Can be fully tested by asking questions against a known dataset (e.g., a specific route with known cash collection) and verifying the answer identifies the correct route and amount and states the data range used.

**Acceptance Scenarios**:

1. **Given** the owner asks "Which route collected the most cash this month?", **When** the assistant answers, **Then** it names the correct route, gives the amount, and states the month it used as the data range.
2. **Given** the owner asks a question outside the data available (e.g., about a milk type that does not exist), **When** the assistant responds, **Then** it clearly states it could not answer from the available data rather than guessing.
3. **Given** the assistant service is unavailable, **When** the owner sends a question, **Then** the chat shows a clear error message and the conversation remains usable for retrying later.
4. **Given** a user with an unauthorized role attempts to use chat, **When** they access the feature, **Then** access is denied and no data is shown.

---

### Edge Cases

- What happens when there is insufficient historical data for a forecast (new route/customer)? Show the available average with a clear "insufficient history" message instead of an empty or misleading forecast.
- What happens when the AI assistant service fails or times out? The dashboard continues to show statistical insights; AI narrative, and chat show a clear unavailable/error state and never crash the page.
- What happens when there are no anomalies, no churn risks, or no forecastable routes? Show clear empty states ("No anomalies detected", "No customers at risk") rather than errors.
- How are soft-deleted records handled? Inactive customers, routes, and milk types are excluded from forecasts, alerts, and risk scores.
- How are role restrictions enforced? Partners and checkers cannot view financial AI insights or the AI dashboard; only the owner sees financial narratives and chat.
- What happens when the owner asks a question about data the system does not track? The assistant answers that the information is not available.
- How are AI-generated insights kept accurate? The narrative always states the data range it covers, and numbers in the narrative are sourced from the system's computed reports rather than invented.
- What happens when a report is cached and underlying data changed? Insight numbers refresh like the existing reports do (cache invalidation/refresh is respected).

## Constitution Alignment

This feature MUST comply with the Milk Management AI constitution:

- **Layered Architecture** (Principle I): All AI logic MUST be placed in the correct layer (routers, services, models, schemas, core). No business logic in routers. AI computation and orchestration belong in services; routers only handle request parameters and response formatting.
- **Role-Based Access Control** (Principle II): All AI endpoints MUST require authentication. Access: OWNER — full access to all AI features including financial narratives and chat; ADMIN — access to forecasts, anomaly alerts, and churn-risk lists but NOT financial narratives/chat; CHECKER and DELIVERY_PARTNER — no access to the AI dashboard.
- **Soft Deletes** (Principle IV): Forecasts, alerts, and risk scores MUST respect soft deletes — inactive customers, routes, and milk types are excluded.
- **Schema-Driven Contracts** (Principle V): Each AI feature MUST have dedicated Request/Response schemas. Responses MUST exclude sensitive personal data (addresses, contact details); only aggregated summaries may be sent to the external AI service.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate an AI-written plain-language summary of the business covering: today's operations (milk loaded, delivered, cash collected, pending items), revenue trend for the selected period, top-performing route, and flagged items needing attention.
- **FR-002**: System MUST forecast expected daily milk demand for the next 7 days (configurable horizon), overall and per route, derived from historical delivered quantities.
- **FR-003**: Each forecast day MUST include a predicted quantity and the period MUST include an expected total and a low–high range; where history is insufficient, the system MUST show a clear "insufficient history" notice.
- **FR-004**: System MUST detect and display anomalies with severity (high/medium/low), expected-vs-actual figures, and a suggested action for: delivery volumes below subscription expectations, reconciliation-unbalanced sessions, unclosed past sessions, sudden customer consumption drops, and unusually large payments.
- **FR-005**: System MUST assign each customer a churn-risk score (0–100), a risk level, contributing factors, and a suggested action, based on consumption trend, delivery exceptions, missed deliveries, and outstanding balances.
- **FR-006**: System MUST let the owner ask business questions in natural language and respond with answers derived from system data, stating the data range used, and MUST decline with a clear message when the data is not available.
- **FR-007**: System MUST degrade gracefully — when the external AI service is unavailable, all statistical insights (forecast, anomalies, churn risk) MUST still render with a clear "AI explanations unavailable" note, and chat MUST show a clear error.
- **FR-008**: System MUST restrict access by role: OWNER and ADMIN see the AI dashboard; only OWNER sees financial narratives and chat; CHECKER and DELIVERY_PARTNER are denied.
- **FR-009**: System MUST NOT send sensitive personal data (addresses, contact details, or any direct contact identifiers) to the external AI service — only aggregated summaries. Customer names may be included only as needed to answer the query (e.g., top-N lists, chat answers), and never alongside contact details.
- **FR-010**: System MUST limit chat usage (e.g., maximum message rate and response length) so one user cannot exhaust shared AI capacity.

### Key Entities *(include if feature involves data)*

- **Demand Forecast**: Projected daily delivery demand per route and overall — forecast date, predicted quantity, low/high range, expected total, and a confidence/insufficiency indicator.
- **Anomaly Alert**: A flagged issue — type, severity, affected entity (session/customer/route), expected vs actual value, deviation, and suggested action.
- **Churn Risk Assessment**: Per-customer risk evaluation — risk score (0–100), risk level, contributing factors, and suggested action.
- **AI Insight Summary**: A plain-language narrative generated from the system's computed reports for a stated date range.
- **Chat Conversation**: A question-and-answer exchange where the assistant's answer references the data range and sources used.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Owner can view the AI-written business summary within 10 seconds of opening the dashboard.
- **SC-002**: The 7-day demand forecast is generated in under 5 seconds and, once a route has 4+ weeks of history, the forecast for at least 70% of days falls within 20% of actual delivered quantity. This accuracy claim is a **point-forecast acceptance target** evaluated by a backtest: for each of the trailing 28 days of history, compare the predicted quantity to the actual delivered quantity and require ≥70% of days within ±20%. The separately delivered low–high range (FR-003) is an interval-coverage output and is not part of this target.
- **SC-003**: Reconciliation-unbalanced sessions and unclosed past sessions appear as anomalies on the day they occur.
- **SC-004**: Customers whose consumption dropped more than 25% in the last month appear in the churn-risk list with "declining consumption" as a factor.
- **SC-005**: When the AI service is unavailable, the dashboard still renders all statistical insights and clearly labels AI explanations as unavailable (no page errors).
- **SC-006**: The owner receives a correct answer to a question about data the system tracks within 15 seconds, and the answer states the data range used.
- **SC-007**: Role enforcement verified — CHECKER and DELIVERY_PARTNER receive a clear access-denied result and never see financial narratives or chat.

## Assumptions

- Historical delivery data (daily delivered quantities per customer/route) already exists in the system from normal operation; the feature derives forecasts, alerts, and risk scores from this data without requiring new data entry screens.
- The AI assistant is an external service configured with credentials by the owner. When the service is unavailable or misconfigured, the system operates in statistical-only mode rather than failing.
- Forecasts are informational guidance for procurement planning, not contractual commitments; the owner makes final decisions.
- Chat answers questions only about data the system tracks and computes; it does not act on the system or modify records.
- The existing authentication and role system is reused; no new login mechanism is introduced.
- The AI Insights feature is delivered as a new section of the existing reporting area of the application.
- Insight numbers follow the same refresh/caching behavior as the existing reports so that figures are consistent between the AI dashboard and the reports.
- Natural-language summaries and answers may occasionally be imperfect; the system always labels them as AI-generated.
