/**
 * Frontend property-based tests for Branch Concierge Orchestrator
 * Properties 15–18 using fast-check + @fast-check/vitest + @testing-library/react
 */
import { describe, expect, vi, beforeEach, afterEach } from 'vitest'
import { it, fc } from '@fast-check/vitest'
import { render, screen, act, renderHook, waitFor } from '@testing-library/react'
import React from 'react'

// ---------------------------------------------------------------------------
// Module mocks — must be declared before any imports that use them
// ---------------------------------------------------------------------------

vi.mock('@/store/orchestratorStore', () => ({
  useOrchestratorStore: vi.fn(),
}))

vi.mock('@/store/sessionStore', () => ({
  useSessionStore: vi.fn(),
}))

vi.mock('@/store/sentimentStore', () => ({
  useSentimentStore: vi.fn(),
}))

vi.mock('@/services/orchestratorService', () => ({
  routeConversation: vi.fn(),
}))

vi.mock('react-hot-toast', () => ({
  default: { error: vi.fn(), success: vi.fn() },
  error: vi.fn(),
  success: vi.fn(),
}))

// ---------------------------------------------------------------------------
// Lazy imports (after mocks are registered)
// ---------------------------------------------------------------------------
import { useOrchestratorStore } from '@/store/orchestratorStore'
import { useSessionStore } from '@/store/sessionStore'
import { useSentimentStore } from '@/store/sentimentStore'
import { routeConversation } from '@/services/orchestratorService'
import toast from 'react-hot-toast'
import RoutingDecisionPanel from '@/components/routing/RoutingDecisionPanel'
import { useWebSocket } from '@/hooks/useWebSocket'

// ---------------------------------------------------------------------------
// Arbitraries
// ---------------------------------------------------------------------------

const VALID_AGENTS = [
  'CUSTOMER_SERVICE_AGENT',
  'DOCUMENT_VERIFICATION_AGENT',
  'QUEUE_MANAGEMENT_AGENT',
  'COMPLIANCE_MONITOR_AGENT',
]

const VALID_URGENCIES = ['low', 'medium', 'high']

/** Generates a non-empty, non-whitespace-only string (realistic field values) */
const nonBlankStringArb = (maxLength = 50) =>
  fc
    .string({ minLength: 1, maxLength })
    .filter((s) => s.trim().length > 0)

/** Generates a valid RoutingDecision object */
const routingDecisionArb = fc.record({
  intent: nonBlankStringArb(50),
  agent: fc.constantFrom(...VALID_AGENTS),
  urgency: fc.constantFrom(...VALID_URGENCIES),
  recommended_action: nonBlankStringArb(100),
})

// ---------------------------------------------------------------------------
// Helper: configure the orchestratorStore mock to return a given state
// Zustand hooks are called as: useStore(selector) or useStore.getState()
// We need to handle both the selector-based call and direct state access.
// ---------------------------------------------------------------------------
function makeOrchestratorState(overrides = {}) {
  return {
    decision: null,
    loading: false,
    error: null,
    setDecision: vi.fn(),
    setLoading: vi.fn(),
    setError: vi.fn(),
    reset: vi.fn(),
    ...overrides,
  }
}

function mockOrchestratorStore(state) {
  const fullState = makeOrchestratorState(state)
  useOrchestratorStore.mockImplementation((selector) => {
    if (typeof selector === 'function') return selector(fullState)
    return fullState
  })
  useOrchestratorStore.getState = vi.fn(() => fullState)
  return fullState
}

// ---------------------------------------------------------------------------
// Helper: build a WebSocket mock that is usable as a constructor
// ---------------------------------------------------------------------------
function makeWsMock() {
  const instance = {
    send: vi.fn(),
    close: vi.fn(),
    readyState: 1, // OPEN
    onopen: null,
    onmessage: null,
    onerror: null,
    onclose: null,
  }

  // Must be a real function (not arrow) so `new` works
  function MockWebSocket() {
    Object.assign(this, instance)
    // Keep a reference so tests can trigger events
    MockWebSocket._instance = this
  }
  MockWebSocket._instance = null

  return MockWebSocket
}

