# Fed into Whisper's initial_prompt to massively improve jargon accuracy

BANKING_TERMS = [
    "RTGS", "NEFT", "IMPS", "UPI", "KYC", "AML", "CIBIL Score",
    "Overdraft", "Cheque", "IFSC Code", "MICR", "NPA", "EMI",
    "Fixed Deposit", "Recurring Deposit", "Savings Account",
    "Current Account", "Demat Account", "Nominee", "Passbook",
    "ATM Card", "Debit Card", "Credit Card", "PIN", "OTP",
    "Net Banking", "Mobile Banking", "Aadhaar", "PAN Card",
    "Form 15G", "Form 15H", "TDS", "Locker", "Demand Draft",
    "Pay Order", "Banker's Cheque", "SWIFT Code", "IBAN",
    "Loan Against Property", "Home Loan", "Personal Loan",
    "Gold Loan", "Vehicle Loan", "Mortgage", "Hypothecation",
    "Guarantor", "Collateral", "Lien", "Foreclosure",
    "Repo Rate", "Base Rate", "MCLR", "GST", "PAN",
    "Aadhaar Seeding", "Account Statement", "Mini Statement",
    "Balance Enquiry", "Beneficiary", "Remittance",
]

BANKING_GLOSSARY_PROMPT = (
    "This is a banking conversation. "
    "Key terms that may appear: " + ", ".join(BANKING_TERMS) + ". "
    "The customer may speak in Marathi, Hindi, Tamil, Telugu, Bengali, or other Indian languages. "
    "Branch staff speak in English. Transcribe accurately."
)