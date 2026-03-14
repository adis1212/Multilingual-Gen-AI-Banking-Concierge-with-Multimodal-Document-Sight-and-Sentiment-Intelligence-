# Requirements Document

## Introduction

The Branch Concierge Orchestrator is an AI routing layer for the Union Bank of India Branch Concierge System. It sits on top of the existing Linguist-Guardian FastAPI backend and analyzes real-time customer conversations — including noisy, short, or emotionally charged speech — to classify intent and route the conversation to the correct internal AI agent. The orchestrator returns a structured JSON response that the frontend dashboard and downstream agents consume to take appropriate action.

The four target agents are: CUSTOMER_SERVICE_AGENT, DOCUMENT_VERIFICATION_AGENT, QUEUE_MANAGEMENT_AGENT, and COMPLIANCE_MONITOR_AGENT.

---

## Glossary

- **Orchestrator**: The Branch Concierge Orchestrator module that classifies intent and routes conversations to agents.
- **Agent**: One of four internal AI agents (CUSTOMER_SERVICE_AGENT, DOCUMENT_VERIFICATION_AGENT, QUEUE_MANAGEMENT_AGENT, COMPLIANCE_MONITOR_AGENT).
- **Transcript**: The text output of speech-to-text processing of a customer utterance.
- **Intent**: The primary purpose or need expressed by the customer in a conversation turn.
- **Urgency**: A three-level classification (low, medium, high) indicating how time-sensitive or emotionally critical the customer's need is.
- **Routing_Decision**: The structured JSON object returned by the Orchestrator containing intent, agent, urgency, and recommended_action.
- **Sentiment_Signal**: Emotional metadata (stress level, emotion label) produced by the existing SentimentEngine and passed to the Orchestrator as context.
- **Session**: An active customer interaction tracked by the existing Linguist-Guardian session management system.
- **Orchestrator_Prompt**: The system prompt stored in the prompts directory that instructs GPT-4o to perform agent routing.
- **CUSTOMER_SERVICE_AGENT**: The agent handling account balance, passbook updates, ATM/debit card queries, loan information, FD/RD inquiries, and internet banking help.
- **DOCUMENT_VERIFICATION_AGENT**: The agent handling Aadhaar verification, PAN verification, passbook validation, KYC updates, and identity confirmation.
- **QUEUE_MANAGEMENT_AGENT**: The agent handling token generation, service routing, counter direction, and waiting time estimation.
- **COMPLIANCE_MONITOR_AGENT**: The agent handling RBI policy compliance, suspicious transaction warnings, and staff advisories.
- **Fallback**: A default routing behavior applied when the Orchestrator cannot determine intent with sufficient confidence.

---

## Requirements

### Requirement 1: Orchestrator Core Routing

**User Story:** As a branch staff member, I want the system to automatically identify what a customer needs and route the conversation to the right agent, so that I can serve customers faster without manually triaging each request.

#### Acceptance Criteria

1. WHEN a non-empty transcript is received, THE Orchestrator SHALL classify the customer intent and return a Routing_Decision JSON object containing exactly the fields: `intent`, `agent`, `urgency`, and `recommended_action`.
2. THE Orchestrator SHALL assign the `agent` field to exactly one of: `CUSTOMER_SERVICE_AGENT`, `DOCUMENT_VERIFICATION_AGENT`, `QUEUE_MANAGEMENT_AGENT`, or `COMPLIANCE_MONITOR_AGENT`.
3. THE Orchestrator SHALL assign the `urgency` field to exactly one of: `low`, `medium`, or `high`.
4. WHEN the transcript contains keywords or context related to account balance, passbook, ATM/debit cards, loans, FD/RD, or internet banking, THE Orchestrator SHALL set `agent` to `CUSTOMER_SERVICE_AGENT`.
5. WHEN the transcript contains keywords or context related to Aadhaar, PAN, KYC, identity documents, or passbook validation, THE Orchestrator SHALL set `agent` to `DOCUMENT_VERIFICATION_AGENT`.
6. WHEN the transcript contains keywords or context related to token numbers, queue position, counter direction, or waiting time, THE Orchestrator SHALL set `agent` to `QUEUE_MANAGEMENT_AGENT`.
7. WHEN the transcript contains keywords or context related to RBI policy, suspicious transactions, or compliance advisories, THE Orchestrator SHALL set `agent` to `COMPLIANCE_MONITOR_AGENT`.
8. THE Orchestrator SHALL populate `recommended_action` with a concise, actionable instruction in plain English directed at branch staff.

