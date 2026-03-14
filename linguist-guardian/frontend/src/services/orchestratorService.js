import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

/**
 * Route a customer conversation to the appropriate agent.
 * @param {string}      transcript – transcript text from the WebSocket
 * @param {string}      language   – ISO 639-1 language code
 * @param {string|null} sessionId  – active session id (optional)
 * @param {object|null} sentiment  – sentiment signal {emotion, stress_level} (optional)
 * @returns {Promise<{intent: string, agent: string, urgency: string, recommended_action: string}>}
 */
export async function routeConversation(transcript, language = 'en', sessionId = null, sentiment = null) {
  const { data } = await axios.post(`${API_URL}/api/orchestrate`, {
    transcript,
    language,
    session_id: sessionId,
    sentiment,
  })
  return data
}
