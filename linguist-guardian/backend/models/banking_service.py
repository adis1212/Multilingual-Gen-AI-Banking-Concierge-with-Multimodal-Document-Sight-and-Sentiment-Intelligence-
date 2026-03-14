from typing import List
from enum import Enum


class BankingIntent(str, Enum):
    ACCOUNT_BALANCE = "account_balance"
    PASSBOOK_UPDATE = "passbook_update"
    CASH_DEPOSIT = "cash_deposit"
    CASH_WITHDRAWAL = "cash_withdrawal"
    LOAN_INQUIRY = "loan_inquiry"
    DEBIT_CARD_ISSUE = "debit_card_issue"
    NEW_ACCOUNT = "new_account"
    KYC_UPDATE = "kyc_update"
    INTERNET_BANKING = "internet_banking"
    ATM_ISSUE = "atm_issue"
    UNKNOWN = "unknown"


class Counter(Enum):
    ACCOUNT_SERVICES = "Counter 1 – Account Services"
    CASH_SERVICES = "Counter 2 – Cash Deposit / Withdrawal"
    LOAN_DESK = "Counter 3 – Loan Desk"
    PASSBOOK_UPDATE = "Counter 4 – Passbook Update"
    CUSTOMER_SUPPORT = "Counter 5 – Customer Support"


# Intent to Counter mapping
INTENT_COUNTER_MAP = {
    BankingIntent.ACCOUNT_BALANCE: Counter.ACCOUNT_SERVICES,
    BankingIntent.PASSBOOK_UPDATE: Counter.PASSBOOK_UPDATE,
    BankingIntent.CASH_DEPOSIT: Counter.CASH_SERVICES,
    BankingIntent.CASH_WITHDRAWAL: Counter.CASH_SERVICES,
    BankingIntent.LOAN_INQUIRY: Counter.LOAN_DESK,
    BankingIntent.DEBIT_CARD_ISSUE: Counter.CUSTOMER_SUPPORT,
    BankingIntent.NEW_ACCOUNT: Counter.ACCOUNT_SERVICES,
    BankingIntent.KYC_UPDATE: Counter.ACCOUNT_SERVICES,
    BankingIntent.INTERNET_BANKING: Counter.CUSTOMER_SUPPORT,
    BankingIntent.ATM_ISSUE: Counter.CUSTOMER_SUPPORT,
    BankingIntent.UNKNOWN: Counter.CUSTOMER_SUPPORT,
}


class BankingAssistantResponse:
    def __init__(self, intent: BankingIntent, counter: Counter, message: str, language: str = "en"):
        self.intent = intent
        self.counter = counter
        self.message = message
        self.language = language
        self.suitable_for_tts = True  # Max 2 sentences, simple language

    def to_dict(self):
        return {
            "intent": self.intent.value,
            "counter": self.counter.value,
            "message": self.message,
            "language": self.language,
            "suitable_for_tts": self.suitable_for_tts
        }