---

### Requirement 2: Urgency Classification Using Sentiment Signals

**User Story:** As a branch manager, I want the orchestrator to factor in the customer's emotional state when determining urgency, so that distressed customers are prioritized before the situation escalates.

#### Acceptance Criteria

1. WHEN the Orchestrator receives a Sentiment_Signal with `emotion` equal to `distressed` or `stress_level` greater than 0.6, THE Orchestrator SHALL set `urgency` to `high`.
2. WHEN the Orchestrator receives a Sentiment_Signal with `emotion` equal to `frustrated` or `stress_level` between 0.3 and 0.6 inclusive, THE Orchestrator SHALL set `urgency` to `medium`.
3. WHEN no Sentiment_Signal is provided, THE Orchestrator SHALL determine urgency from transcript content alone.
4. WHEN the transcript contains explicit distress indicators such as "fraud", "stolen", "emergency", or "urgent", THE Orchestrator SHALL set `urgency` to `high` regardless of Sentiment_Signal values.
5. THE Orchestrator SHALL accept Sentiment_Signal as an optional input field and SHALL NOT fail when it is absent.

---

### Requirement 3: Noisy and Short Transcript Handling

**User Story:** As a branch staff member, I want the orchestrator to still produce a useful routing decision even when the customer's speech is short or partially captured due to branch noise, so that service is not interrupted.

#### Acceptance Criteria

1. WHEN a transcript contains fewer than 5 words, THE Orchestrator SHALL attempt routing based on available keywords and SHALL set `urgency` to `medium` as a default.
2. WHEN the Orchestrator cannot determine intent from a transcript with fewer than 5 words, THE Orchestrator SHALL set `agent` to `QUEUE_MANAGEMENT_AGENT` and `intent` to `unclear` as a safe fallback.
3. WHEN a transcript is provided that contains only non-linguistic noise tokens (e.g., "[inaudible]", "[noise]"), THE Orchestrator SHALL return a Routing_Decision with `agent` set to `QUEUE_MANAGEMENT_AGENT`, `intent` set to `unclear`, and `urgency` set to `low`.
4. THE Orchestrator SHALL process transcripts in any of the supported languages: Marathi, Hindi, Tamil, Telugu, Bengali, Gujarati, Kannada, Malayalam, and English.
5. WHEN a transcript is in a non-English supported language, THE Orchestrator SHALL route correctly without requiring prior translation.

---

### Requirement 4: Structured JSON Response Contract

**User Story:** As a frontend developer, I want the orchestrator to always return a predictable JSON structure, so that the dashboard and downstream agents can reliably parse and act on the response.

#### Acceptance Criteria

1. THE Orchestrator SHALL return a response that is valid JSON parseable by a standard JSON parser.
2. THE Orchestrator SHALL always include all four fields — `intent`, `agent`, `urgency`, `recommended_action` — in every response, with no fields omitted.
3. IF the underlying LLM returns a malformed or non-JSON response, THEN THE Orchestrator SHALL return a fallback Routing_Decision with `agent` set to `QUEUE_MANAGEMENT_AGENT`, `intent` set to `parse_error`, `urgency` set to `medium`, and `recommended_action` set to `"Direct customer to nearest available counter"`.
4. THE Orchestrator SHALL return the Routing_Decision within 3 seconds of receiving the transcript under normal network conditions.
5. THE Orchestrator_Prompt SHALL be stored as a `.txt` file in the existing `linguist-guardian/backend/prompts/` directory and loaded at runtime, consistent with the existing prompt management pattern.

