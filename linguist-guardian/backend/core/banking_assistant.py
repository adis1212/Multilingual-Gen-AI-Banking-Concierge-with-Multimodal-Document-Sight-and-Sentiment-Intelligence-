from typing import Tuple
from core.gpt4o_client import call_gpt4o
from models.banking_service import BankingIntent, Counter, INTENT_COUNTER_MAP, BankingAssistantResponse


BANKING_INTENT_PROMPT = """You are a polite and helpful Union Bank of India branch assistant.
Your job is to understand what banking service the customer needs and guide them.

CUSTOMER QUERY: {query}

Analyze the customer's request and identify one of these intents:
- account_balance: Checking account balance or account info
- passbook_update: Updating or checking passbook
- cash_deposit: Depositing cash
- cash_withdrawal: Withdrawing cash
- loan_inquiry: Asking about loans
- debit_card_issue: Debit card problems or new card
- new_account: Opening a new account
- kyc_update: KYC or document updates
- internet_banking: Internet banking help
- atm_issue: ATM machine issues
- unknown: Cannot determine intent

RESPOND in this format:
INTENT: [one of the above]
CONFIDENCE: [0.0-1.0]
REASON: [brief explanation]"""


async def detect_banking_intent(query: str, language: str = "en") -> BankingIntent:
    """Detect the customer's banking intent from their query."""
    if not query.strip():
        return BankingIntent.UNKNOWN

    prompt = BANKING_INTENT_PROMPT.format(query=query)
    
    try:
        response = await call_gpt4o(prompt, max_tokens=150)
        response_text = response.lower()
        
        # Parse the intent from response
        if "intent:" in response_text:
            intent_line = response_text.split("intent:")[1].split("\n")[0].strip()
            
            for intent in BankingIntent:
                if intent.value in intent_line:
                    return intent
        
        return BankingIntent.UNKNOWN
    except Exception as e:
        print(f"Error detecting intent: {e}")
        return BankingIntent.UNKNOWN


async def generate_assistant_response(
    query: str,
    language: str = "en",
    customer_name: str = ""
) -> BankingAssistantResponse:
    """Generate a polite response and guide customer to correct counter."""
    
    intent = await detect_banking_intent(query, language)
    counter = INTENT_COUNTER_MAP.get(intent, Counter.CUSTOMER_SUPPORT)
    
    # Generate friendly response message
    message = _generate_message(intent, counter, customer_name, language)
    
    return BankingAssistantResponse(intent, counter, message, language)


def _generate_message(
    intent: BankingIntent,
    counter: Counter,
    customer_name: str = "",
    language: str = "en"
) -> str:
    """Generate a voice-friendly response message."""
    
    greeting = f"Namaste, {customer_name}. " if customer_name else "Namaste. "
    
    messages = {
        BankingIntent.ACCOUNT_BALANCE: f"{greeting}I can help you check your account balance. Please visit {counter.value}.",
        BankingIntent.PASSBOOK_UPDATE: f"{greeting}You can update your passbook at {counter.value}.",
        BankingIntent.CASH_DEPOSIT: f"{greeting}For cash deposit, please go to {counter.value}.",
        BankingIntent.CASH_WITHDRAWAL: f"{greeting}For cash withdrawal, please visit {counter.value}.",
        BankingIntent.LOAN_INQUIRY: f"{greeting}Our loan specialist is at {counter.value}. They'll assist you.",
        BankingIntent.DEBIT_CARD_ISSUE: f"{greeting}Please visit {counter.value} for your debit card issue.",
        BankingIntent.NEW_ACCOUNT: f"Welcome to Union Bank of India. {greeting}Please visit {counter.value} to open a new account.",
        BankingIntent.KYC_UPDATE: f"{greeting}You can update your KYC details at {counter.value}.",
        BankingIntent.INTERNET_BANKING: f"{greeting}Our Customer Support team at {counter.value} can help with Internet Banking.",
        BankingIntent.ATM_ISSUE: f"{greeting}For ATM issues, please visit {counter.value} for assistance.",
        BankingIntent.UNKNOWN: f"{greeting}Please visit {counter.value}. Our team will help you with your banking needs.",
    }
    
    return messages.get(intent, f"{greeting}Please visit {counter.value} for assistance.")


async def validate_query(query: str) -> Tuple[bool, str]:
    """Validate if the query is banking-related and appropriate."""
    
    if not query or not query.strip():
        return False, "Query is empty"
    
    if len(query) > 500:
        return False, "Query too long"
    
    # Check for profanity or inappropriate content (basic check)
    inappropriate_words = ["abuse", "hate", "threat"]
    if any(word in query.lower() for word in inappropriate_words):
        return False, "Query contains inappropriate language"
    
    return True, ""
