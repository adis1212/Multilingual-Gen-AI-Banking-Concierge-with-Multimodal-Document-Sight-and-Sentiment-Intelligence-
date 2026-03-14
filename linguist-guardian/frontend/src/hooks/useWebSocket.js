import { useEffect, useRef, useCallback } from 'react'
import toast from 'react-hot-toast'
import { useSessionStore }      from '@/store/sessionStore'
import { useSentimentStore }    from '@/store/sentimentStore'
import { useOrchestratorStore } from '@/store/orchestratorStore'
import { routeConversation }    from '@/services/orchestratorService'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useWebSocket(sessionId) {
  const ws              = useRef(null)
  const addMessage      = useSessionStore(s => s.addMessage)
  const updateSentiment = useSentimentStore(s => s.updateSentiment)
  const setDecision     = useOrchestratorStore(s => s.setDecision)
  const setLoading      = useOrchestratorStore(s => s.setLoading)
  const setError        = useOrchestratorStore(s => s.setError)

  const connect = useCallback(() => {
    if (!sessionId) return
    ws.current = new WebSocket(`${WS_URL}/ws/audio/${sessionId}`)

    ws.current.onopen = () => {
      console.log('✅ WebSocket connected')
    }

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data)

      // Transcription result
      if (data.type === 'transcript' && data.text) {
        addMessage({
          speaker:     data.channel === 'A' ? 'customer' : 'staff',
          channel:     data.channel,
          text:        data.text,
          translation: data.translation || '',
          language:    data.language,
          intent:      data.intent || null,
        })

        // Route conversation via orchestrator
        const sentiment = useSentimentStore.getState()
        const sentimentSignal = sentiment.emotion !== 'neutral' || sentiment.stressLevel > 0
          ? { emotion: sentiment.emotion, stress_level: sentiment.stressLevel }
          : null

        setLoading(true)
        setError(null)
        routeConversation(data.text, data.language || 'en', sessionId, sentimentSignal)
          .then((decision) => {
            setDecision(decision)
          })
          .catch((err) => {
            setError(err?.message || 'Routing failed')
            toast.error('Could not determine routing — please check the customer manually.')
          })
          .finally(() => {
            setLoading(false)
          })
      }

      // Sentiment update
      if (data.sentiment) {
        updateSentiment(data.sentiment)
      }
    }

    ws.current.onerror = (e) => console.error('WS error:', e)
    ws.current.onclose = () => console.log('WS closed')
  }, [sessionId, addMessage, updateSentiment])

  const sendAudioChunk = useCallback((base64Audio, channel = 'A', language = 'mr') => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        channel,
        language,
        audio_chunk: base64Audio,
      }))
    }
  }, [])

  const disconnect = useCallback(() => {
    ws.current?.close()
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return { sendAudioChunk, disconnect, reconnect: connect }
}