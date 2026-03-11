"""
Load banking glossary into a JSON file for use by Whisper initial_prompt.
Run: python scripts/seed_glossary.py
"""
import json
from pathlib import Path

EXTENDED_GLOSSARY = [
    # Core banking
    "RTGS", "NEFT", "IMPS", "UPI", "KYC", "AML", "CDD", "EDD",
    "CIBIL Score", "CRIF Score", "Equifax Score",
    "Overdraft", "OD Limit", "Sweep Account",
    "Cheque", "Demand Draft", "Pay Order", "Banker's Cheque",
    "IFSC Code", "MICR Code", "SWIFT Code", "IBAN",

    # Account types
    "Savings Account", "Current Account", "Salary Account",
    "NRE Account", "NRO Account", "FCNR Account",
    "Demat Account", "Trading Account",
    "Jan Dhan Account", "BSBD Account",

    # Cards
    "Debit Card", "Credit Card", "Prepaid Card", "Forex Card",
    "RuPay", "Visa", "Mastercard", "Contactless",
    "PIN", "OTP", "CVV", "EMV Chip",

    # Loans
    "Home Loan", "Personal Loan", "Auto Loan", "Vehicle Loan",
    "Gold Loan", "Loan Against Property", "LAP",
    "Education Loan", "Mudra Loan", "MSME Loan",
    "EMI", "Moratorium", "Foreclosure", "Prepayment",
    "Processing Fee", "Margin", "Collateral", "Hypothecation",
    "Mortgage", "Guarantor", "Co-applicant",
    "MCLR", "Base Rate", "Repo Rate", "Floating Rate", "Fixed Rate",

    # Deposits
    "Fixed Deposit", "FD", "Recurring Deposit", "RD",
    "Tax Saver FD", "Senior Citizen FD",
    "TDS", "Form 15G", "Form 15H",

    # Digital banking
    "Net Banking", "Mobile Banking", "UPI", "BHIM",
    "Google Pay", "PhonePe", "Paytm",
    "MMID", "VPA", "Virtual Payment Address",

    # Documents
    "Aadhaar", "PAN Card", "Voter ID", "Passport",
    "Driving Licence", "Utility Bill", "Ration Card",
    "Aadhaar Seeding", "KYC Update", "Video KYC",

    # Operations
    "Account Statement", "Mini Statement", "Passbook",
    "Balance Enquiry", "Fund Transfer", "Remittance", "Beneficiary",
    "Nominee", "Standing Instruction", "Auto Debit", "NACH",
    "Locker", "Safe Deposit Vault",

    # Compliance
    "AML", "CFT", "STR", "CTR", "NPA", "SMA",
    "Banking Ombudsman", "Grievance", "RBI",
    "PMLA", "FEMA", "Income Tax",
]

output = {
    "terms":  EXTENDED_GLOSSARY,
    "prompt": (
        "This is a banking branch conversation. "
        "Key terms: " + ", ".join(EXTENDED_GLOSSARY[:50]) + " and more. "
        "Customer may speak Marathi, Hindi, Tamil, Telugu, Bengali, or Gujarati. "
        "Staff speaks English. Transcribe with high accuracy."
    )
}

out_path = Path(__file__).parent.parent / "utils" / "banking_glossary_extended.json"
out_path.parent.mkdir(exist_ok=True)
out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))

print(f"✅ Extended glossary saved: {out_path}")
print(f"   Total terms: {len(EXTENDED_GLOSSARY)}")