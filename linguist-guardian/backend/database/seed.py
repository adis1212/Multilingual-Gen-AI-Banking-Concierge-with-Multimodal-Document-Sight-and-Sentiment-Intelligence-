"""
Seed the database with demo data for hackathon.
Run: python -m database.seed
"""
import asyncio
from database.db import create_tables, AsyncSessionLocal
from models.customer import Customer
from models.session  import Session
import uuid


DEMO_CUSTOMERS = [
    {
        "id":              "PUN-00294871",
        "name":            "Priya Sharma",
        "language":        "mr",
        "cibil_score":     762,
        "kyc_status":      "partial",
        "account_balance": 124500.00,
        "phone":           "+91-98765-43210",
        "email":           "priya.sharma@email.com",
        "meta": {
            "cards":  [{"number": "****4829", "type": "debit",  "status": "active"}],
            "loans":  [],
            "branch": "Pune Koregaon",
        }
    },
    {
        "id":              "PUN-00183042",
        "name":            "Ramesh Patil",
        "language":        "mr",
        "cibil_score":     689,
        "kyc_status":      "full",
        "account_balance": 45200.00,
        "phone":           "+91-97654-32109",
        "email":           "ramesh.patil@email.com",
        "meta": {
            "cards":  [{"number": "****2341", "type": "debit",  "status": "active"}],
            "loans":  [{"type": "home_loan", "emi": 12000, "outstanding": 850000}],
            "branch": "Pune Koregaon",
        }
    },
    {
        "id":              "CHN-00491823",
        "name":            "Kavitha Suresh",
        "language":        "ta",
        "cibil_score":     801,
        "kyc_status":      "full",
        "account_balance": 287300.00,
        "phone":           "+91-96543-21098",
        "email":           "kavitha.suresh@email.com",
        "meta": {
            "cards":  [
                {"number": "****9821", "type": "credit", "status": "active"},
                {"number": "****3312", "type": "debit",  "status": "active"},
            ],
            "loans":  [],
            "branch": "Chennai Anna Nagar",
        }
    },
]

RBI_GUIDELINES = [
    {
        "id":       "rbi-kyc-001",
        "text":     "Banks must obtain a recent photograph and proof of identity and address before opening any account. Aadhaar and PAN are acceptable as OVDs (Officially Valid Documents). Address proof must be dated within the last 3 months if showing current address.",
        "source":   "RBI KYC Master Direction 2016",
        "category": "kyc",
    },
    {
        "id":       "rbi-card-001",
        "text":     "On receiving a report of loss/theft of debit or credit card, the bank must immediately block the card. The customer should not be held liable for any unauthorized transaction if reported promptly. A new card must be issued within 7 working days.",
        "source":   "RBI Card Tokenization Guidelines 2022",
        "category": "card",
    },
    {
        "id":       "rbi-disclosure-001",
        "text":     "Banks must disclose all charges, fees, and penalties before collecting them. Processing fees for loans must be communicated upfront. Insurance products sold through bank branches must clearly state they are not bank deposits and are subject to investment risk.",
        "source":   "RBI Fair Practice Code for Lenders",
        "category": "disclosure",
    },
    {
        "id":       "rbi-grievance-001",
        "text":     "Every bank customer has the right to escalate complaints to the Banking Ombudsman if not resolved within 30 days. Staff must inform customers of the grievance redressal mechanism during any complaint interaction.",
        "source":   "RBI Banking Ombudsman Scheme 2006",
        "category": "grievance",
    },
    {
        "id":       "rbi-loan-001",
        "text":     "Customers have a cooling-off period of 3 days for retail loans to cancel without penalty. This must be communicated at the time of loan disbursement. Prepayment charges on floating rate loans are prohibited.",
        "source":   "RBI Guidelines on Reset of Floating Interest Rate 2023",
        "category": "loan",
    },
    {
        "id":       "rbi-fd-001",
        "text":     "Fixed Deposit interest rates must be displayed on the bank's website and branch notice board. Premature withdrawal is allowed with a penalty not exceeding 1% on the applicable rate. Senior citizens must be offered at least 0.25% higher interest.",
        "source":   "RBI Interest Rate Guidelines on Deposits",
        "category": "deposits",
    },
]


async def seed_customers():
    async with AsyncSessionLocal() as db:
        for data in DEMO_CUSTOMERS:
            existing = await db.get(Customer, data["id"])
            if not existing:
                customer = Customer(**data)
                db.add(customer)
                print(f"  ✅ Added customer: {data['name']}")
            else:
                print(f"  ⏭  Skipped (exists): {data['name']}")
        await db.commit()


async def seed_rbi_guidelines():
    """Ingest RBI guidelines into ChromaDB vector store."""
    try:
        from rag.vector_store import ingest_documents
        ingest_documents(RBI_GUIDELINES)
        print(f"  ✅ Ingested {len(RBI_GUIDELINES)} RBI guidelines into ChromaDB")
    except Exception as e:
        print(f"  ⚠  ChromaDB seeding skipped: {e}")


async def main():
    print("\n🌱 Seeding Linguist-Guardian database...\n")
    await create_tables()

    print("👤 Seeding customers...")
    await seed_customers()

    print("\n📚 Seeding RBI guidelines into vector store...")
    await seed_rbi_guidelines()

    print("\n✅ Database seeding complete!\n")


if __name__ == "__main__":
    asyncio.run(main())