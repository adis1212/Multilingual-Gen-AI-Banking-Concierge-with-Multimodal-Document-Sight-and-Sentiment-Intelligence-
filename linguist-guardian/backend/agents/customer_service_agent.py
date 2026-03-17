"""
AGENT 1 — Customer Service Agent
Purpose: Assist customers with general banking questions.
Handles: account balance, debit card, internet banking, new account, general info.
Responses are short (max 2 sentences) and suitable for voice playback.
"""

import logging
from core.gpt4o_client import get_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the Customer Service Agent for Union Bank of India.
You assist customers with general banking questions inside a bank branch.

You handle:
- Account balance inquiries
- Debit card issues (lost, blocked, re-issue)
- Internet banking help
- New account opening guidance
- General banking information

RULES:
- Respond in maximum 2 sentences.
- Use simple banking language — avoid jargon.
- Always be respectful, calm, and professional.
- Be especially gentle with elderly customers.
- Responses must be suitable for voice playback (text-to-speech).
- Start with "Namaste" for Hindi/Marathi speakers, or a polite greeting.

Respond ONLY with a JSON object:
{
  "response": "Your short, voice-friendly response to the customer",
  "staff_action": "Brief instruction for bank staff on what to do next"
}
"""


async def handle(query: str, language: str = "en", customer_name: str = "") -> dict:
    """Process a customer service query and return a voice-friendly response."""
    client = get_client()

    name_ctx = f" (Customer name: {customer_name})" if customer_name else ""
    user_msg = f"Language: {language}{name_ctx}\nCustomer says: {query}"

    try:
        resp = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            max_tokens=200,
            temperature=0.3,
        )

        import json
        result = json.loads(resp.choices[0].message.content)
        return {
            "response": result.get("response", "Namaste. Please visit the customer support counter for assistance."),
            "staff_action": result.get("staff_action", "Assist customer with their query."),
        }
    except Exception as exc:
        logger.warning("CustomerServiceAgent error: %s", exc)
        greeting = f"Namaste, {customer_name}." if customer_name else "Namaste."
        return {
            "response": f"{greeting} Welcome to Union Bank of India. How may I assist you today?",
            "staff_action": "Greet customer and determine their need.",
        }
