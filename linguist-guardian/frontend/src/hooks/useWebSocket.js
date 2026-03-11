import { useEffect, useRef, useCallback } from 'react'
import { useSessionStore }   from '@/store/sessionStore'
import { useSentimentStore } from '@/store/sentimentStore'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export function useWebSocket(sessionId) {
  const ws            = useRef(null)
  const addMessage    = useSessionStore(s => s.addMessage)
  const updateSentiment = useSentimentStore(s => s.updateSentiment)

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