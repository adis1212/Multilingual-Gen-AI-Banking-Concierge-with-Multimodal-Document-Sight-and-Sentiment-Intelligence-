"""
MASTER AI CONCIERGE — Central Intelligence
Coordinates all 5 banking assistance agents:
  1. Customer Service Agent
  2. Document Verification Agent
  3. Queue Management Agent
  4. Compliance Monitor Agent
  5. Voice Response Agent

Workflow:
  1. Identify customer intent
  2. Determine which agent handles the request
  3. Route to the appropriate agent
  4. Return the unified structured response
"""

import json
import logging
from core.gpt4o_client import get_client
from agents import customer_service_agent
from agents import queue_management_agent
from agents import document_verification_agent
from agents import compliance_monitor_agent

logger = logging.getLogger(__name__)

# ── Intent classification prompt ──
INTENT_SYSTEM_PROMPT = """You are the Master AI Concierge for Union Bank of India.
Given a customer's message, identify their intent.

Possible intents (pick exactly one):
- account_service      (balance, account info, new account, KYC)
- cash_transaction     (deposit, withdrawal, cheque)
- loan_inquiry         (any loan-related question)
- document_verification (KYC docs, Aadhaar, PAN, identity)
- token_request        (wants a token, queue position, where to go)
- complaint            (issue, problem, grievance)
- general_help         (greeting, unclear, or general question)

Respond with ONLY valid JSON:
{
  "intent": "<one of the above>"
}
"""

# ── Intent → Agent mapping ──
INTENT_AGENT_MAP = {
    "account_service":        "CUSTOMER_SERVICE_AGENT",
    "cash_transaction":       "QUEUE_MANAGEMENT_AGENT",
    "loan_inquiry":           "CUSTOMER_SERVICE_AGENT",
    "document_verification":  "DOCUMENT_VERIFICATION_AGENT",
    "token_request":          "QUEUE_MANAGEMENT_AGENT",
    "complaint":              "CUSTOMER_SERVICE_AGENT",
    "general_help":           "CUSTOMER_SERVICE_AGENT",
}

SUPPORTED_INTENTS = set(INTENT_AGENT_MAP.keys())

INTENT_KEYWORDS = {
    "token_request": ["token", "queue", "counter", "line", "waiting", "टोकन", "queue position"],
    "document_verification": ["kyc", "aadhaar", "aadhar", "pan", "passport", "driving licence", "voter id", "passbook", "verify document", "दस्तावेज"],
    "cash_transaction": ["cash deposit", "cash withdrawal", "withdraw", "deposit", "cheque", "नकद", "जमा", "निकासी"],
    "loan_inquiry": ["loan", "emi", "interest rate", "home loan", "personal loan", "ऋण"],
    "account_service": ["account", "balance", "debit card", "internet banking", "new account", "passbook update", "खाता", "बैलेंस"],
    "complaint": ["complaint", "issue", "problem", "grievance", "शिकायत"],
}

DOC_TYPE_KEYWORDS = {
    "aadhaar": ["aadhaar", "aadhar", "आधार"],
    "pan": ["pan", "income tax"],
    "passport": ["passport"],
    "driving_licence": ["driving licence", "driving license", "dl"],
    "voter_id": ["voter id", "epic"],
    "bank_passbook": ["passbook"],
}


def _keyword_intent_fallback(message: str) -> str:
    lower = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return intent
    return "general_help"


def _normalise_intent(raw_intent: str, message: str) -> str:
    intent = (raw_intent or "").strip().lower()
    if intent in SUPPORTED_INTENTS:
        return intent
    return _keyword_intent_fallback(message)


def _detect_doc_type(message: str) -> str:
    lower = message.lower()
    for doc_type, keywords in DOC_TYPE_KEYWORDS.items():
        if any(keyword in lower for keyword in keywords):
            return doc_type
    return "aadhaar"


