/**
 * Banking glossary — common banking terms in Hindi, Marathi, and English.
 * Used for displaying tooltips and aiding transcription accuracy.
 */

export const BANKING_TERMS = {
    // Card related
    'कार्ड': { en: 'Card', category: 'card' },
    'डेबिट कार्ड': { en: 'Debit Card', category: 'card' },
    'क्रेडिट कार्ड': { en: 'Credit Card', category: 'card' },
    'ब्लॉक': { en: 'Block', category: 'card' },
    'पिन': { en: 'PIN', category: 'card' },

    // Account related
    'खाते': { en: 'Account', category: 'account' },
    'बचत खाते': { en: 'Savings Account', category: 'account' },
    'चालू खाते': { en: 'Current Account', category: 'account' },
    'शिल्लक': { en: 'Balance', category: 'account' },
    'जमा': { en: 'Deposit', category: 'account' },

    // Loan related
    'कर्ज': { en: 'Loan', category: 'loan' },
    'गृहकर्ज': { en: 'Home Loan', category: 'loan' },
    'व्याज दर': { en: 'Interest Rate', category: 'loan' },
    'ईएमआई': { en: 'EMI', category: 'loan' },
    'मुद्दल': { en: 'Principal', category: 'loan' },

    // KYC / Documents
    'आधार': { en: 'Aadhaar', category: 'kyc' },
    'पॅन': { en: 'PAN', category: 'kyc' },
    'केवायसी': { en: 'KYC', category: 'kyc' },
    'पासबुक': { en: 'Passbook', category: 'kyc' },

    // Transactions
    'व्यवहार': { en: 'Transaction', category: 'transaction' },
    'हस्तांतरण': { en: 'Transfer', category: 'transaction' },
    'यूपीआई': { en: 'UPI', category: 'transaction' },
    'एनईएफटी': { en: 'NEFT', category: 'transaction' },
    'आरटीजीएस': { en: 'RTGS', category: 'transaction' },

    // FD related
    'मुदत ठेव': { en: 'Fixed Deposit', category: 'fd' },
    'आवर्ती ठेव': { en: 'Recurring Deposit', category: 'fd' },
    'परिपक्वता': { en: 'Maturity', category: 'fd' },

    // General
    'तक्रार': { en: 'Complaint', category: 'general' },
    'शाखा': { en: 'Branch', category: 'general' },
    'व्यवस्थापक': { en: 'Manager', category: 'general' },
    'टोकन': { en: 'Token', category: 'general' },
}

/**
 * Look up the English meaning of a banking term.
 */
export function lookupTerm(term) {
    return BANKING_TERMS[term]?.en || null
}

/**
 * Get all terms in a specific category.
 */
export function getTermsByCategory(category) {
    return Object.entries(BANKING_TERMS)
        .filter(([, v]) => v.category === category)
        .map(([term, v]) => ({ term, ...v }))
}

/**
 * Get all unique categories.
 */
export function getCategories() {
    return [...new Set(Object.values(BANKING_TERMS).map(v => v.category))]
}