---

### Requirement 5: REST API Endpoint Integration

**User Story:** As a backend developer, I want the orchestrator exposed as a REST endpoint within the existing FastAPI application, so that it integrates cleanly with the current routing and middleware infrastructure.

#### Acceptance Criteria

1. THE Orchestrator SHALL be accessible via a `POST /api/orchestrate` endpoint registered in the existing FastAPI application.
2. THE Orchestrator endpoint SHALL accept a request body containing: `transcript` (string, required), `language` (string, optional, default `"en"`), `session_id` (string, optional), and `sentiment` (object, optional).
3. WHEN `transcript` is an empty string, THE Orchestrator endpoint SHALL return an HTTP 400 error with a descriptive message.
4. THE Orchestrator endpoint SHALL apply the existing authentication middleware consistent with other routes in the application.
5. THE Orchestrator SHALL be registered in `main.py` under the prefix `/api/orchestrate` with the tag `"Orchestrator"`, following the existing route registration pattern.

---

### Requirement 6: Orchestrator Prompt Management

**User Story:** As an AI engineer, I want the orchestrator's system prompt to be externalized and version-controlled, so that routing logic can be tuned without code changes.

#### Acceptance Criteria

1. THE Orchestrator SHALL load its system prompt from `linguist-guardian/backend/prompts/orchestrator_routing.txt` at runtime using the existing `load_prompt` utility in `gpt4o_client.py`.
2. THE Orchestrator_Prompt SHALL instruct GPT-4o to return ONLY valid JSON with the four required fields and no additional prose.
3. THE Orchestrator_Prompt SHALL enumerate all four agent names, their handled topics, and the three urgency levels so the model has complete routing context.
4. IF the `orchestrator_routing.txt` file is missing at startup, THEN THE Orchestrator SHALL raise a descriptive startup error identifying the missing file.

---

### Requirement 7: Session Context Enrichment

**User Story:** As a branch staff member, I want the orchestrator to consider prior conversation turns in the same session when routing, so that returning customers or multi-turn conversations are handled correctly.

#### Acceptance Criteria

1. WHEN a `session_id` is provided in the request, THE Orchestrator SHALL retrieve the most recent 3 transcript entries for that session from the database and include them as context in the routing prompt.
2. WHEN no prior session transcripts exist for a given `session_id`, THE Orchestrator SHALL proceed with single-turn routing without error.
3. THE Orchestrator SHALL NOT store the Routing_Decision itself in the database; session transcript storage remains the responsibility of the existing session management module.

---

### Requirement 8: Frontend Routing Display

**User Story:** As a branch staff member, I want to see the orchestrator's routing decision displayed on the dashboard in real time, so that I know which agent is handling the customer and what action to take.

#### Acceptance Criteria

1. THE Frontend SHALL display the `agent`, `urgency`, and `recommended_action` fields from the Routing_Decision on the active session dashboard panel.
2. WHEN `urgency` is `high`, THE Frontend SHALL render the routing decision panel with a visually distinct high-urgency indicator (e.g., red border or alert color) consistent with the existing AlertBar component style.
3. WHEN `urgency` is `medium`, THE Frontend SHALL render the routing decision panel with a medium-urgency indicator (e.g., amber/yellow color).
4. WHEN `urgency` is `low`, THE Frontend SHALL render the routing decision panel with a neutral indicator.
5. THE Frontend SHALL call `POST /api/orchestrate` after each completed transcript is received from the WebSocket, passing the transcript, language, session_id, and available sentiment data.
6. WHEN the orchestrator API call fails, THE Frontend SHALL display a non-blocking error notification and SHALL NOT interrupt the ongoing conversation display.
