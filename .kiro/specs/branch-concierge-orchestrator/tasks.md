# Tasks: Branch Concierge Orchestrator

## Task List

- [x] 1. Create orchestrator system prompt
  - [x] 1.1 Create `linguist-guardian/backend/prompts/orchestrator_routing.txt` with GPT-4o system prompt that enumerates all four agents, their topics, and three urgency levels, and instructs the model to return only valid JSON with the four required fields
  - **Requirements:** 6.1, 6.2, 6.3

- [x] 2. Implement core orchestrator module
  - [x] 2.1 Create `linguist-guardian/backend/core/orchestrator.py` with `route_conversation(transcript, language, sentiment, prior_context)` async function that loads the prompt, builds the user message, calls GPT-4o with `response_format=json_object`, and returns the parsed RoutingDecision dict
  - [x] 2.2 Add `OrchestratorParseError` exception class and fallback RoutingDecision logic for malformed LLM responses
  - **Requirements:** 1.1, 1.2, 1.3, 1.8, 4.3, 6.1, 6.4

- [x] 3. Implement orchestrate REST endpoint
  - [x] 3.1 Create `linguist-guardian/backend/api/routes/orchestrate.py` with `OrchestrateRequest` and `RoutingDecision` Pydantic models and `POST /` handler
  - [x] 3.2 Add session context lookup: when `session_id` is provided, query the last 3 `Transcript` rows and pass them to `route_conversation()`
  - [x] 3.3 Add HTTP 400 validation for empty `transcript` field
  - [x] 3.4 Register the router in `linguist-guardian/backend/main.py` under prefix `/api/orchestrate` with tag `"Orchestrator"`
  - **Requirements:** 5.1, 5.2, 5.3, 5.4, 5.5, 7.1, 7.2, 7.3

- [x] 4. Implement urgency and routing logic in prompt + core
  - [x] 4.1 Ensure the orchestrator prompt and `route_conversation()` correctly handle sentiment signals: `distressed`/`stress_level > 0.6` → `high`, `frustrated`/`0.3–0.6` → `medium`
  - [x] 4.2 Ensure distress keywords (`fraud`, `stolen`, `emergency`, `urgent`) in transcript override sentiment to produce `urgency=high`
  - [x] 4.3 Ensure short transcripts (< 5 words) default to `urgency=medium` and fall back to `QUEUE_MANAGEMENT_AGENT` / `intent=unclear` when routing is ambiguous
  - [x] 4.4 Ensure noise-only transcripts (`[inaudible]`, `[noise]`) return `agent=QUEUE_MANAGEMENT_AGENT`, `intent=unclear`, `urgency=low`
  - **Requirements:** 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 3.3

- [x] 5. Frontend: orchestrator service and store
  - [x] 5.1 Create `linguist-guardian/frontend/src/services/orchestratorService.js` with `routeConversation(transcript, language, sessionId, sentiment)` that calls `POST /api/orchestrate`
  - [x] 5.2 Create `linguist-guardian/frontend/src/store/orchestratorStore.js` Zustand store with `decision`, `loading`, `error` state and `setDecision`, `setLoading`, `setError`, `reset` actions
  - **Requirements:** 8.5

- [x] 6. Frontend: RoutingDecisionPanel component
  - [x] 6.1 Create `linguist-guardian/frontend/src/components/routing/RoutingDecisionPanel.jsx` that reads from `orchestratorStore` and displays `agent`, `urgency`, and `recommended_action`
  - [x] 6.2 Apply urgency-based border/color styling: red for `high`, amber for `medium`, neutral for `low`, consistent with existing `AlertBar` component style
  - [x] 6.3 Add `RoutingDecisionPanel` to the sidebar in `linguist-guardian/frontend/src/pages/index.jsx`
  - **Requirements:** 8.1, 8.2, 8.3, 8.4

- [x] 7. Frontend: WebSocket integration
  - [x] 7.1 Modify `linguist-guardian/frontend/src/hooks/useWebSocket.js` to call `routeConversation()` after each `transcript` event and dispatch the result to `orchestratorStore`
  - [x] 7.2 Add error handling: on API failure, call `toast.error(...)` and leave `sessionStore.messages` unchanged
  - **Requirements:** 8.5, 8.6

- [x] 8. Backend tests
  - [x] 8.1 Write unit tests: empty transcript → 400, noise-only fallback, malformed LLM response fallback, missing prompt file error, empty session context no error, endpoint registered
  - [x] 8.2 Write property tests (Hypothesis, min 100 iterations each) for Properties 1–14 as defined in design.md
  - **Requirements:** All backend requirements

- [x] 9. Frontend tests
  - [x] 9.1 Write property tests (fast-check/vitest + @testing-library/react) for Properties 15–18: panel renders all fields, urgency styling, WS trigger, API failure handling
  - **Requirements:** 8.1–8.6