// ---------------------------------------------------------------------------
// Property 15: RoutingDecisionPanel renders all three decision fields
// ---------------------------------------------------------------------------
describe('Property 15: RoutingDecisionPanel renders all three decision fields', () => {
  // Feature: branch-concierge-orchestrator, Property 15: RoutingDecisionPanel renders all three decision fields

  it.prop([routingDecisionArb], { numRuns: 50 })(
    'renders agent, urgency, and recommended_action for any valid RoutingDecision',
    (decision) => {
      mockOrchestratorStore({ decision, loading: false, error: null })

      const { container, unmount } = render(<RoutingDecisionPanel />)

      const bodyText = container.textContent || ''

      // Agent value should appear (component replaces _ with space)
      const agentText = decision.agent.replace(/_/g, ' ')
      expect(bodyText).toContain(agentText)

      // Urgency value should appear
      expect(bodyText).toContain(decision.urgency)

      // Recommended action should appear (trim to handle leading/trailing whitespace)
      expect(bodyText).toContain(decision.recommended_action.trim())

      unmount()
    }
  )
})

// ---------------------------------------------------------------------------
// Property 16: Urgency indicator styling matches urgency value
// ---------------------------------------------------------------------------
describe('Property 16: Urgency indicator styling matches urgency value', () => {
  // Feature: branch-concierge-orchestrator, Property 16: Urgency indicator styling matches urgency value

  const urgencyClassMap = {
    high: 'border-red-500',
    medium: 'border-amber-500',
    low: 'border-gray-300',
  }

  it.prop([fc.constantFrom(...VALID_URGENCIES)], { numRuns: 30 })(
    'applies correct border CSS class for each urgency level',
    (urgency) => {
      const decision = {
        intent: 'test-intent',
        agent: 'CUSTOMER_SERVICE_AGENT',
        urgency,
        recommended_action: 'Test action',
      }

      mockOrchestratorStore({ decision, loading: false, error: null })

      const { container, unmount } = render(<RoutingDecisionPanel />)

      const expectedClass = urgencyClassMap[urgency]
      const styledDiv = container.querySelector(`.${expectedClass}`)
      expect(styledDiv).not.toBeNull()

      unmount()
    }
  )
})

// ---------------------------------------------------------------------------
// Property 17: WebSocket transcript events trigger orchestrate API call
// ---------------------------------------------------------------------------
describe('Property 17: WebSocket transcript events trigger orchestrate API call', () => {
  // Feature: branch-concierge-orchestrator, Property 17: WebSocket transcript events trigger orchestrate API call

  let originalWebSocket
  let MockWS

  beforeEach(() => {
    originalWebSocket = global.WebSocket
  })

  afterEach(() => {
    global.WebSocket = originalWebSocket
    vi.clearAllMocks()
  })

  it.prop(
    [
      fc.string({ minLength: 1, maxLength: 80 }),
      fc.constantFrom('en', 'hi', 'mr', 'ta'),
      fc.string({ minLength: 1, maxLength: 20 }),
    ],
    { numRuns: 20 }
  )(
    'routeConversation is called with transcript text, language, sessionId, and sentiment after a transcript event',
    async (transcriptText, language, sessionId) => {
      vi.clearAllMocks()

      // Fresh WS mock for each run
      MockWS = makeWsMock()
      global.WebSocket = MockWS

      routeConversation.mockResolvedValue({
        intent: 'test',
        agent: 'QUEUE_MANAGEMENT_AGENT',
        urgency: 'low',
        recommended_action: 'Test',
      })

      const sentimentState = {
        emotion: 'neutral',
        stressLevel: 0,
        updateSentiment: vi.fn(),
      }
      useSentimentStore.mockImplementation((selector) => {
        if (typeof selector === 'function') return selector(sentimentState)
        return sentimentState
      })
      useSentimentStore.getState = vi.fn(() => sentimentState)

      useSessionStore.mockImplementation((selector) => {
        const state = { messages: [], addMessage: vi.fn() }
        if (typeof selector === 'function') return selector(state)
        return state
      })

      const orchestratorState = makeOrchestratorState()
      useOrchestratorStore.mockImplementation((selector) => {
        if (typeof selector === 'function') return selector(orchestratorState)
        return orchestratorState
      })
      useOrchestratorStore.getState = vi.fn(() => orchestratorState)

      const { unmount } = renderHook(() => useWebSocket(sessionId))

      // Simulate a transcript WebSocket message
      await act(async () => {
        const wsInstance = MockWS._instance
        if (wsInstance && wsInstance.onmessage) {
          wsInstance.onmessage({
            data: JSON.stringify({
              type: 'transcript',
              text: transcriptText,
              language,
              channel: 'A',
            }),
          })
        }
      })

      await waitFor(() => {
        expect(routeConversation).toHaveBeenCalledWith(
          transcriptText,
          language,
          sessionId,
          null // neutral sentiment → null signal
        )
      })

      unmount()
    }
  )
})

