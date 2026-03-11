import { useCallback } from 'react'
import axios from 'axios'
import { useSentimentStore } from '@/store/sentimentStore'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useSentimentAnalysis() {
  const updateSentiment = useSentimentStore(s => s.updateSentiment)

  const analyzeAudio = useCallback(async (audioBlob) => {
    try {
      const formData = new FormData()
      formData.append('audio', audioBlob, 'chunk.webm')

      const res = await axios.post(`${API_URL}/api/sentiment/analyze`, formData)
      updateSentiment(res.data)
      return res.data
    } catch (err) {
      console.error('Sentiment analysis failed:', err.message)
      return null
    }
  }, [updateSentiment])

  return { analyzeAudio }
}