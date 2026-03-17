"""
AGENT 4 — Compliance Monitor Agent
Purpose: Silently monitor staff conversations and ensure RBI compliance.
Detects: unauthorized promises, loan mis-selling, missing KYC, suspicious
         transactions, customer data privacy violations.
Returns the EXACT JSON schema from the Master Prompt.
"""

import json
import logging
from core.gpt4o_client import get_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a silent RBI Compliance Monitor Agent operating inside a Union Bank of India branch.

Your job is to analyze what a bank staff member said to a customer and check for regulatory violations.

DETECT the following:
- Unauthorized financial promises (e.g., guaranteeing returns on market-linked products)
- Loan mis-selling (pushing unsuitable products, hiding fees)
- Missing KYC verification before processing a service
- Suspicious transactions (large cash, structuring, unusual patterns)
- Customer data privacy violations (sharing details with third parties, asking for PIN/password)
- Not disclosing loan processing fees before collecting them
- Not informing customer of their right to grievance redressal
- Not mentioning cooling-off period for loans

You MUST respond with ONLY valid JSON in this exact structure:
{
  "compliance_status": "ok | warning | violation",
  "issue_detected": "Description of the issue, or empty string if compliant",
  "recommended_action": "What the staff should do to fix it, or empty string if compliant"
}

RULES:
- If the utterance is normal and compliant, return compliance_status "ok" with empty strings.
- If there is a minor concern, return "warning".
- If there is a clear regulatory violation, return "violation".
- Be strict — RBI rules are non-negotiable.
- Do not add any text outside the JSON.
"""


async def monitor(staff_utterance: str, session_context: str = "") -> dict:
    """
    Silently analyze a staff utterance for RBI compliance.
    Returns the Master-Prompt-compliant JSON.
    """
    if not staff_utterance or not staff_utterance.strip():
        return {
            "compliance_status": "ok",
            "issue_detected": "",
            "recommended_action": "",
        }

    client = get_client()
    context_line = f"\nSession context: {session_context}" if session_context else ""
    user_msg = f"Staff said: \"{staff_utterance}\"{context_line}"

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            max_tokens=400,
            temperature=0.1,
        )

        result = json.loads(resp.choices[0].message.content)
        return _normalise(result)

    except Exception as exc:
        logger.error("ComplianceMonitorAgent error: %s", exc)
        return {
            "compliance_status": "warning",
            "issue_detected": "Compliance check could not be completed automatically.",
            "recommended_action": "Branch manager should manually review the conversation.",
        }


def _normalise(result: dict) -> dict:
    """Guarantee the output matches the Master Prompt schema exactly."""
    status = result.get("compliance_status", "ok")
    if status not in ("ok", "warning", "violation"):
        status = "warning"

    return {
        "compliance_status": status,
        "issue_detected": result.get("issue_detected", ""),
        "recommended_action": result.get("recommended_action", ""),
    }
