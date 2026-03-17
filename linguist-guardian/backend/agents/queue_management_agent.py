"""
AGENT 3 — Queue Management Agent
Purpose: Manage customer flow inside the bank branch.
Responsibilities: assign token numbers, direct to counters, estimate wait, reduce congestion.
"""

import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Counter definitions exactly matching the Master Prompt ──
COUNTERS = {
    1: {"name": "Account Services",         "prefix": "A", "services": ["Account balance", "New account opening", "KYC updates"]},
    2: {"name": "Loan Desk",                "prefix": "L", "services": ["Loan inquiry", "Loan application", "Loan status"]},
    3: {"name": "Cash Deposit / Withdrawal", "prefix": "C", "services": ["Cash deposit", "Cash withdrawal", "Cheque deposit"]},
    4: {"name": "Passbook Update",           "prefix": "P", "services": ["Passbook printing", "Account statement", "Transaction history"]},
    5: {"name": "Customer Support",          "prefix": "S", "services": ["Debit card issues", "Internet banking", "ATM problems", "General support"]},
}

# ── Intent → Counter mapping ──
INTENT_COUNTER = {
    "account_service":        1,
    "account_balance":        1,
    "new_account":            1,
    "kyc_update":             1,
    "loan_inquiry":           2,
    "cash_transaction":       3,
    "cash_deposit":           3,
    "cash_withdrawal":        3,
    "passbook_update":        4,
    "debit_card_issue":       5,
    "internet_banking":       5,
    "atm_issue":              5,
    "complaint":              5,
    "general_help":           5,
    "unknown":                5,
}

# Simple in-memory counter for token numbers (resets on restart; fine for demo)
_token_counters: dict[str, int] = {}


def _next_token(prefix: str) -> str:
    """Generate the next sequential token for a given prefix."""
    current = _token_counters.get(prefix, 0) + 1
    _token_counters[prefix] = current
    return f"{prefix}{current}"


def _estimate_wait(counter_number: int) -> int:
    """Estimate wait time in minutes (simulated for hackathon demo)."""
    # In production this would query a real queue database
    base_wait = {1: 5, 2: 8, 3: 4, 4: 3, 5: 6}
    return base_wait.get(counter_number, 5) + random.randint(0, 4)


async def handle(intent: str, customer_name: str = "", language: str = "en") -> dict:
    """
    Assign a token, direct customer to the correct counter, estimate wait.
    Returns a voice-friendly response (max 2 sentences).
    """
    counter_num = INTENT_COUNTER.get(intent, 5)
    counter = COUNTERS[counter_num]
    token = _next_token(counter["prefix"])
    wait = _estimate_wait(counter_num)

    greeting = f"Namaste, {customer_name}." if customer_name else "Namaste."

    response = (
        f"{greeting} Your token number is {token}. "
        f"Please proceed to Counter {counter_num} for {counter['name'].lower()} — estimated wait is {wait} minutes."
    )

    return {
        "response": response,
        "staff_action": f"Token {token} assigned → Counter {counter_num} ({counter['name']}). Estimated wait: {wait} min.",
        "token": token,
        "counter_number": counter_num,
        "counter_name": counter["name"],
        "estimated_wait_minutes": wait,
    }


async def get_counter_info(counter_number: int) -> dict:
    """Return information about a specific counter."""
    if counter_number not in COUNTERS:
        return {"error": "Counter number must be 1-5"}
    c = COUNTERS[counter_number]
    return {
        "counter": f"Counter {counter_number} – {c['name']}",
        "services": c["services"],
        "token_prefix": c["prefix"],
    }
