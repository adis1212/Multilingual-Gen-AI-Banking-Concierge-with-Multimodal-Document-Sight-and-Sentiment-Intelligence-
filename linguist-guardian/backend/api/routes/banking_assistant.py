from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.banking_assistant import generate_assistant_response, validate_query
from models.banking_service import BankingIntent, Counter

router = APIRouter()


class BankingQueryRequest(BaseModel):
    query: str
    language: str = "en"  # ISO 639-1 code: en, hi, mr, ta, te, bn, gu, kn, ml
    customer_name: str = ""
    session_id: str = ""


class BankingQueryResponse(BaseModel):
    intent: str
    counter: str
    message: str
    language: str
    suitable_for_tts: bool


@router.post("/help", response_model=BankingQueryResponse)
async def get_banking_help(req: BankingQueryRequest):
    """Process customer banking query and provide counter guidance.
    
    This endpoint:
    1. Validates the customer query
    2. Detects the banking intent (account, loan, card, etc.)
    3. Routes to the appropriate counter (1-5)
    4. Returns a polite, voice-friendly response
    
    The response is optimized for Text-to-Speech conversion:
    - Maximum 2 sentences
    - Simple banking language
    - Natural pacing
    """
    
    # Validate request
    is_valid, error_msg = await validate_query(req.query)
    if not is_valid:
        raise HTTPException(400, f"Invalid query: {error_msg}")
    
    # Generate response
    response = await generate_assistant_response(
        query=req.query,
        language=req.language,
        customer_name=req.customer_name
    )
    
    return response.to_dict()


@router.post("/counter-info")
async def get_counter_info(counter_number: int = 1):
    """Get information about a specific counter."""
    
    counter_map = {
        1: {
            "counter": "Counter 1 – Account Services",
            "services": [
                "Account balance inquiry",
                "New account opening",
                "KYC updates",
                "Account details"
            ],
            "token_prefix": "A"
        },
        2: {
            "counter": "Counter 2 – Cash Deposit / Withdrawal",
            "services": [
                "Cash deposit",
                "Cash withdrawal",
                "Cheque deposit"
            ],
            "token_prefix": "C"
        },
        3: {
            "counter": "Counter 3 – Loan Desk",
            "services": [
                "Loan inquiry",
                "Loan application",
                "Loan status"
            ],
            "token_prefix": "L"
        },
        4: {
            "counter": "Counter 4 – Passbook Update",
            "services": [
                "Passbook printing",
                "Account statement",
                "Transaction history"
            ],
            "token_prefix": "P"
        },
        5: {
            "counter": "Counter 5 – Customer Support",
            "services": [
                "Debit card issues",
                "Internet banking help",
                "ATM problems",
                "General support"
            ],
            "token_prefix": "S"
        }
    }
    
    if counter_number not in counter_map:
        raise HTTPException(400, "Counter number must be 1-5")
    
    return counter_map[counter_number]


@router.get("/intents")
async def get_available_intents():
    """Get list of all supported banking intents."""
    return {
        "intents": [
            {"value": intent.value, "display": intent.value.replace("_", " ").title()}
            for intent in BankingIntent
        ]
    }
