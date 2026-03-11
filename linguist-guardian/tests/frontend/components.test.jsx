/**
 * Frontend Component Tests
 *
 * Basic smoke tests for key React components.
 * Run with: npx vitest tests/frontend/components.test.jsx
 */
import { describe, test, expect, vi } from 'vitest'

// ── Mock modules before importing components ──
vi.mock('@/store/customerStore', () => ({
    useCustomerStore: vi.fn(() => ({
        customer: {
            id: 'PUN-00294871',
            name: 'Priya Sharma',
            cibil_score: 742,
            account_balance: 128500,
            kyc_status: 'full',
            language: 'mr',
        },
        isLoading: false,
        loadCustomer: vi.fn(),
    })),
}))

vi.mock('@/store/sessionStore', () => ({
    useSessionStore: vi.fn((selector) => {
        const state = {
            sessionId: 'test-session',
            messages: [],
            addMessage: vi.fn(),
            startSession: vi.fn(),
            setRecording: vi.fn(),
            isRecording: false,
        }
        return typeof selector === 'function' ? selector(state) : state
    }),
}))

vi.mock('@/store/sentimentStore', () => ({
    useSentimentStore: vi.fn(() => ({
        stressLevel: 0.45,
        pitchRisePct: 12,
        speechRate: 'normal',
        volume: 'medium',
        emotion: 'neutral',
        deescalate: false,
        tips: [],
        history: [],
        updateSentiment: vi.fn(),
    })),
}))

// ── Tests ──
describe('Component Smoke Tests', () => {
    test('bankingGlossary exports terms', async () => {
        const { BANKING_TERMS, lookupTerm, getCategories } = await import('@/utils/bankingGlossary')
        expect(Object.keys(BANKING_TERMS).length).toBeGreaterThan(10)
        expect(lookupTerm('खाते')).toBe('Account')
        expect(getCategories()).toContain('account')
    })

    test('formatCurrency formats INR correctly', async () => {
        const { formatINR, parseINR } = await import('@/utils/formatCurrency')

        // Standard format
        const formatted = formatINR(123456)
        expect(formatted).toContain('1,23,456')

        // Compact format
        expect(formatINR(1500000, { compact: true })).toContain('L')
        expect(formatINR(15000000, { compact: true })).toContain('Cr')

        // Parse back
        expect(parseINR('₹1,23,456.00')).toBe(123456)
    })

    test('languageDetect detects Devanagari', async () => {
        const { detectLanguage, isDevanagari } = await import('@/utils/languageDetect')

        const result = detectLanguage('मला माझे कार्ड हरवले आहे')
        expect(result).not.toBeNull()
        expect(['hi', 'mr'].includes(result.code)).toBe(true)

        expect(isDevanagari('Hello World')).toBe(false)
        expect(isDevanagari('नमस्कार')).toBe(true)
    })

    test('languageDetect detects Tamil', async () => {
        const { detectLanguage } = await import('@/utils/languageDetect')
        const result = detectLanguage('வணக்கம் நன்றி')
        expect(result.code).toBe('ta')
    })

    test('languageDetect returns English for Latin text', async () => {
        const { detectLanguage } = await import('@/utils/languageDetect')
        const result = detectLanguage('I want to check my balance')
        expect(result.code).toBe('en')
    })
})