def _looks_like_document_text(message: str) -> bool:
    lower = message.lower()
    markers = ["name", "dob", "date of birth", "address", "document number", "uidai", "govt of india"]
    has_marker = any(marker in lower for marker in markers)
    digit_count = sum(1 for ch in message if ch.isdigit())
    return has_marker or digit_count >= 8


def _doc_status_voice_response(status: str, customer_name: str = "") -> str:
    greeting = f"Namaste, {customer_name}." if customer_name else "Namaste."
    if status == "valid":
        return f"{greeting} Your document appears valid. Our staff will continue your KYC process."
    if status == "mismatch":
        return f"{greeting} We found a mismatch in your document details. Please share the correct document for re-check."
    if status == "suspicious":
        return f"{greeting} Your document needs additional security checks. A staff member will assist you shortly."
    return f"{greeting} We need a manual document review. Please show the original document to branch staff."


async def classify_intent(message: str, language: str = "en") -> str:
    """Use GPT-4o to classify customer intent."""
    if not message or not message.strip():
        return "general_help"

    client = get_client()
    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                {"role": "user", "content": f"Language: {language}\nCustomer says: {message}"},
            ],
            response_format={"type": "json_object"},
            max_tokens=60,
            temperature=0.1,
        )
        result = json.loads(resp.choices[0].message.content)
        return _normalise_intent(result.get("intent", "general_help"), message)
    except Exception as exc:
        logger.warning("Intent classification failed: %s", exc)
        return _keyword_intent_fallback(message)


async def process_request(
    message: str,
    language: str = "en",
    customer_name: str = "",
    session_id: str = "",
    staff_utterance: str | None = None,
) -> dict:
    """
    Master Orchestration Logic:
      1. Identify intent
      2. Route to the correct agent
      3. Return the unified response structure

    Returns:
    {
      "intent": "",
      "agent_used": "",
      "response": "",
      "staff_action": ""
    }

    If staff_utterance is provided, a parallel compliance check is also run.
    """

    # Step 1: Classify intent
    intent = await classify_intent(message, language)
    agent_name = INTENT_AGENT_MAP.get(intent, "CUSTOMER_SERVICE_AGENT")

    # Step 2: Route to the appropriate agent
    response_text = ""
    staff_action = ""
    document_verification = None

    if agent_name == "CUSTOMER_SERVICE_AGENT":
        result = await customer_service_agent.handle(message, language, customer_name)
        response_text = result["response"]
        staff_action = result["staff_action"]

    elif agent_name == "QUEUE_MANAGEMENT_AGENT":
        result = await queue_management_agent.handle(intent, customer_name, language)
        response_text = result["response"]
        staff_action = result["staff_action"]

    elif agent_name == "DOCUMENT_VERIFICATION_AGENT":
        doc_type = _detect_doc_type(message)
        if _looks_like_document_text(message):
            document_verification = await document_verification_agent.verify_from_text(
                ocr_text=message,
                doc_type=doc_type,
                customer_record={},
            )
            status = document_verification.get("verification_status", "manual_review_required")
            response_text = _doc_status_voice_response(status, customer_name)
            staff_action = document_verification.get(
                "staff_action",
                "Review document manually.",
            )
        else:
            response_text = (
                f"{'Namaste, ' + customer_name + '. ' if customer_name else 'Namaste. '}"
                "Please show your document to the camera for verification."
            )
            staff_action = "Prepare for KYC document scan. Ask customer for the original document."

    # Step 3: Build the Master Prompt response structure
    master_response = {
        "intent": intent,
        "agent_used": agent_name,
        "response": response_text,
        "staff_action": staff_action,
        "document_verification": document_verification,
    }

    # Step 3b: If a staff utterance was provided, run compliance check in parallel
    if staff_utterance:
        compliance = await compliance_monitor_agent.monitor(staff_utterance)
        master_response["compliance"] = compliance

    return master_response