// ---------------------------------------------------------------------------
// Property 18: Orchestrator API failure shows toast and preserves conversation
// ---------------------------------------------------------------------------
describe('Property 18: Orchestrator API failure shows toast and preserves conversation', () => {
  // Feature: branch-concierge-orchestrator, Property 18: Orchestrator API failure shows toast and preserves conversation

  let originalWebSocket
  let MockWS

  beforeEach(() => {
    originalWebSocket = global.WebSocket
  })

  afterEach(() => {
    global.WebSocket = originalWebSocket
    vi.clearAllMocks()
  })

  it.prop(
    [
      fc.string({ minLength: 1, maxLength: 80 }),
      fc.string({ minLength: 1, maxLength: 20 }),
      fc.array(
        fc.record({
          id: fc.string({ minLength: 1, maxLength: 10 }),
          speaker: fc.constantFrom('customer', 'staff'),
          text: fc.string({ minLength: 1, maxLength: 50 }),
        }),
        { minLength: 0, maxLength: 5 }
      ),
    ],
    { numRuns: 20 }
  )(
    'toast.error is called and setDecision is not called when routeConversation throws',
    async (transcriptText, sessionId, existingMessages) => {
      vi.clearAllMocks()

      MockWS = makeWsMock()
      global.WebSocket = MockWS

      routeConversation.mockRejectedValue(new Error('Network Error'))

      useSessionStore.mockImplementation((selector) => {
        const state = { messages: existingMessages, addMessage: vi.fn() }
        if (typeof selector === 'function') return selector(state)
        return state
      })

      const sentimentState = {
        emotion: 'neutral',
        stressLevel: 0,
        updateSentiment: vi.fn(),
      }
      useSentimentStore.mockImplementation((selector) => {
        if (typeof selector === 'function') return selector(sentimentState)
        return sentimentState
      })
      useSentimentStore.getState = vi.fn(() => sentimentState)

      const setDecision = vi.fn()
      const setError = vi.fn()
      const setLoading = vi.fn()
      const orchestratorState = {
        decision: null,
        loading: false,
        error: null,
        setDecision,
        setLoading,
        setError,
        reset: vi.fn(),
      }
      useOrchestratorStore.mockImplementation((selector) => {
        if (typeof selector === 'function') return selector(orchestratorState)
        return orchestratorState
      })
      useOrchestratorStore.getState = vi.fn(() => orchestratorState)

      const { unmount } = renderHook(() => useWebSocket(sessionId))

      await act(async () => {
        const wsInstance = MockWS._instance
        if (wsInstance && wsInstance.onmessage) {
          wsInstance.onmessage({
            data: JSON.stringify({
              type: 'transcript',
              text: transcriptText,
              language: 'en',
              channel: 'A',
            }),
          })
        }
      })

      await waitFor(() => {
        expect(toast.error).toHaveBeenCalled()
      })

      // setDecision must NOT have been called — conversation state is preserved
      expect(setDecision).not.toHaveBeenCalled()

      unmount()
    }
  )
})
