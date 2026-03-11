import { useRef, useState, useCallback } from 'react'
import { useSessionStore } from '@/store/sessionStore'

const CHUNK_INTERVAL_MS = 3000   // send a chunk every 3 seconds

export function useAudioCapture({ onChunk, language = 'mr' }) {
  const [isRecording, setIsRecording]   = useState(false)
  const [error, setError]               = useState(null)
  const mediaRecorderRef = useRef(null)
  const chunksRef        = useRef([])
  const intervalRef      = useRef(null)
  const setStoreRecording = useSessionStore(s => s.setRecording)

  const startRecording = useCallback(async (channel = 'A') => {
    try {
      setError(null)

      // Request mic — for dual-mic, deviceId can be passed
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          sampleRate: 44100,
        }
      })

      const recorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      })

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data)
      }

      recorder.start(CHUNK_INTERVAL_MS)
      mediaRecorderRef.current = recorder

      // Every 3s, grab accumulated chunks, convert to base64, send
      intervalRef.current = setInterval(async () => {
        if (chunksRef.current.length === 0) return

        const blob   = new Blob(chunksRef.current, { type: 'audio/webm' })
        chunksRef.current = []

        const buffer = await blob.arrayBuffer()
        const bytes  = new Uint8Array(buffer)
        const b64    = btoa(String.fromCharCode(...bytes))

        onChunk?.(b64, channel, language)
      }, CHUNK_INTERVAL_MS)

      setIsRecording(true)
      setStoreRecording(true)

    } catch (err) {
      setError(err.message)
      console.error('Mic access error:', err)
    }
  }, [onChunk, language, setStoreRecording])

  const stopRecording = useCallback(() => {
    clearInterval(intervalRef.current)
    mediaRecorderRef.current?.stop()
    mediaRecorderRef.current?.stream.getTracks().forEach(t => t.stop())
    mediaRecorderRef.current = null
    chunksRef.current = []
    setIsRecording(false)
    setStoreRecording(false)
  }, [setStoreRecording])

  return { isRecording, error, startRecording, stopRecording }
}