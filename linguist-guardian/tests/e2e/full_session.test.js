/**
 * E2E Test — Full Session Flow
 *
 * Tests the complete lifecycle:
 * 1. Create a session
 * 2. Send audio for transcription
 * 3. Extract intent
 * 4. Check compliance
 * 5. Close session and get summary
 *
 * NOTE: Requires backend running on http://localhost:8000
 * Run with: npx jest tests/e2e/full_session.test.js
 */

const API_URL = process.env.API_URL || 'http://localhost:8000'

// Helper to make API calls
async function api(path, options = {}) {
    const res = await fetch(`${API_URL}${path}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options,
    })
    return res.json()
}

describe('Full Session Flow', () => {
    let sessionId = null

    test('Health check should return ok', async () => {
        const data = await api('/health')
        expect(data.status).toBe('ok')
        expect(data.service).toBe('linguist-guardian')
    })

    test('Create a new session', async () => {
        const data = await api('/api/session/create', {
            method: 'POST',
            body: JSON.stringify({
                customer_id: 'PUN-00294871',
                staff_id: 'staff-001',
                branch_id: 'pune-koregaon',
                token_number: 'Q-14',
            }),
        })

        expect(data.session_id).toBeDefined()
        expect(data.status).toBe('active')
        sessionId = data.session_id
    })

    test('Extract intent from transcript', async () => {
        const data = await api('/api/intent/extract', {
            method: 'POST',
            body: JSON.stringify({
                transcript: 'I lost my credit card and I am very worried',
                language: 'en',
                customer_context: {},
                session_id: sessionId || 'test-session',
            }),
        })

        expect(data.intent).toBeDefined()
        expect(data.urgency).toBeDefined()
        expect(data.emotion).toBeDefined()
    })

    test('Compliance check on staff utterance', async () => {
        const data = await api('/api/intent/compliance', {
            method: 'POST',
            body: JSON.stringify({
                staff_utterance: "Don't worry, we will block your card immediately.",
                session_id: sessionId || 'test-session',
            }),
        })

        expect(data).toHaveProperty('compliant')
        expect(data).toHaveProperty('severity')
    })

    test('Get TTS supported languages', async () => {
        const data = await api('/api/tts/languages')
        expect(data.languages).toBeDefined()
        expect(data.languages.length).toBeGreaterThan(0)
        expect(data.languages[0]).toHaveProperty('code')
        expect(data.languages[0]).toHaveProperty('name')
    })

    test('Close session and get summary', async () => {
        if (!sessionId) return

        const data = await api('/api/session/close', {
            method: 'POST',
            body: JSON.stringify({ session_id: sessionId }),
        })

        expect(data.status).toBe('closed')
        expect(data.summary).toBeDefined()
    })
})
